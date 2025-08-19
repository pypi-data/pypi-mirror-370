"""
GPU监控模块 - 提供GPU硬件监控功能
"""

import os
import sys
import time
import threading
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import json

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    try:
        import nvidia_ml_py3 as pynvml
        PYNVML_AVAILABLE = True
    except ImportError:
        PYNVML_AVAILABLE = False
        pynvml = None

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

from .utils import logger


@dataclass
class GPUMetrics:
    """GPU指标数据类"""
    timestamp: float
    device_id: int
    name: str
    temperature: Optional[float] = None
    power_usage: Optional[float] = None
    power_limit: Optional[float] = None
    gpu_utilization: Optional[float] = None
    memory_utilization: Optional[float] = None
    memory_used: Optional[int] = None
    memory_total: Optional[int] = None
    memory_free: Optional[int] = None
    fan_speed: Optional[float] = None
    clock_graphics: Optional[int] = None
    clock_memory: Optional[int] = None
    clock_sm: Optional[int] = None
    voltage: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'timestamp': self.timestamp,
            'device_id': self.device_id,
            'name': self.name,
            'temperature': self.temperature,
            'power_usage': self.power_usage,
            'power_limit': self.power_limit,
            'gpu_utilization': self.gpu_utilization,
            'memory_utilization': self.memory_utilization,
            'memory_used': self.memory_used,
            'memory_total': self.memory_total,
            'memory_free': self.memory_free,
            'fan_speed': self.fan_speed,
            'clock_graphics': self.clock_graphics,
            'clock_memory': self.clock_memory,
            'clock_sm': self.clock_sm,
            'voltage': self.voltage
        }


class GPUMonitor:
    """GPU监控类，提供实时GPU硬件监控功能"""
    
    def __init__(self):
        """初始化GPU监控器"""
        self.pynvml_available = PYNVML_AVAILABLE
        self.psutil_available = PSUTIL_AVAILABLE
        self.device_count = 0
        self.device_handles = {}
        self.monitoring = False
        self.monitor_thread = None
        self.metrics_history = []
        self.callbacks = []
        
        self._initialize_nvml()
    
    def _initialize_nvml(self):
        """初始化NVML"""
        if not self.pynvml_available:
            logger.warning("NVML不可用，GPU监控功能将受限")
            return
        
        try:
            pynvml.nvmlInit()
            self.device_count = pynvml.nvmlDeviceGetCount()
            logger.info(f"NVML初始化成功，检测到 {self.device_count} 个GPU设备")
            
            # 获取设备句柄
            for i in range(self.device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                self.device_handles[i] = handle
                
                # 获取设备名称
                name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes):
                    name = name.decode('utf-8')
                logger.info(f"设备 {i}: {name}")
                
        except Exception as e:
            logger.error(f"初始化NVML失败: {e}")
            self.pynvml_available = False
    
    def is_available(self) -> bool:
        """检查监控功能是否可用"""
        return self.pynvml_available and self.device_count > 0
    
    def get_device_count(self) -> int:
        """获取GPU设备数量"""
        return self.device_count
    
    def get_device_info(self, device_id: int) -> Dict[str, Any]:
        """获取设备基本信息"""
        if not self.is_available() or device_id not in self.device_handles:
            return {}
        
        try:
            handle = self.device_handles[device_id]
            
            # 基本信息
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            
            # 内存信息
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            # 计算能力
            major, minor = pynvml.nvmlDeviceGetCudaComputeCapability(handle)
            
            # 功耗限制
            try:
                power_limit = pynvml.nvmlDeviceGetPowerManagementLimitConstraints(handle)[1] / 1000.0
            except:
                power_limit = None
            
            # 最大时钟频率
            try:
                max_graphics_clock = pynvml.nvmlDeviceGetMaxClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS)
                max_memory_clock = pynvml.nvmlDeviceGetMaxClockInfo(handle, pynvml.NVML_CLOCK_MEM)
            except:
                max_graphics_clock = None
                max_memory_clock = None
            
            info = {
                'device_id': device_id,
                'name': name,
                'compute_capability': f"{major}.{minor}",
                'memory_total': mem_info.total,
                'power_limit': power_limit,
                'max_graphics_clock': max_graphics_clock,
                'max_memory_clock': max_memory_clock
            }
            
            return info
            
        except Exception as e:
            logger.error(f"获取设备 {device_id} 信息失败: {e}")
            return {}
    
    def get_current_metrics(self, device_id: int) -> Optional[GPUMetrics]:
        """获取当前GPU指标"""
        if not self.is_available() or device_id not in self.device_handles:
            return None
        
        try:
            handle = self.device_handles[device_id]
            timestamp = time.time()
            
            # 设备名称
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            
            metrics = GPUMetrics(
                timestamp=timestamp,
                device_id=device_id,
                name=name
            )
            
            # 温度
            try:
                metrics.temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            except:
                pass
            
            # 功耗
            try:
                metrics.power_usage = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # 转换为瓦特
            except:
                pass
            
            try:
                metrics.power_limit = pynvml.nvmlDeviceGetPowerManagementLimitConstraints(handle)[1] / 1000.0
            except:
                pass
            
            # 利用率
            try:
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                metrics.gpu_utilization = util.gpu
                metrics.memory_utilization = util.memory
            except:
                pass
            
            # 内存信息
            try:
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                metrics.memory_used = mem_info.used
                metrics.memory_total = mem_info.total
                metrics.memory_free = mem_info.free
            except:
                pass
            
            # 风扇转速
            try:
                metrics.fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
            except:
                pass
            
            # 时钟频率
            try:
                metrics.clock_graphics = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS)
            except:
                pass
            
            try:
                metrics.clock_memory = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM)
            except:
                pass
            
            try:
                metrics.clock_sm = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_SM)
            except:
                pass
            
            return metrics
            
        except Exception as e:
            logger.error(f"获取设备 {device_id} 指标失败: {e}")
            return None
    
    def get_all_metrics(self) -> List[GPUMetrics]:
        """获取所有GPU的当前指标"""
        metrics_list = []
        for device_id in range(self.device_count):
            metrics = self.get_current_metrics(device_id)
            if metrics:
                metrics_list.append(metrics)
        return metrics_list
    
    def add_callback(self, callback: Callable[[List[GPUMetrics]], None]):
        """添加监控回调函数"""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[List[GPUMetrics]], None]):
        """移除监控回调函数"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def start_monitoring(self, interval: float = 1.0, max_history: int = 1000):
        """开始监控"""
        if not self.is_available():
            logger.error("GPU监控不可用")
            return False
        
        if self.monitoring:
            logger.warning("监控已在运行")
            return True
        
        self.monitoring = True
        self.metrics_history = []
        
        def monitor_loop():
            logger.info(f"开始GPU监控，采样间隔: {interval}秒")
            
            while self.monitoring:
                try:
                    # 获取所有设备指标
                    current_metrics = self.get_all_metrics()
                    
                    if current_metrics:
                        # 添加到历史记录
                        self.metrics_history.extend(current_metrics)
                        
                        # 限制历史记录长度
                        if len(self.metrics_history) > max_history:
                            self.metrics_history = self.metrics_history[-max_history:]
                        
                        # 调用回调函数
                        for callback in self.callbacks:
                            try:
                                callback(current_metrics)
                            except Exception as e:
                                logger.error(f"监控回调函数执行失败: {e}")
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"监控循环出错: {e}")
                    time.sleep(interval)
            
            logger.info("GPU监控已停止")
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        return True
    
    def stop_monitoring(self):
        """停止监控"""
        if self.monitoring:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5.0)
            logger.info("GPU监控已停止")
    
    def get_metrics_history(self) -> List[GPUMetrics]:
        """获取监控历史数据"""
        return self.metrics_history.copy()
    
    def get_statistics(self, device_id: int = None, 
                      start_time: float = None, 
                      end_time: float = None) -> Dict[str, Any]:
        """获取统计信息"""
        # 筛选数据
        filtered_metrics = []
        for metrics in self.metrics_history:
            if device_id is not None and metrics.device_id != device_id:
                continue
            if start_time is not None and metrics.timestamp < start_time:
                continue
            if end_time is not None and metrics.timestamp > end_time:
                continue
            filtered_metrics.append(metrics)
        
        if not filtered_metrics:
            return {}
        
        # 计算统计信息
        stats = {
            'count': len(filtered_metrics),
            'start_time': min(m.timestamp for m in filtered_metrics),
            'end_time': max(m.timestamp for m in filtered_metrics),
            'duration': max(m.timestamp for m in filtered_metrics) - min(m.timestamp for m in filtered_metrics)
        }
        
        # 温度统计
        temps = [m.temperature for m in filtered_metrics if m.temperature is not None]
        if temps:
            stats['temperature'] = {
                'min': min(temps),
                'max': max(temps),
                'avg': sum(temps) / len(temps),
                'current': temps[-1]
            }
        
        # 功耗统计
        powers = [m.power_usage for m in filtered_metrics if m.power_usage is not None]
        if powers:
            stats['power_usage'] = {
                'min': min(powers),
                'max': max(powers),
                'avg': sum(powers) / len(powers),
                'current': powers[-1]
            }
        
        # GPU利用率统计
        gpu_utils = [m.gpu_utilization for m in filtered_metrics if m.gpu_utilization is not None]
        if gpu_utils:
            stats['gpu_utilization'] = {
                'min': min(gpu_utils),
                'max': max(gpu_utils),
                'avg': sum(gpu_utils) / len(gpu_utils),
                'current': gpu_utils[-1]
            }
        
        # 内存利用率统计
        mem_utils = [m.memory_utilization for m in filtered_metrics if m.memory_utilization is not None]
        if mem_utils:
            stats['memory_utilization'] = {
                'min': min(mem_utils),
                'max': max(mem_utils),
                'avg': sum(mem_utils) / len(mem_utils),
                'current': mem_utils[-1]
            }
        
        return stats
    
    def export_metrics(self, filename: str, format: str = 'json'):
        """导出监控数据"""
        try:
            if format.lower() == 'json':
                data = [metrics.to_dict() for metrics in self.metrics_history]
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif format.lower() == 'csv':
                import csv
                if self.metrics_history:
                    fieldnames = list(self.metrics_history[0].to_dict().keys())
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        for metrics in self.metrics_history:
                            writer.writerow(metrics.to_dict())
            else:
                raise ValueError(f"不支持的格式: {format}")
            
            logger.info(f"监控数据已导出到: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"导出监控数据失败: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        self.stop_monitoring()
        try:
            if self.pynvml_available:
                pynvml.nvmlShutdown()
                logger.info("NVML资源清理完成")
        except Exception as e:
            logger.warning(f"清理NVML资源时出错: {e}")


# 监控回调函数示例
def log_metrics_callback(metrics_list: List[GPUMetrics]):
    """日志记录回调函数"""
    for metrics in metrics_list:
        logger.info(f"GPU {metrics.device_id}: "
                   f"温度={metrics.temperature}°C, "
                   f"功耗={metrics.power_usage}W, "
                   f"GPU利用率={metrics.gpu_utilization}%, "
                   f"内存利用率={metrics.memory_utilization}%")


def alert_callback(metrics_list: List[GPUMetrics], 
                  temp_threshold: float = 85.0,
                  power_threshold: float = None):
    """告警回调函数"""
    for metrics in metrics_list:
        # 温度告警
        if metrics.temperature and metrics.temperature > temp_threshold:
            logger.warning(f"GPU {metrics.device_id} 温度过高: {metrics.temperature}°C")
        
        # 功耗告警
        if (power_threshold and metrics.power_usage and 
            metrics.power_usage > power_threshold):
            logger.warning(f"GPU {metrics.device_id} 功耗过高: {metrics.power_usage}W")


# 全局GPU监控实例
gpu_monitor = GPUMonitor()