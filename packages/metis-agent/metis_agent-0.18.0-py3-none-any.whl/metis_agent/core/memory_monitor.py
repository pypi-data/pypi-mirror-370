"""
Advanced Memory Monitoring System for Metis Agent.

Provides real-time memory tracking, leak detection, performance analysis,
and automatic cleanup recommendations for optimal system performance.
"""
import time
import threading
import psutil
import gc
import os
import sys
import tracemalloc
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum
import logging
import weakref

logger = logging.getLogger(__name__)


class MemoryThresholdLevel(Enum):
    """Memory usage threshold levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class MemoryEventType(Enum):
    """Types of memory events."""
    ALLOCATION = "allocation"
    DEALLOCATION = "deallocation"
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    LEAK_DETECTED = "leak_detected"
    GC_TRIGGERED = "gc_triggered"
    CLEANUP_PERFORMED = "cleanup_performed"


@dataclass
class MemorySnapshot:
    """Represents a memory usage snapshot at a point in time."""
    timestamp: float
    process_memory_mb: float
    system_memory_mb: float
    system_memory_percent: float
    rss_memory_mb: float
    vms_memory_mb: float
    python_objects_count: int
    gc_collections: Dict[int, int]
    active_threads: int
    open_files: int
    
    @property
    def age_seconds(self) -> float:
        """Age of this snapshot in seconds."""
        return time.time() - self.timestamp


@dataclass
class MemoryAllocation:
    """Represents a tracked memory allocation."""
    component: str
    size_mb: float
    timestamp: float
    stack_trace: Optional[str]
    metadata: Dict[str, Any]
    
    @property
    def age_seconds(self) -> float:
        """Age of this allocation in seconds."""
        return time.time() - self.timestamp


@dataclass
class MemoryLeak:
    """Represents a detected memory leak."""
    component: str
    growth_rate_mb_per_min: float
    detected_at: float
    confidence: float
    samples_count: int
    evidence: Dict[str, Any]


@dataclass
class MemoryAlert:
    """Represents a memory-related alert."""
    level: MemoryThresholdLevel
    message: str
    timestamp: float
    component: Optional[str]
    current_usage_mb: float
    threshold_mb: float
    recommended_action: str


class MemoryTracker:
    """Tracks memory allocations for specific components."""
    
    def __init__(self, component_name: str):
        self.component_name = component_name
        self.allocations: List[MemoryAllocation] = []
        self.peak_usage_mb = 0.0
        self.current_usage_mb = 0.0
        self.allocation_count = 0
        self._lock = threading.Lock()
    
    def record_allocation(self, size_mb: float, metadata: Dict[str, Any] = None):
        """Record a memory allocation."""
        with self._lock:
            allocation = MemoryAllocation(
                component=self.component_name,
                size_mb=size_mb,
                timestamp=time.time(),
                stack_trace=self._get_stack_trace() if size_mb > 10 else None,  # Only for large allocations
                metadata=metadata or {}
            )
            
            self.allocations.append(allocation)
            self.current_usage_mb += size_mb
            self.peak_usage_mb = max(self.peak_usage_mb, self.current_usage_mb)
            self.allocation_count += 1
            
            # Cleanup old allocations (keep only last 1000)
            if len(self.allocations) > 1000:
                old_allocation = self.allocations.pop(0)
                self.current_usage_mb -= old_allocation.size_mb
    
    def record_deallocation(self, size_mb: float):
        """Record a memory deallocation."""
        with self._lock:
            self.current_usage_mb = max(0, self.current_usage_mb - size_mb)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics for this component."""
        with self._lock:
            return {
                "component": self.component_name,
                "current_usage_mb": round(self.current_usage_mb, 2),
                "peak_usage_mb": round(self.peak_usage_mb, 2),
                "allocation_count": self.allocation_count,
                "active_allocations": len(self.allocations),
                "recent_allocations": [
                    {
                        "size_mb": round(alloc.size_mb, 2),
                        "age_seconds": round(alloc.age_seconds, 1),
                        "metadata": alloc.metadata
                    }
                    for alloc in self.allocations[-5:]  # Last 5 allocations
                ]
            }
    
    def _get_stack_trace(self) -> Optional[str]:
        """Get current stack trace for debugging."""
        try:
            return ''.join(traceback.format_stack()[-5:])  # Last 5 frames
        except:
            return None


class MemoryLeakDetector:
    """Detects potential memory leaks by analyzing memory growth patterns."""
    
    def __init__(self, window_size: int = 10, min_growth_rate: float = 5.0):
        """
        Initialize leak detector.
        
        Args:
            window_size: Number of samples to analyze for trends
            min_growth_rate: Minimum growth rate (MB/min) to consider a leak
        """
        self.window_size = window_size
        self.min_growth_rate = min_growth_rate
        self.component_samples: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        
    def add_sample(self, component: str, memory_mb: float):
        """Add a memory sample for leak detection."""
        self.component_samples[component].append((time.time(), memory_mb))
    
    def detect_leaks(self) -> List[MemoryLeak]:
        """Detect potential memory leaks across all components."""
        leaks = []
        
        for component, samples in self.component_samples.items():
            if len(samples) < self.window_size:
                continue
            
            # Calculate linear regression to find growth trend
            growth_rate = self._calculate_growth_rate(samples)
            
            if growth_rate > self.min_growth_rate:
                confidence = min(1.0, growth_rate / (self.min_growth_rate * 2))
                
                leak = MemoryLeak(
                    component=component,
                    growth_rate_mb_per_min=growth_rate,
                    detected_at=time.time(),
                    confidence=confidence,
                    samples_count=len(samples),
                    evidence={
                        "memory_trend": list(samples),
                        "analysis_window_minutes": self.window_size,
                        "growth_calculation": "linear_regression"
                    }
                )
                leaks.append(leak)
        
        return leaks
    
    def _calculate_growth_rate(self, samples: deque) -> float:
        """Calculate memory growth rate in MB per minute."""
        if len(samples) < 2:
            return 0.0
        
        # Simple linear regression
        times = [sample[0] for sample in samples]
        memories = [sample[1] for sample in samples]
        
        n = len(samples)
        sum_x = sum(times)
        sum_y = sum(memories)
        sum_xy = sum(t * m for t, m in zip(times, memories))
        sum_x2 = sum(t * t for t in times)
        
        # Calculate slope (growth rate per second)
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        
        # Convert to MB per minute
        return slope * 60.0


class MemoryMonitor:
    """
    Main memory monitoring system providing real-time tracking,
    leak detection, and performance optimization insights.
    """
    
    def __init__(self, 
                 sample_interval: float = 30.0,
                 history_size: int = 288,  # 24 hours at 5-minute intervals
                 enable_tracemalloc: bool = False):
        """
        Initialize memory monitor.
        
        Args:
            sample_interval: Interval between memory samples in seconds
            history_size: Number of historical samples to keep
            enable_tracemalloc: Enable Python's tracemalloc for detailed tracking
        """
        self.sample_interval = sample_interval
        self.history_size = history_size
        self.enable_tracemalloc = enable_tracemalloc
        
        # Core data structures
        self.snapshots: deque = deque(maxlen=history_size)
        self.component_trackers: Dict[str, MemoryTracker] = {}
        self.leak_detector = MemoryLeakDetector()
        self.alerts: List[MemoryAlert] = []
        self.event_log: deque = deque(maxlen=1000)
        
        # Monitoring state
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()
        
        # Thresholds (MB)
        self.thresholds = {
            MemoryThresholdLevel.LOW: 100,
            MemoryThresholdLevel.MODERATE: 250,
            MemoryThresholdLevel.HIGH: 500,
            MemoryThresholdLevel.CRITICAL: 1000
        }
        
        # Event callbacks
        self._event_callbacks: List[Callable[[MemoryEventType, Dict[str, Any]], None]] = []
        
        if self.enable_tracemalloc and not tracemalloc.is_tracing():
            tracemalloc.start()
        
        logger.info(f"MemoryMonitor initialized: interval={sample_interval}s, "
                   f"history_size={history_size}, tracemalloc={enable_tracemalloc}")
    
    def start_monitoring(self):
        """Start continuous memory monitoring."""
        with self._lock:
            if self._monitoring:
                return
            
            self._monitoring = True
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()
            
            self._log_event(MemoryEventType.GC_TRIGGERED, {"action": "monitoring_started"})
            logger.info("Memory monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous memory monitoring."""
        with self._lock:
            self._monitoring = False
            if self._monitor_thread and self._monitor_thread.is_alive():
                self._monitor_thread.join(timeout=5.0)
            
            logger.info("Memory monitoring stopped")
    
    def get_tracker(self, component_name: str) -> MemoryTracker:
        """Get or create a memory tracker for a specific component."""
        with self._lock:
            if component_name not in self.component_trackers:
                self.component_trackers[component_name] = MemoryTracker(component_name)
            return self.component_trackers[component_name]
    
    def take_snapshot(self) -> MemorySnapshot:
        """Take a memory snapshot of current system state."""
        try:
            process = psutil.Process()
            system_memory = psutil.virtual_memory()
            memory_info = process.memory_info()
            
            snapshot = MemorySnapshot(
                timestamp=time.time(),
                process_memory_mb=memory_info.rss / (1024 * 1024),
                system_memory_mb=system_memory.total / (1024 * 1024),
                system_memory_percent=system_memory.percent,
                rss_memory_mb=memory_info.rss / (1024 * 1024),
                vms_memory_mb=memory_info.vms / (1024 * 1024),
                python_objects_count=len(gc.get_objects()),
                gc_collections={i: gc.get_count()[i] for i in range(3)},
                active_threads=threading.active_count(),
                open_files=len(process.open_files())
            )
            
            with self._lock:
                self.snapshots.append(snapshot)
                
                # Check thresholds and generate alerts
                self._check_thresholds(snapshot)
                
                # Update leak detector
                self.leak_detector.add_sample("system", snapshot.process_memory_mb)
                for component, tracker in self.component_trackers.items():
                    self.leak_detector.add_sample(component, tracker.current_usage_mb)
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Failed to take memory snapshot: {e}")
            raise
    
    def force_garbage_collection(self) -> Dict[str, Any]:
        """Force garbage collection and return statistics."""
        start_time = time.time()
        
        # Take before snapshot
        before_snapshot = self.take_snapshot()
        
        # Force GC
        collected = gc.collect()
        
        # Take after snapshot
        after_snapshot = self.take_snapshot()
        
        # Calculate savings
        memory_freed_mb = before_snapshot.process_memory_mb - after_snapshot.process_memory_mb
        objects_freed = before_snapshot.python_objects_count - after_snapshot.python_objects_count
        gc_time = time.time() - start_time
        
        result = {
            "objects_collected": collected,
            "memory_freed_mb": round(memory_freed_mb, 2),
            "objects_freed": objects_freed,
            "gc_time_seconds": round(gc_time, 3),
            "before_memory_mb": round(before_snapshot.process_memory_mb, 2),
            "after_memory_mb": round(after_snapshot.process_memory_mb, 2)
        }
        
        self._log_event(MemoryEventType.GC_TRIGGERED, result)
        logger.info(f"Garbage collection: freed {memory_freed_mb:.2f}MB, {objects_freed} objects")
        
        return result
    
    def detect_memory_leaks(self) -> List[MemoryLeak]:
        """Detect potential memory leaks."""
        leaks = self.leak_detector.detect_leaks()
        
        for leak in leaks:
            self._log_event(MemoryEventType.LEAK_DETECTED, {
                "component": leak.component,
                "growth_rate": leak.growth_rate_mb_per_min,
                "confidence": leak.confidence
            })
            
            # Generate alert for leak
            alert = MemoryAlert(
                level=MemoryThresholdLevel.HIGH,
                message=f"Memory leak detected in {leak.component}: {leak.growth_rate_mb_per_min:.2f}MB/min growth",
                timestamp=time.time(),
                component=leak.component,
                current_usage_mb=self.component_trackers.get(leak.component, MemoryTracker("unknown")).current_usage_mb,
                threshold_mb=0,
                recommended_action="Investigate component for memory leaks and implement proper cleanup"
            )
            self.alerts.append(alert)
        
        return leaks
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics."""
        with self._lock:
            latest_snapshot = self.snapshots[-1] if self.snapshots else None
            
            # Component statistics
            component_stats = {}
            total_component_memory = 0
            for name, tracker in self.component_trackers.items():
                stats = tracker.get_stats()
                component_stats[name] = stats
                total_component_memory += stats["current_usage_mb"]
            
            # Memory trends
            memory_trend = []
            if len(self.snapshots) >= 2:
                for i in range(1, min(len(self.snapshots), 11)):  # Last 10 samples
                    snapshot = self.snapshots[-i]
                    memory_trend.append({
                        "timestamp": snapshot.timestamp,
                        "memory_mb": snapshot.process_memory_mb,
                        "age_minutes": (time.time() - snapshot.timestamp) / 60
                    })
            
            # Recent alerts
            recent_alerts = [
                {
                    "level": alert.level.value,
                    "message": alert.message,
                    "component": alert.component,
                    "age_minutes": (time.time() - alert.timestamp) / 60
                }
                for alert in self.alerts[-10:]  # Last 10 alerts
            ]
            
            return {
                "current_snapshot": asdict(latest_snapshot) if latest_snapshot else None,
                "component_tracking": {
                    "total_components": len(component_stats),
                    "total_component_memory_mb": round(total_component_memory, 2),
                    "components": component_stats
                },
                "memory_trends": memory_trend,
                "leak_detection": {
                    "active_leaks": len(self.detect_memory_leaks()),
                    "monitoring_components": len(self.leak_detector.component_samples)
                },
                "alerts": {
                    "total_alerts": len(self.alerts),
                    "recent_alerts": recent_alerts
                },
                "monitoring_status": {
                    "is_active": self._monitoring,
                    "sample_interval": self.sample_interval,
                    "snapshots_collected": len(self.snapshots),
                    "tracemalloc_enabled": tracemalloc.is_tracing()
                },
                "thresholds": {level.value: mb for level, mb in self.thresholds.items()}
            }
    
    def set_threshold(self, level: MemoryThresholdLevel, memory_mb: float):
        """Set memory threshold for alerts."""
        self.thresholds[level] = memory_mb
        logger.info(f"Memory threshold set: {level.value} = {memory_mb}MB")
    
    def add_event_callback(self, callback: Callable[[MemoryEventType, Dict[str, Any]], None]):
        """Add callback for memory events."""
        self._event_callbacks.append(callback)
    
    def cleanup_old_data(self, max_age_hours: float = 24.0):
        """Clean up old monitoring data."""
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        with self._lock:
            # Clean up old alerts
            self.alerts = [alert for alert in self.alerts if alert.timestamp > cutoff_time]
            
            # Clean up component allocations
            for tracker in self.component_trackers.values():
                with tracker._lock:
                    tracker.allocations = [
                        alloc for alloc in tracker.allocations 
                        if alloc.timestamp > cutoff_time
                    ]
        
        self._log_event(MemoryEventType.CLEANUP_PERFORMED, {"max_age_hours": max_age_hours})
    
    def _monitor_loop(self):
        """Main monitoring loop running in background thread."""
        while self._monitoring:
            try:
                self.take_snapshot()
                
                # Detect leaks periodically (every 10 samples)
                if len(self.snapshots) % 10 == 0:
                    self.detect_memory_leaks()
                
                time.sleep(self.sample_interval)
                
            except Exception as e:
                logger.error(f"Error in memory monitoring loop: {e}")
                time.sleep(self.sample_interval)
    
    def _check_thresholds(self, snapshot: MemorySnapshot):
        """Check memory thresholds and generate alerts."""
        memory_mb = snapshot.process_memory_mb
        
        # Find the highest threshold exceeded
        exceeded_level = None
        for level in [MemoryThresholdLevel.CRITICAL, MemoryThresholdLevel.HIGH, 
                     MemoryThresholdLevel.MODERATE, MemoryThresholdLevel.LOW]:
            if memory_mb > self.thresholds[level]:
                exceeded_level = level
                break
        
        if exceeded_level:
            # Check if we already have a recent alert for this level
            recent_alerts = [a for a in self.alerts[-5:] if a.level == exceeded_level]
            if not recent_alerts or (time.time() - recent_alerts[-1].timestamp) > 300:  # 5 minutes
                
                recommendations = {
                    MemoryThresholdLevel.LOW: "Monitor memory usage patterns",
                    MemoryThresholdLevel.MODERATE: "Consider garbage collection or cache cleanup",
                    MemoryThresholdLevel.HIGH: "Investigate high memory usage and optimize algorithms",
                    MemoryThresholdLevel.CRITICAL: "Take immediate action: force GC, restart components, or scale system"
                }
                
                alert = MemoryAlert(
                    level=exceeded_level,
                    message=f"Memory usage {exceeded_level.value}: {memory_mb:.2f}MB exceeds {self.thresholds[exceeded_level]}MB threshold",
                    timestamp=time.time(),
                    component=None,
                    current_usage_mb=memory_mb,
                    threshold_mb=self.thresholds[exceeded_level],
                    recommended_action=recommendations[exceeded_level]
                )
                
                self.alerts.append(alert)
                self._log_event(MemoryEventType.THRESHOLD_EXCEEDED, {
                    "level": exceeded_level.value,
                    "memory_mb": memory_mb,
                    "threshold_mb": self.thresholds[exceeded_level]
                })
    
    def _log_event(self, event_type: MemoryEventType, data: Dict[str, Any]):
        """Log a memory event."""
        event = {
            "timestamp": time.time(),
            "event_type": event_type.value,
            "data": data
        }
        self.event_log.append(event)
        
        # Notify callbacks
        for callback in self._event_callbacks:
            try:
                callback(event_type, data)
            except Exception as e:
                logger.error(f"Error in memory event callback: {e}")


# Global memory monitor instance
_memory_monitor: Optional[MemoryMonitor] = None


def get_memory_monitor() -> MemoryMonitor:
    """Get or create global memory monitor instance."""
    global _memory_monitor
    if _memory_monitor is None:
        _memory_monitor = MemoryMonitor()
        _memory_monitor.start_monitoring()
    return _memory_monitor


def configure_memory_monitor(sample_interval: float = 30.0,
                           history_size: int = 288,
                           enable_tracemalloc: bool = False) -> MemoryMonitor:
    """Configure global memory monitor with custom settings."""
    global _memory_monitor
    if _memory_monitor and _memory_monitor._monitoring:
        _memory_monitor.stop_monitoring()
    
    _memory_monitor = MemoryMonitor(sample_interval, history_size, enable_tracemalloc)
    _memory_monitor.start_monitoring()
    return _memory_monitor