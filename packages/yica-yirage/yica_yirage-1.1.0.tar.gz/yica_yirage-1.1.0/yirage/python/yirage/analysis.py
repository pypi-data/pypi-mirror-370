"""
YiRage Analysis Module
深度分析和优化建议工具

Features:
- 性能瓶颈分析
- 优化机会识别
- CIM效率评估
- 自动优化建议
"""

import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import warnings

@dataclass
class PerformanceBottleneck:
    """性能瓶颈描述"""
    name: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    impact: float  # 影响程度 (0-1)
    description: str
    recommendation: str
    estimated_improvement: float  # 预期改进程度 (0-1)

@dataclass
class OptimizationOpportunity:
    """优化机会描述"""
    category: str  # 'memory', 'compute', 'cim', 'fusion'
    description: str
    potential_gain: float  # 潜在收益 (0-1)
    implementation_effort: str  # 'low', 'medium', 'high'
    recommendation: str

class YirageAnalyzer:
    """YiRage深度分析器"""
    
    def __init__(self):
        self.thresholds = {
            'memory_efficiency': 0.8,  # 内存效率阈值
            'compute_efficiency': 0.7,  # 计算效率阈值
            'cim_utilization': 0.6,    # CIM利用率阈值
            'operation_duration': 0.1,  # 操作耗时阈值(秒)
        }
    
    def analyze_performance(self, profiler_data) -> Dict[str, Any]:
        """全面性能分析"""
        analysis_result = {
            'timestamp': time.time(),
            'total_duration': profiler_data.get_total_duration(),
            'bottlenecks': self._identify_bottlenecks(profiler_data),
            'opportunities': self._identify_opportunities(profiler_data),
            'efficiency_metrics': self._calculate_efficiency_metrics(profiler_data),
            'cim_analysis': self._analyze_cim_usage(profiler_data),
            'recommendations': self._generate_recommendations(profiler_data)
        }
        
        return analysis_result
    
    def _identify_bottlenecks(self, profiler_data) -> List[PerformanceBottleneck]:
        """识别性能瓶颈"""
        bottlenecks = []
        
        # 分析操作耗时
        if profiler_data.operations:
            total_time = profiler_data.get_total_duration()
            operations = profiler_data.operations
            
            # 找出耗时最长的操作
            slow_operations = [
                op for op in operations 
                if op['duration'] > self.thresholds['operation_duration']
            ]
            
            for op in sorted(slow_operations, key=lambda x: x['duration'], reverse=True)[:5]:
                severity = 'critical' if op['duration'] > total_time * 0.3 else \
                          'high' if op['duration'] > total_time * 0.1 else 'medium'
                
                bottlenecks.append(PerformanceBottleneck(
                    name=f"Slow Operation: {op['name']}",
                    severity=severity,
                    impact=op['duration'] / total_time,
                    description=f"Operation '{op['name']}' takes {op['duration']:.3f}s ({op['duration']/total_time*100:.1f}% of total time)",
                    recommendation=f"Consider optimizing '{op['name']}' operation or using CIM acceleration",
                    estimated_improvement=min(0.5, op['duration'] / total_time * 0.8)
                ))
        
        # 分析内存使用
        if profiler_data.memory_usage:
            memory_values = [sample['memory_mb'] for sample in profiler_data.memory_usage]
            peak_memory = max(memory_values)
            avg_memory = sum(memory_values) / len(memory_values)
            
            if peak_memory > 1000:  # > 1GB
                bottlenecks.append(PerformanceBottleneck(
                    name="High Memory Usage",
                    severity='high' if peak_memory > 2000 else 'medium',
                    impact=min(1.0, peak_memory / 2000),
                    description=f"Peak memory usage: {peak_memory:.1f}MB",
                    recommendation="Consider memory optimization techniques or batch processing",
                    estimated_improvement=0.3
                ))
        
        return bottlenecks
    
    def _identify_opportunities(self, profiler_data) -> List[OptimizationOpportunity]:
        """识别优化机会"""
        opportunities = []
        
        # CIM利用率分析
        if profiler_data.operations and profiler_data.cim_operations:
            total_ops = len(profiler_data.operations)
            cim_ops = len(profiler_data.cim_operations)
            cim_utilization = cim_ops / total_ops
            
            if cim_utilization < self.thresholds['cim_utilization']:
                opportunities.append(OptimizationOpportunity(
                    category='cim',
                    description=f"Low CIM utilization: {cim_utilization:.1%}",
                    potential_gain=0.4,
                    implementation_effort='medium',
                    recommendation="Identify more operations that can be accelerated with CIM"
                ))
        
        # 操作融合机会
        if profiler_data.operations:
            # 查找可融合的操作模式
            op_names = [op['name'] for op in profiler_data.operations]
            fusion_patterns = self._detect_fusion_patterns(op_names)
            
            for pattern in fusion_patterns:
                opportunities.append(OptimizationOpportunity(
                    category='fusion',
                    description=f"Detected fusable pattern: {pattern['pattern']}",
                    potential_gain=pattern['potential_gain'],
                    implementation_effort='low',
                    recommendation=f"Use @fuse_operators decorator to fuse {pattern['pattern']}"
                ))
        
        # 内存优化机会
        if profiler_data.memory_usage:
            memory_variance = self._calculate_memory_variance(profiler_data.memory_usage)
            if memory_variance > 100:  # 变化大于100MB
                opportunities.append(OptimizationOpportunity(
                    category='memory',
                    description=f"High memory variance: {memory_variance:.1f}MB",
                    potential_gain=0.2,
                    implementation_effort='medium',
                    recommendation="Implement memory pooling or more efficient allocation strategies"
                ))
        
        return opportunities
    
    def _calculate_efficiency_metrics(self, profiler_data) -> Dict[str, float]:
        """计算效率指标"""
        metrics = {}
        
        # 计算利用率
        if profiler_data.operations:
            total_duration = profiler_data.get_total_duration()
            active_duration = sum(op['duration'] for op in profiler_data.operations)
            metrics['compute_efficiency'] = min(1.0, active_duration / total_duration)
        
        # CIM效率
        if profiler_data.cim_operations and profiler_data.operations:
            cim_count = len(profiler_data.cim_operations)
            total_count = len(profiler_data.operations)
            metrics['cim_utilization'] = cim_count / total_count
        
        # 内存效率
        if profiler_data.memory_usage:
            memory_values = [sample['memory_mb'] for sample in profiler_data.memory_usage]
            peak_memory = max(memory_values)
            avg_memory = sum(memory_values) / len(memory_values)
            metrics['memory_efficiency'] = avg_memory / peak_memory if peak_memory > 0 else 1.0
        
        return metrics
    
    def _analyze_cim_usage(self, profiler_data) -> Dict[str, Any]:
        """分析CIM使用情况"""
        if not profiler_data.cim_operations:
            return {'available': False, 'message': 'No CIM operations recorded'}
        
        cim_ops = profiler_data.cim_operations
        
        # 操作类型统计
        op_types = {}
        for op in cim_ops:
            op_type = op['operation']
            if op_type not in op_types:
                op_types[op_type] = {'count': 0, 'total_time': 0, 'shapes': set()}
            op_types[op_type]['count'] += 1
            op_types[op_type]['total_time'] += op['duration']
            op_types[op_type]['shapes'].add(str(op['shape']))
        
        # 计算CIM效率
        total_cim_time = sum(op['duration'] for op in cim_ops)
        total_time = profiler_data.get_total_duration()
        cim_time_ratio = total_cim_time / total_time if total_time > 0 else 0
        
        return {
            'available': True,
            'operation_types': {k: {**v, 'shapes': list(v['shapes'])} for k, v in op_types.items()},
            'total_cim_operations': len(cim_ops),
            'total_cim_time': total_cim_time,
            'cim_time_ratio': cim_time_ratio,
            'avg_operation_time': total_cim_time / len(cim_ops),
            'efficiency_score': min(1.0, cim_time_ratio * 2)  # 理想情况下CIM占50%+时间
        }
    
    def _generate_recommendations(self, profiler_data) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 基于瓶颈的建议
        bottlenecks = self._identify_bottlenecks(profiler_data)
        for bottleneck in bottlenecks[:3]:  # 只显示前3个最重要的
            recommendations.append(bottleneck.recommendation)
        
        # 基于机会的建议
        opportunities = self._identify_opportunities(profiler_data)
        for opp in opportunities[:2]:  # 只显示前2个最有价值的
            recommendations.append(opp.recommendation)
        
        # 通用建议
        if profiler_data.operations:
            op_count = len(profiler_data.operations)
            if op_count > 100:
                recommendations.append("Consider batching operations to reduce overhead")
        
        if not profiler_data.cim_operations:
            recommendations.append("Consider using @cim_operator decorator for compute-intensive operations")
        
        return recommendations
    
    def _detect_fusion_patterns(self, op_names: List[str]) -> List[Dict]:
        """检测可融合的操作模式"""
        patterns = []
        
        # 检测常见模式
        common_patterns = [
            (['linear', 'relu'], 0.3),
            (['matmul', 'add'], 0.25),
            (['conv', 'batchnorm'], 0.35),
            (['attention', 'linear'], 0.4)
        ]
        
        for pattern, gain in common_patterns:
            if self._pattern_exists(op_names, pattern):
                patterns.append({
                    'pattern': ' -> '.join(pattern),
                    'potential_gain': gain,
                    'occurrences': self._count_pattern_occurrences(op_names, pattern)
                })
        
        return patterns
    
    def _pattern_exists(self, op_names: List[str], pattern: List[str]) -> bool:
        """检查操作序列中是否存在特定模式"""
        op_names_lower = [name.lower() for name in op_names]
        pattern_lower = [p.lower() for p in pattern]
        
        for i in range(len(op_names_lower) - len(pattern_lower) + 1):
            if all(any(p in op_names_lower[i+j] for p in [pattern_lower[j]]) 
                   for j in range(len(pattern_lower))):
                return True
        return False
    
    def _count_pattern_occurrences(self, op_names: List[str], pattern: List[str]) -> int:
        """计算模式出现次数"""
        count = 0
        op_names_lower = [name.lower() for name in op_names]
        pattern_lower = [p.lower() for p in pattern]
        
        for i in range(len(op_names_lower) - len(pattern_lower) + 1):
            if all(any(p in op_names_lower[i+j] for p in [pattern_lower[j]]) 
                   for j in range(len(pattern_lower))):
                count += 1
        return count
    
    def _calculate_memory_variance(self, memory_usage: List[Dict]) -> float:
        """计算内存使用方差"""
        if len(memory_usage) < 2:
            return 0.0
        
        values = [sample['memory_mb'] for sample in memory_usage]
        mean_val = sum(values) / len(values)
        variance = sum((v - mean_val) ** 2 for v in values) / len(values)
        return variance ** 0.5  # 标准差

# 全局分析器实例
_analyzer = YirageAnalyzer()

def analyze_performance(profiler_data) -> Dict[str, Any]:
    """分析性能数据"""
    return _analyzer.analyze_performance(profiler_data)

def generate_optimization_report(profiler_data, output_file: str = "optimization_report.json"):
    """生成优化报告"""
    analysis_result = analyze_performance(profiler_data)
    
    # 生成详细报告
    report = {
        'metadata': {
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'yirage_version': '1.0.9',
            'analysis_duration': analysis_result['total_duration']
        },
        'executive_summary': {
            'total_bottlenecks': len(analysis_result['bottlenecks']),
            'optimization_opportunities': len(analysis_result['opportunities']),
            'top_recommendation': analysis_result['recommendations'][0] if analysis_result['recommendations'] else 'No specific recommendations'
        },
        'detailed_analysis': analysis_result,
        'action_items': _generate_action_items(analysis_result)
    }
    
    # 保存报告
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"✅ Optimization report saved to: {output_file}")
    return report

def _generate_action_items(analysis_result: Dict) -> List[Dict]:
    """生成行动项目"""
    action_items = []
    
    # 从瓶颈生成行动项目
    for bottleneck in analysis_result['bottlenecks']:
        action_items.append({
            'priority': bottleneck.severity,
            'category': 'bottleneck',
            'title': f"Address {bottleneck.name}",
            'description': bottleneck.description,
            'action': bottleneck.recommendation,
            'estimated_impact': bottleneck.estimated_improvement
        })
    
    # 从机会生成行动项目
    for opportunity in analysis_result['opportunities']:
        priority = 'high' if opportunity.potential_gain > 0.3 else \
                  'medium' if opportunity.potential_gain > 0.1 else 'low'
        
        action_items.append({
            'priority': priority,
            'category': 'opportunity',
            'title': f"Implement {opportunity.category} optimization",
            'description': opportunity.description,
            'action': opportunity.recommendation,
            'estimated_impact': opportunity.potential_gain
        })
    
    # 按优先级排序
    priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    action_items.sort(key=lambda x: priority_order.get(x['priority'], 3))
    
    return action_items

def print_analysis_summary(profiler_data):
    """打印分析摘要"""
    analysis = analyze_performance(profiler_data)
    
    print("\n" + "="*60)
    print("🔍 YiRage Performance Analysis Summary")
    print("="*60)
    
    # 效率指标
    metrics = analysis['efficiency_metrics']
    print("\n📊 Efficiency Metrics:")
    for metric, value in metrics.items():
        status = "✅" if value > 0.8 else "⚠️" if value > 0.5 else "❌"
        print(f"   {status} {metric.replace('_', ' ').title()}: {value:.1%}")
    
    # 瓶颈
    bottlenecks = analysis['bottlenecks']
    if bottlenecks:
        print(f"\n🚧 Performance Bottlenecks ({len(bottlenecks)}):")
        for bottleneck in bottlenecks[:3]:
            severity_icon = "🔴" if bottleneck.severity == 'critical' else \
                           "🟠" if bottleneck.severity == 'high' else "🟡"
            print(f"   {severity_icon} {bottleneck.name} ({bottleneck.severity})")
            print(f"      Impact: {bottleneck.impact:.1%} | {bottleneck.description}")
    
    # 优化机会
    opportunities = analysis['opportunities']
    if opportunities:
        print(f"\n🎯 Optimization Opportunities ({len(opportunities)}):")
        for opp in opportunities[:3]:
            print(f"   💡 {opp.category.title()}: {opp.description}")
            print(f"      Potential gain: {opp.potential_gain:.1%} | Effort: {opp.implementation_effort}")
    
    # 建议
    recommendations = analysis['recommendations']
    if recommendations:
        print(f"\n🎯 Top Recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec}")
    
    print("="*60)
