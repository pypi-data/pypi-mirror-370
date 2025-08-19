"""
演示测试模块 - 用于在没有GPU环境下演示功能
"""

import time
import random
import threading
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from .monitor import GPUMetrics
from .csv_logger import CSVLogger, CSVLoggerConfig
from .enhanced_reporter import EnhancedReporter
from .utils import logger


@dataclass
class DemoTestConfig:
    """演示测试配置"""
    duration: int = 60
    device_count: int = 2
    sample_interval: float = 1.0
    enable_csv: bool = True


class DemoGPUTester:
    """演示GPU测试器"""
    
    def __init__(self):
        """初始化演示测试器"""
        self.running = False
        self.csv_logger = None
        self.metrics_history = []
    
    def _generate_mock_metrics(self, device_id: int, timestamp: float) -> GPUMetrics:
        """生成模拟GPU指标数据"""
        # 模拟温度变化（基础温度 + 随机波动）
        base_temp = 45 + device_id * 5  # 不同设备有不同基础温度
        temperature = base_temp + random.uniform(-3, 8)
        
        # 模拟功耗变化
        base_power = 150 + device_id * 50
        power_usage = base_power + random.uniform(-20, 50)
        power_limit = base_power + 100
        
        # 模拟利用率
        gpu_utilization = random.uniform(80, 100)
        memory_utilization = random.uniform(70, 95)
        
        # 模拟内存信息（以字节为单位）
        memory_total = (8 + device_id * 4) * 1024 * 1024 * 1024  # 8GB, 12GB等
        memory_used = int(memory_total * memory_utilization / 100)
        memory_free = memory_total - memory_used
        
        # 模拟其他指标
        fan_speed = random.uniform(30, 80)
        clock_graphics = int(random.uniform(1200, 1800))
        clock_memory = int(random.uniform(5000, 7000))
        clock_sm = int(random.uniform(1200, 1800))
        voltage = random.uniform(0.8, 1.2)
        
        return GPUMetrics(
            device_id=device_id,
            name=f"NVIDIA GeForce RTX 308{device_id}",
            timestamp=timestamp,
            temperature=temperature,
            power_usage=power_usage,
            power_limit=power_limit,
            gpu_utilization=gpu_utilization,
            memory_utilization=memory_utilization,
            memory_used=memory_used,
            memory_total=memory_total,
            memory_free=memory_free,
            fan_speed=fan_speed,
            clock_graphics=clock_graphics,
            clock_memory=clock_memory,
            clock_sm=clock_sm,
            voltage=voltage
        )
    
    def run_demo_test(self, config: DemoTestConfig) -> Dict[str, Any]:
        """运行演示测试"""
        logger.info(f"开始演示GPU压力测试，模拟 {config.device_count} 个GPU设备")
        logger.info(f"测试持续时间: {config.duration}秒，采样间隔: {config.sample_interval}秒")
        
        # 初始化CSV记录器
        if config.enable_csv:
            csv_config = CSVLoggerConfig(
                filename_prefix="demo_gpu_metrics",
                auto_flush=True,
                flush_interval=2.0,
                max_buffer_size=30
            )
            self.csv_logger = CSVLogger(csv_config)
            self.csv_logger.start_logging()
            logger.info(f"CSV数据记录已启动: {self.csv_logger.get_filepath()}")
        
        self.running = True
        start_time = time.time()
        
        try:
            # 模拟测试循环
            while self.running and (time.time() - start_time) < config.duration:
                current_time = time.time()
                
                # 为每个设备生成模拟数据
                metrics_batch = []
                for device_id in range(config.device_count):
                    metrics = self._generate_mock_metrics(device_id, current_time)
                    metrics_batch.append(metrics)
                    self.metrics_history.append(metrics)
                
                # 记录到CSV
                if self.csv_logger:
                    self.csv_logger.log_metrics(metrics_batch)
                
                # 显示实时数据
                for metrics in metrics_batch:
                    logger.info(f"GPU {metrics.device_id}: "
                               f"温度={metrics.temperature:.1f}°C, "
                               f"功耗={metrics.power_usage:.1f}W, "
                               f"GPU利用率={metrics.gpu_utilization:.1f}%, "
                               f"内存利用率={metrics.memory_utilization:.1f}%")
                
                # 等待下一次采样
                time.sleep(config.sample_interval)
            
            end_time = time.time()
            actual_duration = end_time - start_time
            
            logger.info(f"演示测试完成，实际运行时间: {actual_duration:.1f}秒")
            
            # 计算统计信息
            stats = self._calculate_statistics()
            
            result = {
                'success': True,
                'start_time': start_time,
                'end_time': end_time,
                'duration': actual_duration,
                'device_count': config.device_count,
                'total_samples': len(self.metrics_history),
                'statistics': stats
            }
            
            return result
            
        except Exception as e:
            logger.error(f"演示测试执行失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'start_time': start_time,
                'end_time': time.time(),
                'duration': time.time() - start_time
            }
        
        finally:
            self.running = False
            
            # 停止CSV记录器
            if self.csv_logger:
                self.csv_logger.stop_logging()
                record_count = self.csv_logger.get_record_count()
                logger.info(f"CSV数据已保存，共记录 {record_count} 条数据")
    
    def _calculate_statistics(self) -> Dict[str, Any]:
        """计算统计信息"""
        if not self.metrics_history:
            return {}
        
        # 按设备分组统计
        device_stats = {}
        for metrics in self.metrics_history:
            device_id = metrics.device_id
            if device_id not in device_stats:
                device_stats[device_id] = {
                    'temperatures': [],
                    'power_usage': [],
                    'gpu_utilization': [],
                    'memory_utilization': []
                }
            
            device_stats[device_id]['temperatures'].append(metrics.temperature)
            device_stats[device_id]['power_usage'].append(metrics.power_usage)
            device_stats[device_id]['gpu_utilization'].append(metrics.gpu_utilization)
            device_stats[device_id]['memory_utilization'].append(metrics.memory_utilization)
        
        # 计算每个设备的统计信息
        stats = {}
        for device_id, data in device_stats.items():
            stats[f'device_{device_id}'] = {
                'temperature': {
                    'min': min(data['temperatures']),
                    'max': max(data['temperatures']),
                    'avg': sum(data['temperatures']) / len(data['temperatures'])
                },
                'power_usage': {
                    'min': min(data['power_usage']),
                    'max': max(data['power_usage']),
                    'avg': sum(data['power_usage']) / len(data['power_usage'])
                },
                'gpu_utilization': {
                    'min': min(data['gpu_utilization']),
                    'max': max(data['gpu_utilization']),
                    'avg': sum(data['gpu_utilization']) / len(data['gpu_utilization'])
                },
                'memory_utilization': {
                    'min': min(data['memory_utilization']),
                    'max': max(data['memory_utilization']),
                    'avg': sum(data['memory_utilization']) / len(data['memory_utilization'])
                }
            }
        
        return stats
    
    def stop(self):
        """停止测试"""
        self.running = False
    
    def get_csv_filepath(self):
        """获取CSV文件路径"""
        if self.csv_logger:
            return self.csv_logger.get_filepath()
        return None
    
    def get_metrics_history(self) -> List[GPUMetrics]:
        """获取指标历史数据"""
        return self.metrics_history.copy()


def run_demo_test(duration: int = 30, device_count: int = 2, enable_csv: bool = True) -> Dict[str, Any]:
    """运行演示测试的便捷函数"""
    config = DemoTestConfig(
        duration=duration,
        device_count=device_count,
        sample_interval=1.0,
        enable_csv=enable_csv
    )
    
    tester = DemoGPUTester()
    return tester.run_demo_test(config)


def demo_csv_analysis(csv_file: str):
    """演示CSV数据分析功能"""
    logger.info(f"开始分析CSV文件: {csv_file}")
    
    try:
        # 使用增强报告器分析CSV数据
        reporter = EnhancedReporter()
        dashboard_data = reporter.create_csv_dashboard_data(csv_file)
        
        if dashboard_data:
            logger.info("CSV数据分析完成:")
            logger.info(f"• 设备数量: {len(dashboard_data.get('devices', []))}")
            logger.info(f"• 时间点数量: {len(dashboard_data.get('timestamps', []))}")
            
            # 显示统计信息
            stats = dashboard_data.get('statistics', {})
            if 'temperature' in stats:
                temp_stats = stats['temperature']
                logger.info(f"• 温度统计: {temp_stats}")
            
            if 'power' in stats:
                power_stats = stats['power']
                logger.info(f"• 功耗统计: {power_stats}")
            
            # 生成分析报告
            analysis_files = reporter.generate_comprehensive_report([csv_file], "demo_test")
            if analysis_files:
                logger.info("分析报告已生成:")
                for name, file_path in analysis_files.items():
                    logger.info(f"• {name}: {file_path}")
        else:
            logger.warning("CSV数据分析失败")
    
    except Exception as e:
        logger.error(f"CSV数据分析异常: {e}")


if __name__ == "__main__":
    # 运行演示测试
    result = run_demo_test(duration=30, device_count=2, enable_csv=True)
    
    if result['success']:
        print(f"演示测试成功完成，运行时间: {result['duration']:.1f}秒")
        print(f"总采样数: {result['total_samples']}")
        
        # 如果有CSV文件，进行分析
        tester = DemoGPUTester()
        csv_file = tester.get_csv_filepath()
        if csv_file:
            demo_csv_analysis(str(csv_file))
    else:
        print(f"演示测试失败: {result.get('error', '未知错误')}")