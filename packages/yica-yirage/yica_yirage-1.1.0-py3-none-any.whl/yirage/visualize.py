"""
YiRage Visualization Module
可视化和图表生成工具

Features:
- 性能数据可视化
- 内存使用图表
- CIM操作热力图
- 优化前后对比
"""

import warnings
from typing import Dict, List, Any, Optional, Tuple

try:
    import matplotlib
    matplotlib.use('Agg')  # 非交互式后端
    import matplotlib.pyplot as plt
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    warnings.warn("matplotlib not available, visualization disabled", UserWarning)

class YirageVisualizer:
    """YiRage可视化工具"""
    
    def __init__(self):
        self.fig_size = (12, 8)
        self.dpi = 100
        
    def _ensure_matplotlib(self):
        """确保matplotlib可用"""
        if not MATPLOTLIB_AVAILABLE:
            raise RuntimeError("matplotlib not available. Install with: pip install matplotlib")
    
    def plot_memory_usage(self, profiler_data, save_path: str = "memory_usage.png"):
        """绘制内存使用图表"""
        self._ensure_matplotlib()
        
        if not profiler_data.memory_usage:
            print("⚠️  No memory usage data available")
            return
        
        # 提取时间和内存数据
        timestamps = [sample['timestamp'] for sample in profiler_data.memory_usage]
        memory_values = [sample['memory_mb'] for sample in profiler_data.memory_usage]
        
        # 转换为相对时间
        start_time = min(timestamps)
        relative_times = [(t - start_time) for t in timestamps]
        
        # 创建图表
        plt.figure(figsize=self.fig_size, dpi=self.dpi)
        plt.plot(relative_times, memory_values, 'b-', linewidth=2, label='Memory Usage')
        plt.fill_between(relative_times, memory_values, alpha=0.3)
        
        # 标记峰值
        max_memory = max(memory_values)
        max_idx = memory_values.index(max_memory)
        plt.plot(relative_times[max_idx], max_memory, 'ro', markersize=8, label=f'Peak: {max_memory:.1f}MB')
        
        plt.xlabel('Time (seconds)')
        plt.ylabel('Memory Usage (MB)')
        plt.title('🧠 YiRage Memory Usage Over Time')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Memory usage plot saved to: {save_path}")
    
    def plot_compute_utilization(self, profiler_data, save_path: str = "compute_utilization.png"):
        """绘制计算利用率图表"""
        self._ensure_matplotlib()
        
        if not profiler_data.operations:
            print("⚠️  No operation data available")
            return
        
        # 统计操作类型
        op_types = {}
        for op in profiler_data.operations:
            op_name = op['name']
            if op_name not in op_types:
                op_types[op_name] = {'count': 0, 'total_time': 0}
            op_types[op_name]['count'] += 1
            op_types[op_name]['total_time'] += op['duration']
        
        # 创建饼图
        plt.figure(figsize=self.fig_size, dpi=self.dpi)
        
        names = list(op_types.keys())
        times = [op_types[name]['total_time'] for name in names]
        counts = [op_types[name]['count'] for name in names]
        
        # 计算百分比
        total_time = sum(times)
        percentages = [t/total_time*100 for t in times]
        
        # 绘制饼图
        colors = plt.cm.Set3(np.linspace(0, 1, len(names)))
        wedges, texts, autotexts = plt.pie(
            times, 
            labels=[f"{name}\n({count} ops)" for name, count in zip(names, counts)],
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        
        plt.title('⚡ YiRage Compute Utilization by Operation Type')
        plt.axis('equal')
        
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Compute utilization plot saved to: {save_path}")
    
    def plot_cim_heatmap(self, profiler_data, save_path: str = "cim_heatmap.png"):
        """绘制CIM操作热力图"""
        self._ensure_matplotlib()
        
        if not profiler_data.cim_operations:
            print("⚠️  No CIM operation data available")
            return
        
        # 提取CIM操作数据
        operations = []
        durations = []
        shapes = []
        
        for cim_op in profiler_data.cim_operations:
            operations.append(cim_op['operation'])
            durations.append(cim_op['duration'])
            shapes.append(f"{cim_op['shape']}")
        
        # 创建热力图数据
        unique_ops = list(set(operations))
        unique_shapes = list(set(shapes))
        
        heatmap_data = np.zeros((len(unique_ops), len(unique_shapes)))
        
        for i, op in enumerate(unique_ops):
            for j, shape in enumerate(unique_shapes):
                # 找到匹配的操作和形状
                matching_durations = [
                    d for o, s, d in zip(operations, shapes, durations)
                    if o == op and s == shape
                ]
                if matching_durations:
                    heatmap_data[i, j] = sum(matching_durations)
        
        # 绘制热力图
        plt.figure(figsize=self.fig_size, dpi=self.dpi)
        im = plt.imshow(heatmap_data, cmap='YlOrRd', aspect='auto')
        
        # 设置标签
        plt.xticks(range(len(unique_shapes)), unique_shapes, rotation=45, ha='right')
        plt.yticks(range(len(unique_ops)), unique_ops)
        
        # 添加数值标注
        for i in range(len(unique_ops)):
            for j in range(len(unique_shapes)):
                if heatmap_data[i, j] > 0:
                    plt.text(j, i, f'{heatmap_data[i, j]:.3f}', 
                            ha='center', va='center', color='black', fontsize=8)
        
        plt.colorbar(im, label='Duration (seconds)')
        plt.title('🔥 CIM Operations Heatmap')
        plt.xlabel('Tensor Shapes')
        plt.ylabel('Operations')
        plt.tight_layout()
        
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        print(f"✅ CIM heatmap saved to: {save_path}")
    
    def plot_optimization_comparison(self, before_data: Dict, after_data: Dict, 
                                   save_path: str = "optimization_comparison.png"):
        """绘制优化前后对比图"""
        self._ensure_matplotlib()
        
        metrics = ['execution_time', 'memory_usage', 'operations_count']
        before_values = [before_data.get(m, 0) for m in metrics]
        after_values = [after_data.get(m, 0) for m in metrics]
        
        x = np.arange(len(metrics))
        width = 0.35
        
        plt.figure(figsize=self.fig_size, dpi=self.dpi)
        
        bars1 = plt.bar(x - width/2, before_values, width, label='Before Optimization', color='lightcoral')
        bars2 = plt.bar(x + width/2, after_values, width, label='After Optimization', color='lightgreen')
        
        # 添加改进百分比
        for i, (before, after) in enumerate(zip(before_values, after_values)):
            if before > 0:
                improvement = (before - after) / before * 100
                plt.text(i, max(before, after) + max(before_values) * 0.05, 
                        f'{improvement:+.1f}%', ha='center', fontweight='bold')
        
        plt.xlabel('Metrics')
        plt.ylabel('Values')
        plt.title('📊 YiRage Optimization Results Comparison')
        plt.xticks(x, ['Execution Time', 'Memory Usage', 'Operations Count'])
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Optimization comparison plot saved to: {save_path}")

# 全局可视化器实例
_visualizer = YirageVisualizer()

def plot_memory_usage(profiler_data, save_path: str = "memory_usage.png"):
    """绘制内存使用图表"""
    _visualizer.plot_memory_usage(profiler_data, save_path)

def plot_compute_utilization(profiler_data, save_path: str = "compute_utilization.png"):
    """绘制计算利用率图表"""
    _visualizer.plot_compute_utilization(profiler_data, save_path)

def plot_cim_heatmap(profiler_data, save_path: str = "cim_heatmap.png"):
    """绘制CIM操作热力图"""
    _visualizer.plot_cim_heatmap(profiler_data, save_path)

def plot_optimization_comparison(before_data: Dict, after_data: Dict, 
                               save_path: str = "optimization_comparison.png"):
    """绘制优化前后对比图"""
    _visualizer.plot_optimization_comparison(before_data, after_data, save_path)

def create_dashboard(profiler_data, output_dir: str = "./yirage_dashboard"):
    """创建完整的可视化仪表板"""
    import os
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    print("🎨 Creating YiRage visualization dashboard...")
    
    # 生成各类图表
    plot_memory_usage(profiler_data, os.path.join(output_dir, "memory_usage.png"))
    plot_compute_utilization(profiler_data, os.path.join(output_dir, "compute_utilization.png"))
    plot_cim_heatmap(profiler_data, os.path.join(output_dir, "cim_heatmap.png"))
    
    # 生成HTML报告
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>YiRage Performance Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ text-align: center; color: #2c3e50; }}
            .chart {{ margin: 20px 0; text-align: center; }}
            .chart img {{ max-width: 100%; height: auto; border: 1px solid #ddd; }}
            .stats {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 YiRage Performance Dashboard</h1>
            <p>Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats">
            <h3>📊 Performance Summary</h3>
            <p><strong>Total Duration:</strong> {profiler_data.get_total_duration():.3f}s</p>
            <p><strong>Operations Count:</strong> {len(profiler_data.operations)}</p>
            <p><strong>CIM Operations:</strong> {len(profiler_data.cim_operations)}</p>
        </div>
        
        <div class="chart">
            <h3>💾 Memory Usage</h3>
            <img src="memory_usage.png" alt="Memory Usage">
        </div>
        
        <div class="chart">
            <h3>⚡ Compute Utilization</h3>
            <img src="compute_utilization.png" alt="Compute Utilization">
        </div>
        
        <div class="chart">
            <h3>🔥 CIM Operations Heatmap</h3>
            <img src="cim_heatmap.png" alt="CIM Heatmap">
        </div>
    </body>
    </html>
    """
    
    with open(os.path.join(output_dir, "dashboard.html"), 'w') as f:
        f.write(html_content)
    
    print(f"✅ Dashboard created in: {output_dir}")
    print(f"📖 Open {os.path.join(output_dir, 'dashboard.html')} in your browser")

# 为了兼容性，如果matplotlib不可用，提供基本的文本输出
def text_summary(profiler_data):
    """生成文本格式的性能摘要"""
    print("\n" + "="*60)
    print("📊 YiRage Performance Summary (Text Mode)")
    print("="*60)
    
    # 基本统计
    print(f"⏱️  Total Duration: {profiler_data.get_total_duration():.3f}s")
    print(f"📊 Total Operations: {len(profiler_data.operations)}")
    print(f"🧠 CIM Operations: {len(profiler_data.cim_operations)}")
    
    # 内存统计
    if profiler_data.memory_usage:
        memory_values = [sample['memory_mb'] for sample in profiler_data.memory_usage]
        print(f"💾 Peak Memory: {max(memory_values):.1f}MB")
        print(f"💾 Avg Memory: {sum(memory_values)/len(memory_values):.1f}MB")
    
    # 操作类型统计
    if profiler_data.operations:
        op_types = {}
        for op in profiler_data.operations:
            op_name = op['name']
            if op_name not in op_types:
                op_types[op_name] = 0
            op_types[op_name] += 1
        
        print("\n🎯 Operation Types:")
        for op_name, count in sorted(op_types.items()):
            print(f"   {op_name}: {count}")
    
    print("="*60)
