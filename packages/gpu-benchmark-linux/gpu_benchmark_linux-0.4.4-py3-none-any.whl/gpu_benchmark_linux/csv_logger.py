"""
CSV数据记录器 - 实时保存详细的GPU监控数据到CSV文件
"""

import os
import csv
import time
import threading
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

from .monitor import GPUMetrics
from .utils import logger


@dataclass
class CSVLoggerConfig:
    """CSV记录器配置"""
    output_dir: str = "gpu_benchmark_linux_results"
    filename_prefix: str = "gpu_metrics"
    auto_flush: bool = True  # 自动刷新到磁盘
    flush_interval: float = 5.0  # 刷新间隔（秒）
    max_buffer_size: int = 100  # 最大缓冲区大小
    include_timestamp_in_filename: bool = True
    custom_fields: Optional[List[str]] = None  # 自定义字段


class CSVLogger:
    """CSV数据记录器"""
    
    def __init__(self, config: Optional[CSVLoggerConfig] = None):
        """初始化CSV记录器"""
        if config is None:
            config = CSVLoggerConfig()
        
        self.config = config
        self.csv_file = None
        self.csv_writer = None
        self.fieldnames = None
        self.buffer = []
        self.lock = threading.Lock()
        self.flush_thread = None
        self.running = False
        
        # 确保输出目录存在
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
        
        # 生成CSV文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if self.config.include_timestamp_in_filename:
            filename = f"{self.config.filename_prefix}_{timestamp}.csv"
        else:
            filename = f"{self.config.filename_prefix}.csv"
        
        self.csv_filepath = Path(self.config.output_dir) / filename
        
        # 定义CSV字段
        self._setup_fieldnames()
    
    def _setup_fieldnames(self):
        """设置CSV字段名"""
        # 基础字段
        self.fieldnames = [
            'timestamp',
            'datetime',
            'device_id',
            'device_name',
            'temperature_c',
            'power_usage_w',
            'power_limit_w',
            'gpu_utilization_percent',
            'memory_utilization_percent',
            'memory_used_mb',
            'memory_total_mb',
            'memory_free_mb',
            'memory_used_percent',
            'fan_speed_percent',
            'clock_graphics_mhz',
            'clock_memory_mhz',
            'clock_sm_mhz',
            'voltage_v'
        ]
        
        # 添加自定义字段
        if self.config.custom_fields:
            self.fieldnames.extend(self.config.custom_fields)
    
    def start_logging(self):
        """开始记录"""
        if self.running:
            logger.warning("CSV记录器已在运行")
            return
        
        try:
            # 打开CSV文件
            self.csv_file = open(self.csv_filepath, 'w', newline='', encoding='utf-8')
            if self.fieldnames:
                self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=self.fieldnames)
                
                # 写入表头
                self.csv_writer.writeheader()
            
            self.running = True
            
            # 启动自动刷新线程
            if self.config.auto_flush:
                self._start_flush_thread()
            
            logger.info(f"CSV记录器已启动，输出文件: {self.csv_filepath}")
            
        except Exception as e:
            logger.error(f"启动CSV记录器失败: {e}")
            self.running = False
    
    def stop_logging(self):
        """停止记录"""
        if not self.running:
            return
        
        self.running = False
        
        # 停止刷新线程
        if self.flush_thread:
            self.flush_thread.join(timeout=5.0)
        
        # 刷新缓冲区
        self._flush_buffer()
        
        # 关闭文件
        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None
            self.csv_writer = None
        
        logger.info(f"CSV记录器已停止，数据已保存到: {self.csv_filepath}")
    
    def _start_flush_thread(self):
        """启动自动刷新线程"""
        def flush_loop():
            while self.running:
                time.sleep(self.config.flush_interval)
                if self.running:
                    self._flush_buffer()
        
        self.flush_thread = threading.Thread(target=flush_loop, daemon=True)
        self.flush_thread.start()
    
    def _flush_buffer(self):
        """刷新缓冲区到文件"""
        with self.lock:
            if self.buffer and self.csv_writer and self.csv_file:
                try:
                    # 写入所有缓冲的数据
                    for row in self.buffer:
                        self.csv_writer.writerow(row)
                    
                    # 刷新到磁盘
                    self.csv_file.flush()
                    os.fsync(self.csv_file.fileno())
                    
                    # 清空缓冲区
                    buffer_size = len(self.buffer)
                    self.buffer.clear()
                    
                    if buffer_size > 0:
                        logger.debug(f"已刷新 {buffer_size} 条记录到CSV文件")
                
                except Exception as e:
                    logger.error(f"刷新CSV缓冲区失败: {e}")
    
    def log_metrics(self, metrics_list: List[GPUMetrics]):
        """记录GPU指标数据"""
        if not self.running:
            return
        
        with self.lock:
            for metrics in metrics_list:
                # 转换为CSV行数据
                row = self._metrics_to_csv_row(metrics)
                self.buffer.append(row)
                
                # 检查缓冲区大小
                if len(self.buffer) >= self.config.max_buffer_size:
                    self._flush_buffer()
    
    def _metrics_to_csv_row(self, metrics: GPUMetrics) -> Dict[str, Any]:
        """将GPU指标转换为CSV行数据"""
        # 计算内存使用百分比
        memory_used_percent = None
        if metrics.memory_used is not None and metrics.memory_total is not None and metrics.memory_total > 0:
            memory_used_percent = (metrics.memory_used / metrics.memory_total) * 100
        
        # 转换内存单位为MB
        memory_used_mb = metrics.memory_used / (1024 * 1024) if metrics.memory_used else None
        memory_total_mb = metrics.memory_total / (1024 * 1024) if metrics.memory_total else None
        memory_free_mb = metrics.memory_free / (1024 * 1024) if metrics.memory_free else None
        
        # 格式化时间戳
        dt = datetime.fromtimestamp(metrics.timestamp)
        datetime_str = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # 保留毫秒
        
        row = {
            'timestamp': metrics.timestamp,
            'datetime': datetime_str,
            'device_id': metrics.device_id,
            'device_name': metrics.name,
            'temperature_c': metrics.temperature,
            'power_usage_w': metrics.power_usage,
            'power_limit_w': metrics.power_limit,
            'gpu_utilization_percent': metrics.gpu_utilization,
            'memory_utilization_percent': metrics.memory_utilization,
            'memory_used_mb': memory_used_mb,
            'memory_total_mb': memory_total_mb,
            'memory_free_mb': memory_free_mb,
            'memory_used_percent': memory_used_percent,
            'fan_speed_percent': metrics.fan_speed,
            'clock_graphics_mhz': metrics.clock_graphics,
            'clock_memory_mhz': metrics.clock_memory,
            'clock_sm_mhz': metrics.clock_sm,
            'voltage_v': metrics.voltage
        }
        
        return row
    
    def log_custom_data(self, custom_data: Dict[str, Any]):
        """记录自定义数据"""
        if not self.running:
            return
        
        with self.lock:
            # 确保fieldnames已初始化
            if self.fieldnames is None:
                self._setup_fieldnames()
            else:    
                # 创建基础行数据
                row: Dict[str, Any] = {field: None for field in self.fieldnames}
            
                # 添加时间戳
                timestamp = time.time()
                dt = datetime.fromtimestamp(timestamp)
                row['timestamp'] = timestamp
                row['datetime'] = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            
                # 添加自定义数据
                if self.fieldnames:
                    for key, value in custom_data.items():
                        if key in self.fieldnames:
                            row[key] = value
                
                self.buffer.append(row)
            
            # 检查缓冲区大小
            if len(self.buffer) >= self.config.max_buffer_size:
                self._flush_buffer()
    
    def get_filepath(self) -> Path:
        """获取CSV文件路径"""
        return self.csv_filepath
    
    def get_record_count(self) -> int:
        """获取已记录的数据条数（估算）"""
        if not self.csv_filepath.exists():
            return 0
        
        try:
            with open(self.csv_filepath, 'r', encoding='utf-8') as f:
                # 减去表头行
                return sum(1 for _ in f) - 1
        except Exception:
            return 0


class EnhancedGPUMonitor:
    """增强的GPU监控器，集成CSV记录功能"""
    
    def __init__(self, monitor, csv_config: Optional[CSVLoggerConfig] = None):
        """初始化增强监控器"""
        self.monitor = monitor
        self.csv_logger = CSVLogger(csv_config)
        self.monitoring = False
        
        # 添加CSV记录回调
        self.monitor.add_callback(self._csv_callback)
    
    def _csv_callback(self, metrics_list: List[GPUMetrics]):
        """CSV记录回调函数"""
        if self.csv_logger.running:
            self.csv_logger.log_metrics(metrics_list)
    
    def start_monitoring(self, interval: float = 1.0, max_history: int = 1000):
        """开始监控（包含CSV记录）"""
        # 启动CSV记录器
        self.csv_logger.start_logging()
        
        # 启动GPU监控
        result = self.monitor.start_monitoring(interval, max_history)
        
        if result:
            self.monitoring = True
            logger.info("增强GPU监控已启动（包含实时CSV记录）")
        
        return result
    
    def stop_monitoring(self):
        """停止监控"""
        if self.monitoring:
            # 停止GPU监控
            self.monitor.stop_monitoring()
            
            # 停止CSV记录器
            self.csv_logger.stop_logging()
            
            self.monitoring = False
            logger.info("增强GPU监控已停止")
    
    def get_csv_filepath(self) -> Path:
        """获取CSV文件路径"""
        return self.csv_logger.get_filepath()
    
    def get_record_count(self) -> int:
        """获取CSV记录数量"""
        return self.csv_logger.get_record_count()
    
    def log_test_event(self, event_type: str, event_data: Dict[str, Any]):
        """记录测试事件"""
        custom_data = {
            'event_type': event_type,
            **event_data
        }
        self.csv_logger.log_custom_data(custom_data)


def create_csv_logger_for_test(test_name: str, output_dir: Optional[str] = None) -> CSVLogger:
    """为特定测试创建CSV记录器"""
    if output_dir is None:
        output_dir = "gpu_benchmark_linux_results"
    
    config = CSVLoggerConfig(
        output_dir=output_dir,
        filename_prefix=f"gpu_metrics_{test_name}",
        auto_flush=True,
        flush_interval=2.0,  # 更频繁的刷新
        max_buffer_size=50,
        include_timestamp_in_filename=True
    )
    
    return CSVLogger(config)


def create_enhanced_monitor(monitor, test_name: str = "stress_test") -> EnhancedGPUMonitor:
    """创建增强监控器"""
    csv_config = CSVLoggerConfig(
        filename_prefix=f"gpu_metrics_{test_name}",
        auto_flush=True,
        flush_interval=1.0,  # 1秒刷新一次
        max_buffer_size=30
    )
    
    return EnhancedGPUMonitor(monitor, csv_config)
