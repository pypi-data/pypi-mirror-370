"""
增强HTML报告器 - 包含详细的性能指标和FLOPS/TOPS总结
"""

import json
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

from .utils import logger
from .performance_summary import PerformanceSummaryGenerator


class EnhancedHTMLReporter:
    """增强HTML报告器"""
    
    def __init__(self):
        """初始化增强HTML报告器"""
        self.performance_generator = PerformanceSummaryGenerator()
    
    def generate_enhanced_report(self, results: Dict[str, Any], 
                               csv_analysis: Dict[str, Any] = None,
                               output_dir: str = "gpu_benchmark_linux_results") -> str:
        """生成增强的HTML报告"""
        try:
            # 生成性能总结
            performance_summary = self.performance_generator.generate_performance_summary(
                results, csv_analysis
            )
            
            # 生成HTML内容
            html_content = self._generate_html_content(results, performance_summary, csv_analysis)
            
            # 保存HTML文件
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_file = output_path / f"enhanced_benchmark_report_{timestamp}.html"
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"增强HTML报告已生成: {html_file}")
            return str(html_file)
            
        except Exception as e:
            logger.error(f"生成增强HTML报告失败: {e}")
            return ""
    
    def _generate_html_content(self, results: Dict[str, Any], 
                             performance_summary: Dict[str, Any],
                             csv_analysis: Dict[str, Any] = None) -> str:
        """生成HTML内容"""
        
        # 提取关键数据
        system_info = results.get('system_info', {})
        device_results = results.get('device_results', {})
        overall_scores = performance_summary.get('performance_metrics', {}).get('overall_scores', {})
        
        html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GPU性能基准测试报告 - 增强版</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 GPU性能基准测试报告</h1>
            <p class="subtitle">增强版 - 包含详细性能指标分析</p>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="content">
            {self._generate_performance_overview(overall_scores)}
            {self._generate_system_info_section(system_info)}
            {self._generate_detailed_metrics_section(performance_summary)}
            {self._generate_device_results_section(device_results, performance_summary)}
            {self._generate_efficiency_analysis_section(performance_summary)}
            {self._generate_recommendations_section(performance_summary)}
            {self._generate_charts_section(performance_summary, csv_analysis)}
        </div>
        
        <div class="footer">
            <p>GPU Benchmark Linux - 专业GPU性能测试工具 (增强版)</p>
            <p>支持FLOPS、TOPS、内存带宽等详细性能指标分析</p>
        </div>
    </div>

    <script>
        {self._generate_javascript(performance_summary, csv_analysis)}
    </script>
</body>
</html>
"""
        return html_template
    
    def _get_css_styles(self) -> str:
        """获取CSS样式"""
        return """
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 3em;
            font-weight: 300;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle {
            font-size: 1.2em;
            margin: 10px 0;
            opacity: 0.9;
        }
        .content {
            padding: 40px;
        }
        .section {
            margin-bottom: 50px;
            background: #f8f9fa;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
            margin-bottom: 25px;
            font-size: 1.8em;
        }
        .performance-overview {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            text-align: center;
        }
        .performance-overview h2 {
            color: white;
            border-bottom: 3px solid white;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin: 30px 0;
        }
        .metric-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-5px);
        }
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        .metric-label {
            color: #666;
            font-size: 1em;
            font-weight: 500;
        }
        .metric-unit {
            font-size: 0.8em;
            color: #999;
        }
        .device-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .device-title {
            color: #495057;
            margin-bottom: 20px;
            font-size: 1.4em;
            font-weight: bold;
            display: flex;
            align-items: center;
        }
        .status-success {
            color: #28a745;
            margin-left: 10px;
        }
        .status-error {
            color: #dc3545;
            margin-left: 10px;
        }
        .info-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
        }
        .info-table th,
        .info-table td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        .info-table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: bold;
        }
        .info-table tr:hover {
            background-color: #f8f9fa;
        }
        .chart-container {
            position: relative;
            height: 400px;
            margin: 30px 0;
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .efficiency-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin-left: 10px;
        }
        .badge-excellent {
            background: #28a745;
            color: white;
        }
        .badge-good {
            background: #17a2b8;
            color: white;
        }
        .badge-average {
            background: #ffc107;
            color: #212529;
        }
        .badge-poor {
            background: #dc3545;
            color: white;
        }
        .recommendations {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        }
        .recommendation-item {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #ff6b6b;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .footer {
            background: #343a40;
            color: white;
            padding: 30px;
            text-align: center;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
        }
        """
    
    def _generate_performance_overview(self, overall_scores: Dict[str, Any]) -> str:
        """生成性能概览部分"""
        total_fp32 = overall_scores.get('total_fp32_tflops', 0)
        total_fp16 = overall_scores.get('total_fp16_tflops', 0)
        total_int8 = overall_scores.get('total_int8_tops', 0)
        total_bandwidth = overall_scores.get('total_memory_bandwidth_gbps', 0)
        performance_rating = overall_scores.get('performance_rating', '未知')
        
        return f"""
        <div class="section performance-overview">
            <h2>⚡ 性能概览</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{total_fp32}</div>
                    <div class="metric-label">总FP32性能</div>
                    <div class="metric-unit">TFLOPS</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{total_fp16}</div>
                    <div class="metric-label">总FP16性能</div>
                    <div class="metric-unit">TFLOPS</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{total_int8}</div>
                    <div class="metric-label">总AI性能</div>
                    <div class="metric-unit">TOPS</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{total_bandwidth}</div>
                    <div class="metric-label">总内存带宽</div>
                    <div class="metric-unit">GB/s</div>
                </div>
            </div>
            <h3>性能等级: {performance_rating}</h3>
        </div>
        """
    
    def _generate_system_info_section(self, system_info: Dict[str, Any]) -> str:
        """生成系统信息部分"""
        gpu_count = system_info.get('gpu_count', 0)
        gpus = system_info.get('gpus', [])
        
        gpu_rows = ""
        for i, gpu in enumerate(gpus):
            name = gpu.get('name', f'GPU {i}')
            memory = gpu.get('memory_total', 0)
            memory_gb = round(memory / 1024, 1) if memory > 0 else 0
            gpu_rows += f"<tr><td>GPU {i}</td><td>{name}</td><td>{memory_gb} GB</td></tr>"
        
        return f"""
        <div class="section">
            <h2>📊 系统信息</h2>
            <table class="info-table">
                <tr><th>项目</th><th>值</th></tr>
                <tr><td>GPU数量</td><td>{gpu_count}</td></tr>
                <tr><td>测试时间</td><td>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
            </table>
            
            <h3>GPU详细信息</h3>
            <table class="info-table">
                <tr><th>设备</th><th>型号</th><th>显存</th></tr>
                {gpu_rows}
            </table>
        </div>
        """
    
    def _generate_detailed_metrics_section(self, performance_summary: Dict[str, Any]) -> str:
        """生成详细指标部分"""
        compute_performance = performance_summary.get('performance_metrics', {}).get('compute_performance', {})
        
        device_cards = ""
        for device_id, metrics in compute_performance.items():
            device_name = metrics.get('device_name', f'GPU {device_id}')
            theoretical = metrics.get('theoretical_specs', {})
            measured = metrics.get('measured_performance', {})
            utilization = metrics.get('utilization_rates', {})
            
            device_cards += f"""
            <div class="device-card">
                <div class="device-title">{device_name}</div>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{measured.get('actual_fp32_tflops', 0)}</div>
                        <div class="metric-label">实际FP32性能</div>
                        <div class="metric-unit">TFLOPS</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {utilization.get('fp32_utilization_percent', 0)}%"></div>
                        </div>
                        <small>利用率: {utilization.get('fp32_utilization_percent', 0)}%</small>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{measured.get('actual_int8_tops', 0)}</div>
                        <div class="metric-label">实际AI性能</div>
                        <div class="metric-unit">TOPS</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {utilization.get('int8_utilization_percent', 0)}%"></div>
                        </div>
                        <small>利用率: {utilization.get('int8_utilization_percent', 0)}%</small>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{measured.get('actual_memory_bandwidth_gbps', 0)}</div>
                        <div class="metric-label">实际内存带宽</div>
                        <div class="metric-unit">GB/s</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {utilization.get('memory_bandwidth_utilization_percent', 0)}%"></div>
                        </div>
                        <small>利用率: {utilization.get('memory_bandwidth_utilization_percent', 0)}%</small>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{measured.get('efficiency_gflops_per_watt', 0)}</div>
                        <div class="metric-label">功效比</div>
                        <div class="metric-unit">GFLOPS/W</div>
                    </div>
                </div>
            </div>
            """
        
        return f"""
        <div class="section">
            <h2>📈 详细性能指标</h2>
            {device_cards}
        </div>
        """
    
    def _generate_device_results_section(self, device_results: Dict[str, Any], 
                                       performance_summary: Dict[str, Any]) -> str:
        """生成设备测试结果部分"""
        results_html = ""
        
        for device_id, result in device_results.items():
            success = result.get('success', False)
            device_name = result.get('device_name', f'GPU {device_id}')
            status_class = "status-success" if success else "status-error"
            status_icon = "✅ 成功" if success else "❌ 失败"
            
            test_results = ""
            if 'matrix_multiply' in result:
                mm_result = result['matrix_multiply']
                gflops = mm_result.get('gflops', 0)
                duration = mm_result.get('duration', 0)
                test_results += f"""
                <tr><td>矩阵乘法性能</td><td>{gflops:.2f} GFLOPS</td></tr>
                <tr><td>测试持续时间</td><td>{duration:.2f} 秒</td></tr>
                """
            
            results_html += f"""
            <div class="device-card">
                <div class="device-title">
                    {device_name} - <span class="{status_class}">{status_icon}</span>
                </div>
                <table class="info-table">
                    {test_results}
                </table>
            </div>
            """
        
        return f"""
        <div class="section">
            <h2>🎯 设备测试结果</h2>
            {results_html}
        </div>
        """
    
    def _generate_efficiency_analysis_section(self, performance_summary: Dict[str, Any]) -> str:
        """生成效率分析部分"""
        efficiency_analysis = performance_summary.get('efficiency_analysis', {})
        power_efficiency = efficiency_analysis.get('power_efficiency', {})
        
        efficiency_cards = ""
        for device_id, efficiency in power_efficiency.items():
            device_name = efficiency.get('device_name', f'GPU {device_id}')
            power_metrics = efficiency.get('power_metrics', {})
            thermal_metrics = efficiency.get('thermal_metrics', {})
            
            # 功耗效率徽章
            efficiency_rating = power_metrics.get('efficiency_rating', '未知')
            badge_class = self._get_badge_class(efficiency_rating)
            
            # 温度徽章
            thermal_rating = thermal_metrics.get('thermal_rating', '未知')
            thermal_badge_class = self._get_badge_class(thermal_rating)
            
            efficiency_cards += f"""
            <div class="device-card">
                <div class="device-title">{device_name}</div>
                <table class="info-table">
                    <tr>
                        <td>功耗效率</td>
                        <td>
                            {power_metrics.get('gflops_per_watt', 0):.2f} GFLOPS/W
                            <span class="efficiency-badge {badge_class}">{efficiency_rating}</span>
                        </td>
                    </tr>
                    <tr>
                        <td>AI功效比</td>
                        <td>{power_metrics.get('tops_per_watt', 0):.2f} TOPS/W</td>
                    </tr>
                    <tr>
                        <td>温度表现</td>
                        <td>
                            平均 {thermal_metrics.get('avg_temperature_c', 0):.1f}°C, 
                            最高 {thermal_metrics.get('max_temperature_c', 0):.1f}°C
                            <span class="efficiency-badge {thermal_badge_class}">{thermal_rating}</span>
                        </td>
                    </tr>
                </table>
            </div>
            """
        
        return f"""
        <div class="section">
            <h2>🔥 效率分析</h2>
            {efficiency_cards}
        </div>
        """
    
    def _get_badge_class(self, rating: str) -> str:
        """获取徽章样式类"""
        if '优秀' in rating or 'Excellent' in rating:
            return 'badge-excellent'
        elif '良好' in rating or 'Good' in rating:
            return 'badge-good'
        elif '一般' in rating or 'Average' in rating:
            return 'badge-average'
        else:
            return 'badge-poor'
    
    def _generate_recommendations_section(self, performance_summary: Dict[str, Any]) -> str:
        """生成建议部分"""
        recommendations = performance_summary.get('recommendations', [])
        
        recommendation_items = ""
        for i, rec in enumerate(recommendations, 1):
            recommendation_items += f"""
            <div class="recommendation-item">
                <strong>{i}.</strong> {rec}
            </div>
            """
        
        return f"""
        <div class="section recommendations">
            <h2>💡 优化建议</h2>
            {recommendation_items}
        </div>
        """
    
    def _generate_charts_section(self, performance_summary: Dict[str, Any], 
                                csv_analysis: Dict[str, Any] = None) -> str:
        """生成图表部分"""
        return """
        <div class="section">
            <h2>📊 性能图表</h2>
            <div class="chart-container">
                <canvas id="performanceChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="efficiencyChart"></canvas>
            </div>
        </div>
        """
    
    def _generate_javascript(self, performance_summary: Dict[str, Any], 
                           csv_analysis: Dict[str, Any] = None) -> str:
        """生成JavaScript代码"""
        compute_performance = performance_summary.get('performance_metrics', {}).get('compute_performance', {})
        
        # 准备图表数据
        device_names = []
        fp32_values = []
        int8_values = []
        efficiency_values = []
        
        for device_id, metrics in compute_performance.items():
            device_names.append(metrics.get('device_name', f'GPU {device_id}'))
            measured = metrics.get('measured_performance', {})
            fp32_values.append(measured.get('actual_fp32_tflops', 0))
            int8_values.append(measured.get('actual_int8_tops', 0))
            efficiency_values.append(measured.get('efficiency_gflops_per_watt', 0))
        
        return f"""
        // 性能对比图表
        const performanceCtx = document.getElementById('performanceChart');
        if (performanceCtx) {{
            new Chart(performanceCtx, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(device_names)},
                    datasets: [{{
                        label: 'FP32 (TFLOPS)',
                        data: {json.dumps(fp32_values)},
                        backgroundColor: 'rgba(102, 126, 234, 0.8)',
                        borderColor: 'rgba(102, 126, 234, 1)',
                        borderWidth: 1,
                        yAxisID: 'y'
                    }}, {{
                        label: 'AI性能 (TOPS)',
                        data: {json.dumps(int8_values)},
                        backgroundColor: 'rgba(255, 99, 132, 0.8)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1,
                        yAxisID: 'y1'
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
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {{
                                display: true,
                                text: 'TFLOPS'
                            }}
                        }},
                        y1: {{
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {{
                                display: true,
                                text: 'TOPS'
                            }},
                            grid: {{
                                drawOnChartArea: false,
                            }},
                        }}
                    }}
                }}
            }});
        }}

        // 效率图表
        const efficiencyCtx = document.getElementById('efficiencyChart');
        if (efficiencyCtx) {{
            new Chart(efficiencyCtx, {{
                type: 'radar',
                data: {{
                    labels: {json.dumps(device_names)},
                    datasets: [{{
                        label: '功效比 (GFLOPS/W)',
                        data: {json.dumps(efficiency_values)},
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'GPU功效比分析'
                        }}
                    }}
                }}
            }});
        }}
        """


def generate_enhanced_html_report(results: Dict[str, Any], 
                                csv_analysis: Dict[str, Any] = None,
                                output_dir: str = "gpu_benchmark_linux_results") -> str:
    """生成增强HTML报告的便捷函数"""
    reporter = EnhancedHTMLReporter()
    return reporter.generate_enhanced_report(results, csv_analysis, output_dir)