"""
图表生成器模块 - 自动生成GPU压力测试可视化图表
"""

import os
import time
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import numpy as np
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    plt = None
    mdates = None
    np = None
    sns = None

from .monitor import GPUMetrics
from .utils import logger


@dataclass
class ChartConfig:
    """图表配置"""
    figure_size: Tuple[int, int] = (16, 12)
    dpi: int = 300
    style: str = 'seaborn-v0_8'
    color_palette: str = 'husl'
    save_format: str = 'png'
    show_grid: bool = True
    title_fontsize: int = 14
    label_fontsize: int = 12
    legend_fontsize: int = 10


class ChartGenerator:
    """GPU压力测试图表生成器"""
    
    def __init__(self, config: Optional[ChartConfig] = None):
        """初始化图表生成器"""
        if not PLOTTING_AVAILABLE:
            logger.warning("matplotlib, numpy 或 seaborn 未安装，图表功能不可用")
            return
            
        self.config = config or ChartConfig()
        
        # 设置matplotlib样式
        try:
            plt.style.use(self.config.style)
        except:
            plt.style.use('default')
        
        # 设置seaborn调色板
        if sns:
            sns.set_palette(self.config.color_palette)
        
        # 设置中文字体支持
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
    
    def generate_comprehensive_chart(self, result: Any, output_dir: Optional[str] = None) -> Optional[str]:
        """生成综合性能图表"""
        if not PLOTTING_AVAILABLE:
            logger.warning("绘图库不可用，无法生成图表")
            return None
            
        if not hasattr(result, 'monitoring_data') or not result.monitoring_data:
            logger.warning("没有监控数据，无法生成图表")
            return None
        
        # 创建输出目录
        if output_dir is None:
            output_dir = "gpu_benchmark_linux_results"
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gpu_stress_test_chart_{timestamp}.{self.config.save_format}"
        filepath = os.path.join(output_dir, filename)
        
        # 创建图表
        fig = plt.figure(figsize=self.config.figure_size, dpi=self.config.dpi)
        
        # 准备数据
        chart_data = self._prepare_chart_data(result)
        
        # 创建子图布局 (3行2列)
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # 1. 温度趋势图
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_temperature_trend(ax1, chart_data)
        
        # 2. 功耗趋势图
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_power_trend(ax2, chart_data)
        
        # 3. GPU利用率趋势图
        ax3 = fig.add_subplot(gs[1, 0])
        self._plot_gpu_utilization_trend(ax3, chart_data)
        
        # 4. 内存利用率趋势图
        ax4 = fig.add_subplot(gs[1, 1])
        self._plot_memory_utilization_trend(ax4, chart_data)
        
        # 5. 性能指标对比图
        ax5 = fig.add_subplot(gs[2, 0])
        self._plot_performance_comparison(ax5, result)
        
        # 6. 系统状态雷达图
        ax6 = fig.add_subplot(gs[2, 1], projection='polar')
        self._plot_system_radar(ax6, result)
        
        # 添加总标题
        test_duration = f"{getattr(result, 'duration', 0):.1f}秒"
        device_count = len(getattr(result, 'device_results', {}))
        device_results = getattr(result, 'device_results', {})
        success_rate = 0.0
        if device_results:
            success_count = sum(1 for dr in device_results.values() if dr.get('success', False))
            success_rate = success_count / len(device_results) * 100
        
        fig.suptitle(f'GPU压力测试综合报告\n'
                    f'测试时长: {test_duration} | GPU数量: {device_count} | 成功率: {success_rate:.1f}%',
                    fontsize=self.config.title_fontsize + 2, fontweight='bold')
        
        # 保存图表
        plt.savefig(filepath, dpi=self.config.dpi, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        logger.info(f"综合性能图表已生成: {filepath}")
        return filepath
    
    def _prepare_chart_data(self, result: Any) -> Dict[str, Any]:
        """准备图表数据"""
        data: Dict[str, Any] = {
            'timestamps': [],
            'devices': {},
            'timeline_minutes': []
        }
        
        monitoring_data = getattr(result, 'monitoring_data', [])
        if not monitoring_data:
            return data
        
        # 按设备ID分组数据
        for metrics in monitoring_data:
            device_id = getattr(metrics, 'device_id', 0)
            
            if device_id not in data['devices']:
                data['devices'][device_id] = {
                    'timestamps': [],
                    'temperatures': [],
                    'power_usage': [],
                    'gpu_utilization': [],
                    'memory_utilization': [],
                    'memory_used': [],
                    'memory_total': []
                }
            
            device_data = data['devices'][device_id]
            timestamp = getattr(metrics, 'timestamp', time.time())
            device_data['timestamps'].append(datetime.fromtimestamp(timestamp))
            device_data['temperatures'].append(getattr(metrics, 'temperature', None) or 0)
            device_data['power_usage'].append(getattr(metrics, 'power_usage', None) or 0)
            device_data['gpu_utilization'].append(getattr(metrics, 'gpu_utilization', None) or 0)
            device_data['memory_utilization'].append(getattr(metrics, 'memory_utilization', None) or 0)
            device_data['memory_used'].append(getattr(metrics, 'memory_used', None) or 0)
            device_data['memory_total'].append(getattr(metrics, 'memory_total', None) or 0)
        
        return data
    
    def _plot_temperature_trend(self, ax: Any, chart_data: Dict[str, Any]) -> None:
        """绘制温度趋势图"""
        ax.set_title('GPU温度趋势', fontsize=self.config.title_fontsize, fontweight='bold')
        
        for device_id, device_data in chart_data['devices'].items():
            if device_data['temperatures']:
                ax.plot(device_data['timestamps'], device_data['temperatures'], 
                       label=f'GPU {device_id}', linewidth=2, marker='o', markersize=3)
        
        ax.set_ylabel('温度 (°C)', fontsize=self.config.label_fontsize)
        ax.set_xlabel('时间', fontsize=self.config.label_fontsize)
        ax.legend(fontsize=self.config.legend_fontsize)
        ax.grid(self.config.show_grid, alpha=0.3)
        
        # 添加危险温度线
        ax.axhline(y=80, color='orange', linestyle='--', alpha=0.7, label='警告温度')
        ax.axhline(y=90, color='red', linestyle='--', alpha=0.7, label='危险温度')
        
        # 格式化时间轴
        if mdates:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def _plot_power_trend(self, ax: Any, chart_data: Dict[str, Any]) -> None:
        """绘制功耗趋势图"""
        ax.set_title('GPU功耗趋势', fontsize=self.config.title_fontsize, fontweight='bold')
        
        for device_id, device_data in chart_data['devices'].items():
            if device_data['power_usage']:
                ax.plot(device_data['timestamps'], device_data['power_usage'], 
                       label=f'GPU {device_id}', linewidth=2, marker='s', markersize=3)
        
        ax.set_ylabel('功耗 (W)', fontsize=self.config.label_fontsize)
        ax.set_xlabel('时间', fontsize=self.config.label_fontsize)
        ax.legend(fontsize=self.config.legend_fontsize)
        ax.grid(self.config.show_grid, alpha=0.3)
        
        # 格式化时间轴
        if mdates:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def _plot_gpu_utilization_trend(self, ax: Any, chart_data: Dict[str, Any]) -> None:
        """绘制GPU利用率趋势图"""
        ax.set_title('GPU利用率趋势', fontsize=self.config.title_fontsize, fontweight='bold')
        
        for device_id, device_data in chart_data['devices'].items():
            if device_data['gpu_utilization']:
                ax.plot(device_data['timestamps'], device_data['gpu_utilization'], 
                       label=f'GPU {device_id}', linewidth=2, marker='^', markersize=3)
        
        ax.set_ylabel('GPU利用率 (%)', fontsize=self.config.label_fontsize)
        ax.set_xlabel('时间', fontsize=self.config.label_fontsize)
        ax.set_ylim(0, 100)
        ax.legend(fontsize=self.config.legend_fontsize)
        ax.grid(self.config.show_grid, alpha=0.3)
        
        # 添加目标利用率线
        ax.axhline(y=90, color='green', linestyle='--', alpha=0.7, label='目标利用率')
        
        # 格式化时间轴
        if mdates:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def _plot_memory_utilization_trend(self, ax: Any, chart_data: Dict[str, Any]) -> None:
        """绘制内存利用率趋势图"""
        ax.set_title('GPU内存利用率趋势', fontsize=self.config.title_fontsize, fontweight='bold')
        
        for device_id, device_data in chart_data['devices'].items():
            if device_data['memory_utilization']:
                ax.plot(device_data['timestamps'], device_data['memory_utilization'], 
                       label=f'GPU {device_id}', linewidth=2, marker='d', markersize=3)
        
        ax.set_ylabel('内存利用率 (%)', fontsize=self.config.label_fontsize)
        ax.set_xlabel('时间', fontsize=self.config.label_fontsize)
        ax.set_ylim(0, 100)
        ax.legend(fontsize=self.config.legend_fontsize)
        ax.grid(self.config.show_grid, alpha=0.3)
        
        # 格式化时间轴
        if mdates:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def _plot_performance_comparison(self, ax: Any, result: Any) -> None:
        """绘制性能指标对比图"""
        ax.set_title('设备性能对比', fontsize=self.config.title_fontsize, fontweight='bold')
        
        devices = []
        gflops_values = []
        
        # 收集GFLOPS数据
        device_results = getattr(result, 'device_results', {})
        for device_id, device_result in device_results.items():
            if ('matrix_multiply' in device_result and 
                isinstance(device_result['matrix_multiply'], dict) and
                'gflops' in device_result['matrix_multiply']):
                devices.append(f'GPU {device_id}')
                gflops_values.append(device_result['matrix_multiply']['gflops'])
        
        if devices and gflops_values:
            bars = ax.bar(devices, gflops_values, alpha=0.7)
            ax.set_ylabel('GFLOPS', fontsize=self.config.label_fontsize)
            ax.set_xlabel('设备', fontsize=self.config.label_fontsize)
            
            # 添加数值标签
            for bar, value in zip(bars, gflops_values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'{value:.1f}', ha='center', va='bottom')
        else:
            ax.text(0.5, 0.5, '无性能数据', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12)
        
        ax.grid(self.config.show_grid, alpha=0.3)
    
    def _plot_system_radar(self, ax: Any, result: Any) -> None:
        """绘制系统状态雷达图"""
        ax.set_title('系统状态雷达图', fontsize=self.config.title_fontsize, fontweight='bold', pad=20)
        
        # 准备雷达图数据
        categories = ['温度稳定性', 'GPU利用率', '内存利用率', '功耗效率', '性能表现', '系统稳定性']
        
        # 计算各项指标得分 (0-100)
        scores = self._calculate_radar_scores(result)
        
        # 添加第一个点到末尾以闭合雷达图
        scores_closed = scores + scores[:1]
        
        # 计算角度
        if np:
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            angles += angles[:1]
            
            # 绘制雷达图
            ax.plot(angles, scores_closed, 'o-', linewidth=2, label='当前测试')
            ax.fill(angles, scores_closed, alpha=0.25)
            
            # 设置标签
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontsize=self.config.legend_fontsize)
            ax.set_ylim(0, 100)
            ax.set_yticks([20, 40, 60, 80, 100])
            ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=8)
            ax.grid(True, alpha=0.3)
    
    def _calculate_radar_scores(self, result: Any) -> List[float]:
        """计算雷达图各项得分"""
        scores = [50.0, 50.0, 50.0, 50.0, 50.0, 50.0]  # 默认得分
        
        try:
            monitoring_data = getattr(result, 'monitoring_data', [])
            if monitoring_data and np:
                # 温度稳定性 (温度越低越好，变化越小越好)
                temps = [getattr(m, 'temperature', None) for m in monitoring_data]
                temps = [t for t in temps if t is not None]
                if temps:
                    avg_temp = float(np.mean(temps))
                    temp_std = float(np.std(temps))
                    temp_score = max(0, 100 - (avg_temp - 30) * 2 - temp_std * 5)
                    scores[0] = min(100.0, max(0.0, temp_score))
                
                # GPU利用率 (越接近100%越好)
                gpu_utils = [getattr(m, 'gpu_utilization', None) for m in monitoring_data]
                gpu_utils = [u for u in gpu_utils if u is not None]
                if gpu_utils:
                    avg_gpu_util = float(np.mean(gpu_utils))
                    scores[1] = min(100.0, max(0.0, avg_gpu_util))
                
                # 内存利用率 (适中最好，过高或过低都不好)
                mem_utils = [getattr(m, 'memory_utilization', None) for m in monitoring_data]
                mem_utils = [u for u in mem_utils if u is not None]
                if mem_utils:
                    avg_mem_util = float(np.mean(mem_utils))
                    if avg_mem_util < 50:
                        scores[2] = avg_mem_util * 2
                    else:
                        scores[2] = 100 - (avg_mem_util - 50) * 1.5
                    scores[2] = min(100.0, max(0.0, scores[2]))
                
                # 功耗效率 (功耗稳定性)
                powers = [getattr(m, 'power_usage', None) for m in monitoring_data]
                powers = [p for p in powers if p is not None]
                if powers:
                    power_std = float(np.std(powers))
                    power_score = max(0, 100 - power_std * 2)
                    scores[3] = min(100.0, max(0.0, power_score))
            
            # 性能表现 (基于GFLOPS)
            performance_metrics = getattr(result, 'performance_metrics', {})
            if performance_metrics and 'avg_gflops_per_device' in performance_metrics:
                gflops = performance_metrics['avg_gflops_per_device']
                # 假设5000 GFLOPS为满分
                scores[4] = min(100.0, (gflops / 5000) * 100)
            
            # 系统稳定性 (基于成功率)
            device_results = getattr(result, 'device_results', {})
            if device_results:
                success_count = sum(1 for dr in device_results.values() if dr.get('success', False))
                success_rate = success_count / len(device_results) * 100
                scores[5] = float(success_rate)
        
        except Exception as e:
            logger.error(f"计算雷达图得分失败: {e}")
        
        return scores


# 全局图表生成器实例
chart_generator = ChartGenerator()


# 便捷函数
def generate_all_charts(result: Any, output_dir: Optional[str] = None) -> Dict[str, str]:
    """生成所有类型的图表"""
    charts: Dict[str, str] = {}
    
    if not PLOTTING_AVAILABLE:
        logger.warning("绘图库不可用，无法生成图表")
        return charts
    
    try:
        # 生成综合图表
        comprehensive_chart = chart_generator.generate_comprehensive_chart(result, output_dir)
        if comprehensive_chart:
            charts['comprehensive'] = comprehensive_chart
        
        logger.info(f"已生成 {len(charts)} 个图表文件")
        
    except Exception as e:
        logger.error(f"生成图表失败: {e}")
    
    return charts