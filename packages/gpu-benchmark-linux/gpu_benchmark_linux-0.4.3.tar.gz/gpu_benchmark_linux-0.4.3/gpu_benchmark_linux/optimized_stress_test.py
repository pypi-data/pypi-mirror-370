"""
优化版GPU压力测试模块
集成内存管理和性能优化功能
"""

import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import cupy as cp
import numpy as np

from .memory_optimizer import ResourceManager
from .stress_test import GPUStressTester, StressTestConfig, StressTestResult
from .monitor import GPUMonitor

logger = logging.getLogger(__name__)


class OptimizedStressTest(GPUStressTester):
    """优化版GPU压力测试类"""
    
    def __init__(self, device_id: int = 0):
        super().__init__()
        self.device_id = device_id
        self.resource_manager = ResourceManager(device_id)
        self.optimization_enabled = True
        
    def run_stress_test(self, config: StressTestConfig) -> StressTestResult:
        """运行优化版压力测试"""
        logger.info(f"开始优化版GPU压力测试 (设备 {self.device_id})")
        
        # 启动资源监控
        if self.optimization_enabled:
            self.resource_manager.start_monitoring(interval=1.0)
        
        result = None
        
        try:
            # 使用优化的上下文运行测试
            with self.resource_manager.optimized_context(matrix_size=2048) as ctx:
                # 获取优化参数
                memory_params = ctx['memory_params']
                perf_params = ctx['performance_params']
                
                logger.info(f"优化参数 - 批次大小: {memory_params['batch_size']}, "
                           f"块大小: {memory_params['block_size']}, "
                           f"算法: {perf_params['algorithm']}")
                
                # 运行原始压力测试逻辑，但使用优化参数
                result = self._run_optimized_test_with_params(config, memory_params, perf_params)
                
        except Exception as e:
            logger.error(f"优化版压力测试失败: {e}")
            # 回退到标准测试
            result = super().run_stress_test(config)
        
        finally:
            # 停止资源监控并获取统计数据
            if self.optimization_enabled:
                monitor_stats = self.resource_manager.stop_monitoring()
                if result is not None and hasattr(result, 'optimization_stats'):
                    result.optimization_stats = monitor_stats
        
        return result
    
    def _run_optimized_test_with_params(self, config: StressTestConfig, 
                                      memory_params: Dict, perf_params: Dict) -> StressTestResult:
        """使用优化参数运行测试"""
        start_time = time.time()
        device_results = {}
        
        try:
            with cp.cuda.Device(self.device_id):
                # 初始化监控
                monitor = GPUMonitor(self.device_id)
                monitor.start_monitoring()
                
                # 运行各种测试类型
                test_results = {}
                
                if 'matrix_multiply' in config.test_types:
                    test_results['matrix_multiply'] = self._optimized_matrix_multiply_test(
                        config.duration // len(config.test_types),
                        memory_params, perf_params
                    )
                
                if 'compute_intensive' in config.test_types:
                    test_results['compute_intensive'] = self._optimized_compute_intensive_test(
                        config.duration // len(config.test_types),
                        memory_params, perf_params
                    )
                
                if 'memory_bandwidth' in config.test_types:
                    test_results['memory_bandwidth'] = self._optimized_memory_bandwidth_test(
                        config.duration // len(config.test_types),
                        memory_params, perf_params
                    )
                
                # 停止监控并获取结果
                monitor.stop_monitoring()
                monitoring_data = monitor.get_monitoring_data()
                
                device_results[self.device_id] = test_results
                
                # 计算性能指标
                performance_metrics = self._calculate_optimized_performance_metrics(
                    device_results, monitoring_data
                )
                
                return StressTestResult(
                    success=True,
                    start_time=start_time,
                    end_time=time.time(),
                    duration=time.time() - start_time,
                    device_results=device_results,
                    performance_metrics=performance_metrics,
                    monitoring_data=monitoring_data
                )
                
        except Exception as e:
            logger.error(f"优化测试执行失败: {e}")
            return StressTestResult(
                success=False,
                start_time=start_time,
                end_time=time.time(),
                duration=time.time() - start_time,
                device_results={},
                error_message=str(e)
            )
    
    def _optimized_matrix_multiply_test(self, duration: float, 
                                      memory_params: Dict, perf_params: Dict) -> Dict[str, Any]:
        """优化版矩阵乘法测试"""
        logger.info("运行优化版矩阵乘法测试")
        
        # 使用优化参数
        batch_size = memory_params['batch_size']
        matrix_size = 2048  # 基础矩阵大小
        dtype = perf_params['dtype']
        
        start_time = time.time()
        iterations = 0
        total_operations = 0
        
        try:
            # 预分配矩阵以减少内存分配开销
            matrices_a = []
            matrices_b = []
            matrices_c = []
            
            for i in range(batch_size):
                a = cp.random.random((matrix_size, matrix_size), dtype=dtype)
                b = cp.random.random((matrix_size, matrix_size), dtype=dtype)
                c = cp.zeros((matrix_size, matrix_size), dtype=dtype)
                matrices_a.append(a)
                matrices_b.append(b)
                matrices_c.append(c)
            
            # 同步确保初始化完成
            cp.cuda.Stream.null.synchronize()
            
            # 运行测试
            while time.time() - start_time < duration:
                for i in range(batch_size):
                    # 使用优化的矩阵乘法
                    matrices_c[i] = cp.dot(matrices_a[i], matrices_b[i])
                
                # 同步计算
                cp.cuda.Stream.null.synchronize()
                
                iterations += 1
                total_operations += batch_size * (2 * matrix_size**3)  # 每次矩阵乘法的操作数
            
            elapsed_time = time.time() - start_time
            gflops = (total_operations / elapsed_time) / 1e9
            
            return {
                'iterations': iterations,
                'total_operations': total_operations,
                'elapsed_time': elapsed_time,
                'gflops': gflops,
                'batch_size': batch_size,
                'matrix_size': matrix_size,
                'optimization_used': True
            }
            
        except Exception as e:
            logger.error(f"优化矩阵乘法测试失败: {e}")
            return {'error': str(e), 'optimization_used': True}
    
    def _optimized_compute_intensive_test(self, duration: float,
                                        memory_params: Dict, perf_params: Dict) -> Dict[str, Any]:
        """优化版计算密集型测试"""
        logger.info("运行优化版计算密集型测试")
        
        batch_size = memory_params['batch_size']
        array_size = 1024 * 1024  # 1M elements
        dtype = perf_params['dtype']
        
        start_time = time.time()
        iterations = 0
        
        try:
            # 预分配数组
            arrays = []
            for i in range(batch_size):
                arr = cp.random.random(array_size, dtype=dtype)
                arrays.append(arr)
            
            cp.cuda.Stream.null.synchronize()
            
            # 运行计算密集型操作
            while time.time() - start_time < duration:
                for i in range(batch_size):
                    # 复杂数学运算
                    arrays[i] = cp.sin(arrays[i]) * cp.cos(arrays[i])
                    arrays[i] = cp.exp(cp.log(cp.abs(arrays[i]) + 1e-8))
                    arrays[i] = cp.sqrt(arrays[i] * arrays[i] + 1.0)
                
                cp.cuda.Stream.null.synchronize()
                iterations += 1
            
            elapsed_time = time.time() - start_time
            iterations_per_second = iterations / elapsed_time
            
            return {
                'iterations': iterations,
                'elapsed_time': elapsed_time,
                'iterations_per_second': iterations_per_second,
                'batch_size': batch_size,
                'array_size': array_size,
                'optimization_used': True
            }
            
        except Exception as e:
            logger.error(f"优化计算密集型测试失败: {e}")
            return {'error': str(e), 'optimization_used': True}
    
    def _optimized_memory_bandwidth_test(self, duration: float,
                                       memory_params: Dict, perf_params: Dict) -> Dict[str, Any]:
        """优化版内存带宽测试"""
        logger.info("运行优化版内存带宽测试")
        
        # 使用可用内存的一部分进行测试
        available_memory = memory_params['available_memory_gb'] * 1024**3
        test_size = min(int(available_memory * 0.3), 512 * 1024 * 1024)  # 最大512MB
        
        start_time = time.time()
        
        try:
            # Host to Device 测试
            h2d_bytes = 0
            h2d_start = time.time()
            
            while time.time() - h2d_start < duration / 2:
                host_data = np.random.random(test_size // 4).astype(np.float32)
                device_data = cp.asarray(host_data)
                cp.cuda.Stream.null.synchronize()
                h2d_bytes += test_size
            
            h2d_time = time.time() - h2d_start
            h2d_bandwidth = (h2d_bytes / h2d_time) / 1e9  # GB/s
            
            # Device to Host 测试
            d2h_bytes = 0
            d2h_start = time.time()
            
            device_data = cp.random.random(test_size // 4, dtype=cp.float32)
            
            while time.time() - d2h_start < duration / 2:
                host_data = cp.asnumpy(device_data)
                d2h_bytes += test_size
            
            d2h_time = time.time() - d2h_start
            d2h_bandwidth = (d2h_bytes / d2h_time) / 1e9  # GB/s
            
            return {
                'h2d_bandwidth_gbps': h2d_bandwidth,
                'd2h_bandwidth_gbps': d2h_bandwidth,
                'test_size_mb': test_size / 1024**2,
                'h2d_time': h2d_time,
                'd2h_time': d2h_time,
                'optimization_used': True
            }
            
        except Exception as e:
            logger.error(f"优化内存带宽测试失败: {e}")
            return {'error': str(e), 'optimization_used': True}
    
    def _calculate_optimized_performance_metrics(self, device_results: Dict, 
                                               monitoring_data: Dict) -> Dict[str, Any]:
        """计算优化版性能指标"""
        metrics = {}
        
        # 基础性能指标
        total_gflops = 0
        device_count = max(len(device_results), 1)  # 确保至少为1避免除零错误
        
        for device_id, results in device_results.items():
            if 'matrix_multiply' in results and 'gflops' in results['matrix_multiply']:
                total_gflops += results['matrix_multiply']['gflops']
        
        metrics['total_gflops'] = total_gflops
        metrics['avg_gflops_per_device'] = total_gflops / device_count
        metrics['device_count'] = len(device_results)  # 添加设备数量
        
        # 监控数据统计 - 修复数据结构访问
        if monitoring_data:
            # 处理温度数据
            if hasattr(monitoring_data, 'temperatures') and monitoring_data.temperatures:
                temps = monitoring_data.temperatures
                metrics['temperature_stats'] = {
                    'min': float(min(temps)),
                    'max': float(max(temps)),
                    'avg': float(sum(temps) / len(temps))
                }
            elif isinstance(monitoring_data, dict) and 'temperatures' in monitoring_data:
                temps = monitoring_data['temperatures']
                if temps:
                    metrics['temperature_stats'] = {
                        'min': float(min(temps)),
                        'max': float(max(temps)),
                        'avg': float(sum(temps) / len(temps))
                    }
            
            # 处理功耗数据
            if hasattr(monitoring_data, 'power_usage') and monitoring_data.power_usage:
                powers = monitoring_data.power_usage
                metrics['power_stats'] = {
                    'min': float(min(powers)),
                    'max': float(max(powers)),
                    'avg': float(sum(powers) / len(powers))
                }
            elif isinstance(monitoring_data, dict) and 'power_usage' in monitoring_data:
                powers = monitoring_data['power_usage']
                if powers:
                    metrics['power_stats'] = {
                        'min': float(min(powers)),
                        'max': float(max(powers)),
                        'avg': float(sum(powers) / len(powers))
                    }
            
            # 处理GPU利用率数据
            if hasattr(monitoring_data, 'gpu_utilization') and monitoring_data.gpu_utilization:
                utils = monitoring_data.gpu_utilization
                metrics['gpu_utilization_stats'] = {
                    'min': float(min(utils)),
                    'max': float(max(utils)),
                    'avg': float(sum(utils) / len(utils))
                }
            elif isinstance(monitoring_data, dict) and 'gpu_utilization' in monitoring_data:
                utils = monitoring_data['gpu_utilization']
                if utils:
                    metrics['gpu_utilization_stats'] = {
                        'min': float(min(utils)),
                        'max': float(max(utils)),
                        'avg': float(sum(utils) / len(utils))
                    }
        
        # 优化效果指标
        metrics['optimization_enabled'] = True
        metrics['memory_optimization_active'] = True
        metrics['performance_optimization_active'] = True
        
        return metrics
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """获取优化报告"""
        if self.optimization_enabled:
            return self.resource_manager.get_optimization_report()
        else:
            return {'optimization_enabled': False}
    
    def cleanup(self):
        """清理资源"""
        if self.optimization_enabled:
            self.resource_manager.cleanup()
        super().cleanup()


# 创建优化版压力测试器实例
optimized_stress_tester = OptimizedStressTest()