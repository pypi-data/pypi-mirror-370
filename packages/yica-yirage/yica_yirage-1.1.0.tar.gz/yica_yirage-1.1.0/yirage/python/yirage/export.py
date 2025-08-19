"""
YiRage Export Module
数据导出和格式转换工具

Features:
- 性能数据导出
- 多种格式支持
- 报告生成
- 数据共享
"""

import json
import csv
import time
import warnings
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    warnings.warn("pandas not available, some export features disabled", UserWarning)

class YirageExporter:
    """YiRage数据导出器"""
    
    def __init__(self):
        self.supported_formats = ['json', 'csv', 'txt', 'html']
        if PANDAS_AVAILABLE:
            self.supported_formats.extend(['xlsx', 'parquet'])
    
    def export_performance_data(self, profiler_data, format: str = 'json', 
                               filename: str = None) -> str:
        """导出性能数据"""
        
        if format not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format}. Supported: {self.supported_formats}")
        
        # 生成默认文件名
        if filename is None:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"yirage_performance_{timestamp}.{format}"
        
        # 准备数据
        data = self._prepare_export_data(profiler_data)
        
        # 根据格式导出
        if format == 'json':
            return self._export_json(data, filename)
        elif format == 'csv':
            return self._export_csv(data, filename)
        elif format == 'txt':
            return self._export_txt(data, filename)
        elif format == 'html':
            return self._export_html(data, filename)
        elif format == 'xlsx' and PANDAS_AVAILABLE:
            return self._export_xlsx(data, filename)
        elif format == 'parquet' and PANDAS_AVAILABLE:
            return self._export_parquet(data, filename)
        else:
            raise ValueError(f"Export format {format} not available")
    
    def _prepare_export_data(self, profiler_data) -> Dict[str, Any]:
        """准备导出数据"""
        return {
            'metadata': {
                'exported_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'yirage_version': '1.0.9',
                'total_duration': profiler_data.get_total_duration(),
                'data_points': {
                    'operations': len(profiler_data.operations),
                    'cim_operations': len(profiler_data.cim_operations),
                    'memory_samples': len(profiler_data.memory_usage)
                }
            },
            'summary': profiler_data.get_operation_summary(),
            'operations': profiler_data.operations,
            'cim_operations': profiler_data.cim_operations,
            'memory_usage': profiler_data.memory_usage,
            'profiler_metadata': profiler_data.metadata
        }
    
    def _export_json(self, data: Dict, filename: str) -> str:
        """导出JSON格式"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"✅ JSON export saved to: {filename}")
        return filename
    
    def _export_csv(self, data: Dict, filename: str) -> str:
        """导出CSV格式"""
        # 导出操作数据
        base_name = Path(filename).stem
        
        # 操作数据CSV
        ops_filename = f"{base_name}_operations.csv"
        with open(ops_filename, 'w', newline='') as f:
            if data['operations']:
                writer = csv.DictWriter(f, fieldnames=data['operations'][0].keys())
                writer.writeheader()
                writer.writerows(data['operations'])
        
        # CIM操作数据CSV
        cim_filename = f"{base_name}_cim_operations.csv"
        with open(cim_filename, 'w', newline='') as f:
            if data['cim_operations']:
                writer = csv.DictWriter(f, fieldnames=data['cim_operations'][0].keys())
                writer.writeheader()
                writer.writerows(data['cim_operations'])
        
        # 内存数据CSV
        memory_filename = f"{base_name}_memory_usage.csv"
        with open(memory_filename, 'w', newline='') as f:
            if data['memory_usage']:
                writer = csv.DictWriter(f, fieldnames=data['memory_usage'][0].keys())
                writer.writeheader()
                writer.writerows(data['memory_usage'])
        
        # 元数据CSV
        meta_filename = f"{base_name}_metadata.csv"
        with open(meta_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Value'])
            for key, value in data['metadata'].items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        writer.writerow([f"{key}.{subkey}", subvalue])
                else:
                    writer.writerow([key, value])
        
        print(f"✅ CSV exports saved to: {base_name}_*.csv")
        return ops_filename
    
    def _export_txt(self, data: Dict, filename: str) -> str:
        """导出文本格式"""
        with open(filename, 'w') as f:
            f.write("YiRage Performance Report\n")
            f.write("=" * 50 + "\n\n")
            
            # 元数据
            f.write("Metadata:\n")
            f.write("-" * 20 + "\n")
            for key, value in data['metadata'].items():
                if isinstance(value, dict):
                    f.write(f"{key}:\n")
                    for subkey, subvalue in value.items():
                        f.write(f"  {subkey}: {subvalue}\n")
                else:
                    f.write(f"{key}: {value}\n")
            f.write("\n")
            
            # 摘要
            if data['summary']:
                f.write("Summary:\n")
                f.write("-" * 20 + "\n")
                for key, value in data['summary'].items():
                    f.write(f"{key}: {value}\n")
                f.write("\n")
            
            # 操作统计
            if data['operations']:
                f.write("Operations:\n")
                f.write("-" * 20 + "\n")
                op_types = {}
                for op in data['operations']:
                    op_name = op['name']
                    if op_name not in op_types:
                        op_types[op_name] = {'count': 0, 'total_time': 0}
                    op_types[op_name]['count'] += 1
                    op_types[op_name]['total_time'] += op['duration']
                
                for op_name, stats in sorted(op_types.items()):
                    f.write(f"{op_name}: {stats['count']} ops, {stats['total_time']:.3f}s total\n")
                f.write("\n")
            
            # CIM操作统计
            if data['cim_operations']:
                f.write("CIM Operations:\n")
                f.write("-" * 20 + "\n")
                cim_types = {}
                for cim_op in data['cim_operations']:
                    op_name = cim_op['operation']
                    if op_name not in cim_types:
                        cim_types[op_name] = {'count': 0, 'total_time': 0}
                    cim_types[op_name]['count'] += 1
                    cim_types[op_name]['total_time'] += cim_op['duration']
                
                for op_name, stats in sorted(cim_types.items()):
                    f.write(f"{op_name}: {stats['count']} ops, {stats['total_time']:.3f}s total\n")
        
        print(f"✅ Text export saved to: {filename}")
        return filename
    
    def _export_html(self, data: Dict, filename: str) -> str:
        """导出HTML格式"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>YiRage Performance Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ color: #2c3e50; text-align: center; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .metadata {{ background-color: #f8f9fa; }}
                .summary {{ background-color: #e3f2fd; }}
                .operations {{ background-color: #f3e5f5; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f5f5f5; }}
                .metric {{ display: inline-block; margin: 5px 10px; padding: 5px; background: #e8f5e8; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 YiRage Performance Report</h1>
                <p>Generated on {data['metadata']['exported_at']}</p>
            </div>
            
            <div class="section metadata">
                <h2>📊 Metadata</h2>
                <div class="metric">Duration: {data['metadata']['total_duration']:.3f}s</div>
                <div class="metric">Operations: {data['metadata']['data_points']['operations']}</div>
                <div class="metric">CIM Ops: {data['metadata']['data_points']['cim_operations']}</div>
                <div class="metric">Memory Samples: {data['metadata']['data_points']['memory_samples']}</div>
            </div>
        """
        
        # 添加摘要
        if data['summary']:
            html_content += f"""
            <div class="section summary">
                <h2>📈 Summary</h2>
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
            """
            for key, value in data['summary'].items():
                html_content += f"<tr><td>{key.replace('_', ' ').title()}</td><td>{value}</td></tr>"
            html_content += "</table></div>"
        
        # 添加操作表格
        if data['operations']:
            html_content += """
            <div class="section operations">
                <h2>⚡ Operations</h2>
                <table>
                    <tr><th>Name</th><th>Duration (s)</th><th>Timestamp</th></tr>
            """
            for op in data['operations'][:20]:  # 只显示前20个
                html_content += f"""
                <tr>
                    <td>{op['name']}</td>
                    <td>{op['duration']:.3f}</td>
                    <td>{time.strftime('%H:%M:%S', time.localtime(op['timestamp']))}</td>
                </tr>
                """
            if len(data['operations']) > 20:
                html_content += f"<tr><td colspan='3'>... and {len(data['operations'])-20} more operations</td></tr>"
            html_content += "</table></div>"
        
        html_content += """
        </body>
        </html>
        """
        
        with open(filename, 'w') as f:
            f.write(html_content)
        
        print(f"✅ HTML export saved to: {filename}")
        return filename
    
    def _export_xlsx(self, data: Dict, filename: str) -> str:
        """导出Excel格式"""
        if not PANDAS_AVAILABLE:
            raise RuntimeError("pandas required for Excel export")
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 元数据工作表
            metadata_df = pd.DataFrame([
                {'Metric': key, 'Value': value} 
                for key, value in data['metadata'].items()
                if not isinstance(value, dict)
            ])
            metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
            
            # 操作工作表
            if data['operations']:
                operations_df = pd.DataFrame(data['operations'])
                operations_df.to_excel(writer, sheet_name='Operations', index=False)
            
            # CIM操作工作表
            if data['cim_operations']:
                cim_df = pd.DataFrame(data['cim_operations'])
                cim_df.to_excel(writer, sheet_name='CIM_Operations', index=False)
            
            # 内存使用工作表
            if data['memory_usage']:
                memory_df = pd.DataFrame(data['memory_usage'])
                memory_df.to_excel(writer, sheet_name='Memory_Usage', index=False)
        
        print(f"✅ Excel export saved to: {filename}")
        return filename
    
    def _export_parquet(self, data: Dict, filename: str) -> str:
        """导出Parquet格式"""
        if not PANDAS_AVAILABLE:
            raise RuntimeError("pandas required for Parquet export")
        
        base_name = Path(filename).stem
        
        # 操作数据
        if data['operations']:
            operations_df = pd.DataFrame(data['operations'])
            operations_df.to_parquet(f"{base_name}_operations.parquet")
        
        # CIM操作数据
        if data['cim_operations']:
            cim_df = pd.DataFrame(data['cim_operations'])
            cim_df.to_parquet(f"{base_name}_cim_operations.parquet")
        
        # 内存数据
        if data['memory_usage']:
            memory_df = pd.DataFrame(data['memory_usage'])
            memory_df.to_parquet(f"{base_name}_memory_usage.parquet")
        
        print(f"✅ Parquet exports saved to: {base_name}_*.parquet")
        return f"{base_name}_operations.parquet"

# 全局导出器实例
_exporter = YirageExporter()

def save_performance_data(profiler_data, format: str = 'json', filename: str = None) -> str:
    """保存性能数据"""
    return _exporter.export_performance_data(profiler_data, format, filename)

def export_to_json(profiler_data, filename: str = None) -> str:
    """导出为JSON格式"""
    return save_performance_data(profiler_data, 'json', filename)

def export_to_csv(profiler_data, filename: str = None) -> str:
    """导出为CSV格式"""
    return save_performance_data(profiler_data, 'csv', filename)

def export_to_html(profiler_data, filename: str = None) -> str:
    """导出为HTML格式"""
    return save_performance_data(profiler_data, 'html', filename)

def create_performance_bundle(profiler_data, output_dir: str = "./yirage_export"):
    """创建完整的性能数据包"""
    from pathlib import Path
    import os
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print(f"📦 Creating YiRage performance bundle in: {output_dir}")
    
    # 生成多种格式的导出
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    base_name = f"yirage_performance_{timestamp}"
    
    exports = []
    
    # JSON导出
    json_file = output_path / f"{base_name}.json"
    save_performance_data(profiler_data, 'json', str(json_file))
    exports.append(json_file)
    
    # HTML报告
    html_file = output_path / f"{base_name}_report.html"
    save_performance_data(profiler_data, 'html', str(html_file))
    exports.append(html_file)
    
    # CSV导出
    csv_file = output_path / f"{base_name}.csv"
    save_performance_data(profiler_data, 'csv', str(csv_file))
    exports.append(csv_file)
    
    # 如果pandas可用，也生成Excel
    if PANDAS_AVAILABLE:
        try:
            xlsx_file = output_path / f"{base_name}.xlsx"
            save_performance_data(profiler_data, 'xlsx', str(xlsx_file))
            exports.append(xlsx_file)
        except Exception as e:
            print(f"⚠️  Excel export failed: {e}")
    
    # 创建README
    readme_content = f"""
# YiRage Performance Bundle

Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}
YiRage Version: 1.0.9

## Files

- `{base_name}.json` - Complete performance data in JSON format
- `{base_name}_report.html` - HTML performance report (open in browser)
- `{base_name}_*.csv` - CSV data files for analysis tools
{"- `" + base_name + ".xlsx` - Excel workbook with multiple sheets" if PANDAS_AVAILABLE else ""}

## Usage

1. Open the HTML report in your browser for visual analysis
2. Use JSON file for programmatic access to all data
3. Import CSV files into your preferred analysis tools
4. Share this bundle with team members for collaboration

## Data Summary

- Total Duration: {profiler_data.get_total_duration():.3f}s
- Operations: {len(profiler_data.operations)}
- CIM Operations: {len(profiler_data.cim_operations)}
- Memory Samples: {len(profiler_data.memory_usage)}
"""
    
    readme_file = output_path / "README.md"
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    
    print(f"✅ Performance bundle created with {len(exports)} files")
    print(f"📖 Open {html_file} in your browser to view the report")
    
    return str(output_path)

def get_supported_formats() -> List[str]:
    """获取支持的导出格式"""
    return _exporter.supported_formats.copy()
