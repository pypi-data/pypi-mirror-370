"""
Optimized Import System for Metis Agent.

Provides intelligent import management, dependency tracking, and startup
optimization through deferred imports and parallel loading strategies.
"""
import sys
import time
import threading
import importlib
import importlib.util
from typing import Dict, Any, List, Optional, Set, Callable, Type
from dataclasses import dataclass
from collections import defaultdict
import logging
import weakref
import ast
import os

logger = logging.getLogger(__name__)


@dataclass
class ImportMetrics:
    """Metrics for import performance tracking."""
    module_name: str
    import_time_ms: float
    size_bytes: int
    dependency_count: int
    lazy_loaded: bool
    import_count: int = 0
    last_import_time: Optional[float] = None


class DeferredImport:
    """
    Deferred import wrapper that loads modules only when accessed.
    """
    
    def __init__(self, module_name: str, from_list: List[str] = None):
        self.module_name = module_name
        self.from_list = from_list or []
        self._module = None
        self._imported = False
        self._import_time = None
        self._lock = threading.Lock()
    
    def __getattr__(self, name: str):
        """Load module on first attribute access."""
        if not self._imported:
            self._load_module()
        
        if self._module is None:
            raise ImportError(f"Failed to import module '{self.module_name}'")
        
        return getattr(self._module, name)
    
    def _load_module(self):
        """Load the actual module."""
        with self._lock:
            if self._imported:
                return
            
            start_time = time.time()
            try:
                if self.from_list:
                    # Handle 'from module import item1, item2' style imports
                    self._module = importlib.import_module(self.module_name)
                    # Create a namespace with only the requested items
                    namespace = {}
                    for item in self.from_list:
                        namespace[item] = getattr(self._module, item)
                    self._module = type('DeferredModule', (), namespace)()
                else:
                    # Handle 'import module' style imports
                    self._module = importlib.import_module(self.module_name)
                
                self._import_time = (time.time() - start_time) * 1000
                self._imported = True
                
                logger.debug(f"Deferred import of '{self.module_name}' completed in {self._import_time:.2f}ms")
                
            except Exception as e:
                logger.error(f"Failed to import '{self.module_name}': {e}")
                self._imported = True  # Mark as attempted to avoid repeated failures
    
    @property
    def is_loaded(self) -> bool:
        """Check if module is loaded."""
        return self._imported and self._module is not None
    
    @property
    def import_time_ms(self) -> Optional[float]:
        """Get import time in milliseconds."""
        return self._import_time


class ImportOptimizer:
    """
    Optimizes import patterns for faster startup and reduced memory usage.
    """
    
    def __init__(self):
        self.deferred_imports: Dict[str, DeferredImport] = {}
        self.import_metrics: Dict[str, ImportMetrics] = {}
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self._import_hooks: List[Callable] = []
        self._startup_imports: Set[str] = set()
        self._optional_imports: Set[str] = set()
        
    def defer_import(self, module_name: str, from_list: List[str] = None) -> DeferredImport:
        """
        Create a deferred import that loads only when accessed.
        
        Args:
            module_name: Name of module to import
            from_list: List of items to import from module
            
        Returns:
            DeferredImport instance
        """
        key = f"{module_name}:{','.join(from_list or [])}"
        
        if key not in self.deferred_imports:
            self.deferred_imports[key] = DeferredImport(module_name, from_list)
        
        return self.deferred_imports[key]
    
    def mark_startup_essential(self, module_name: str):
        """Mark a module as essential for startup (will be imported eagerly)."""
        self._startup_imports.add(module_name)
    
    def mark_optional(self, module_name: str):
        """Mark a module as optional (graceful failure if import fails)."""
        self._optional_imports.add(module_name)
    
    def analyze_dependencies(self, file_path: str) -> Dict[str, Set[str]]:
        """
        Analyze Python file to extract import dependencies.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Dictionary mapping modules to their dependencies
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            dependencies = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.add(node.module.split('.')[0])
            
            module_name = os.path.basename(file_path).replace('.py', '')
            self.dependency_graph[module_name] = dependencies
            
            return {module_name: dependencies}
            
        except Exception as e:
            logger.error(f"Failed to analyze dependencies for {file_path}: {e}")
            return {}
    
    def optimize_startup_imports(self) -> Dict[str, Any]:
        """
        Optimize startup by identifying and prioritizing critical imports.
        
        Returns:
            Dictionary with optimization statistics
        """
        start_time = time.time()
        
        # Import startup-essential modules immediately
        essential_imports = []
        for module_name in self._startup_imports:
            try:
                import_start = time.time()
                module = importlib.import_module(module_name)
                import_time = (time.time() - import_start) * 1000
                
                essential_imports.append({
                    "module": module_name,
                    "import_time_ms": import_time
                })
                
                # Track metrics
                self.import_metrics[module_name] = ImportMetrics(
                    module_name=module_name,
                    import_time_ms=import_time,
                    size_bytes=sys.getsizeof(module),
                    dependency_count=len(self.dependency_graph.get(module_name, set())),
                    lazy_loaded=False,
                    import_count=1,
                    last_import_time=time.time()
                )
                
            except Exception as e:
                logger.error(f"Failed to import essential module '{module_name}': {e}")
        
        optimization_time = (time.time() - start_time) * 1000
        
        return {
            "optimization_time_ms": optimization_time,
            "essential_imports": essential_imports,
            "deferred_imports": len(self.deferred_imports),
            "dependency_mappings": len(self.dependency_graph)
        }
    
    def get_import_statistics(self) -> Dict[str, Any]:
        """Get comprehensive import statistics."""
        total_imports = len(self.import_metrics)
        lazy_imports = sum(1 for m in self.import_metrics.values() if m.lazy_loaded)
        
        if total_imports > 0:
            avg_import_time = sum(m.import_time_ms for m in self.import_metrics.values()) / total_imports
            total_import_time = sum(m.import_time_ms for m in self.import_metrics.values())
        else:
            avg_import_time = 0
            total_import_time = 0
        
        # Calculate memory saved by lazy loading
        lazy_modules = [m for m in self.import_metrics.values() if m.lazy_loaded]
        memory_saved = sum(m.size_bytes for m in lazy_modules)
        
        return {
            "total_imports": total_imports,
            "lazy_imports": lazy_imports,
            "eager_imports": total_imports - lazy_imports,
            "average_import_time_ms": round(avg_import_time, 2),
            "total_import_time_ms": round(total_import_time, 2),
            "memory_saved_bytes": memory_saved,
            "deferred_imports_created": len(self.deferred_imports),
            "dependency_graph_size": len(self.dependency_graph),
            "startup_essential_modules": len(self._startup_imports),
            "optional_modules": len(self._optional_imports)
        }
    
    def add_import_hook(self, hook: Callable[[str, float], None]):
        """
        Add hook to be called when modules are imported.
        
        Args:
            hook: Function called with (module_name, import_time_ms)
        """
        self._import_hooks.append(hook)
    
    def safe_import(self, module_name: str, default=None) -> Any:
        """
        Safely import a module with graceful failure handling.
        
        Args:
            module_name: Module to import
            default: Default value if import fails
            
        Returns:
            Imported module or default value
        """
        try:
            start_time = time.time()
            module = importlib.import_module(module_name)
            import_time = (time.time() - start_time) * 1000
            
            # Track metrics
            if module_name in self.import_metrics:
                self.import_metrics[module_name].import_count += 1
                self.import_metrics[module_name].last_import_time = time.time()
            else:
                self.import_metrics[module_name] = ImportMetrics(
                    module_name=module_name,
                    import_time_ms=import_time,
                    size_bytes=sys.getsizeof(module),
                    dependency_count=len(self.dependency_graph.get(module_name, set())),
                    lazy_loaded=True,
                    import_count=1,
                    last_import_time=time.time()
                )
            
            # Call import hooks
            for hook in self._import_hooks:
                try:
                    hook(module_name, import_time)
                except Exception as e:
                    logger.error(f"Error in import hook: {e}")
            
            return module
            
        except (ImportError, ModuleNotFoundError) as e:
            if module_name in self._optional_imports:
                logger.debug(f"Optional import '{module_name}' failed: {e}")
                return default
            else:
                logger.warning(f"Import '{module_name}' failed, using default: {e}")
                return default
    
    def clear_import_cache(self, module_pattern: str = None):
        """
        Clear import cache for development/testing.
        
        Args:
            module_pattern: Pattern to match modules (None for all)
        """
        modules_to_remove = []
        
        for module_name in sys.modules:
            if module_pattern is None or module_pattern in module_name:
                modules_to_remove.append(module_name)
        
        for module_name in modules_to_remove:
            if module_name in sys.modules:
                del sys.modules[module_name]
        
        logger.info(f"Cleared {len(modules_to_remove)} modules from import cache")


# Global import optimizer instance
_import_optimizer: Optional[ImportOptimizer] = None


def get_import_optimizer() -> ImportOptimizer:
    """Get or create global import optimizer."""
    global _import_optimizer
    if _import_optimizer is None:
        _import_optimizer = ImportOptimizer()
    return _import_optimizer


def lazy_import(module_name: str, from_list: List[str] = None):
    """
    Create a lazy import that loads only when accessed.
    
    Args:
        module_name: Module to import
        from_list: Specific items to import from module
        
    Returns:
        DeferredImport instance
    """
    optimizer = get_import_optimizer()
    return optimizer.defer_import(module_name, from_list)


def safe_import(module_name: str, default=None):
    """
    Safely import a module with graceful failure handling.
    
    Args:
        module_name: Module to import  
        default: Default value if import fails
        
    Returns:
        Imported module or default value
    """
    optimizer = get_import_optimizer()
    return optimizer.safe_import(module_name, default)


# Common lazy imports for Metis Agent components
def get_common_lazy_imports():
    """Get dictionary of commonly used lazy imports."""
    optimizer = get_import_optimizer()
    
    # Mark essential startup modules
    essential_modules = [
        'os', 'sys', 'time', 'logging', 'threading', 'asyncio'
    ]
    
    for module in essential_modules:
        optimizer.mark_startup_essential(module)
    
    # Mark optional modules (for enhanced features)
    optional_modules = [
        'psutil', 'numpy', 'pandas', 'aiohttp', 'requests',
        'tiktoken', 'anthropic', 'openai', 'groq'
    ]
    
    for module in optional_modules:
        optimizer.mark_optional(module)
    
    # Create lazy imports for heavy modules
    return {
        'numpy': lazy_import('numpy'),
        'pandas': lazy_import('pandas'), 
        'requests': lazy_import('requests'),
        'aiohttp': lazy_import('aiohttp'),
        'psutil': lazy_import('psutil'),
        'tiktoken': lazy_import('tiktoken'),
        'anthropic': lazy_import('anthropic'),
        'openai': lazy_import('openai'),
        'groq': lazy_import('groq'),
        'json': lazy_import('json'),
        'yaml': lazy_import('yaml'),
        'xml': lazy_import('xml.etree.ElementTree'),
        'csv': lazy_import('csv'),
        'sqlite3': lazy_import('sqlite3'),
        'hashlib': lazy_import('hashlib'),
        'base64': lazy_import('base64'),
        'urllib': lazy_import('urllib.parse'),
        'pathlib': lazy_import('pathlib'),
        'tempfile': lazy_import('tempfile'),
        'subprocess': lazy_import('subprocess'),
        'multiprocessing': lazy_import('multiprocessing'),
        'concurrent_futures': lazy_import('concurrent.futures'),
        'dataclasses': lazy_import('dataclasses'),
        'typing': lazy_import('typing'),
        'collections': lazy_import('collections'),
        'itertools': lazy_import('itertools'),
        'functools': lazy_import('functools'),
        'operator': lazy_import('operator'),
        'inspect': lazy_import('inspect'),
        'traceback': lazy_import('traceback'),
        'warnings': lazy_import('warnings'),
        'contextlib': lazy_import('contextlib')
    }


# Optimization utilities
def optimize_startup_imports():
    """Optimize imports for faster startup."""
    optimizer = get_import_optimizer()
    return optimizer.optimize_startup_imports()


def analyze_file_dependencies(file_path: str):
    """Analyze import dependencies for a Python file."""
    optimizer = get_import_optimizer()
    return optimizer.analyze_dependencies(file_path)


def get_import_statistics():
    """Get comprehensive import performance statistics."""
    optimizer = get_import_optimizer()
    return optimizer.get_import_statistics()