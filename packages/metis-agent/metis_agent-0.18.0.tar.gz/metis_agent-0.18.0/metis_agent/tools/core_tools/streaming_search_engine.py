#!/usr/bin/env python3
"""
Real-Time Streaming Search Engine
Provides asynchronous search with live result streaming and cancellation support.
"""

import asyncio
import threading
import queue
import time
from typing import Dict, List, Any, Optional, Generator, Callable, Union, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from dataclasses import dataclass, asdict
from datetime import datetime
import os
import signal
from enum import Enum

try:
    from ..core_tools.enhanced_search_tool import SearchResult
except ImportError:
    # Fallback if import fails
    from dataclasses import dataclass
    
    @dataclass
    class SearchResult:
        file_path: str
        matches: List[Dict[str, Any]]
        relevance_score: float = 0.0
        context_type: str = "text"
        language: Optional[str] = None
        encoding: str = "utf-8"
        total_lines: int = 0
        error: Optional[str] = None


class StreamingStatus(Enum):
    """Status of streaming search operation"""
    INITIALIZING = "initializing"
    SCANNING = "scanning"
    SEARCHING = "searching"
    FILTERING = "filtering"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass
class SearchProgress:
    """Progress information for streaming search"""
    status: StreamingStatus
    files_scanned: int = 0
    files_searched: int = 0
    files_with_matches: int = 0
    total_matches: int = 0
    current_file: Optional[str] = None
    elapsed_time: float = 0.0
    estimated_remaining: Optional[float] = None
    error_message: Optional[str] = None


@dataclass
class StreamingSearchResult:
    """Result object for streaming search"""
    result: Optional[SearchResult] = None
    progress: Optional[SearchProgress] = None
    is_final: bool = False
    metadata: Dict[str, Any] = None


class CancellationToken:
    """Token for cancelling search operations"""
    
    def __init__(self):
        self._cancelled = threading.Event()
        self._callbacks = []
    
    def cancel(self):
        """Cancel the operation"""
        self._cancelled.set()
        
        # Execute cancellation callbacks
        for callback in self._callbacks:
            try:
                callback()
            except Exception:
                pass  # Ignore callback errors
    
    def is_cancelled(self) -> bool:
        """Check if operation is cancelled"""
        return self._cancelled.is_set()
    
    def add_cancellation_callback(self, callback: Callable):
        """Add callback to execute on cancellation"""
        self._callbacks.append(callback)


class SearchMetrics:
    """Tracks search performance metrics"""
    
    def __init__(self):
        self.start_time = time.time()
        self.files_processed = 0
        self.total_file_size = 0
        self.search_errors = 0
        self.peak_memory_usage = 0
        self.processing_times = []
    
    def record_file_processed(self, file_path: str, processing_time: float, error: bool = False):
        """Record file processing metrics"""
        self.files_processed += 1
        self.processing_times.append(processing_time)
        
        if error:
            self.search_errors += 1
        
        try:
            self.total_file_size += os.path.getsize(file_path)
        except OSError:
            pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        elapsed = time.time() - self.start_time
        avg_time = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
        
        return {
            'elapsed_time': elapsed,
            'files_processed': self.files_processed,
            'total_file_size_mb': self.total_file_size / (1024 * 1024),
            'files_per_second': self.files_processed / elapsed if elapsed > 0 else 0,
            'avg_processing_time': avg_time,
            'error_rate': self.search_errors / max(self.files_processed, 1),
            'total_errors': self.search_errors
        }


class LiveResultFilter:
    """Filters and ranks search results in real-time"""
    
    def __init__(self, max_results: int = 100, min_relevance: float = 0.1):
        self.max_results = max_results
        self.min_relevance = min_relevance
        self.results_buffer = []
        self.seen_files = set()
        self.filter_lock = threading.Lock()
    
    def add_result(self, result: SearchResult) -> bool:
        """Add result to filter buffer, returns True if result should be yielded"""
        with self.filter_lock:
            # Skip duplicates
            if result.file_path in self.seen_files:
                return False
            
            # Skip low-relevance results
            if result.relevance_score < self.min_relevance:
                return False
            
            self.seen_files.add(result.file_path)
            
            # Add to buffer
            self.results_buffer.append(result)
            
            # Sort buffer by relevance
            self.results_buffer.sort(key=lambda r: r.relevance_score, reverse=True)
            
            # Trim buffer if too large
            if len(self.results_buffer) > self.max_results:
                self.results_buffer = self.results_buffer[:self.max_results]
            
            return True
    
    def get_top_results(self, limit: int = None) -> List[SearchResult]:
        """Get top results from buffer"""
        with self.filter_lock:
            limit = limit or len(self.results_buffer)
            return self.results_buffer[:limit]
    
    def clear(self):
        """Clear filter state"""
        with self.filter_lock:
            self.results_buffer.clear()
            self.seen_files.clear()


class StreamingSearchEngine:
    """Core streaming search engine with real-time capabilities"""
    
    def __init__(self, max_workers: int = 4, buffer_size: int = 1000):
        self.max_workers = max_workers
        self.buffer_size = buffer_size
        self.active_searches = {}  # Track active search operations
    
    def search_stream(self, 
                     search_function: Callable[[str], SearchResult],
                     file_list: List[str],
                     cancellation_token: CancellationToken,
                     progress_callback: Optional[Callable[[SearchProgress], None]] = None,
                     result_callback: Optional[Callable[[SearchResult], None]] = None) -> Generator[StreamingSearchResult, None, None]:
        """
        Stream search results in real-time
        
        Args:
            search_function: Function to search individual files
            file_list: List of files to search
            cancellation_token: Token for cancelling operation
            progress_callback: Optional callback for progress updates
            result_callback: Optional callback for individual results
            
        Yields:
            StreamingSearchResult objects with results or progress updates
        """
        search_id = id(cancellation_token)
        metrics = SearchMetrics()
        filter = LiveResultFilter()
        
        try:
            self.active_searches[search_id] = {
                'token': cancellation_token,
                'metrics': metrics,
                'filter': filter
            }
            
            # Initial progress
            progress = SearchProgress(
                status=StreamingStatus.INITIALIZING,
                files_scanned=len(file_list)
            )
            
            if progress_callback:
                progress_callback(progress)
            
            yield StreamingSearchResult(progress=progress)
            
            # Start searching
            progress.status = StreamingStatus.SEARCHING
            if progress_callback:
                progress_callback(progress)
            
            yield StreamingSearchResult(progress=progress)
            
            # Use ThreadPoolExecutor for concurrent file processing
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all file search tasks
                future_to_file = {}
                
                for file_path in file_list:
                    if cancellation_token.is_cancelled():
                        break
                    
                    future = executor.submit(self._search_file_with_metrics, 
                                           search_function, file_path, metrics, cancellation_token)
                    future_to_file[future] = file_path
                
                # Process results as they complete
                for future in as_completed(future_to_file):
                    if cancellation_token.is_cancelled():
                        # Cancel remaining futures
                        for f in future_to_file:
                            if not f.done():
                                f.cancel()
                        break
                    
                    file_path = future_to_file[future]
                    
                    try:
                        result = future.result(timeout=1.0)  # Short timeout for responsiveness
                        
                        if result and result.matches:
                            # Filter result
                            if filter.add_result(result):
                                # Update progress
                                progress.files_searched += 1
                                progress.files_with_matches += 1
                                progress.total_matches += len(result.matches)
                                progress.current_file = file_path
                                progress.elapsed_time = time.time() - metrics.start_time
                                
                                # Estimate remaining time
                                if progress.files_searched > 0:
                                    avg_time_per_file = progress.elapsed_time / progress.files_searched
                                    remaining_files = len(file_list) - progress.files_searched
                                    progress.estimated_remaining = avg_time_per_file * remaining_files
                                
                                if progress_callback:
                                    progress_callback(progress)
                                
                                if result_callback:
                                    result_callback(result)
                                
                                # Yield result
                                yield StreamingSearchResult(
                                    result=result,
                                    progress=progress,
                                    metadata={'search_stats': metrics.get_stats()}
                                )
                        else:
                            # File processed but no matches
                            progress.files_searched += 1
                            progress.current_file = file_path
                            progress.elapsed_time = time.time() - metrics.start_time
                    
                    except Exception as e:
                        # Handle individual file errors
                        metrics.record_file_processed(file_path, 0.0, error=True)
                        progress.files_searched += 1
                        
                        # Yield error result
                        error_result = SearchResult(
                            file_path=file_path,
                            matches=[],
                            error=str(e)
                        )
                        
                        yield StreamingSearchResult(
                            result=error_result,
                            progress=progress
                        )
            
            # Final progress update
            if cancellation_token.is_cancelled():
                progress.status = StreamingStatus.CANCELLED
            else:
                progress.status = StreamingStatus.COMPLETED
            
            progress.elapsed_time = time.time() - metrics.start_time
            
            if progress_callback:
                progress_callback(progress)
            
            # Final result with complete statistics
            yield StreamingSearchResult(
                progress=progress,
                is_final=True,
                metadata={
                    'final_stats': metrics.get_stats(),
                    'top_results': [asdict(r) for r in filter.get_top_results(10)]
                }
            )
        
        except Exception as e:
            # Handle search engine errors
            progress = SearchProgress(
                status=StreamingStatus.ERROR,
                error_message=str(e),
                elapsed_time=time.time() - metrics.start_time
            )
            
            yield StreamingSearchResult(
                progress=progress,
                is_final=True,
                metadata={'error': str(e)}
            )
        
        finally:
            # Cleanup
            if search_id in self.active_searches:
                del self.active_searches[search_id]
    
    def _search_file_with_metrics(self, search_function: Callable, file_path: str, 
                                 metrics: SearchMetrics, cancellation_token: CancellationToken) -> Optional[SearchResult]:
        """Search individual file with metrics tracking"""
        if cancellation_token.is_cancelled():
            return None
        
        start_time = time.time()
        
        try:
            result = search_function(file_path)
            processing_time = time.time() - start_time
            
            metrics.record_file_processed(file_path, processing_time, error=result and result.error is not None)
            
            return result
        
        except Exception as e:
            processing_time = time.time() - start_time
            metrics.record_file_processed(file_path, processing_time, error=True)
            
            return SearchResult(
                file_path=file_path,
                matches=[],
                error=str(e)
            )
    
    def cancel_search(self, search_id: int):
        """Cancel active search by ID"""
        if search_id in self.active_searches:
            self.active_searches[search_id]['token'].cancel()
    
    def get_active_searches(self) -> List[Dict[str, Any]]:
        """Get information about active searches"""
        active = []
        
        for search_id, search_info in self.active_searches.items():
            active.append({
                'search_id': search_id,
                'cancelled': search_info['token'].is_cancelled(),
                'stats': search_info['metrics'].get_stats(),
                'top_results_count': len(search_info['filter'].get_top_results())
            })
        
        return active


class SearchResultBuffer:
    """Thread-safe buffer for collecting streaming results"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.buffer = queue.Queue(maxsize=max_size)
        self.results = []
        self.lock = threading.Lock()
        self.closed = False
    
    def add_result(self, result: StreamingSearchResult):
        """Add result to buffer"""
        if self.closed:
            return
        
        try:
            self.buffer.put_nowait(result)
        except queue.Full:
            # Buffer full, remove oldest result
            try:
                self.buffer.get_nowait()
                self.buffer.put_nowait(result)
            except queue.Empty:
                pass
    
    def get_results(self, timeout: float = 0.1) -> List[StreamingSearchResult]:
        """Get available results from buffer"""
        results = []
        
        while True:
            try:
                result = self.buffer.get(timeout=timeout)
                results.append(result)
                
                if result.is_final:
                    break
                    
            except queue.Empty:
                break
        
        return results
    
    def close(self):
        """Close buffer"""
        self.closed = True
    
    def is_empty(self) -> bool:
        """Check if buffer is empty"""
        return self.buffer.empty()


class StreamingSearchManager:
    """High-level manager for streaming search operations"""
    
    def __init__(self, max_concurrent_searches: int = 2):
        self.max_concurrent_searches = max_concurrent_searches
        self.search_engine = StreamingSearchEngine()
        self.active_operations = {}
        self.operation_counter = 0
        self.lock = threading.Lock()
    
    def start_search(self, 
                    search_function: Callable,
                    file_list: List[str],
                    progress_callback: Optional[Callable] = None,
                    result_callback: Optional[Callable] = None) -> Tuple[int, CancellationToken]:
        """
        Start new streaming search operation
        
        Returns:
            Tuple of (operation_id, cancellation_token)
        """
        with self.lock:
            if len(self.active_operations) >= self.max_concurrent_searches:
                raise RuntimeError("Maximum number of concurrent searches reached")
            
            self.operation_counter += 1
            operation_id = self.operation_counter
            
            cancellation_token = CancellationToken()
            result_buffer = SearchResultBuffer()
            
            # Start search in background thread
            search_thread = threading.Thread(
                target=self._run_search,
                args=(operation_id, search_function, file_list, cancellation_token, 
                     result_buffer, progress_callback, result_callback),
                daemon=True
            )
            
            self.active_operations[operation_id] = {
                'thread': search_thread,
                'token': cancellation_token,
                'buffer': result_buffer,
                'start_time': time.time(),
                'file_count': len(file_list)
            }
            
            search_thread.start()
            
            return operation_id, cancellation_token
    
    def _run_search(self, operation_id: int, search_function: Callable, file_list: List[str],
                   cancellation_token: CancellationToken, result_buffer: SearchResultBuffer,
                   progress_callback: Optional[Callable], result_callback: Optional[Callable]):
        """Run search operation in background thread"""
        try:
            for streaming_result in self.search_engine.search_stream(
                search_function, file_list, cancellation_token, 
                progress_callback, result_callback
            ):
                result_buffer.add_result(streaming_result)
                
                if streaming_result.is_final or cancellation_token.is_cancelled():
                    break
        
        except Exception as e:
            # Add error result to buffer
            error_result = StreamingSearchResult(
                progress=SearchProgress(
                    status=StreamingStatus.ERROR,
                    error_message=str(e)
                ),
                is_final=True
            )
            result_buffer.add_result(error_result)
        
        finally:
            result_buffer.close()
            
            # Remove from active operations
            with self.lock:
                if operation_id in self.active_operations:
                    del self.active_operations[operation_id]
    
    def get_results(self, operation_id: int, timeout: float = 0.1) -> List[StreamingSearchResult]:
        """Get available results for operation"""
        with self.lock:
            if operation_id not in self.active_operations:
                return []
            
            return self.active_operations[operation_id]['buffer'].get_results(timeout)
    
    def cancel_search(self, operation_id: int):
        """Cancel search operation"""
        with self.lock:
            if operation_id in self.active_operations:
                self.active_operations[operation_id]['token'].cancel()
    
    def get_operation_status(self, operation_id: int) -> Optional[Dict[str, Any]]:
        """Get status information for operation"""
        with self.lock:
            if operation_id not in self.active_operations:
                return None
            
            op = self.active_operations[operation_id]
            
            return {
                'operation_id': operation_id,
                'is_active': op['thread'].is_alive(),
                'is_cancelled': op['token'].is_cancelled(),
                'start_time': op['start_time'],
                'elapsed_time': time.time() - op['start_time'],
                'file_count': op['file_count'],
                'buffer_empty': op['buffer'].is_empty()
            }
    
    def list_active_operations(self) -> List[Dict[str, Any]]:
        """List all active search operations"""
        with self.lock:
            return [self.get_operation_status(op_id) for op_id in self.active_operations.keys()]
    
    def cleanup_completed_operations(self):
        """Remove completed operations from tracking"""
        with self.lock:
            completed_ops = []
            
            for op_id, op_info in self.active_operations.items():
                if not op_info['thread'].is_alive():
                    completed_ops.append(op_id)
            
            for op_id in completed_ops:
                del self.active_operations[op_id]