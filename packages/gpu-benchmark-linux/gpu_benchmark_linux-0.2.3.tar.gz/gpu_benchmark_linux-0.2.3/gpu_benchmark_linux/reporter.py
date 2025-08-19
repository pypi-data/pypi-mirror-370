"""
报告生成模块 - 提供测试结果的格式化输出和报告生成功能
"""

import os
import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from .utils import logger


class BenchmarkReporter:
    """基准测试报告生成器"""
    
    def __init__(self, output_dir: str = "./gpu_benchmark_linux_results"):
        """初始化报告生成器"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def generate_json_report(self, data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """生成JSON格式报告"""
        if filename is None:
            filename = f"benchmark_report_{self.timestamp}.json"
        
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"JSON报告已生成: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"生成JSON报告失败: {e}")
            raise
    
    def generate_html_report(self, data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """生成HTML可视化报告 - 使用独立的HTML报告生成器"""
        from .html_reporter import HTMLReporter
        
        html_reporter = HTMLReporter(str(self.output_dir))
        return html_reporter.generate_html_report(data, filename)
    
    def _create_html_content(self, data: Dict[str, Any]) -> str:
        """创建HTML报告内容"""
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GPU基准测试报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        .content {
            padding: 30px;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            border-left: 4px solid #667eea;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        .metric-label {
            color: #666;
            font-size: 0.9em;
        }
        .chart-container {
            position: relative;
            height: 400px;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .device-section {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .device-title {
            color: #495057;
            margin-bottom: 15px;
            font-size: 1.2em;
            font-weight: bold;
        }
        .status-success {
            color: #28a745;
            font-weight: bold;
        }
        .status-error {
            color: #dc3545;
            font-weight: bold;
        }
        .info-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .info-table th,
        .info-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        .info-table th {
            background-color: #e9ecef;
            font-weight: bold;
        }
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #dee2e6;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 GPU基准测试报告</h1>
            <p>生成时间: {timestamp}</p>
        </div>
        
        <div class="content">
            {system_info_section}
            {performance_metrics_section}
            {charts_section}
            {device_results_section}
            {monitoring_section}
        </div>
        
        <div class="footer">
            <p>GPU Benchmark Linux - 专业GPU性能测试工具</p>
        </div>
    </div>

    <script>
        {chart_scripts}
    </script>
</body>
</html>
        """
        
        # 生成各个部分的内容
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        system_info_section = self._create_system_info_section(data)
        performance_metrics_section = self._create_performance_metrics_section(data)
        charts_section = self._create_charts_section(data)
        device_results_section = self._create_device_results_section(data)
        monitoring_section = self._create_monitoring_section(data)
        chart_scripts = self._create_chart_scripts(data)
        
        return html_template.format(
            timestamp=timestamp,
            system_info_section=system_info_section,
            performance_metrics_section=performance_metrics_section,
            charts_section=charts_section,
            device_results_section=device_results_section,
            monitoring_section=monitoring_section,
            chart_scripts=chart_scripts
        )
    
    def _create_system_info_section(self, data: Dict[str, Any]) -> str:
        """创建系统信息部分"""
        if 'system_info' not in data:
            return ""
        
        system_info = data['system_info']
        rows = []
        for key, value in system_info.items():
            rows.append(f"<tr><th>{key}</th><td>{value}</td></tr>")
        
        return f"""
        <div class="section">
            <h2>📊 系统信息</h2>
            <table class="info-table">
                {''.join(rows)}
            </table>
        </div>
        """
    
    def _create_performance_metrics_section(self, data: Dict[str, Any]) -> str:
        """创建性能指标部分"""
        if 'performance_metrics' not in data:
            return ""
        
        metrics = data['performance_metrics']
        cards = []
        
        # 主要性能指标卡片
        if 'total_gflops' in metrics:
            cards.append(f"""
            <div class="metric-card">
                <div class="metric-value">{metrics['total_gflops']:.2f}</div>
                <div class="metric-label">总计算性能 (GFLOPS)</div>
            </div>
            """)
        
        if 'temperature_stats' in metrics:
            temp_stats = metrics['temperature_stats']
            cards.append(f"""
            <div class="metric-card">
                <div class="metric-value">{temp_stats['max']:.1f}°C</div>
                <div class="metric-label">最高温度</div>
            </div>
            """)
        
        if 'power_stats' in metrics:
            power_stats = metrics['power_stats']
            cards.append(f"""
            <div class="metric-card">
                <div class="metric-value">{power_stats['avg']:.1f}W</div>
                <div class="metric-label">平均功耗</div>
            </div>
            """)
        
        if 'gpu_utilization_stats' in metrics:
            util_stats = metrics['gpu_utilization_stats']
            cards.append(f"""
            <div class="metric-card">
                <div class="metric-value">{util_stats['avg']:.1f}%</div>
                <div class="metric-label">平均GPU利用率</div>
            </div>
            """)
        
        return f"""
        <div class="section">
            <h2>⚡ 性能指标</h2>
            <div class="metrics-grid">
                {''.join(cards)}
            </div>
        </div>
        """
    
    def _create_charts_section(self, data: Dict[str, Any]) -> str:
        """创建图表部分"""
        charts_html = []
        
        # 性能对比图表
        if 'device_results' in data:
            charts_html.append("""
            <div class="chart-container">
                <canvas id="performanceChart"></canvas>
            </div>
            """)
        
        # 监控数据时间序列图表
        if 'monitoring_data' in data and data['monitoring_data']:
            charts_html.append("""
            <div class="chart-container">
                <canvas id="monitoringChart"></canvas>
            </div>
            """)
        
        if charts_html:
            return f"""
            <div class="section">
                <h2>📈 性能图表</h2>
                {''.join(charts_html)}
            </div>
            """
        
        return ""
    
    def _create_device_results_section(self, data: Dict[str, Any]) -> str:
        """创建设备结果部分"""
        if 'device_results' not in data:
            return ""
        
        device_sections = []
        for device_id, results in data['device_results'].items():
            status_class = "status-success" if results.get('success', False) else "status-error"
            status_text = "✅ 成功" if results.get('success', False) else "❌ 失败"
            
            test_results = []
            for test_name, test_result in results.items():
                if test_name in ['success', 'duration', 'error']:
                    continue
                
                if isinstance(test_result, dict):
                    if 'gflops' in test_result:
                        test_results.append(f"<tr><td>矩阵乘法性能</td><td>{test_result['gflops']:.2f} GFLOPS</td></tr>")
                    if 'iterations_per_second' in test_result:
                        test_results.append(f"<tr><td>计算密集型性能</td><td>{test_result['iterations_per_second']:.2f} iter/s</td></tr>")
                    if 'h2d_bandwidth_gbps' in test_result:
                        test_results.append(f"<tr><td>Host->Device带宽</td><td>{test_result['h2d_bandwidth_gbps']:.2f} GB/s</td></tr>")
                    if 'd2h_bandwidth_gbps' in test_result:
                        test_results.append(f"<tr><td>Device->Host带宽</td><td>{test_result['d2h_bandwidth_gbps']:.2f} GB/s</td></tr>")
            
            device_sections.append(f"""
            <div class="device-section">
                <div class="device-title">GPU {device_id} - <span class="{status_class}">{status_text}</span></div>
                <table class="info-table">
                    {''.join(test_results)}
                    <tr><td>测试持续时间</td><td>{results.get('duration', 0):.1f} 秒</td></tr>
                </table>
                {f'<p class="status-error">错误: {results["error"]}</p>' if 'error' in results else ''}
            </div>
            """)
        
        return f"""
        <div class="section">
            <h2>🎯 设备测试结果</h2>
            {''.join(device_sections)}
        </div>
        """
    
    def _create_monitoring_section(self, data: Dict[str, Any]) -> str:
        """创建监控数据部分"""
        if 'monitoring_data' not in data or not data['monitoring_data']:
            return ""
        
        return """
        <div class="section">
            <h2>📊 实时监控数据</h2>
            <p>监控数据已集成到上方的时间序列图表中，包含温度、功耗、GPU利用率等关键指标的变化趋势。</p>
        </div>
        """
    
    def _create_chart_scripts(self, data: Dict[str, Any]) -> str:
        """创建图表JavaScript代码"""
        scripts = []
        
        # 性能对比图表
        if 'device_results' in data:
            device_labels = []
            gflops_data = []
            
            for device_id, results in data['device_results'].items():
                device_labels.append(f'GPU {device_id}')
                gflops = 0
                if 'matrix_multiply' in results and 'gflops' in results['matrix_multiply']:
                    gflops = results['matrix_multiply']['gflops']
                gflops_data.append(gflops)
            
            scripts.append(f"""
            // 性能对比图表
            const performanceCtx = document.getElementById('performanceChart');
            if (performanceCtx) {{
                new Chart(performanceCtx, {{
                    type: 'bar',
                    data: {{
                        labels: {json.dumps(device_labels)},
                        datasets: [{{
                            label: 'GFLOPS',
                            data: {json.dumps(gflops_data)},
                            backgroundColor: 'rgba(102, 126, 234, 0.8)',
                            borderColor: 'rgba(102, 126, 234, 1)',
                            borderWidth: 1
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            title: {{
                                display: true,
                                text: 'GPU计算性能对比'
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                title: {{
                                    display: true,
                                    text: 'GFLOPS'
                                }}
                            }}
                        }}
                    }}
                }});
            }}
            """)
        
        # 监控数据时间序列图表
        if 'monitoring_data' in data and data['monitoring_data']:
            monitoring_data = data['monitoring_data']
            timestamps = []
            temperatures = []
            power_usage = []
            gpu_utilization = []
            
            for entry in monitoring_data:
                if isinstance(entry, dict):
                    timestamps.append(entry.get('timestamp', 0))
                    temperatures.append(entry.get('temperature'))
                    power_usage.append(entry.get('power_usage'))
                    gpu_utilization.append(entry.get('gpu_utilization'))
            
            # 转换时间戳为相对时间（秒）
            if timestamps:
                start_time = min(timestamps)
                relative_times = [(t - start_time) for t in timestamps]
            else:
                relative_times = []
            
            scripts.append(f"""
            // 监控数据时间序列图表
            const monitoringCtx = document.getElementById('monitoringChart');
            if (monitoringCtx) {{
                new Chart(monitoringCtx, {{
                    type: 'line',
                    data: {{
                        labels: {json.dumps(relative_times)},
                        datasets: [
                            {{
                                label: '温度 (°C)',
                                data: {json.dumps(temperatures)},
                                borderColor: 'rgb(255, 99, 132)',
                                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                                yAxisID: 'y'
                            }},
                            {{
                                label: '功耗 (W)',
                                data: {json.dumps(power_usage)},
                                borderColor: 'rgb(54, 162, 235)',
                                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                                yAxisID: 'y1'
                            }},
                            {{
                                label: 'GPU利用率 (%)',
                                data: {json.dumps(gpu_utilization)},
                                borderColor: 'rgb(75, 192, 192)',
                                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                                yAxisID: 'y2'
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            title: {{
                                display: true,
                                text: 'GPU监控数据时间序列'
                            }}
                        }},
                        scales: {{
                            x: {{
                                title: {{
                                    display: true,
                                    text: '时间 (秒)'
                                }}
                            }},
                            y: {{
                                type: 'linear',
                                display: true,
                                position: 'left',
                                title: {{
                                    display: true,
                                    text: '温度 (°C)'
                                }}
                            }},
                            y1: {{
                                type: 'linear',
                                display: true,
                                position: 'right',
                                title: {{
                                    display: true,
                                    text: '功耗 (W)'
                                }},
                                grid: {{
                                    drawOnChartArea: false,
                                }}
                            }},
                            y2: {{
                                type: 'linear',
                                display: false,
                                position: 'right'
                            }}
                        }}
                    }}
                }});
            }}
            """)
        
        return '\n'.join(scripts)
    
    def generate_csv_report(self, data: Dict[str, Any], filename: str = None) -> str:
        """生成CSV格式报告"""
        if filename is None:
            filename = f"benchmark_report_{self.timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # 写入标题行
                writer.writerow(['Metric', 'Value', 'Unit', 'Description'])
                
                # 写入基本信息
                if 'system_info' in data:
                    system_info = data['system_info']
                    for key, value in system_info.items():
                        writer.writerow([f'System_{key}', value, '', 'System Information'])
                
                # 写入性能指标
                if 'performance_metrics' in data:
                    metrics = data['performance_metrics']
                    for key, value in metrics.items():
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                writer.writerow([f'{key}_{sub_key}', sub_value, self._get_unit(key), f'{key} metrics'])
                        else:
                            writer.writerow([key, value, self._get_unit(key), 'Performance metric'])
            
            logger.info(f"CSV报告已生成: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"生成CSV报告失败: {e}")
            raise
    
    def _get_unit(self, metric_name: str) -> str:
        """获取指标单位"""
        unit_map = {
            'gflops': 'GFLOPS',
            'temperature': '°C',
            'power': 'W',
            'memory': 'MB',
            'bandwidth': 'GB/s',
            'utilization': '%',
            'time': 's'
        }
        
        for key, unit in unit_map.items():
            if key in metric_name.lower():
                return unit
        
        return ''
    
    def generate_summary_report(self, data: Dict[str, Any]) -> str:
        """生成摘要报告"""
        summary = []
        summary.append("=" * 60)
        summary.append("GPU基准测试报告摘要")
        summary.append("=" * 60)
        summary.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")
        
        # 系统信息
        if 'system_info' in data:
            summary.append("系统信息:")
            system_info = data['system_info']
            for key, value in system_info.items():
                summary.append(f"  {key}: {value}")
            summary.append("")
        
        # 性能指标
        if 'performance_metrics' in data:
            summary.append("性能指标:")
            metrics = data['performance_metrics']
            for key, value in metrics.items():
                if isinstance(value, dict):
                    summary.append(f"  {key}:")
                    for sub_key, sub_value in value.items():
                        unit = self._get_unit(key)
                        summary.append(f"    {sub_key}: {sub_value} {unit}")
                else:
                    unit = self._get_unit(key)
                    summary.append(f"  {key}: {value} {unit}")
            summary.append("")
        
        # 测试结果
        if 'test_results' in data:
            summary.append("测试结果:")
            results = data['test_results']
            for test_name, result in results.items():
                status = "✅ 通过" if result.get('success', False) else "❌ 失败"
                summary.append(f"  {test_name}: {status}")
                if 'error' in result:
                    summary.append(f"    错误: {result['error']}")
            summary.append("")
        
        summary.append("=" * 60)
        
        return "\n".join(summary)
    
    def save_summary_report(self, data: Dict[str, Any], filename: str = None) -> str:
        """保存摘要报告到文件"""
        if filename is None:
            filename = f"benchmark_summary_{self.timestamp}.txt"
        
        filepath = self.output_dir / filename
        summary = self.generate_summary_report(data)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            logger.info(f"摘要报告已生成: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"生成摘要报告失败: {e}")
            raise
    
    def print_summary(self, data: Dict[str, Any]):
        """打印摘要到控制台"""
        summary = self.generate_summary_report(data)
        print(summary)


# 全局报告生成器实例
reporter = BenchmarkReporter()