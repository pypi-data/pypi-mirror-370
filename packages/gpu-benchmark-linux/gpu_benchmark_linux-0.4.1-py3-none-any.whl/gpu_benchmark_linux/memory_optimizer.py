"""
GPU内存和性能优化模块
提供内存管理、性能优化和资源清理功能
"""

import gc
import time
import logging
import threading
from contextlib import contextmanager
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

import cupy as cp
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class MemoryStats:
    """内存统计信息"""
    gpu_total: int
    gpu_used: int
    gpu_free: int
    cpu_used: float
    cpu_percent: float


class MemoryOptimizer:
    """GPU内存和性能优化器"""
    
    def __init__(self, device_id: int = 0):
        self.device_id = device_id
        self.memory_pool = None
        self.pinned_memory_pool = None
        self._setup_memory_pools()
        
    def _setup_memory_pools(self):
        """设置内存池以提高内存分配效率"""
        try:
            with cp.cuda.Device(self.device_id):
                # 设置GPU内存池
                self.memory_pool = cp.get_default_memory_pool()
                self.pinned_memory_pool = cp.get_default_pinned_memory_pool()
                
                # 预分配一些内存以减少分配开销
                self.memory_pool.set_limit(size=2**30)  # 1GB限制
                logger.info(f"GPU {self.device_id}: 内存池设置完成")
                
        except Exception as e:
            logger.warning(f"内存池设置失败: {e}")
    
    def get_memory_stats(self) -> MemoryStats:
        """获取当前内存使用统计"""
        try:
            with cp.cuda.Device(self.device_id):
                meminfo = cp.cuda.MemoryInfo()
                gpu_total = meminfo.total
                gpu_free = meminfo.free
                gpu_used = gpu_total - gpu_free
                
                # CPU内存统计
                import psutil
                cpu_memory = psutil.virtual_memory()
                
                return MemoryStats(
                    gpu_total=gpu_total,
                    gpu_used=gpu_used,
                    gpu_free=gpu_free,
                    cpu_used=cpu_memory.used,
                    cpu_percent=cpu_memory.percent
                )
        except Exception as e:
            logger.error(f"获取内存统计失败: {e}")
            return MemoryStats(0, 0, 0, 0, 0)
    
    @contextmanager
    def memory_context(self, clear_cache: bool = True):
        """内存管理上下文管理器"""
        initial_stats = self.get_memory_stats()
        logger.debug(f"进入内存上下文 - GPU使用: {initial_stats.gpu_used / 1024**3:.2f}GB")
        
        try:
            yield
        finally:
            if clear_cache:
                self.clear_memory_cache()
            
            final_stats = self.get_memory_stats()
            logger.debug(f"退出内存上下文 - GPU使用: {final_stats.gpu_used / 1024**3:.2f}GB")
    
    def clear_memory_cache(self):
        """清理GPU内存缓存"""
        try:
            with cp.cuda.Device(self.device_id):
                # 清理CuPy内存池
                if self.memory_pool:
                    self.memory_pool.free_all_blocks()
                if self.pinned_memory_pool:
                    self.pinned_memory_pool.free_all_blocks()
                
                # 强制垃圾回收
                gc.collect()
                
                # 同步CUDA设备
                cp.cuda.Stream.null.synchronize()
                
                logger.debug(f"GPU {self.device_id}: 内存缓存已清理")
                
        except Exception as e:
            logger.warning(f"清理内存缓存失败: {e}")
    
    def optimize_for_computation(self, matrix_size: int) -> Dict[str, Any]:
        """根据矩阵大小优化计算参数"""
        stats = self.get_memory_stats()
        available_memory = stats.gpu_free
        
        # 计算最优的块大小和批次大小
        element_size = 4  # float32
        matrix_memory = matrix_size * matrix_size * element_size
        
        # 确保不超过可用内存的80%
        safe_memory = int(available_memory * 0.8)
        max_matrices = safe_memory // matrix_memory
        
        # 计算最优批次大小
        optimal_batch_size = min(max_matrices // 3, 32)  # 保留3个矩阵的空间，最大32
        optimal_batch_size = max(optimal_batch_size, 1)
        
        # 计算最优块大小
        if matrix_size > 4096:
            block_size = 512
        elif matrix_size > 2048:
            block_size = 256
        else:
            block_size = 128
        
        return {
            'batch_size': optimal_batch_size,
            'block_size': block_size,
            'available_memory_gb': available_memory / 1024**3,
            'estimated_memory_per_matrix_gb': matrix_memory / 1024**3
        }


class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self, device_id: int = 0):
        self.device_id = device_id
        self.stream_pool = []
        self.event_pool = []
        self._setup_cuda_streams()
    
    def _setup_cuda_streams(self):
        """设置CUDA流池以支持并发执行"""
        try:
            with cp.cuda.Device(self.device_id):
                # 创建多个CUDA流
                for i in range(4):
                    stream = cp.cuda.Stream(non_blocking=True)
                    self.stream_pool.append(stream)
                
                # 创建事件池用于同步
                for i in range(8):
                    event = cp.cuda.Event()
                    self.event_pool.append(event)
                
                logger.info(f"GPU {self.device_id}: CUDA流池设置完成 ({len(self.stream_pool)} 流)")
                
        except Exception as e:
            logger.warning(f"CUDA流池设置失败: {e}")
    
    def get_stream(self, index: int = 0) -> cp.cuda.Stream:
        """获取CUDA流"""
        if self.stream_pool:
            return self.stream_pool[index % len(self.stream_pool)]
        return cp.cuda.Stream.null
    
    def get_event(self, index: int = 0) -> cp.cuda.Event:
        """获取CUDA事件"""
        if self.event_pool:
            return self.event_pool[index % len(self.event_pool)]
        return cp.cuda.Event()
    
    @contextmanager
    def performance_context(self, stream_index: int = 0):
        """性能优化上下文管理器"""
        stream = self.get_stream(stream_index)
        
        try:
            with stream:
                yield stream
        finally:
            stream.synchronize()
    
    def optimize_matrix_multiplication(self, size: int, dtype=cp.float32) -> Dict[str, Any]:
        """优化矩阵乘法参数"""
        # 根据GPU架构和矩阵大小选择最优算法
        if size >= 4096:
            # 大矩阵使用分块计算
            return {
                'algorithm': 'blocked',
                'block_size': 1024,
                'use_streams': True,
                'dtype': dtype
            }
        elif size >= 1024:
            # 中等矩阵使用标准GEMM
            return {
                'algorithm': 'gemm',
                'block_size': 512,
                'use_streams': False,
                'dtype': dtype
            }
        else:
            # 小矩阵直接计算
            return {
                'algorithm': 'direct',
                'block_size': size,
                'use_streams': False,
                'dtype': dtype
            }
    
    def cleanup(self):
        """清理资源"""
        try:
            # 同步所有流
            for stream in self.stream_pool:
                stream.synchronize()
            
            # 清理事件
            self.event_pool.clear()
            
            logger.debug(f"GPU {self.device_id}: 性能优化器资源已清理")
            
        except Exception as e:
            logger.warning(f"清理性能优化器资源失败: {e}")


class ResourceManager:
    """资源管理器 - 统一管理内存和性能优化"""
    
    def __init__(self, device_id: int = 0):
        self.device_id = device_id
        self.memory_optimizer = MemoryOptimizer(device_id)
        self.performance_optimizer = PerformanceOptimizer(device_id)
        self._monitoring = False
        self._monitor_thread = None
        self._monitor_stats = []
    
    @contextmanager
    def optimized_context(self, matrix_size: int = 1024, stream_index: int = 0):
        """优化的计算上下文"""
        with self.memory_optimizer.memory_context():
            with self.performance_optimizer.performance_context(stream_index) as stream:
                # 获取优化参数
                memory_params = self.memory_optimizer.optimize_for_computation(matrix_size)
                perf_params = self.performance_optimizer.optimize_matrix_multiplication(matrix_size)
                
                yield {
                    'stream': stream,
                    'memory_params': memory_params,
                    'performance_params': perf_params
                }
    
    def start_monitoring(self, interval: float = 1.0):
        """开始资源监控"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_stats = []
        
        def monitor_loop():
            while self._monitoring:
                try:
                    stats = self.memory_optimizer.get_memory_stats()
                    timestamp = time.time()
                    self._monitor_stats.append({
                        'timestamp': timestamp,
                        'gpu_used_gb': stats.gpu_used / 1024**3,
                        'gpu_free_gb': stats.gpu_free / 1024**3,
                        'cpu_percent': stats.cpu_percent
                    })
                    
                    # 保持最近100个记录
                    if len(self._monitor_stats) > 100:
                        self._monitor_stats = self._monitor_stats[-100:]
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"资源监控错误: {e}")
                    break
        
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("资源监控已启动")
    
    def stop_monitoring(self) -> List[Dict[str, Any]]:
        """停止资源监控并返回统计数据"""
        if not self._monitoring:
            return []
        
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
        
        stats = self._monitor_stats.copy()
        self._monitor_stats.clear()
        
        logger.info(f"资源监控已停止，收集了 {len(stats)} 个数据点")
        return stats
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """获取优化报告"""
        current_stats = self.memory_optimizer.get_memory_stats()
        
        return {
            'memory_usage': {
                'gpu_total_gb': current_stats.gpu_total / 1024**3,
                'gpu_used_gb': current_stats.gpu_used / 1024**3,
                'gpu_utilization_percent': (current_stats.gpu_used / current_stats.gpu_total) * 100,
                'cpu_memory_percent': current_stats.cpu_percent
            },
            'optimization_status': {
                'memory_pools_active': self.memory_optimizer.memory_pool is not None,
                'cuda_streams_count': len(self.performance_optimizer.stream_pool),
                'monitoring_active': self._monitoring
            },
            'recommendations': self._generate_recommendations(current_stats)
        }
    
    def _generate_recommendations(self, stats: MemoryStats) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        gpu_utilization = (stats.gpu_used / stats.gpu_total) * 100 if stats.gpu_total > 0 else 0
        
        if gpu_utilization > 90:
            recommendations.append("GPU内存使用率过高，建议减小批次大小或矩阵尺寸")
        elif gpu_utilization < 30:
            recommendations.append("GPU内存使用率较低，可以增加批次大小以提高性能")
        
        if stats.cpu_percent > 80:
            recommendations.append("CPU内存使用率较高，建议关闭不必要的程序")
        
        if not self.memory_optimizer.memory_pool:
            recommendations.append("建议启用内存池以提高内存分配效率")
        
        if len(self.performance_optimizer.stream_pool) == 0:
            recommendations.append("建议启用CUDA流以支持并发计算")
        
        return recommendations
    
    def cleanup(self):
        """清理所有资源"""
        self.stop_monitoring()
        self.memory_optimizer.clear_memory_cache()
        self.performance_optimizer.cleanup()
        logger.info(f"GPU {self.device_id}: 资源管理器已清理")