"""
GPU压力测试模块 - 提供GPU压力测试核心功能
"""

import os
import sys
import time
import threading
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import json
import signal

from .cuda_ops import CUDAOperations
from .monitor import GPUMonitor, GPUMetrics
from .utils import logger


@dataclass
class StressTestConfig:
    """压力测试配置"""
    duration: int = 60  # 测试持续时间（秒）
    device_ids: Optional[List[int]] = None  # 要测试的设备ID列表，None表示所有设备
    matrix_size: int = 4096  # 矩阵大小
    memory_usage_ratio: float = 0.8  # 内存使用比例
    test_types: Optional[List[str]] = None  # 测试类型列表
    monitor_interval: float = 1.0  # 监控采样间隔
    temperature_limit: float = 90.0  # 温度限制
    power_limit_ratio: float = 0.95  # 功耗限制比例
    auto_stop_on_limit: bool = True  # 达到限制时自动停止
    
    def __post_init__(self):
        if self.device_ids is None:
            self.device_ids = []
        if self.test_types is None:
            self.test_types = ['matrix_multiply', 'compute_intensive', 'memory_bandwidth']


@dataclass
class StressTestResult:
    """压力测试结果"""
    config: StressTestConfig
    start_time: float
    end_time: float
    duration: float
    success: bool
    error_message: str = ""
    device_results: Dict[int, Dict[str, Any]] = None
    monitoring_data: List[GPUMetrics] = None
    performance_metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.device_results is None:
            self.device_results = {}
        if self.monitoring_data is None:
            self.monitoring_data = []
        if self.performance_metrics is None:
            self.performance_metrics = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'config': {
                'duration': self.config.duration,
                'device_ids': self.config.device_ids,
                'matrix_size': self.config.matrix_size,
                'memory_usage_ratio': self.config.memory_usage_ratio,
                'test_types': self.config.test_types,
                'monitor_interval': self.config.monitor_interval,
                'temperature_limit': self.config.temperature_limit,
                'power_limit_ratio': self.config.power_limit_ratio,
                'auto_stop_on_limit': self.config.auto_stop_on_limit
            },
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration,
            'success': self.success,
            'error_message': self.error_message,
            'device_results': self.device_results,
            'monitoring_data': [m.to_dict() for m in self.monitoring_data],
            'performance_metrics': self.performance_metrics
        }


class GPUStressTester:
    """GPU压力测试器"""
    
    def __init__(self, cuda_ops: CUDAOperations = None, monitor: GPUMonitor = None, enable_csv_logging: bool = True):
        """初始化压力测试器"""
        if cuda_ops is None:
            cuda_ops = CUDAOperations()
        if monitor is None:
            monitor = GPUMonitor()
        self.cuda_ops = cuda_ops
        self.monitor = monitor
        self.running = False
        self.test_threads = {}
        self.results = {}
        self.stop_event = threading.Event()
        self.callbacks = []
        self.enable_csv_logging = enable_csv_logging
        self.csv_logger = None
        
        # 信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"接收到信号 {signum}，停止压力测试...")
        self.stop()
    
    def add_callback(self, callback: Callable[[StressTestResult], None]):
        """添加测试完成回调函数"""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[StressTestResult], None]):
        """移除测试完成回调函数"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _check_limits(self, metrics: GPUMetrics, config: StressTestConfig) -> bool:
        """检查是否超过安全限制"""
        if not config.auto_stop_on_limit:
            return False
        
        # 检查温度限制
        if metrics.temperature and metrics.temperature > config.temperature_limit:
            logger.warning(f"GPU {metrics.device_id} 温度超限: {metrics.temperature}°C > {config.temperature_limit}°C")
            return True
        
        # 检查功耗限制
        if (metrics.power_usage and metrics.power_limit and 
            metrics.power_usage > metrics.power_limit * config.power_limit_ratio):
            logger.warning(f"GPU {metrics.device_id} 功耗超限: {metrics.power_usage}W > {metrics.power_limit * config.power_limit_ratio}W")
            return True
        
        return False
    
    def _monitor_callback(self, metrics_list: List[GPUMetrics], config: StressTestConfig):
        """监控回调函数"""
        for metrics in metrics_list:
            if metrics.device_id in config.device_ids:
                # 检查安全限制
                if self._check_limits(metrics, config):
                    logger.error(f"GPU {metrics.device_id} 超过安全限制，停止测试")
                    self.stop()
                    return
                
                # 记录关键指标
                logger.info(f"GPU {metrics.device_id}: "
                           f"温度={metrics.temperature}°C, "
                           f"功耗={metrics.power_usage}W, "
                           f"GPU利用率={metrics.gpu_utilization}%, "
                           f"内存利用率={metrics.memory_utilization}%")
    
    def _run_matrix_multiply_test(self, device_id: int, config: StressTestConfig) -> Dict[str, Any]:
        """运行矩阵乘法测试"""
        logger.info(f"GPU {device_id}: 开始矩阵乘法压力测试")
        
        try:
            # 设置设备
            self.cuda_ops.set_device(device_id)
            
            # 计算迭代次数
            estimated_time_per_iter = 0.1  # 估计每次迭代时间
            iterations = max(1, int(config.duration / estimated_time_per_iter))
            
            # 执行测试
            result = self.cuda_ops.matrix_multiply_stress(
                size=config.matrix_size,
                iterations=iterations
            )
            
            logger.info(f"GPU {device_id}: 矩阵乘法测试完成，GFLOPS: {result['gflops']:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"GPU {device_id}: 矩阵乘法测试失败: {e}")
            return {'error': str(e)}
    
    def _run_compute_intensive_test(self, device_id: int, config: StressTestConfig) -> Dict[str, Any]:
        """运行计算密集型测试"""
        logger.info(f"GPU {device_id}: 开始计算密集型压力测试")
        
        try:
            # 设置设备
            self.cuda_ops.set_device(device_id)
            
            # 执行测试
            result = self.cuda_ops.compute_intensive_test(duration=config.duration)
            
            logger.info(f"GPU {device_id}: 计算密集型测试完成，迭代次数: {result['iterations']}")
            return result
            
        except Exception as e:
            logger.error(f"GPU {device_id}: 计算密集型测试失败: {e}")
            return {'error': str(e)}
    
    def _run_memory_bandwidth_test(self, device_id: int, config: StressTestConfig) -> Dict[str, Any]:
        """运行内存带宽测试"""
        logger.info(f"GPU {device_id}: 开始内存带宽压力测试")
        
        try:
            # 设置设备
            self.cuda_ops.set_device(device_id)
            
            # 获取设备内存信息
            _, total_memory = self.cuda_ops.get_memory_info(device_id)
            test_size_mb = int(total_memory * config.memory_usage_ratio / (1024 * 1024))
            
            # 计算迭代次数
            iterations = max(1, config.duration // 2)  # 每2秒一次迭代
            
            # 执行测试
            result = self.cuda_ops.memory_bandwidth_test(
                size_mb=test_size_mb,
                iterations=iterations
            )
            
            logger.info(f"GPU {device_id}: 内存带宽测试完成")
            return result
            
        except Exception as e:
            logger.error(f"GPU {device_id}: 内存带宽测试失败: {e}")
            return {'error': str(e)}
    
    def _run_device_test(self, device_id: int, config: StressTestConfig) -> Dict[str, Any]:
        """运行单个设备的压力测试"""
        logger.info(f"GPU {device_id}: 开始压力测试")
        
        device_results = {}
        start_time = time.time()
        
        try:
            # 运行各种测试
            for test_type in config.test_types:
                if self.stop_event.is_set():
                    break
                
                if test_type == 'matrix_multiply':
                    device_results['matrix_multiply'] = self._run_matrix_multiply_test(device_id, config)
                elif test_type == 'compute_intensive':
                    device_results['compute_intensive'] = self._run_compute_intensive_test(device_id, config)
                elif test_type == 'memory_bandwidth':
                    device_results['memory_bandwidth'] = self._run_memory_bandwidth_test(device_id, config)
                else:
                    logger.warning(f"未知的测试类型: {test_type}")
            
            end_time = time.time()
            device_results['duration'] = end_time - start_time
            device_results['success'] = True
            
            logger.info(f"GPU {device_id}: 压力测试完成")
            
        except Exception as e:
            logger.error(f"GPU {device_id}: 压力测试失败: {e}")
            device_results['error'] = str(e)
            device_results['success'] = False
        
        return device_results
    
    def run_stress_test(self, config: StressTestConfig) -> StressTestResult:
        """运行压力测试"""
        if self.cuda_ops is None or not self.cuda_ops.is_available():
            raise RuntimeError("CUDA不可用，无法运行压力测试")
        
        if self.monitor is None or not self.monitor.is_available():
            logger.warning("GPU监控不可用，将无法监控硬件指标")
        
        # 验证设备ID
        if not config.device_ids:
            config.device_ids = list(range(self.cuda_ops.get_device_count()))
        
        for device_id in config.device_ids:
            if device_id >= self.cuda_ops.get_device_count():
                raise ValueError(f"设备ID {device_id} 超出范围")
        
        logger.info(f"开始GPU压力测试，设备: {config.device_ids}, 持续时间: {config.duration}秒")
        
        # 初始化结果
        result = StressTestResult(
            config=config,
            start_time=time.time(),
            end_time=0,
            duration=0,
            success=False
        )
        
        self.running = True
        self.stop_event.clear()
        
        # 初始化CSV记录器
        if self.enable_csv_logging:
            try:
                from .csv_logger import CSVLogger, CSVLoggerConfig
                csv_config = CSVLoggerConfig(
                    filename_prefix="gpu_stress_test",
                    auto_flush=True,
                    flush_interval=2.0,
                    max_buffer_size=50
                )
                self.csv_logger = CSVLogger(csv_config)
                self.csv_logger.start_logging()
                logger.info(f"CSV数据记录已启动: {self.csv_logger.get_filepath()}")
            except Exception as e:
                logger.warning(f"启动CSV记录器失败: {e}")
                self.csv_logger = None
        
        try:
            # 启动监控
            if self.monitor and self.monitor.is_available():
                # 添加监控回调
                monitor_callback = lambda metrics: self._monitor_callback(metrics, config)
                self.monitor.add_callback(monitor_callback)
                
                # 添加CSV记录回调
                if self.csv_logger:
                    csv_callback = lambda metrics: self.csv_logger.log_metrics(metrics)
                    self.monitor.add_callback(csv_callback)
                
                self.monitor.start_monitoring(interval=config.monitor_interval)
            
            # 启动各设备的测试线程
            self.test_threads = {}
            for device_id in config.device_ids:
                thread = threading.Thread(
                    target=lambda did=device_id: self.results.update({did: self._run_device_test(did, config)}),
                    daemon=True
                )
                thread.start()
                self.test_threads[device_id] = thread
            
            # 等待所有测试完成或超时
            timeout_time = time.time() + config.duration + 30  # 额外30秒缓冲
            
            while self.running and time.time() < timeout_time:
                # 检查所有线程是否完成
                all_finished = True
                for thread in self.test_threads.values():
                    if thread.is_alive():
                        all_finished = False
                        break
                
                if all_finished:
                    break
                
                time.sleep(1)
            
            # 停止测试
            self.stop()
            
            # 收集结果
            result.end_time = time.time()
            result.duration = result.end_time - result.start_time
            result.device_results = self.results.copy()
            
            # 获取监控数据
            if self.monitor and self.monitor.is_available():
                result.monitoring_data = self.monitor.get_metrics_history()
                self.monitor.remove_callback(monitor_callback)
            
            # 计算性能指标
            result.performance_metrics = self._calculate_performance_metrics(result)
            
            # 判断测试是否成功
            result.success = all(
                device_result.get('success', False) 
                for device_result in result.device_results.values()
            )
            
            if result.success:
                logger.info("GPU压力测试成功完成")
            else:
                logger.warning("GPU压力测试部分失败")
            
            # 调用回调函数
            for callback in self.callbacks:
                try:
                    callback(result)
                except Exception as e:
                    logger.error(f"测试完成回调函数执行失败: {e}")
            
            # 自动生成HTML报告
            try:
                from .html_reporter import HTMLReporter
                html_reporter = HTMLReporter()
                
                # 准备HTML报告数据
                html_data = self._prepare_html_data(result)
                html_file = html_reporter.generate_html_report(html_data)
                logger.info(f"HTML可视化报告已生成: {html_file}")
                
            except Exception as e:
                logger.error(f"生成HTML报告失败: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"压力测试执行失败: {e}")
            result.error_message = str(e)
            result.end_time = time.time()
            result.duration = result.end_time - result.start_time
            return result
        
        finally:
            self.running = False
            self.stop_event.set()
            
            # 停止CSV记录器
            if self.csv_logger:
                try:
                    self.csv_logger.stop_logging()
                    logger.info(f"CSV数据已保存，共记录 {self.csv_logger.get_record_count()} 条数据")
                except Exception as e:
                    logger.error(f"停止CSV记录器失败: {e}")
            
            # 清理资源
            if self.monitor and self.monitor.is_available():
                self.monitor.stop_monitoring()
            
            if self.cuda_ops:
                self.cuda_ops.cleanup()
    
    def _calculate_performance_metrics(self, result: StressTestResult) -> Dict[str, Any]:
        """计算性能指标"""
        metrics = {}
        
        try:
            # 计算总体GFLOPS
            total_gflops = 0
            gflops_count = 0
            
            for device_id, device_result in result.device_results.items():
                if 'matrix_multiply' in device_result:
                    mm_result = device_result['matrix_multiply']
                    if 'gflops' in mm_result:
                        total_gflops += mm_result['gflops']
                        gflops_count += 1
            
            if gflops_count > 0:
                metrics['total_gflops'] = total_gflops
                metrics['avg_gflops_per_device'] = total_gflops / gflops_count
            
            # 计算监控统计
            if result.monitoring_data:
                # 温度统计
                temps = [m.temperature for m in result.monitoring_data if m.temperature is not None]
                if temps:
                    metrics['temperature_stats'] = {
                        'min': min(temps),
                        'max': max(temps),
                        'avg': sum(temps) / len(temps)
                    }
                
                # 功耗统计
                powers = [m.power_usage for m in result.monitoring_data if m.power_usage is not None]
                if powers:
                    metrics['power_stats'] = {
                        'min': min(powers),
                        'max': max(powers),
                        'avg': sum(powers) / len(powers)
                    }
                
                # GPU利用率统计
                gpu_utils = [m.gpu_utilization for m in result.monitoring_data if m.gpu_utilization is not None]
                if gpu_utils:
                    metrics['gpu_utilization_stats'] = {
                        'min': min(gpu_utils),
                        'max': max(gpu_utils),
                        'avg': sum(gpu_utils) / len(gpu_utils)
                    }
        
        except Exception as e:
            logger.error(f"计算性能指标失败: {e}")
        
        return metrics
    
    def _prepare_html_data(self, result: StressTestResult) -> Dict[str, Any]:
        """准备HTML报告数据"""
        try:
            # 系统信息
            system_info = {
                'GPU数量': len(result.device_results),
                '测试持续时间': f"{result.duration:.1f}秒",
                '测试类型': ', '.join(result.config.test_types),
                '矩阵大小': result.config.matrix_size,
                '内存使用比例': f"{result.config.memory_usage_ratio*100:.0f}%"
            }
            
            # 添加CUDA信息
            if self.cuda_ops and self.cuda_ops.is_available():
                try:
                    import cupy as cp
                    system_info['CUDA版本'] = f"{cp.cuda.runtime.runtimeGetVersion()}"
                except:
                    system_info['CUDA版本'] = "未知"
            
            # 性能指标
            performance_metrics = result.performance_metrics.copy()
            
            # 设备结果
            device_results = {}
            for device_id, device_result in result.device_results.items():
                device_data = {
                    'success': device_result.get('success', False),
                    'duration': device_result.get('duration', 0)
                }
                
                # 添加各种测试结果
                if 'matrix_multiply' in device_result:
                    mm_result = device_result['matrix_multiply']
                    if 'gflops' in mm_result:
                        device_data['matrix_multiply'] = {'gflops': mm_result['gflops']}
                
                if 'compute_intensive' in device_result:
                    ci_result = device_result['compute_intensive']
                    if 'iterations' in ci_result:
                        device_data['compute_intensive'] = {'iterations': ci_result['iterations']}
                
                if 'memory_bandwidth' in device_result:
                    mb_result = device_result['memory_bandwidth']
                    if 'bandwidth_gbps' in mb_result:
                        device_data['memory_bandwidth'] = {'bandwidth_gbps': mb_result['bandwidth_gbps']}
                
                device_results[device_id] = device_data
            
            # 监控数据时间序列
            monitoring_timeline = []
            if result.monitoring_data:
                for metrics in result.monitoring_data:
                    monitoring_timeline.append({
                        'timestamp': metrics.timestamp,
                        'device_id': metrics.device_id,
                        'temperature': metrics.temperature,
                        'power_usage': metrics.power_usage,
                        'gpu_utilization': metrics.gpu_utilization,
                        'memory_utilization': metrics.memory_utilization
                    })
            
            return {
                'system_info': system_info,
                'performance_metrics': performance_metrics,
                'device_results': device_results,
                'monitoring_timeline': monitoring_timeline,
                'test_config': {
                    'duration': result.config.duration,
                    'device_count': len(result.device_results),
                    'success_rate': sum(1 for dr in device_results.values() if dr.get('success', False)) / len(device_results) * 100 if device_results else 0
                }
            }
            
        except Exception as e:
            logger.error(f"准备HTML数据失败: {e}")
            # 返回基本数据
            return {
                'system_info': {'GPU数量': len(result.device_results)},
                'performance_metrics': result.performance_metrics,
                'device_results': result.device_results
            }
    
    def stop(self):
        """停止压力测试"""
        if self.running:
            logger.info("正在停止GPU压力测试...")
            self.running = False
            self.stop_event.set()
            
            # 等待所有测试线程结束
            for thread in self.test_threads.values():
                thread.join(timeout=5.0)
    
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self.running
    
    def export_result(self, result: StressTestResult, filename: str, format: str = 'json'):
        """导出测试结果"""
        try:
            if format.lower() == 'json':
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"不支持的格式: {format}")
            
            logger.info(f"测试结果已导出到: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"导出测试结果失败: {e}")
            return False


# 全局压力测试器实例
stress_tester = GPUStressTester()


# 便捷函数
def run_quick_stress_test(duration: int = 60, device_ids: List[int] = None) -> StressTestResult:
    """运行快速压力测试"""
    config = StressTestConfig(
        duration=duration,
        device_ids=device_ids,
        test_types=['matrix_multiply', 'compute_intensive']
    )
    return stress_tester.run_stress_test(config)


def run_full_stress_test(duration: int = 300, device_ids: List[int] = None) -> StressTestResult:
    """运行完整压力测试"""
    config = StressTestConfig(
        duration=duration,
        device_ids=device_ids,
        test_types=['matrix_multiply', 'compute_intensive', 'memory_bandwidth'],
        matrix_size=8192,
        memory_usage_ratio=0.9
    )
    return stress_tester.run_stress_test(config)