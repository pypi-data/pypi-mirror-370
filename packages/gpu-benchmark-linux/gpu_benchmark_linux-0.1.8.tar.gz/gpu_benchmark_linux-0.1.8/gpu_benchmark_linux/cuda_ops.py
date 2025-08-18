"""
CUDA操作模块 - 封装基础CUDA计算操作
"""

import os
import sys
import time
import numpy as np
from typing import Optional, Tuple, List, Dict, Any
import logging

try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False
    cp = None

try:
    import pycuda.driver as cuda
    import pycuda.autoinit
    from pycuda.compiler import SourceModule
    PYCUDA_AVAILABLE = True
except ImportError:
    PYCUDA_AVAILABLE = False
    cuda = None
    SourceModule = None

from .utils import logger


class CUDAOperations:
    """CUDA计算操作类，提供GPU计算和内存操作功能"""
    
    def __init__(self):
        """初始化CUDA操作环境"""
        self.cupy_available = CUPY_AVAILABLE
        self.pycuda_available = PYCUDA_AVAILABLE
        self.device_count = 0
        self.current_device = 0
        self.device_info = {}
        
        self._initialize_cuda()
    
    def _initialize_cuda(self):
        """初始化CUDA环境"""
        try:
            if self.cupy_available:
                self.device_count = cp.cuda.runtime.getDeviceCount()
                logger.info(f"检测到 {self.device_count} 个CUDA设备")
                
                # 获取设备信息
                for i in range(self.device_count):
                    with cp.cuda.Device(i):
                        props = cp.cuda.runtime.getDeviceProperties(i)
                        self.device_info[i] = {
                            'name': props['name'].decode('utf-8'),
                            'compute_capability': f"{props['major']}.{props['minor']}",
                            'total_memory': props['totalGlobalMem'],
                            'multiprocessor_count': props['multiProcessorCount'],
                            'max_threads_per_block': props['maxThreadsPerBlock'],
                            'max_block_dim': props['maxThreadsDim'],
                            'max_grid_dim': props['maxGridSize']
                        }
                        logger.info(f"设备 {i}: {self.device_info[i]['name']}")
            else:
                logger.warning("CuPy不可用，某些功能将受限")
                
        except Exception as e:
            logger.error(f"初始化CUDA环境失败: {e}")
            self.cupy_available = False
    
    def is_available(self) -> bool:
        """检查CUDA是否可用"""
        return self.cupy_available and self.device_count > 0
    
    def get_device_count(self) -> int:
        """获取CUDA设备数量"""
        return self.device_count
    
    def get_device_info(self, device_id: int = None) -> Dict[str, Any]:
        """获取设备信息"""
        if device_id is None:
            device_id = self.current_device
        return self.device_info.get(device_id, {})
    
    def set_device(self, device_id: int):
        """设置当前设备"""
        if not self.is_available():
            raise RuntimeError("CUDA不可用")
        
        if device_id >= self.device_count:
            raise ValueError(f"设备ID {device_id} 超出范围 (0-{self.device_count-1})")
        
        if self.cupy_available:
            cp.cuda.Device(device_id).use()
            self.current_device = device_id
            logger.info(f"切换到设备 {device_id}")
    
    def get_memory_info(self, device_id: int = None) -> Tuple[int, int]:
        """获取GPU内存信息 (已用内存, 总内存)"""
        if not self.is_available():
            return 0, 0
        
        if device_id is not None:
            original_device = self.current_device
            self.set_device(device_id)
        
        try:
            if self.cupy_available:
                mempool = cp.get_default_memory_pool()
                used_bytes = mempool.used_bytes()
                total_bytes = cp.cuda.runtime.memGetInfo()[1]
                return used_bytes, total_bytes
        except Exception as e:
            logger.error(f"获取内存信息失败: {e}")
            return 0, 0
        finally:
            if device_id is not None:
                self.set_device(original_device)
    
    def matrix_multiply_stress(self, size: int = 4096, iterations: int = 100, 
                             dtype=np.float32) -> Dict[str, Any]:
        """矩阵乘法压力测试"""
        if not self.is_available():
            raise RuntimeError("CUDA不可用")
        
        logger.info(f"开始矩阵乘法压力测试: {size}x{size}, {iterations}次迭代")
        
        try:
            # 创建随机矩阵
            a_cpu = np.random.random((size, size)).astype(dtype)
            b_cpu = np.random.random((size, size)).astype(dtype)
            
            # 传输到GPU
            start_time = time.time()
            a_gpu = cp.asarray(a_cpu)
            b_gpu = cp.asarray(b_cpu)
            transfer_time = time.time() - start_time
            
            # 执行计算
            compute_times = []
            for i in range(iterations):
                cp.cuda.Stream.null.synchronize()  # 同步
                iter_start = time.time()
                
                c_gpu = cp.dot(a_gpu, b_gpu)
                
                cp.cuda.Stream.null.synchronize()  # 同步
                iter_time = time.time() - iter_start
                compute_times.append(iter_time)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"完成 {i + 1}/{iterations} 次迭代")
            
            # 传输回CPU
            start_time = time.time()
            c_cpu = cp.asnumpy(c_gpu)
            transfer_back_time = time.time() - start_time
            
            # 计算统计信息
            total_compute_time = sum(compute_times)
            avg_compute_time = total_compute_time / iterations
            min_compute_time = min(compute_times)
            max_compute_time = max(compute_times)
            
            # 计算GFLOPS
            ops_per_iteration = 2 * size ** 3  # 矩阵乘法的浮点运算数
            gflops = (ops_per_iteration * iterations) / (total_compute_time * 1e9)
            
            results = {
                'matrix_size': size,
                'iterations': iterations,
                'dtype': str(dtype),
                'total_compute_time': total_compute_time,
                'avg_compute_time': avg_compute_time,
                'min_compute_time': min_compute_time,
                'max_compute_time': max_compute_time,
                'transfer_to_gpu_time': transfer_time,
                'transfer_to_cpu_time': transfer_back_time,
                'gflops': gflops,
                'compute_times': compute_times
            }
            
            logger.info(f"矩阵乘法测试完成: {gflops:.2f} GFLOPS")
            return results
            
        except Exception as e:
            logger.error(f"矩阵乘法压力测试失败: {e}")
            raise
    
    def memory_bandwidth_test(self, size_mb: int = 1024, iterations: int = 10) -> Dict[str, Any]:
        """内存带宽测试"""
        if not self.is_available():
            raise RuntimeError("CUDA不可用")
        
        logger.info(f"开始内存带宽测试: {size_mb}MB, {iterations}次迭代")
        
        try:
            # 计算数组大小
            size_bytes = size_mb * 1024 * 1024
            size_elements = size_bytes // 4  # float32
            
            # 创建测试数据
            data_cpu = np.random.random(size_elements).astype(np.float32)
            
            # 测试CPU到GPU传输
            h2d_times = []
            for i in range(iterations):
                start_time = time.time()
                data_gpu = cp.asarray(data_cpu)
                cp.cuda.Stream.null.synchronize()
                h2d_time = time.time() - start_time
                h2d_times.append(h2d_time)
            
            # 测试GPU到CPU传输
            d2h_times = []
            for i in range(iterations):
                start_time = time.time()
                result_cpu = cp.asnumpy(data_gpu)
                d2h_time = time.time() - start_time
                d2h_times.append(d2h_time)
            
            # 测试GPU内存复制
            gpu_copy_times = []
            data_gpu2 = cp.empty_like(data_gpu)
            for i in range(iterations):
                start_time = time.time()
                cp.copyto(data_gpu2, data_gpu)
                cp.cuda.Stream.null.synchronize()
                gpu_copy_time = time.time() - start_time
                gpu_copy_times.append(gpu_copy_time)
            
            # 计算带宽
            avg_h2d_time = sum(h2d_times) / iterations
            avg_d2h_time = sum(d2h_times) / iterations
            avg_gpu_copy_time = sum(gpu_copy_times) / iterations
            
            h2d_bandwidth = size_bytes / (avg_h2d_time * 1e9)  # GB/s
            d2h_bandwidth = size_bytes / (avg_d2h_time * 1e9)  # GB/s
            gpu_bandwidth = size_bytes / (avg_gpu_copy_time * 1e9)  # GB/s
            
            results = {
                'size_mb': size_mb,
                'iterations': iterations,
                'h2d_bandwidth_gbps': h2d_bandwidth,
                'd2h_bandwidth_gbps': d2h_bandwidth,
                'gpu_copy_bandwidth_gbps': gpu_bandwidth,
                'avg_h2d_time': avg_h2d_time,
                'avg_d2h_time': avg_d2h_time,
                'avg_gpu_copy_time': avg_gpu_copy_time,
                'h2d_times': h2d_times,
                'd2h_times': d2h_times,
                'gpu_copy_times': gpu_copy_times
            }
            
            logger.info(f"内存带宽测试完成:")
            logger.info(f"  Host->Device: {h2d_bandwidth:.2f} GB/s")
            logger.info(f"  Device->Host: {d2h_bandwidth:.2f} GB/s")
            logger.info(f"  Device Copy: {gpu_bandwidth:.2f} GB/s")
            
            return results
            
        except Exception as e:
            logger.error(f"内存带宽测试失败: {e}")
            raise
    
    def compute_intensive_test(self, duration: int = 60) -> Dict[str, Any]:
        """计算密集型测试"""
        if not self.is_available():
            raise RuntimeError("CUDA不可用")
        
        logger.info(f"开始计算密集型测试: {duration}秒")
        
        try:
            # 创建大型矩阵进行连续计算
            size = 2048
            a = cp.random.random((size, size), dtype=cp.float32)
            b = cp.random.random((size, size), dtype=cp.float32)
            
            start_time = time.time()
            end_time = start_time + duration
            iteration_count = 0
            compute_times = []
            
            while time.time() < end_time:
                iter_start = time.time()
                
                # 执行多种计算操作
                c = cp.dot(a, b)
                d = cp.sin(c) + cp.cos(c)
                e = cp.exp(d * 0.001)  # 避免溢出
                f = cp.sqrt(cp.abs(e))
                
                # 更新矩阵以保持计算活跃
                a = f[:size, :size]
                
                cp.cuda.Stream.null.synchronize()
                iter_time = time.time() - iter_start
                compute_times.append(iter_time)
                iteration_count += 1
                
                if iteration_count % 10 == 0:
                    elapsed = time.time() - start_time
                    logger.info(f"计算进行中... {elapsed:.1f}s/{duration}s")
            
            total_time = time.time() - start_time
            avg_iter_time = sum(compute_times) / len(compute_times)
            
            results = {
                'duration': duration,
                'actual_duration': total_time,
                'iterations': iteration_count,
                'avg_iteration_time': avg_iter_time,
                'iterations_per_second': iteration_count / total_time,
                'compute_times': compute_times
            }
            
            logger.info(f"计算密集型测试完成: {iteration_count}次迭代, {iteration_count/total_time:.2f} iter/s")
            return results
            
        except Exception as e:
            logger.error(f"计算密集型测试失败: {e}")
            raise
    
    def cleanup(self):
        """清理CUDA资源"""
        try:
            if self.cupy_available:
                # 清理内存池
                mempool = cp.get_default_memory_pool()
                mempool.free_all_blocks()
                logger.info("CUDA资源清理完成")
        except Exception as e:
            logger.warning(f"清理CUDA资源时出错: {e}")


# 全局CUDA操作实例
cuda_ops = CUDAOperations()