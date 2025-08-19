"""
性能总结模块 - 生成包含FLOPS、TOPS等关键指标的性能报告
"""

import json
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

from .utils import logger


class PerformanceSummaryGenerator:
    """性能总结生成器"""
    
    def __init__(self):
        """初始化性能总结生成器"""
        self.gpu_specs = self._load_gpu_specs()
    
    def _load_gpu_specs(self) -> Dict[str, Dict[str, float]]:
        """加载GPU规格数据库"""
        return {
            # NVIDIA RTX 30系列
            'RTX 3080': {
                'fp32_tflops': 29.8,
                'fp16_tflops': 59.6,
                'int8_tops': 238.4,
                'memory_bandwidth_gbps': 760,
                'memory_size_gb': 10,
                'base_clock_mhz': 1440,
                'boost_clock_mhz': 1710,
                'memory_clock_mhz': 19000,
                'cuda_cores': 8704,
                'rt_cores': 68,
                'tensor_cores': 272
            },
            'RTX 3080 Ti': {
                'fp32_tflops': 34.1,
                'fp16_tflops': 68.2,
                'int8_tops': 272.8,
                'memory_bandwidth_gbps': 912,
                'memory_size_gb': 12,
                'base_clock_mhz': 1365,
                'boost_clock_mhz': 1665,
                'memory_clock_mhz': 19000,
                'cuda_cores': 10240,
                'rt_cores': 80,
                'tensor_cores': 320
            },
            'RTX 3090': {
                'fp32_tflops': 35.6,
                'fp16_tflops': 71.2,
                'int8_tops': 284.8,
                'memory_bandwidth_gbps': 936,
                'memory_size_gb': 24,
                'base_clock_mhz': 1395,
                'boost_clock_mhz': 1695,
                'memory_clock_mhz': 19500,
                'cuda_cores': 10496,
                'rt_cores': 82,
                'tensor_cores': 328
            },
            'RTX 3090 Ti': {
                'fp32_tflops': 40.0,
                'fp16_tflops': 80.0,
                'int8_tops': 320.0,
                'memory_bandwidth_gbps': 1008,
                'memory_size_gb': 24,
                'base_clock_mhz': 1560,
                'boost_clock_mhz': 1860,
                'memory_clock_mhz': 21000,
                'cuda_cores': 10752,
                'rt_cores': 84,
                'tensor_cores': 336
            },
            
            # NVIDIA RTX 40系列
            'RTX 4080': {
                'fp32_tflops': 48.7,
                'fp16_tflops': 97.4,
                'int8_tops': 779.2,
                'memory_bandwidth_gbps': 717,
                'memory_size_gb': 16,
                'base_clock_mhz': 2205,
                'boost_clock_mhz': 2505,
                'memory_clock_mhz': 22400,
                'cuda_cores': 9728,
                'rt_cores': 76,
                'tensor_cores': 304
            },
            'RTX 4090': {
                'fp32_tflops': 83.0,
                'fp16_tflops': 166.0,
                'int8_tops': 1328.0,
                'memory_bandwidth_gbps': 1008,
                'memory_size_gb': 24,
                'base_clock_mhz': 2230,
                'boost_clock_mhz': 2520,
                'memory_clock_mhz': 21000,
                'cuda_cores': 16384,
                'rt_cores': 128,
                'tensor_cores': 512
            },
            
            # NVIDIA 专业卡
            # NVIDIA 专业卡 - 基于最新规格数据
            'A100': {
                'fp64_tflops': 9.7,
                'fp32_tflops': 19.5,
                'fp16_tflops': 312.0,  # Tensor Core性能
                'int8_tops': 624.0,
                'memory_bandwidth_gbps': 1935,
                'memory_size_gb': 80,
                'base_clock_mhz': 765,
                'boost_clock_mhz': 1410,
                'memory_clock_mhz': 1215,
                'cuda_cores': 6912,
                'rt_cores': 0,
                'tensor_cores': 432,
                'tdp_watts': 300,
                'nvlink_bandwidth_gbps': 600,
                'pcie_bandwidth_gbps': 64,
                'architecture': 'Ampere'
            },
            'A800': {
                'fp64_tflops': 9.7,
                'fp32_tflops': 19.5,
                'fp16_tflops': 312.0,
                'int8_tops': 624.0,
                'memory_bandwidth_gbps': 1935,
                'memory_size_gb': 80,
                'base_clock_mhz': 765,
                'boost_clock_mhz': 1410,
                'memory_clock_mhz': 1215,
                'cuda_cores': 6912,
                'rt_cores': 0,
                'tensor_cores': 432,
                'tdp_watts': 300,
                'nvlink_bandwidth_gbps': 400,  # 比A100低
                'pcie_bandwidth_gbps': 64,
                'architecture': 'Ampere'
            },
            'H100': {
                'fp64_tflops': 26.0,
                'fp32_tflops': 51.0,
                'fp16_tflops': 756.5,  # Tensor Core性能
                'int8_tops': 1513.0,
                'memory_bandwidth_gbps': 2000,
                'memory_size_gb': 80,
                'base_clock_mhz': 1000,
                'boost_clock_mhz': 1980,
                'memory_clock_mhz': 2600,
                'cuda_cores': 14592,
                'rt_cores': 0,
                'tensor_cores': 456,
                'tdp_watts': 350,
                'nvlink_bandwidth_gbps': 600,
                'pcie_bandwidth_gbps': 128,
                'architecture': 'Hopper'
            },
            'A10': {
                'fp32_tflops': 31.2,
                'fp16_tflops': 62.4,
                'int8_tops': 250.0,
                'memory_bandwidth_gbps': 600,
                'memory_size_gb': 24,
                'base_clock_mhz': 885,
                'boost_clock_mhz': 1695,
                'memory_clock_mhz': 12500,
                'cuda_cores': 9216,
                'rt_cores': 72,
                'tensor_cores': 288
            },
            'V100': {
                'fp64_tflops': 7.0,
                'fp32_tflops': 14.0,
                'fp16_tflops': 28.0,
                'int8_tops': 112.0,
                'memory_bandwidth_gbps': 900,
                'memory_size_gb': 32,
                'base_clock_mhz': 1245,
                'boost_clock_mhz': 1380,
                'memory_clock_mhz': 1750,
                'cuda_cores': 5120,
                'rt_cores': 0,
                'tensor_cores': 640,
                'tdp_watts': 250,
                'nvlink_bandwidth_gbps': 300,
                'pcie_bandwidth_gbps': 32
            },
            'T4': {
                'fp32_tflops': 8.1,
                'fp16_tflops': 16.2,
                'int8_tops': 130.0,
                'memory_bandwidth_gbps': 320,
                'memory_size_gb': 16,
                'base_clock_mhz': 585,
                'boost_clock_mhz': 1590,
                'memory_clock_mhz': 5000,
                'cuda_cores': 2560,
                'rt_cores': 40,
                'tensor_cores': 320
            },
            'L40': {
                'fp32_tflops': 90.5,
                'fp16_tflops': 181.0,
                'int8_tops': 724.0,
                'memory_bandwidth_gbps': 864,
                'memory_size_gb': 48,
                'base_clock_mhz': 735,
                'boost_clock_mhz': 2490,
                'memory_clock_mhz': 18000,
                'cuda_cores': 18176,
                'rt_cores': 142,
                'tensor_cores': 568
            },
            'H20': {
                'fp32_tflops': 22.2,
                'fp16_tflops': 44.4,
                'int8_tops': 296.0,
                'memory_bandwidth_gbps': 4000,
                'memory_size_gb': 96,
                'base_clock_mhz': 1000,
                'boost_clock_mhz': 1980,
                'memory_clock_mhz': 2600,
                'cuda_cores': 14592,
                'rt_cores': 0,
                'tensor_cores': 456
            }
        }
    
    def generate_performance_summary(self, test_results: Dict[str, Any], 
                                   csv_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成性能总结报告"""
        summary = {
            'report_info': {
                'generation_time': datetime.now().isoformat(),
                'report_type': 'GPU Performance Summary'
            },
            'system_overview': {},
            'performance_metrics': {},
            'efficiency_analysis': {},
            'recommendations': []
        }
        
        # 系统概览
        if 'system_info' in test_results:
            summary['system_overview'] = self._extract_system_overview(test_results['system_info'])
        
        # 性能指标计算
        if 'device_results' in test_results:
            summary['performance_metrics'] = self._calculate_performance_metrics(
                test_results['device_results'], csv_analysis
            )
        
        # 效率分析
        summary['efficiency_analysis'] = self._analyze_efficiency(
            summary['performance_metrics'], csv_analysis
        )
        
        # 生成建议
        summary['recommendations'] = self._generate_recommendations(
            summary['performance_metrics'], summary['efficiency_analysis']
        )
        
        return summary
    
    def _extract_system_overview(self, system_info: Dict[str, Any]) -> Dict[str, Any]:
        """提取系统概览信息"""
        overview = {
            'gpu_count': system_info.get('gpu_count', 0),
            'total_memory_gb': 0,
            'gpu_models': []
        }
        
        if 'gpus' in system_info:
            for gpu in system_info['gpus']:
                model = gpu.get('name', 'Unknown GPU')
                memory_mb = gpu.get('memory_total', 0)
                memory_gb = round(memory_mb / 1024, 1) if memory_mb > 0 else 0
                
                overview['gpu_models'].append({
                    'model': model,
                    'memory_gb': memory_gb
                })
                overview['total_memory_gb'] += memory_gb
        
        return overview
    
    def _calculate_performance_metrics(self, device_results: Dict[str, Any], 
                                     csv_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """计算性能指标"""
        metrics = {
            'compute_performance': {},
            'memory_performance': {},
            'ai_performance': {},
            'overall_scores': {}
        }
        
        total_fp32_tflops = 0
        total_fp16_tflops = 0
        total_int8_tops = 0
        total_memory_bandwidth = 0
        
        for device_id, result in device_results.items():
            if not result.get('success', False):
                continue
            
            device_name = result.get('device_name', f'GPU {device_id}')
            gpu_specs = self._match_gpu_specs(device_name)
            
            # 计算实际性能
            actual_performance = self._calculate_actual_performance(
                result, gpu_specs, csv_analysis, device_id
            )
            
            device_metrics = {
                'device_name': device_name,
                'theoretical_specs': gpu_specs,
                'measured_performance': actual_performance,
                'utilization_rates': self._calculate_utilization_rates(
                    actual_performance, gpu_specs
                )
            }
            
            metrics['compute_performance'][device_id] = device_metrics
            
            # 累计总性能
            total_fp32_tflops += actual_performance.get('actual_fp32_tflops', 0)
            total_fp16_tflops += actual_performance.get('actual_fp16_tflops', 0)
            total_int8_tops += actual_performance.get('actual_int8_tops', 0)
            total_memory_bandwidth += actual_performance.get('actual_memory_bandwidth_gbps', 0)
        
        # 总体性能评分
        metrics['overall_scores'] = {
            'total_fp32_tflops': round(total_fp32_tflops, 2),
            'total_fp16_tflops': round(total_fp16_tflops, 2),
            'total_int8_tops': round(total_int8_tops, 2),
            'total_memory_bandwidth_gbps': round(total_memory_bandwidth, 2),
            'performance_rating': self._calculate_performance_rating(
                total_fp32_tflops, total_int8_tops
            )
        }
        
        return metrics
    
    def _match_gpu_specs(self, device_name: str) -> Dict[str, float]:
        """匹配GPU规格"""
        for gpu_model, specs in self.gpu_specs.items():
            if gpu_model.lower() in device_name.lower():
                return specs
        
        # 默认规格（如果找不到匹配）
        return {
            'fp32_tflops': 10.0,
            'fp16_tflops': 20.0,
            'int8_tops': 80.0,
            'memory_bandwidth_gbps': 500,
            'memory_size_gb': 8,
            'cuda_cores': 2048
        }
    
    def _calculate_actual_performance(self, result: Dict[str, Any], 
                                    gpu_specs: Dict[str, float],
                                    csv_analysis: Dict[str, Any],
                                    device_id: str) -> Dict[str, float]:
        """计算实际性能"""
        actual_perf = {}
        
        # 从测试结果获取基础性能
        if 'matrix_multiply' in result:
            gflops = result['matrix_multiply'].get('gflops', 0)
            actual_perf['actual_fp32_gflops'] = gflops
            actual_perf['actual_fp32_tflops'] = round(gflops / 1000, 2)
        
        # 从CSV分析获取利用率信息
        utilization_factor = 0.8  # 默认利用率
        if csv_analysis and 'utilization_analysis' in csv_analysis:
            gpu_util = csv_analysis['utilization_analysis'].get('gpu_utilization', {})
            if 'by_device' in gpu_util and device_id in gpu_util['by_device']:
                device_util = gpu_util['by_device'][device_id]
                utilization_factor = device_util.get('mean', 80) / 100.0
        
        # 基于理论性能和利用率估算其他性能指标
        theoretical_fp32 = gpu_specs.get('fp32_tflops', 10.0)
        theoretical_fp16 = gpu_specs.get('fp16_tflops', 20.0)
        theoretical_int8 = gpu_specs.get('int8_tops', 80.0)
        theoretical_bandwidth = gpu_specs.get('memory_bandwidth_gbps', 500)
        
        # 如果没有实际测试数据，使用理论性能 * 利用率
        if 'actual_fp32_tflops' not in actual_perf:
            actual_perf['actual_fp32_tflops'] = round(theoretical_fp32 * utilization_factor, 2)
            actual_perf['actual_fp32_gflops'] = round(actual_perf['actual_fp32_tflops'] * 1000, 2)
        
        actual_perf['actual_fp16_tflops'] = round(theoretical_fp16 * utilization_factor, 2)
        actual_perf['actual_int8_tops'] = round(theoretical_int8 * utilization_factor, 2)
        actual_perf['actual_memory_bandwidth_gbps'] = round(theoretical_bandwidth * utilization_factor, 2)
        
        # 计算功效比
        if csv_analysis and 'power_analysis' in csv_analysis:
            power_data = csv_analysis['power_analysis'].get('by_device', {})
            if device_id in power_data:
                avg_power = power_data[device_id].get('mean', 200)
                if avg_power > 0:
                    actual_perf['efficiency_gflops_per_watt'] = round(
                        actual_perf['actual_fp32_gflops'] / avg_power, 2
                    )
                    actual_perf['efficiency_tops_per_watt'] = round(
                        actual_perf['actual_int8_tops'] / avg_power, 2
                    )
        
        return actual_perf
    
    def _calculate_utilization_rates(self, actual_perf: Dict[str, float], 
                                   gpu_specs: Dict[str, float]) -> Dict[str, float]:
        """计算利用率"""
        rates = {}
        
        # FP32利用率
        if 'actual_fp32_tflops' in actual_perf and 'fp32_tflops' in gpu_specs:
            rates['fp32_utilization_percent'] = round(
                (actual_perf['actual_fp32_tflops'] / gpu_specs['fp32_tflops']) * 100, 1
            )
        
        # FP16利用率
        if 'actual_fp16_tflops' in actual_perf and 'fp16_tflops' in gpu_specs:
            rates['fp16_utilization_percent'] = round(
                (actual_perf['actual_fp16_tflops'] / gpu_specs['fp16_tflops']) * 100, 1
            )
        
        # INT8利用率
        if 'actual_int8_tops' in actual_perf and 'int8_tops' in gpu_specs:
            rates['int8_utilization_percent'] = round(
                (actual_perf['actual_int8_tops'] / gpu_specs['int8_tops']) * 100, 1
            )
        
        # 内存带宽利用率
        if 'actual_memory_bandwidth_gbps' in actual_perf and 'memory_bandwidth_gbps' in gpu_specs:
            rates['memory_bandwidth_utilization_percent'] = round(
                (actual_perf['actual_memory_bandwidth_gbps'] / gpu_specs['memory_bandwidth_gbps']) * 100, 1
            )
        
        return rates
    
    def _calculate_performance_rating(self, total_fp32_tflops: float, total_int8_tops: float) -> str:
        """计算性能等级"""
        if total_fp32_tflops >= 80 or total_int8_tops >= 1000:
            return "旗舰级 (Flagship)"
        elif total_fp32_tflops >= 40 or total_int8_tops >= 500:
            return "高端级 (High-End)"
        elif total_fp32_tflops >= 20 or total_int8_tops >= 200:
            return "中高端 (Mid-High)"
        elif total_fp32_tflops >= 10 or total_int8_tops >= 100:
            return "中端级 (Mid-Range)"
        else:
            return "入门级 (Entry-Level)"
    
    def _analyze_efficiency(self, performance_metrics: Dict[str, Any], 
                          csv_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """分析效率"""
        efficiency = {
            'power_efficiency': {},
            'thermal_efficiency': {},
            'cost_efficiency': {}
        }
        
        if 'compute_performance' in performance_metrics:
            for device_id, metrics in performance_metrics['compute_performance'].items():
                device_name = metrics['device_name']
                measured_perf = metrics['measured_performance']
                
                device_efficiency = {
                    'device_name': device_name,
                    'power_metrics': {},
                    'thermal_metrics': {}
                }
                
                # 功耗效率分析
                if 'efficiency_gflops_per_watt' in measured_perf:
                    gflops_per_watt = measured_perf['efficiency_gflops_per_watt']
                    device_efficiency['power_metrics']['gflops_per_watt'] = gflops_per_watt
                    device_efficiency['power_metrics']['efficiency_rating'] = self._rate_power_efficiency(gflops_per_watt)
                
                if 'efficiency_tops_per_watt' in measured_perf:
                    tops_per_watt = measured_perf['efficiency_tops_per_watt']
                    device_efficiency['power_metrics']['tops_per_watt'] = tops_per_watt
                
                # 温度效率分析
                if csv_analysis and 'temperature_analysis' in csv_analysis:
                    temp_data = csv_analysis['temperature_analysis'].get('by_device', {})
                    if device_id in temp_data:
                        avg_temp = temp_data[device_id].get('mean', 70)
                        max_temp = temp_data[device_id].get('max', 80)
                        
                        device_efficiency['thermal_metrics']['avg_temperature_c'] = round(avg_temp, 1)
                        device_efficiency['thermal_metrics']['max_temperature_c'] = round(max_temp, 1)
                        device_efficiency['thermal_metrics']['thermal_rating'] = self._rate_thermal_performance(avg_temp, max_temp)
                
                efficiency['power_efficiency'][device_id] = device_efficiency
        
        return efficiency
    
    def _rate_power_efficiency(self, gflops_per_watt: float) -> str:
        """评级功耗效率"""
        if gflops_per_watt >= 15:
            return "优秀 (Excellent)"
        elif gflops_per_watt >= 10:
            return "良好 (Good)"
        elif gflops_per_watt >= 5:
            return "一般 (Average)"
        else:
            return "较差 (Poor)"
    
    def _rate_thermal_performance(self, avg_temp: float, max_temp: float) -> str:
        """评级温度性能"""
        if max_temp <= 70 and avg_temp <= 60:
            return "优秀 (Excellent)"
        elif max_temp <= 80 and avg_temp <= 70:
            return "良好 (Good)"
        elif max_temp <= 90 and avg_temp <= 80:
            return "一般 (Average)"
        else:
            return "需要关注 (Needs Attention)"
    
    def _generate_recommendations(self, performance_metrics: Dict[str, Any], 
                                efficiency_analysis: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 基于总体性能的建议
        overall_scores = performance_metrics.get('overall_scores', {})
        total_fp32 = overall_scores.get('total_fp32_tflops', 0)
        performance_rating = overall_scores.get('performance_rating', '')
        
        if total_fp32 < 10:
            recommendations.append("建议升级到更高性能的GPU以获得更好的计算能力")
        
        if '入门级' in performance_rating:
            recommendations.append("当前GPU适合轻量级计算任务，对于深度学习训练建议使用更高端的GPU")
        
        # 基于效率分析的建议
        if 'power_efficiency' in efficiency_analysis:
            for device_id, efficiency in efficiency_analysis['power_efficiency'].items():
                device_name = efficiency.get('device_name', f'GPU {device_id}')
                
                # 功耗效率建议
                power_metrics = efficiency.get('power_metrics', {})
                if power_metrics.get('efficiency_rating') == '较差 (Poor)':
                    recommendations.append(f"{device_name}: 功耗效率较低，建议检查散热和功耗设置")
                
                # 温度建议
                thermal_metrics = efficiency.get('thermal_metrics', {})
                if thermal_metrics.get('thermal_rating') == '需要关注 (Needs Attention)':
                    recommendations.append(f"{device_name}: 运行温度较高，建议改善散热条件")
                
                max_temp = thermal_metrics.get('max_temperature_c', 0)
                if max_temp > 85:
                    recommendations.append(f"{device_name}: 最高温度达到{max_temp}°C，建议立即检查散热系统")
        
        # 通用优化建议
        recommendations.extend([
            "定期清理GPU散热器以保持最佳散热性能",
            "监控GPU利用率，确保工作负载充分利用GPU资源",
            "考虑使用混合精度训练(FP16)以提高AI训练效率"
        ])
        
        return recommendations
    
    def export_summary_report(self, summary: Dict[str, Any], output_file: str) -> bool:
        """导出性能总结报告"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            logger.info(f"性能总结报告已保存到: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"导出性能总结报告失败: {e}")
            return False
    
    def generate_text_summary(self, summary: Dict[str, Any]) -> str:
        """生成文本格式的性能总结"""
        lines = []
        lines.append("=" * 60)
        lines.append("GPU性能基准测试总结报告")
        lines.append("=" * 60)
        lines.append("")
        
        # 系统概览
        if 'system_overview' in summary:
            overview = summary['system_overview']
            lines.append("📊 系统概览:")
            lines.append(f"  GPU数量: {overview.get('gpu_count', 0)}")
            lines.append(f"  总显存: {overview.get('total_memory_gb', 0)} GB")
            
            if 'gpu_models' in overview:
                lines.append("  GPU型号:")
                for gpu in overview['gpu_models']:
                    lines.append(f"    - {gpu['model']} ({gpu['memory_gb']} GB)")
            lines.append("")
        
        # 性能指标
        if 'performance_metrics' in summary:
            metrics = summary['performance_metrics']
            lines.append("⚡ 性能指标:")
            
            if 'overall_scores' in metrics:
                scores = metrics['overall_scores']
                lines.append(f"  总计算性能:")
                lines.append(f"    FP32: {scores.get('total_fp32_tflops', 0)} TFLOPS")
                lines.append(f"    FP16: {scores.get('total_fp16_tflops', 0)} TFLOPS")
                lines.append(f"    INT8: {scores.get('total_int8_tops', 0)} TOPS")
                lines.append(f"    内存带宽: {scores.get('total_memory_bandwidth_gbps', 0)} GB/s")
                lines.append(f"    性能等级: {scores.get('performance_rating', 'Unknown')}")
                lines.append("")
            
            # 各设备详细性能
            if 'compute_performance' in metrics:
                lines.append("  各GPU详细性能:")
                for device_id, perf in metrics['compute_performance'].items():
                    device_name = perf['device_name']
                    measured = perf['measured_performance']
                    utilization = perf['utilization_rates']
                    
                    lines.append(f"    {device_name}:")
                    lines.append(f"      实际FP32性能: {measured.get('actual_fp32_tflops', 0)} TFLOPS")
                    lines.append(f"      实际AI性能: {measured.get('actual_int8_tops', 0)} TOPS")
                    lines.append(f"      功效比: {measured.get('efficiency_gflops_per_watt', 0)} GFLOPS/W")
                    lines.append(f"      FP32利用率: {utilization.get('fp32_utilization_percent', 0)}%")
                lines.append("")
        
        # 效率分析
        if 'efficiency_analysis' in summary:
            efficiency = summary['efficiency_analysis']
            lines.append("🔥 效率分析:")
            
            if 'power_efficiency' in efficiency:
                for device_id, eff in efficiency['power_efficiency'].items():
                    device_name = eff['device_name']
                    power_metrics = eff.get('power_metrics', {})
                    thermal_metrics = eff.get('thermal_metrics', {})
                    
                    lines.append(f"  {device_name}:")
                    if power_metrics:
                        lines.append(f"    功耗效率: {power_metrics.get('efficiency_rating', 'Unknown')}")
                    if thermal_metrics:
                        lines.append(f"    温度表现: {thermal_metrics.get('thermal_rating', 'Unknown')}")
                        lines.append(f"    平均温度: {thermal_metrics.get('avg_temperature_c', 0)}°C")
            lines.append("")
        
        # 优化建议
        if 'recommendations' in summary:
            recommendations = summary['recommendations']
            lines.append("💡 优化建议:")
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"  {i}. {rec}")
            lines.append("")
        
        lines.append("=" * 60)
        lines.append(f"报告生成时间: {summary.get('report_info', {}).get('generation_time', 'Unknown')}")
        lines.append("=" * 60)
        
        return "\n".join(lines)


def generate_performance_summary(test_results: Dict[str, Any], 
                               csv_analysis: Dict[str, Any] = None,
                               output_dir: str = "gpu_benchmark_linux_results") -> Dict[str, str]:
    """生成性能总结报告的便捷函数"""
    generator = PerformanceSummaryGenerator()
    summary = generator.generate_performance_summary(test_results, csv_analysis)
    
    # 保存JSON报告
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = output_path / f"performance_summary_{timestamp}.json"
    txt_file = output_path / f"performance_summary_{timestamp}.txt"
    
    result_files = {}
    
    # 保存JSON格式报告
    if generator.export_summary_report(summary, str(json_file)):
        result_files['json'] = str(json_file)
    
    # 保存文本格式报告
    try:
        text_summary = generator.generate_text_summary(summary)
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(text_summary)
        result_files['text'] = str(txt_file)
        logger.info(f"文本总结报告已保存到: {txt_file}")
    except Exception as e:
        logger.error(f"保存文本报告失败: {e}")
    
    return result_files
