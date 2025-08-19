"""
YiRage Performance Profiler Module
性能分析和监控工具

Features:
- 代码性能分析
- 内存使用监控
- CIM操作追踪
- 优化建议生成
"""

import time
import threading
import contextlib
from typing import Dict, List, Any, Optional
import json
import warnings

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    warnings.warn("psutil not available, memory profiling limited", UserWarning)

class ProfilerData:
    """性能分析数据类"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.operations = []
        self.memory_usage = []
        self.cim_operations = []
        self.metadata = {}
    
    def add_operation(self, name: str, duration: float, metadata: Optional[Dict] = None):
        """添加操作记录"""
        self.operations.append({
            'name': name,
            'duration': duration,
            'timestamp': time.time(),
            'metadata': metadata or {}
        })
    
    def add_memory_sample(self, memory_mb: float):
        """添加内存使用样本"""
        self.memory_usage.append({
            'timestamp': time.time(),
            'memory_mb': memory_mb
        })
    
    def add_cim_operation(self, operation: str, shape: tuple, dtype: str, duration: float):
        """添加CIM操作记录"""
        self.cim_operations.append({
            'operation': operation,
            'shape': shape,
            'dtype': dtype,
            'duration': duration,
            'timestamp': time.time()
        })
    
    def get_total_duration(self) -> float:
        """获取总执行时间"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    def get_operation_summary(self) -> Dict[str, Any]:
        """获取操作统计摘要"""
        if not self.operations:
            return {}
        
        total_ops = len(self.operations)
        total_duration = sum(op['duration'] for op in self.operations)
        avg_duration = total_duration / total_ops if total_ops > 0 else 0
        
        return {
            'total_operations': total_ops,
            'total_duration': total_duration,
            'average_duration': avg_duration,
            'operations_per_second': total_ops / total_duration if total_duration > 0 else 0
        }

class YirageProfiler:
    """YiRage性能分析器"""
    
    def __init__(self, enable_memory_tracking: bool = True):
        self.enable_memory_tracking = enable_memory_tracking
        self.data = ProfilerData()
        self._monitoring = False
        self._monitor_thread = None
        
    def start(self):
        """开始性能分析"""
        self.data.start_time = time.time()
        
        if self.enable_memory_tracking and PSUTIL_AVAILABLE:
            self._monitoring = True
            self._monitor_thread = threading.Thread(target=self._memory_monitor)
            self._monitor_thread.daemon = True
            self._monitor_thread.start()
    
    def stop(self):
        """停止性能分析"""
        self.data.end_time = time.time()
        self._monitoring = False
        
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
    
    def _memory_monitor(self):
        """内存监控线程"""
        if not PSUTIL_AVAILABLE:
            return
            
        process = psutil.Process()
        
        while self._monitoring:
            try:
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024  # 转换为MB
                self.data.add_memory_sample(memory_mb)
                time.sleep(0.1)  # 100ms采样间隔
            except:
                break
    
    def record_operation(self, name: str, duration: float, metadata: Optional[Dict] = None):
        """记录操作"""
        self.data.add_operation(name, duration, metadata)
    
    def record_cim_operation(self, operation: str, shape: tuple, dtype: str, duration: float):
        """记录CIM操作"""
        self.data.add_cim_operation(operation, shape, dtype, duration)
    
    def export_chrome_trace(self, filename: str):
        """导出Chrome跟踪格式"""
        trace_events = []
        
        # 添加操作事件
        for op in self.data.operations:
            trace_events.append({
                'name': op['name'],
                'cat': 'operation',
                'ph': 'X',  # Complete event
                'ts': int(op['timestamp'] * 1000000),  # 微秒
                'dur': int(op['duration'] * 1000000),  # 微秒
                'pid': 1,
                'tid': 1,
                'args': op['metadata']
            })
        
        # 添加CIM操作事件
        for cim_op in self.data.cim_operations:
            trace_events.append({
                'name': f"CIM_{cim_op['operation']}",
                'cat': 'cim',
                'ph': 'X',
                'ts': int(cim_op['timestamp'] * 1000000),
                'dur': int(cim_op['duration'] * 1000000),
                'pid': 1,
                'tid': 2,
                'args': {
                    'shape': cim_op['shape'],
                    'dtype': cim_op['dtype']
                }
            })
        
        trace_data = {'traceEvents': trace_events}
        
        with open(filename, 'w') as f:
            json.dump(trace_data, f, indent=2)
    
    def print_summary(self):
        """打印性能摘要"""
        print("\n" + "="*60)
        print("🚀 YiRage Performance Profile Summary")
        print("="*60)
        
        # 总体统计
        total_duration = self.data.get_total_duration()
        print(f"⏱️  Total Duration: {total_duration:.3f}s")
        
        # 操作统计
        op_summary = self.data.get_operation_summary()
        if op_summary:
            print(f"📊 Total Operations: {op_summary['total_operations']}")
            print(f"📊 Average Duration: {op_summary['average_duration']:.3f}s")
            print(f"📊 Operations/sec: {op_summary['operations_per_second']:.1f}")
        
        # CIM操作统计
        if self.data.cim_operations:
            cim_count = len(self.data.cim_operations)
            cim_total_time = sum(op['duration'] for op in self.data.cim_operations)
            print(f"🧠 CIM Operations: {cim_count}")
            print(f"🧠 CIM Total Time: {cim_total_time:.3f}s")
            print(f"🧠 CIM Efficiency: {cim_total_time/total_duration*100:.1f}%")
        
        # 内存统计
        if self.data.memory_usage:
            memory_values = [sample['memory_mb'] for sample in self.data.memory_usage]
            print(f"💾 Peak Memory: {max(memory_values):.1f}MB")
            print(f"💾 Avg Memory: {sum(memory_values)/len(memory_values):.1f}MB")
        
        print("="*60)

# 全局分析器实例
_global_profiler = None

@contextlib.contextmanager
def profile(enable_memory_tracking: bool = True):
    """性能分析上下文管理器"""
    global _global_profiler
    
    profiler = YirageProfiler(enable_memory_tracking)
    _global_profiler = profiler
    
    try:
        profiler.start()
        yield profiler
    finally:
        profiler.stop()
        _global_profiler = None

def get_current_profiler() -> Optional[YirageProfiler]:
    """获取当前活跃的分析器"""
    return _global_profiler

def record_operation(name: str, duration: float, metadata: Optional[Dict] = None):
    """记录操作到当前分析器"""
    if _global_profiler:
        _global_profiler.record_operation(name, duration, metadata)

def record_cim_operation(operation: str, shape: tuple, dtype: str, duration: float):
    """记录CIM操作到当前分析器"""
    if _global_profiler:
        _global_profiler.record_cim_operation(operation, shape, dtype, duration)

# 装饰器支持
def profile_function(func):
    """函数性能分析装饰器"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            record_operation(func.__name__, duration, {
                'args_count': len(args),
                'kwargs_count': len(kwargs)
            })
            return result
        except Exception as e:
            duration = time.time() - start_time
            record_operation(func.__name__, duration, {
                'error': str(e),
                'args_count': len(args),
                'kwargs_count': len(kwargs)
            })
            raise
    return wrapper
