"""
增强报告器 - 提供详细的CSV数据分析和报告功能
"""

import os
import csv
import json
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import numpy as np

from .utils import logger


class CSVDataAnalyzer:
    """CSV数据分析器"""
    
    def __init__(self, csv_file_path: str):
        """初始化分析器"""
        self.csv_file_path = Path(csv_file_path)
        self.data = None
        self.load_data()
    
    def load_data(self):
        """加载CSV数据"""
        try:
            if not self.csv_file_path.exists():
                logger.error(f"CSV文件不存在: {self.csv_file_path}")
                return False
            
            # 使用pandas加载数据
            self.data = pd.read_csv(self.csv_file_path)
            logger.info(f"成功加载CSV数据，共 {len(self.data)} 条记录")
            return True
            
        except Exception as e:
            logger.error(f"加载CSV数据失败: {e}")
            return False
    
    def get_basic_statistics(self) -> Dict[str, Any]:
        """获取基础统计信息"""
        if self.data is None or self.data.empty:
            return {}
        
        stats = {
            'total_records': len(self.data),
            'time_range': {
                'start': self.data['datetime'].iloc[0] if 'datetime' in self.data.columns else None,
                'end': self.data['datetime'].iloc[-1] if 'datetime' in self.data.columns else None,
                'duration_seconds': (self.data['timestamp'].iloc[-1] - self.data['timestamp'].iloc[0]) if 'timestamp' in self.data.columns else None
            },
            'devices': list(self.data['device_id'].unique()) if 'device_id' in self.data.columns else [],
            'device_count': self.data['device_id'].nunique() if 'device_id' in self.data.columns else 0
        }
        
        return stats
    
    def get_temperature_analysis(self) -> Dict[str, Any]:
        """温度数据分析"""
        if self.data is None or 'temperature_c' not in self.data.columns:
            return {}
        
        temp_data = self.data['temperature_c'].dropna()
        if temp_data.empty:
            return {}
        
        analysis = {
            'overall': {
                'min': float(temp_data.min()),
                'max': float(temp_data.max()),
                'mean': float(temp_data.mean()),
                'std': float(temp_data.std()),
                'median': float(temp_data.median())
            },
            'by_device': {}
        }
        
        # 按设备分析
        if 'device_id' in self.data.columns:
            for device_id in self.data['device_id'].unique():
                device_temps = self.data[self.data['device_id'] == device_id]['temperature_c'].dropna()
                if not device_temps.empty:
                    analysis['by_device'][device_id] = {
                        'min': float(device_temps.min()),
                        'max': float(device_temps.max()),
                        'mean': float(device_temps.mean()),
                        'std': float(device_temps.std()),
                        'median': float(device_temps.median())
                    }
        
        return analysis
    
    def get_power_analysis(self) -> Dict[str, Any]:
        """功耗数据分析"""
        if self.data is None or 'power_usage_w' not in self.data.columns:
            return {}
        
        power_data = self.data['power_usage_w'].dropna()
        if power_data.empty:
            return {}
        
        analysis = {
            'overall': {
                'min': float(power_data.min()),
                'max': float(power_data.max()),
                'mean': float(power_data.mean()),
                'std': float(power_data.std()),
                'median': float(power_data.median())
            },
            'by_device': {}
        }
        
        # 按设备分析
        if 'device_id' in self.data.columns:
            for device_id in self.data['device_id'].unique():
                device_power = self.data[self.data['device_id'] == device_id]['power_usage_w'].dropna()
                if not device_power.empty:
                    analysis['by_device'][device_id] = {
                        'min': float(device_power.min()),
                        'max': float(device_power.max()),
                        'mean': float(device_power.mean()),
                        'std': float(device_power.std()),
                        'median': float(device_power.median())
                    }
        
        return analysis
    
    def get_utilization_analysis(self) -> Dict[str, Any]:
        """利用率数据分析"""
        analysis = {}
        
        # GPU利用率分析
        if self.data is not None and 'gpu_utilization_percent' in self.data.columns:
            gpu_util_data = self.data['gpu_utilization_percent'].dropna()
            if not gpu_util_data.empty:
                analysis['gpu_utilization'] = {
                    'overall': {
                        'min': float(gpu_util_data.min()),
                        'max': float(gpu_util_data.max()),
                        'mean': float(gpu_util_data.mean()),
                        'std': float(gpu_util_data.std()),
                        'median': float(gpu_util_data.median())
                    },
                    'by_device': {}
                }
                
                # 按设备分析
                if 'device_id' in self.data.columns:
                    for device_id in self.data['device_id'].unique():
                        device_util = self.data[self.data['device_id'] == device_id]['gpu_utilization_percent'].dropna()
                        if not device_util.empty:
                            analysis['gpu_utilization']['by_device'][device_id] = {
                                'min': float(device_util.min()),
                                'max': float(device_util.max()),
                                'mean': float(device_util.mean()),
                                'std': float(device_util.std()),
                                'median': float(device_util.median())
                            }
        
        # 内存利用率分析
        if self.data is not None and 'memory_utilization_percent' in self.data.columns:
            mem_util_data = self.data['memory_utilization_percent'].dropna()
            if not mem_util_data.empty:
                analysis['memory_utilization'] = {
                    'overall': {
                        'min': float(mem_util_data.min()),
                        'max': float(mem_util_data.max()),
                        'mean': float(mem_util_data.mean()),
                        'std': float(mem_util_data.std()),
                        'median': float(mem_util_data.median())
                    },
                    'by_device': {}
                }
                
                # 按设备分析
                if 'device_id' in self.data.columns:
                    for device_id in self.data['device_id'].unique():
                        device_mem_util = self.data[self.data['device_id'] == device_id]['memory_utilization_percent'].dropna()
                        if not device_mem_util.empty:
                            analysis['memory_utilization']['by_device'][device_id] = {
                                'min': float(device_mem_util.min()),
                                'max': float(device_mem_util.max()),
                                'mean': float(device_mem_util.mean()),
                                'std': float(device_mem_util.std()),
                                'median': float(device_mem_util.median())
                            }
        
        return analysis
    
    def calculate_performance_metrics(self) -> Dict[str, Any]:
        """计算性能指标 (FLOPS, TOPS, 内存带宽等)"""
        if self.data is None:
            return {}
        
        metrics = {}
        
        # 按设备计算性能指标
        if 'device_id' in self.data.columns:
            for device_id in self.data['device_id'].unique():
                device_data = self.data[self.data['device_id'] == device_id]
                device_name = device_data['device_name'].iloc[0] if 'device_name' in device_data.columns else f"GPU {device_id}"
                
                device_metrics = {
                    'device_name': device_name,
                    'theoretical_performance': self._get_theoretical_performance(device_name),
                    'measured_performance': {}
                }
                
                # 计算实际性能指标
                if 'gpu_utilization_percent' in device_data.columns and 'clock_graphics_mhz' in device_data.columns:
                    avg_utilization = device_data['gpu_utilization_percent'].mean()
                    avg_clock = device_data['clock_graphics_mhz'].mean()
                    
                    # 估算实际FLOPS (基于理论性能和利用率)
                    theoretical_flops = device_metrics['theoretical_performance'].get('fp32_flops_tflops', 0)
                    if theoretical_flops > 0:
                        actual_flops = theoretical_flops * (avg_utilization / 100.0)
                        device_metrics['measured_performance']['actual_fp32_tflops'] = round(actual_flops, 2)
                        device_metrics['measured_performance']['actual_fp32_gflops'] = round(actual_flops * 1000, 2)
                
                # 计算内存带宽利用率
                if 'memory_utilization_percent' in device_data.columns and 'clock_memory_mhz' in device_data.columns:
                    avg_mem_util = device_data['memory_utilization_percent'].mean()
                    avg_mem_clock = device_data['clock_memory_mhz'].mean()
                    
                    theoretical_bandwidth = device_metrics['theoretical_performance'].get('memory_bandwidth_gbps', 0)
                    if theoretical_bandwidth > 0:
                        actual_bandwidth = theoretical_bandwidth * (avg_mem_util / 100.0)
                        device_metrics['measured_performance']['actual_memory_bandwidth_gbps'] = round(actual_bandwidth, 2)
                
                # 计算功效比 (FLOPS/Watt)
                if 'power_usage_w' in device_data.columns:
                    avg_power = device_data['power_usage_w'].mean()
                    actual_flops = device_metrics['measured_performance'].get('actual_fp32_gflops', 0)
                    if avg_power > 0 and actual_flops > 0:
                        efficiency = actual_flops / avg_power
                        device_metrics['measured_performance']['efficiency_gflops_per_watt'] = round(efficiency, 2)
                
                # 计算AI性能 (TOPS估算)
                theoretical_tops = device_metrics['theoretical_performance'].get('ai_tops', 0)
                if theoretical_tops > 0 and 'gpu_utilization_percent' in device_data.columns:
                    avg_utilization = device_data['gpu_utilization_percent'].mean()
                    actual_tops = theoretical_tops * (avg_utilization / 100.0)
                    device_metrics['measured_performance']['actual_ai_tops'] = round(actual_tops, 2)
                
                metrics[f'device_{device_id}'] = device_metrics
        
        return metrics
    
    def _get_theoretical_performance(self, device_name: str) -> Dict[str, float]:
        """获取GPU理论性能参数"""
        # GPU性能数据库 (主流GPU的理论性能)
        gpu_specs = {
            # NVIDIA RTX 30系列
            'RTX 3080': {'fp32_flops_tflops': 29.8, 'memory_bandwidth_gbps': 760, 'ai_tops': 119},
            'RTX 3080 Ti': {'fp32_flops_tflops': 34.1, 'memory_bandwidth_gbps': 912, 'ai_tops': 136},
            'RTX 3090': {'fp32_flops_tflops': 35.6, 'memory_bandwidth_gbps': 936, 'ai_tops': 142},
            'RTX 3090 Ti': {'fp32_flops_tflops': 40.0, 'memory_bandwidth_gbps': 1008, 'ai_tops': 160},
            
            # NVIDIA RTX 40系列
            'RTX 4080': {'fp32_flops_tflops': 48.7, 'memory_bandwidth_gbps': 717, 'ai_tops': 195},
            'RTX 4090': {'fp32_flops_tflops': 83.0, 'memory_bandwidth_gbps': 1008, 'ai_tops': 332},
            
            # NVIDIA 专业卡
            'A100': {'fp32_flops_tflops': 19.5, 'memory_bandwidth_gbps': 1935, 'ai_tops': 312},
            'A10': {'fp32_flops_tflops': 31.2, 'memory_bandwidth_gbps': 600, 'ai_tops': 125},
            'V100': {'fp32_flops_tflops': 14.0, 'memory_bandwidth_gbps': 900, 'ai_tops': 112},
            'T4': {'fp32_flops_tflops': 8.1, 'memory_bandwidth_gbps': 320, 'ai_tops': 65},
            'L40': {'fp32_flops_tflops': 90.5, 'memory_bandwidth_gbps': 864, 'ai_tops': 362},
            'H20': {'fp32_flops_tflops': 22.2, 'memory_bandwidth_gbps': 4000, 'ai_tops': 296},
        }
        
        # 尝试匹配GPU型号
        for gpu_model, specs in gpu_specs.items():
            if gpu_model.lower() in device_name.lower():
                return specs
        
        # 默认估算值 (如果找不到匹配的GPU)
        return {
            'fp32_flops_tflops': 10.0,
            'memory_bandwidth_gbps': 500,
            'ai_tops': 40
        }
    
    def get_time_series_data(self, metrics: List[str], device_id: Optional[int] = None) -> Dict[str, List]:
        """获取时间序列数据"""
        if self.data is None:
            return {}
        
        # 筛选设备数据
        if device_id is not None:
            filtered_data = self.data[self.data['device_id'] == device_id]
        else:
            filtered_data = self.data
        
        if filtered_data.empty:
            return {}
        
        time_series = {
            'timestamps': filtered_data['timestamp'].tolist() if 'timestamp' in filtered_data.columns else [],
            'datetime': filtered_data['datetime'].tolist() if 'datetime' in filtered_data.columns else []
        }
        
        # 添加指定的指标数据
        for metric in metrics:
            if metric in filtered_data.columns:
                time_series[metric] = filtered_data[metric].tolist()
        
        return time_series
    
    def detect_anomalies(self, metric: str, threshold_std: float = 2.0) -> Dict[str, Any]:
        """检测异常值"""
        if self.data is None or metric not in self.data.columns:
            return {}
        
        metric_data = self.data[metric].dropna()
        if metric_data.empty:
            return {}
        
        mean_val = metric_data.mean()
        std_val = metric_data.std()
        
        # 检测异常值
        anomalies = []
        for idx, value in metric_data.items():
            if abs(value - mean_val) > threshold_std * std_val:
                anomalies.append({
                    'index': int(idx),
                    'value': float(value),
                    'timestamp': self.data.loc[idx, 'timestamp'] if 'timestamp' in self.data.columns else None,
                    'device_id': self.data.loc[idx, 'device_id'] if 'device_id' in self.data.columns else None,
                    'deviation': float(abs(value - mean_val) / std_val)
                })
        
        return {
            'metric': metric,
            'threshold_std': threshold_std,
            'mean': float(mean_val),
            'std': float(std_val),
            'anomaly_count': len(anomalies),
            'anomalies': anomalies
        }
    
    def export_analysis_report(self, output_file: str):
        """导出分析报告"""
        try:
            report = {
                'file_info': {
                    'csv_file': str(self.csv_file_path),
                    'analysis_time': datetime.now().isoformat()
                },
                'basic_statistics': self.get_basic_statistics(),
                'temperature_analysis': self.get_temperature_analysis(),
                'power_analysis': self.get_power_analysis(),
                'utilization_analysis': self.get_utilization_analysis()
            }
            
            # 添加异常检测
            anomaly_metrics = ['temperature_c', 'power_usage_w', 'gpu_utilization_percent']
            report['anomaly_detection'] = {}
            for metric in anomaly_metrics:
                anomalies = self.detect_anomalies(metric)
                if anomalies:
                    report['anomaly_detection'][metric] = anomalies
            
            # 保存报告
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"分析报告已保存到: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"导出分析报告失败: {e}")
            return False


class EnhancedReporter:
    """增强报告器"""
    
    def __init__(self, output_dir: str = "gpu_benchmark_linux_results"):
        """初始化报告器"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_comprehensive_report(self, csv_files: List[str], test_name: str = "gpu_test") -> Dict[str, str]:
        """生成综合报告"""
        report_files = {}
        
        try:
            # 为每个CSV文件生成分析报告
            for csv_file in csv_files:
                if not Path(csv_file).exists():
                    logger.warning(f"CSV文件不存在: {csv_file}")
                    continue
                
                # 创建分析器
                analyzer = CSVDataAnalyzer(csv_file)
                
                # 生成分析报告
                csv_name = Path(csv_file).stem
                analysis_file = self.output_dir / f"{csv_name}_analysis.json"
                
                if analyzer.export_analysis_report(str(analysis_file)):
                    report_files[csv_name] = str(analysis_file)
            
            # 生成汇总报告
            if report_files:
                summary_file = self.output_dir / f"{test_name}_summary_report.json"
                self._generate_summary_report(list(report_files.values()), str(summary_file))
                report_files['summary'] = str(summary_file)
            
            return report_files
            
        except Exception as e:
            logger.error(f"生成综合报告失败: {e}")
            return {}
    
    def _generate_summary_report(self, analysis_files: List[str], output_file: str):
        """生成汇总报告"""
        try:
            summary = {
                'report_info': {
                    'generation_time': datetime.now().isoformat(),
                    'analysis_files': analysis_files
                },
                'overall_statistics': {},
                'device_comparison': {},
                'performance_summary': {}
            }
            
            # 汇总所有分析文件的数据
            all_temp_data = []
            all_power_data = []
            all_gpu_util_data = []
            device_stats = {}
            
            for analysis_file in analysis_files:
                try:
                    with open(analysis_file, 'r', encoding='utf-8') as f:
                        analysis = json.load(f)
                    
                    # 收集温度数据
                    if 'temperature_analysis' in analysis and 'overall' in analysis['temperature_analysis']:
                        temp_stats = analysis['temperature_analysis']['overall']
                        all_temp_data.append(temp_stats)
                    
                    # 收集功耗数据
                    if 'power_analysis' in analysis and 'overall' in analysis['power_analysis']:
                        power_stats = analysis['power_analysis']['overall']
                        all_power_data.append(power_stats)
                    
                    # 收集GPU利用率数据
                    if ('utilization_analysis' in analysis and 
                        'gpu_utilization' in analysis['utilization_analysis'] and
                        'overall' in analysis['utilization_analysis']['gpu_utilization']):
                        gpu_util_stats = analysis['utilization_analysis']['gpu_utilization']['overall']
                        all_gpu_util_data.append(gpu_util_stats)
                    
                    # 收集设备统计
                    if 'basic_statistics' in analysis:
                        basic_stats = analysis['basic_statistics']
                        if 'devices' in basic_stats:
                            for device_id in basic_stats['devices']:
                                if device_id not in device_stats:
                                    device_stats[device_id] = []
                                device_stats[device_id].append(analysis_file)
                
                except Exception as e:
                    logger.warning(f"处理分析文件失败 {analysis_file}: {e}")
            
            # 计算汇总统计
            if all_temp_data:
                summary['overall_statistics']['temperature'] = {
                    'min_across_tests': min(data['min'] for data in all_temp_data),
                    'max_across_tests': max(data['max'] for data in all_temp_data),
                    'avg_mean': sum(data['mean'] for data in all_temp_data) / len(all_temp_data)
                }
            
            if all_power_data:
                summary['overall_statistics']['power'] = {
                    'min_across_tests': min(data['min'] for data in all_power_data),
                    'max_across_tests': max(data['max'] for data in all_power_data),
                    'avg_mean': sum(data['mean'] for data in all_power_data) / len(all_power_data)
                }
            
            if all_gpu_util_data:
                summary['overall_statistics']['gpu_utilization'] = {
                    'min_across_tests': min(data['min'] for data in all_gpu_util_data),
                    'max_across_tests': max(data['max'] for data in all_gpu_util_data),
                    'avg_mean': sum(data['mean'] for data in all_gpu_util_data) / len(all_gpu_util_data)
                }
            
            # 设备比较
            summary['device_comparison'] = device_stats
            
            # 保存汇总报告
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            logger.info(f"汇总报告已保存到: {output_file}")
            
        except Exception as e:
            logger.error(f"生成汇总报告失败: {e}")
    
    def create_csv_dashboard_data(self, csv_file: str) -> Dict[str, Any]:
        """为CSV数据创建仪表板数据"""
        try:
            analyzer = CSVDataAnalyzer(csv_file)
            
            if analyzer.data is None:
                return {}
            
            # 获取所有设备的时间序列数据
            dashboard_data = {
                'devices': [],
                'metrics': {
                    'temperature': [],
                    'power': [],
                    'gpu_utilization': [],
                    'memory_utilization': []
                },
                'timestamps': [],
                'statistics': {}
            }
            
            # 获取设备列表
            if 'device_id' in analyzer.data.columns:
                dashboard_data['devices'] = sorted(analyzer.data['device_id'].unique().tolist())
            
            # 获取时间序列数据
            for device_id in dashboard_data['devices']:
                device_data = analyzer.get_time_series_data(
                    ['temperature_c', 'power_usage_w', 'gpu_utilization_percent', 'memory_utilization_percent'],
                    device_id
                )
                
                if device_data:
                    dashboard_data['metrics']['temperature'].append({
                        'device_id': device_id,
                        'data': device_data.get('temperature_c', [])
                    })
                    dashboard_data['metrics']['power'].append({
                        'device_id': device_id,
                        'data': device_data.get('power_usage_w', [])
                    })
                    dashboard_data['metrics']['gpu_utilization'].append({
                        'device_id': device_id,
                        'data': device_data.get('gpu_utilization_percent', [])
                    })
                    dashboard_data['metrics']['memory_utilization'].append({
                        'device_id': device_id,
                        'data': device_data.get('memory_utilization_percent', [])
                    })
                    
                    # 使用第一个设备的时间戳
                    if not dashboard_data['timestamps'] and 'datetime' in device_data:
                        dashboard_data['timestamps'] = device_data['datetime']
            
            # 获取统计信息
            dashboard_data['statistics'] = {
                'basic': analyzer.get_basic_statistics(),
                'temperature': analyzer.get_temperature_analysis(),
                'power': analyzer.get_power_analysis(),
                'utilization': analyzer.get_utilization_analysis()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"创建仪表板数据失败: {e}")
            return {}


def analyze_csv_files(csv_files: List[str], output_dir: str = None) -> Dict[str, str]:
    """分析CSV文件的便捷函数"""
    if output_dir is None:
        output_dir = "gpu_benchmark_linux_results"
    
    reporter = EnhancedReporter(output_dir)
    return reporter.generate_comprehensive_report(csv_files, "batch_analysis")


def create_dashboard_data(csv_file: str) -> Dict[str, Any]:
    """创建仪表板数据的便捷函数"""
    reporter = EnhancedReporter()
    return reporter.create_csv_dashboard_data(csv_file)