"""
报告生成模块 - 提供测试结果输出和报告生成功能
"""

import os
import sys
import json
import csv
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import base64

from .utils import logger, RESULT_DIR, format_bytes, format_temperature, format_power, format_percentage
from .stress_test import StressTestResult
from .monitor import GPUMetrics


class BenchmarkReporter:
    """基准测试报告生成器"""
    
    def __init__(self, output_dir: Path = None):
        """初始化报告生成器"""
        self.output_dir = output_dir or RESULT_DIR
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_json_report(self, result: StressTestResult, filename: Optional[str] = None) -> Optional[str]:
        """生成JSON格式报告"""
        if filename is None:
            timestamp = int(result.start_time)
            filename = f"stress_test_report_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"JSON报告已生成: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"生成JSON报告失败: {e}")
            return None
    
    def generate_csv_report(self, result: StressTestResult, filename: Optional[str] = None) -> Optional[str]:
        """生成CSV格式报告"""
        if filename is None:
            timestamp = int(result.start_time)
            filename = f"stress_test_report_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # 写入基本信息
                writer.writerow(['测试信息', ''])
                writer.writerow(['开始时间', datetime.fromtimestamp(result.start_time).strftime('%Y-%m-%d %H:%M:%S')])
                writer.writerow(['结束时间', datetime.fromtimestamp(result.end_time).strftime('%Y-%m-%d %H:%M:%S')])
                writer.writerow(['持续时间', f"{result.duration:.1f}秒"])
                writer.writerow(['测试状态', '成功' if result.success else '失败'])
                writer.writerow(['设备数量', len(result.device_results)])
                writer.writerow([])
                
                # 写入性能指标
                if result.performance_metrics:
                    writer.writerow(['性能指标', ''])
                    for key, value in result.performance_metrics.items():
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                writer.writerow([f"{key}_{sub_key}", sub_value])
                        else:
                            writer.writerow([key, value])
                    writer.writerow([])
                
                # 写入设备结果
                writer.writerow(['设备测试结果', ''])
                writer.writerow(['设备ID', '测试类型', '指标', '数值'])
                
                for device_id, device_result in result.device_results.items():
                    for test_type, test_result in device_result.items():
                        if isinstance(test_result, dict):
                            for metric, value in test_result.items():
                                writer.writerow([device_id, test_type, metric, value])
                        else:
                            writer.writerow([device_id, test_type, '', test_result])
            
            logger.info(f"CSV报告已生成: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"生成CSV报告失败: {e}")
            return None
    
    def generate_html_report(self, result: StressTestResult, filename: Optional[str] = None) -> Optional[str]:
        """生成HTML格式报告"""
        if filename is None:
            timestamp = int(result.start_time)
            filename = f"stress_test_report_{timestamp}.html"
        
        filepath = self.output_dir / filename
        
        try:
            html_content = self._create_html_content(result)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML报告已生成: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"生成HTML报告失败: {e}")
            return None
    
    def _create_html_content(self, result: StressTestResult) -> str:
        """创建HTML报告内容"""
        # 基本信息
        start_time_str = datetime.fromtimestamp(result.start_time).strftime('%Y-%m-%d %H:%M:%S')
        end_time_str = datetime.fromtimestamp(result.end_time).strftime('%Y-%m-%d %H:%M:%S')
        status_class = "status-success" if result.success else "status-error"
        status_text = "成功" if result.success else "失败"
        
        # 生成设备信息HTML
        device_info_html = self._generate_device_info_html(result)
        
        # 生成性能结果HTML
        performance_html = self._generate_performance_html(result)
        
        # 生成监控数据HTML
        monitoring_html = self._generate_monitoring_html(result)
        
        # 生成图表数据
        chart_data = self._generate_chart_data(result)
        
        html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GPU压力测试报告</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 2.5em; font-weight: 300; }}
        .header .subtitle {{ margin-top: 10px; opacity: 0.9; font-size: 1.1em; }}
        .content {{ padding: 30px; }}
        .summary {{ background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); padding: 25px; border-radius: 8px; margin-bottom: 30px; }}
        .summary h2 {{ margin-top: 0; color: #333; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }}
        .metric-card {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .metric-label {{ font-size: 0.9em; color: #666; margin-bottom: 5px; }}
        .metric-value {{ font-size: 1.5em; font-weight: bold; color: #2196F3; }}
        .status-success {{ color: #4CAF50; }}
        .status-error {{ color: #F44336; }}
        .section {{ margin-bottom: 40px; }}
        .section h2 {{ color: #333; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; }}
        .device-card {{ background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 20px; margin: 15px 0; }}
        .device-card h3 {{ margin-top: 0; color: #495057; }}
        .performance-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .performance-table th, .performance-table td {{ border: 1px solid #dee2e6; padding: 12px; text-align: left; }}
        .performance-table th {{ background-color: #f8f9fa; font-weight: 600; }}
        .performance-table tr:nth-child(even) {{ background-color: #f8f9fa; }}
        .chart-container {{ background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 20px 0; min-height: 300px; }}
        .monitoring-stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
        .stat-card {{ background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .stat-title {{ font-weight: bold; color: #333; margin-bottom: 10px; }}
        .stat-value {{ font-size: 1.2em; color: #2196F3; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 0.9em; }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>GPU压力测试报告</h1>
            <div class="subtitle">内置GPU压力测试工具 - 详细测试报告</div>
        </div>
        
        <div class="content">
            <div class="summary">
                <h2>测试摘要</h2>
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="metric-label">开始时间</div>
                        <div class="metric-value">{start_time_str}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">结束时间</div>
                        <div class="metric-value">{end_time_str}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">持续时间</div>
                        <div class="metric-value">{result.duration:.1f}秒</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">测试状态</div>
                        <div class="metric-value {status_class}">{status_text}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">GPU设备数</div>
                        <div class="metric-value">{len(result.device_results)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">监控数据点</div>
                        <div class="metric-value">{len(result.monitoring_data)}</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>设备测试结果</h2>
                {device_info_html}
            </div>
            
            <div class="section">
                <h2>性能指标</h2>
                {performance_html}
            </div>
            
            <div class="section">
                <h2>监控数据统计</h2>
                {monitoring_html}
            </div>
            
            <div class="section">
                <h2>性能趋势图表</h2>
                <div class="chart-container">
                    <canvas id="performanceChart" width="400" height="200"></canvas>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | GPU基准测试工具 v0.1.6</p>
        </div>
    </div>
    
    <script>
        // 图表数据
        const chartData = {chart_data};
        
        // 创建性能趋势图
        const ctx = document.getElementById('performanceChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: chartData.labels,
                datasets: chartData.datasets
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'GPU性能监控趋势'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
        """
        
        return html_template
    
    def _generate_device_info_html(self, result: StressTestResult) -> str:
        """生成设备信息HTML"""
        html = ""
        
        for device_id, device_result in result.device_results.items():
            html += f"""
            <div class="device-card">
                <h3>GPU {device_id}</h3>
                <table class="performance-table">
                    <thead>
                        <tr>
                            <th>测试类型</th>
                            <th>关键指标</th>
                            <th>数值</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for test_type, test_result in device_result.items():
                if isinstance(test_result, dict):
                    for metric, value in test_result.items():
                        if metric in ['gflops', 'iterations_per_second', 'h2d_bandwidth_gbps', 'd2h_bandwidth_gbps']:
                            html += f"""
                            <tr>
                                <td>{test_type}</td>
                                <td>{metric}</td>
                                <td>{value}</td>
                            </tr>
                            """
            
            html += """
                    </tbody>
                </table>
            </div>
            """
        
        return html
    
    def _generate_performance_html(self, result: StressTestResult) -> str:
        """生成性能指标HTML"""
        if not result.performance_metrics:
            return "<p>暂无性能指标数据</p>"
        
        html = '<div class="monitoring-stats">'
        
        for key, value in result.performance_metrics.items():
            if isinstance(value, dict):
                html += f"""
                <div class="stat-card">
                    <div class="stat-title">{key}</div>
                """
                for sub_key, sub_value in value.items():
                    html += f'<div class="stat-value">{sub_key}: {sub_value}</div>'
                html += "</div>"
            else:
                html += f"""
                <div class="stat-card">
                    <div class="stat-title">{key}</div>
                    <div class="stat-value">{value}</div>
                </div>
                """
        
        html += "</div>"
        return html
    
    def _generate_monitoring_html(self, result: StressTestResult) -> str:
        """生成监控数据HTML"""
        if not result.monitoring_data:
            return "<p>暂无监控数据</p>"
        
        # 计算统计信息
        temps = [m.temperature for m in result.monitoring_data if m.temperature is not None]
        powers = [m.power_usage for m in result.monitoring_data if m.power_usage is not None]
        gpu_utils = [m.gpu_utilization for m in result.monitoring_data if m.gpu_utilization is not None]
        mem_utils = [m.memory_utilization for m in result.monitoring_data if m.memory_utilization is not None]
        
        html = '<div class="monitoring-stats">'
        
        if temps:
            html += f"""
            <div class="stat-card">
                <div class="stat-title">温度统计</div>
                <div class="stat-value">最低: {min(temps):.1f}°C</div>
                <div class="stat-value">最高: {max(temps):.1f}°C</div>
                <div class="stat-value">平均: {sum(temps)/len(temps):.1f}°C</div>
            </div>
            """
        
        if powers:
            html += f"""
            <div class="stat-card">
                <div class="stat-title">功耗统计</div>
                <div class="stat-value">最低: {min(powers):.1f}W</div>
                <div class="stat-value">最高: {max(powers):.1f}W</div>
                <div class="stat-value">平均: {sum(powers)/len(powers):.1f}W</div>
            </div>
            """
        
        if gpu_utils:
            html += f"""
            <div class="stat-card">
                <div class="stat-title">GPU利用率统计</div>
                <div class="stat-value">最低: {min(gpu_utils):.1f}%</div>
                <div class="stat-value">最高: {max(gpu_utils):.1f}%</div>
                <div class="stat-value">平均: {sum(gpu_utils)/len(gpu_utils):.1f}%</div>
            </div>
            """
        
        if mem_utils:
            html += f"""
            <div class="stat-card">
                <div class="stat-title">内存利用率统计</div>
                <div class="stat-value">最低: {min(mem_utils):.1f}%</div>
                <div class="stat-value">最高: {max(mem_utils):.1f}%</div>
                <div class="stat-value">平均: {sum(mem_utils)/len(mem_utils):.1f}%</div>
            </div>
            """
        
        html += "</div>"
        return html
    
    def _generate_chart_data(self, result: StressTestResult) -> str:
        """生成图表数据"""
        if not result.monitoring_data:
            return "null"
        
        # 按时间排序
        sorted_data = sorted(result.monitoring_data, key=lambda x: x.timestamp)
        
        # 生成时间标签
        start_time = sorted_data[0].timestamp
        labels = [f"{(m.timestamp - start_time):.0f}s" for m in sorted_data]
        
        # 生成数据集
        datasets = []
        
        # 温度数据
        temp_data = [m.temperature for m in sorted_data]
        if any(t is not None for t in temp_data):
            datasets.append({
                'label': '温度 (°C)',
                'data': temp_data,
                'borderColor': 'rgb(255, 99, 132)',
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'yAxisID': 'y'
            })
        
        # 功耗数据
        power_data = [m.power_usage for m in sorted_data]
        if any(p is not None for p in power_data):
            datasets.append({
                'label': '功耗 (W)',
                'data': power_data,
                'borderColor': 'rgb(54, 162, 235)',
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'yAxisID': 'y1'
            })
        
        # GPU利用率数据
        gpu_util_data = [m.gpu_utilization for m in sorted_data]
        if any(u is not None for u in gpu_util_data):
            datasets.append({
                'label': 'GPU利用率 (%)',
                'data': gpu_util_data,
                'borderColor': 'rgb(75, 192, 192)',
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'yAxisID': 'y2'
            })
        
        chart_data = {
            'labels': labels,
            'datasets': datasets
        }
        
        return json.dumps(chart_data)
    
    def generate_summary_report(self, result: StressTestResult) -> str:
        """生成摘要报告"""
        summary = []
        summary.append("=" * 60)
        summary.append("GPU压力测试报告摘要")
        summary.append("=" * 60)
        
        # 基本信息
        start_time = datetime.fromtimestamp(result.start_time).strftime('%Y-%m-%d %H:%M:%S')
        end_time = datetime.fromtimestamp(result.end_time).strftime('%Y-%m-%d %H:%M:%S')
        
        summary.append(f"测试时间: {start_time} - {end_time}")
        summary.append(f"持续时间: {result.duration:.1f}秒")
        summary.append(f"测试状态: {'成功' if result.success else '失败'}")
        summary.append(f"设备数量: {len(result.device_results)}")
        summary.append("")
        
        # 性能指标
        if result.performance_metrics:
            summary.append("性能指标:")
            summary.append("-" * 40)
            
            metrics = result.performance_metrics
            if 'total_gflops' in metrics:
                summary.append(f"总计算性能: {metrics['total_gflops']:.2f} GFLOPS")
            
            if 'temperature_stats' in metrics:
                temp_stats = metrics['temperature_stats']
                summary.append(f"温度范围: {temp_stats['min']:.1f}°C - {temp_stats['max']:.1f}°C")
            
            if 'power_stats' in metrics:
                power_stats = metrics['power_stats']
                summary.append(f"功耗范围: {power_stats['min']:.1f}W - {power_stats['max']:.1f}W")
            
            summary.append("")
        
        # 设备结果
        summary.append("设备测试结果:")
        summary.append("-" * 40)
        
        for device_id, device_result in result.device_results.items():
            summary.append(f"GPU {device_id}:")
            
            if 'matrix_multiply' in device_result:
                mm_result = device_result['matrix_multiply']
                if 'gflops' in mm_result:
                    summary.append(f"  矩阵乘法: {mm_result['gflops']:.2f} GFLOPS")
            
            if 'compute_intensive' in device_result:
                ci_result = device_result['compute_intensive']
                if 'iterations_per_second' in ci_result:
                    summary.append(f"  计算密集型: {ci_result['iterations_per_second']:.2f} iter/s")
            
            if 'memory_bandwidth' in device_result:
                mb_result = device_result['memory_bandwidth']
                if 'h2d_bandwidth_gbps' in mb_result:
                    summary.append(f"  内存带宽(H2D): {mb_result['h2d_bandwidth_gbps']:.2f} GB/s")
        
        summary.append("")
        summary.append("=" * 60)
        
        return "\n".join(summary)
    
    def export_all_formats(self, result: StressTestResult, base_filename: Optional[str] = None) -> Dict[str, str]:
        """导出所有格式的报告"""
        if base_filename is None:
            timestamp = int(result.start_time)
            base_filename = f"stress_test_report_{timestamp}"
        
        exported_files = {}
        
        # JSON报告
        json_file = self.generate_json_report(result, f"{base_filename}.json")
        if json_file:
            exported_files['json'] = json_file
        
        # CSV报告
        csv_file = self.generate_csv_report(result, f"{base_filename}.csv")
        if csv_file:
            exported_files['csv'] = csv_file
        
        # HTML报告
        html_file = self.generate_html_report(result, f"{base_filename}.html")
        if html_file:
            exported_files['html'] = html_file
        
        # 摘要报告
        try:
            summary_content = self.generate_summary_report(result)
            summary_file = self.output_dir / f"{base_filename}_summary.txt"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            exported_files['summary'] = str(summary_file)
            logger.info(f"摘要报告已生成: {summary_file}")
        except Exception as e:
            logger.error(f"生成摘要报告失败: {e}")
        
        return exported_files


# 全局报告生成器实例
benchmark_reporter = BenchmarkReporter()


# 便捷函数
def export_stress_test_result(result: StressTestResult, formats: Optional[List[str]] = None) -> Dict[str, str]:
    """导出压力测试结果"""
    if formats is None:
        formats = ['json', 'html', 'summary']
    
    timestamp = int(result.start_time)
    base_filename = f"stress_test_report_{timestamp}"
    
    exported_files = {}
    
    if 'json' in formats:
        json_file = benchmark_reporter.generate_json_report(result, f"{base_filename}.json")
        if json_file:
            exported_files['json'] = json_file
    
    if 'csv' in formats:
        csv_file = benchmark_reporter.generate_csv_report(result, f"{base_filename}.csv")
        if csv_file:
            exported_files['csv'] = csv_file
    
    if 'html' in formats:
        html_file = benchmark_reporter.generate_html_report(result, f"{base_filename}.html")
        if html_file:
            exported_files['html'] = html_file
    
    if 'summary' in formats:
        try:
            summary_content = benchmark_reporter.generate_summary_report(result)
            summary_file = benchmark_reporter.output_dir / f"{base_filename}_summary.txt"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            exported_files['summary'] = str(summary_file)
            logger.info(f"摘要报告已生成: {summary_file}")
        except Exception as e:
            logger.error(f"生成摘要报告失败: {e}")
    
    return exported_files
