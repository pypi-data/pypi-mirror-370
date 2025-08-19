"""
CSV数据查看器 - 用于分析GPU监控数据
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from .utils import logger


class CSVDataViewer:
    """CSV数据查看器"""
    
    def __init__(self, csv_file: str):
        """初始化CSV查看器"""
        self.csv_file = Path(csv_file)
        self.df = None
        self.load_data()
    
    def load_data(self):
        """加载CSV数据"""
        try:
            if not self.csv_file.exists():
                raise FileNotFoundError(f"CSV文件不存在: {self.csv_file}")
            
            self.df = pd.read_csv(self.csv_file)
            logger.info(f"成功加载CSV数据: {len(self.df)} 条记录")
            
        except Exception as e:
            logger.error(f"加载CSV数据失败: {e}")
            raise
    
    def get_basic_info(self) -> Dict[str, Any]:
        """获取基本信息"""
        if self.df is None:
            return {}
        
        devices = self.df['device_id'].unique().tolist()
        time_range = {
            'start': self.df['datetime'].min(),
            'end': self.df['datetime'].max(),
            'duration_seconds': (pd.to_datetime(self.df['datetime'].max()) - 
                               pd.to_datetime(self.df['datetime'].min())).total_seconds()
        }
        
        return {
            'total_records': len(self.df),
            'devices': devices,
            'device_count': len(devices),
            'time_range': time_range,
            'columns': self.df.columns.tolist()
        }
    
    def get_device_statistics(self, device_id: Optional[int] = None) -> Dict[str, Any]:
        """获取设备统计信息"""
        if self.df is None:
            return {}
        
        if device_id is not None:
            df_filtered = self.df[self.df['device_id'] == device_id]
            if df_filtered.empty:
                return {}
        else:
            df_filtered = self.df
        
        # 数值列统计
        numeric_columns = [
            'temperature_c', 'power_usage_w', 'gpu_utilization_percent',
            'memory_utilization_percent', 'fan_speed_percent',
            'clock_graphics_mhz', 'clock_memory_mhz', 'voltage_v'
        ]
        
        stats = {}
        for col in numeric_columns:
            if col in df_filtered.columns:
                # 直接使用 pandas Series 方法确保类型安全
                col_series = df_filtered[col]
                median_val = col_series.median()
                
                stats[col] = {
                    'min': float(col_series.min()),
                    'max': float(col_series.max()),
                    'mean': float(col_series.mean()),
                    'std': float(col_series.std()),
                    'median': float(median_val) if pd.notna(median_val) else 0.0
                }
        
        return stats
    
    def get_temperature_analysis(self) -> Dict[str, Any]:
        """温度分析"""
        if self.df is None or 'temperature_c' not in self.df.columns:
            return {}
        
        analysis = {}
        for device_id in self.df['device_id'].unique():
            device_data = self.df[self.df['device_id'] == device_id]
            temps = device_data['temperature_c']
            
            analysis[f'device_{device_id}'] = {
                'min_temp': float(temps.min()),
                'max_temp': float(temps.max()),
                'avg_temp': float(temps.mean()),
                'temp_range': float(temps.max() - temps.min()),
                'high_temp_count': int((temps > 80).sum()),  # 高温次数
                'critical_temp_count': int((temps > 90).sum())  # 危险温度次数
            }
        
        return analysis
    
    def get_power_analysis(self) -> Dict[str, Any]:
        """功耗分析"""
        if self.df is None or 'power_usage_w' not in self.df.columns:
            return {}
        
        analysis = {}
        for device_id in self.df['device_id'].unique():
            device_data = self.df[self.df['device_id'] == device_id]
            power = device_data['power_usage_w']
            power_limit = device_data['power_limit_w'].iloc[0] if 'power_limit_w' in device_data.columns else None
            
            device_analysis = {
                'min_power': float(power.min()),
                'max_power': float(power.max()),
                'avg_power': float(power.mean()),
                'power_efficiency': float(power.mean() / power_limit) if power_limit else None
            }
            
            if power_limit:
                device_analysis['power_limit'] = float(power_limit)
                device_analysis['power_usage_ratio'] = float(power.mean() / power_limit)
            
            analysis[f'device_{device_id}'] = device_analysis
        
        return analysis
    
    def get_utilization_analysis(self) -> Dict[str, Any]:
        """利用率分析"""
        if self.df is None:
            return {}
        
        analysis = {}
        for device_id in self.df['device_id'].unique():
            device_data = self.df[self.df['device_id'] == device_id]
            
            device_analysis = {}
            
            if 'gpu_utilization_percent' in device_data.columns:
                gpu_util = device_data['gpu_utilization_percent']
                device_analysis['gpu_utilization'] = {
                    'min': float(gpu_util.min()),
                    'max': float(gpu_util.max()),
                    'avg': float(gpu_util.mean()),
                    'high_util_count': int((gpu_util > 90).sum())
                }
            
            if 'memory_utilization_percent' in device_data.columns:
                mem_util = device_data['memory_utilization_percent']
                device_analysis['memory_utilization'] = {
                    'min': float(mem_util.min()),
                    'max': float(mem_util.max()),
                    'avg': float(mem_util.mean()),
                    'high_util_count': int((mem_util > 90).sum())
                }
            
            analysis[f'device_{device_id}'] = device_analysis
        
        return analysis
    
    def get_performance_trends(self) -> Dict[str, Any]:
        """性能趋势分析"""
        if self.df is None:
            return {}
        
        # 按时间排序
        df_sorted = self.df.sort_values('timestamp')
        
        trends = {}
        for device_id in df_sorted['device_id'].unique():
            device_data = df_sorted[df_sorted['device_id'] == device_id]
            
            device_trends = {}
            
            # 温度趋势
            if 'temperature_c' in device_data.columns:
                temps = device_data['temperature_c'].values
                if len(temps) > 1:
                    temp_trend = 'increasing' if temps[-1] > temps[0] else 'decreasing'
                    device_trends['temperature_trend'] = temp_trend
                    device_trends['temperature_change'] = float(temps[-1] - temps[0])
            
            # 功耗趋势
            if 'power_usage_w' in device_data.columns:
                power = device_data['power_usage_w'].values
                if len(power) > 1:
                    power_trend = 'increasing' if power[-1] > power[0] else 'decreasing'
                    device_trends['power_trend'] = power_trend
                    device_trends['power_change'] = float(power[-1] - power[0])
            
            trends[f'device_{device_id}'] = device_trends
        
        return trends
    
    def export_summary_report(self, output_file: Optional[str] = None) -> str:
        """导出汇总报告"""
        if output_file is None:
            output_file = str(self.csv_file.parent / f"{self.csv_file.stem}_summary.json")
        
        report = {
            'file_info': {
                'csv_file': str(self.csv_file),
                'analysis_time': datetime.now().isoformat()
            },
            'basic_info': self.get_basic_info(),
            'device_statistics': {},
            'temperature_analysis': self.get_temperature_analysis(),
            'power_analysis': self.get_power_analysis(),
            'utilization_analysis': self.get_utilization_analysis(),
            'performance_trends': self.get_performance_trends()
        }
        
        # 为每个设备生成统计信息
        for device_id in self.df['device_id'].unique():
            report['device_statistics'][f'device_{device_id}'] = self.get_device_statistics(device_id)
        
        # 保存报告
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"汇总报告已保存至: {output_file}")
        return output_file
    
    def print_summary(self):
        """打印数据摘要"""
        if self.df is None:
            print("❌ 没有可用的数据")
            return
        
        basic_info = self.get_basic_info()
        temp_analysis = self.get_temperature_analysis()
        power_analysis = self.get_power_analysis()
        
        print(f"\n📊 GPU监控数据摘要")
        print(f"{'='*50}")
        print(f"📁 文件: {self.csv_file.name}")
        print(f"📈 总记录数: {basic_info['total_records']}")
        print(f"🖥️  设备数量: {basic_info['device_count']}")
        print(f"⏱️  时间范围: {basic_info['time_range']['duration_seconds']:.1f}秒")
        
        print(f"\n🌡️  温度分析:")
        for device_key, temp_data in temp_analysis.items():
            print(f"  {device_key}: {temp_data['min_temp']:.1f}°C - {temp_data['max_temp']:.1f}°C "
                  f"(平均: {temp_data['avg_temp']:.1f}°C)")
            if temp_data['high_temp_count'] > 0:
                print(f"    ⚠️  高温次数(>80°C): {temp_data['high_temp_count']}")
            if temp_data['critical_temp_count'] > 0:
                print(f"    🔥 危险温度次数(>90°C): {temp_data['critical_temp_count']}")
        
        print(f"\n⚡ 功耗分析:")
        for device_key, power_data in power_analysis.items():
            print(f"  {device_key}: {power_data['min_power']:.1f}W - {power_data['max_power']:.1f}W "
                  f"(平均: {power_data['avg_power']:.1f}W)")
            if 'power_usage_ratio' in power_data:
                print(f"    📊 功耗比例: {power_data['power_usage_ratio']:.1%}")


def analyze_csv_file(csv_file: str, export_summary: bool = True) -> CSVDataViewer:
    """分析CSV文件的便捷函数"""
    viewer = CSVDataViewer(csv_file)
    viewer.print_summary()
    
    if export_summary:
        summary_file = viewer.export_summary_report()
        print(f"\n📄 详细分析报告: {summary_file}")
    
    return viewer


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python csv_viewer.py <csv_file>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    analyze_csv_file(csv_file)