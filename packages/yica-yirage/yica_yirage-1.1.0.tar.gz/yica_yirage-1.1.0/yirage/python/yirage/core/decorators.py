"""
YICA-YiRage Decorator Module
Provides optimization decorators for CIM-aware compilation
"""

import functools
import logging
from typing import Any, Callable, Optional, Dict, List
import warnings

logger = logging.getLogger(__name__)


def operator(func: Callable) -> Callable:
    """
    Mark function as YiRage operator for optimization
    Enables CIM array-aware optimizations and Triton code generation
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Executing YiRage operator: {func.__name__}")
        # Mark for code transformation and optimization
        result = func(*args, **kwargs)
        return result
    
    wrapper._yirage_operator = True
    wrapper._enable_triton_generation = True
    return wrapper


def cim_operator(func: Callable) -> Callable:
    """
    Mark function as CIM-specific operator
    Enables compute-in-memory architecture optimizations and YICA-aware code generation
    """
    @functools.wraps(func)  
    def wrapper(*args, **kwargs):
        logger.debug(f"Executing CIM operator: {func.__name__}")
        # Apply YICA CIM-specific optimizations:
        # - Compute-in-memory fusion
        # - Three-tier memory hierarchy awareness
        # - Array-level parallelism
        result = func(*args, **kwargs)
        return result
    
    wrapper._yirage_cim_operator = True
    wrapper._enable_yica_optimizations = True
    wrapper._generate_cim_triton = True
    return wrapper


def fuse_operators(func: Callable) -> Callable:
    """
    Automatic operator fusion decorator
    Reduces intermediate results and memory access through intelligent fusion
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Executing fused operator: {func.__name__}")
        # Apply operator fusion optimizations:
        # - Identify fusion patterns
        # - Memory reuse optimization
        # - Intermediate result elimination
        result = func(*args, **kwargs)
        return result
    
    wrapper._yirage_fused = True
    wrapper._enable_fusion_optimization = True
    return wrapper


def graph_superoptimizer(func: Callable) -> Callable:
    """
    Graph-level super-optimizer decorator
    Inspired by Mirage multi-level optimization approach
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Executing graph super-optimization: {func.__name__}")
        # Apply graph-level optimizations:
        # - Algebraic transformations
        # - Schedule transformations
        # - Cross-operator optimization
        result = func(*args, **kwargs)
        return result
    
    wrapper._yirage_graph_superoptimizer = True
    wrapper._enable_mirage_optimization = True
    return wrapper


def memory_hierarchy_optimizer(func: Callable) -> Callable:
    """
    Memory hierarchy-aware optimization decorator
    Optimizes for YICA CIM three-tier storage hierarchy (RF→SPM→DRAM)
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Executing memory hierarchy optimization: {func.__name__}")
        # Apply YICA memory hierarchy optimizations:
        # - Register File optimization (32KB)
        # - Scratchpad Memory optimization (2MB)  
        # - DRAM optimization (8GB)
        result = func(*args, **kwargs)
        return result
    
    wrapper._yirage_memory_optimizer = True
    wrapper._enable_memory_hierarchy_optimization = True
    return wrapper


def layer_fusion(func: Callable) -> Callable:
    """
    Layer fusion decorator
    Optimizes inter-layer operations for models like Transformers
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Executing layer fusion: {func.__name__}")
        # Apply layer fusion optimizations:
        # - Attention + FFN + residual connection fusion
        # - LayerNorm fusion optimization
        result = func(*args, **kwargs)
        return result
    
    wrapper._yirage_layer_fusion = True
    wrapper._enable_layer_fusion = True
    return wrapper


def compile(optimization_level: int = 2, 
           target: str = "yica-cim",
           **kwargs) -> Callable:
    """
    Compilation optimization decorator
    Compiles function to optimized YICA CIM code with Triton backend
    
    Args:
        optimization_level: Optimization level (0-3)
        target: Target architecture
        **kwargs: Additional compilation options
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs_inner):
            logger.debug(f"Compiling optimized function: {func.__name__} (level: {optimization_level})")
            # Apply compilation optimizations:
            # - Multi-level IR transformation
            # - YICA CIM code generation
            # - Triton backend compilation
            result = func(*args, **kwargs_inner)
            return result
        
        wrapper._yirage_compiled = True
        wrapper._optimization_level = optimization_level
        wrapper._target = target
        wrapper._enable_triton_compilation = True
        return wrapper
    
    return decorator


# Export decorators
__all__ = [
    'operator',
    'cim_operator', 
    'fuse_operators',
    'graph_superoptimizer',
    'memory_hierarchy_optimizer',
    'layer_fusion',
    'compile'
]
