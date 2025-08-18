"""
异常处理模块 - 定义自定义异常类和错误处理机制
"""

import sys
import traceback
from typing import Optional, Dict, Any, Callable
from enum import Enum
import logging

from .utils import logger


class ErrorLevel(Enum):
    """错误级别枚举"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class GPUBenchmarkError(Exception):
    """GPU基准测试基础异常类"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        self.level = ErrorLevel.ERROR
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code,
            'level': self.level.value,
            'details': self.details
        }


class CUDAError(GPUBenchmarkError):
    """CUDA相关错误"""
    
    def __init__(self, message: str, cuda_error_code: Optional[int] = None, 
                 device_id: Optional[int] = None):
        super().__init__(message, "CUDA_ERROR")
        self.cuda_error_code = cuda_error_code
        self.device_id = device_id
        self.level = ErrorLevel.ERROR
        
        if cuda_error_code:
            self.details['cuda_error_code'] = cuda_error_code
        if device_id is not None:
            self.details['device_id'] = device_id


class CUDAInitializationError(CUDAError):
    """CUDA初始化错误"""
    
    def __init__(self, message: str = "CUDA初始化失败"):
        super().__init__(message, error_code="CUDA_INIT_ERROR")
        self.level = ErrorLevel.CRITICAL


class CUDADeviceError(CUDAError):
    """CUDA设备错误"""
    
    def __init__(self, message: str, device_id: int):
        super().__init__(message, error_code="CUDA_DEVICE_ERROR", device_id=device_id)


class CUDAMemoryError(CUDAError):
    """CUDA内存错误"""
    
    def __init__(self, message: str, device_id: Optional[int] = None, 
                 requested_bytes: Optional[int] = None, available_bytes: Optional[int] = None):
        super().__init__(message, error_code="CUDA_MEMORY_ERROR", device_id=device_id)
        
        if requested_bytes:
            self.details['requested_bytes'] = requested_bytes
        if available_bytes:
            self.details['available_bytes'] = available_bytes


class MonitoringError(GPUBenchmarkError):
    """监控相关错误"""
    
    def __init__(self, message: str, device_id: Optional[int] = None):
        super().__init__(message, "MONITORING_ERROR")
        self.device_id = device_id
        
        if device_id is not None:
            self.details['device_id'] = device_id


class NVMLError(MonitoringError):
    """NVML相关错误"""
    
    def __init__(self, message: str, nvml_error_code: Optional[int] = None, 
                 device_id: Optional[int] = None):
        super().__init__(message, device_id)
        self.error_code = "NVML_ERROR"
        self.nvml_error_code = nvml_error_code
        
        if nvml_error_code:
            self.details['nvml_error_code'] = nvml_error_code


class StressTestError(GPUBenchmarkError):
    """压力测试相关错误"""
    
    def __init__(self, message: str, test_type: Optional[str] = None, 
                 device_id: Optional[int] = None):
        super().__init__(message, "STRESS_TEST_ERROR")
        self.test_type = test_type
        self.device_id = device_id
        
        if test_type:
            self.details['test_type'] = test_type
        if device_id is not None:
            self.details['device_id'] = device_id


class ConfigurationError(GPUBenchmarkError):
    """配置相关错误"""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message, "CONFIGURATION_ERROR")
        self.config_key = config_key
        self.level = ErrorLevel.WARNING
        
        if config_key:
            self.details['config_key'] = config_key


class DependencyError(GPUBenchmarkError):
    """依赖相关错误"""
    
    def __init__(self, message: str, dependency_name: Optional[str] = None):
        super().__init__(message, "DEPENDENCY_ERROR")
        self.dependency_name = dependency_name
        self.level = ErrorLevel.CRITICAL
        
        if dependency_name:
            self.details['dependency_name'] = dependency_name


class ReportGenerationError(GPUBenchmarkError):
    """报告生成相关错误"""
    
    def __init__(self, message: str, report_format: Optional[str] = None):
        super().__init__(message, "REPORT_GENERATION_ERROR")
        self.report_format = report_format
        self.level = ErrorLevel.WARNING
        
        if report_format:
            self.details['report_format'] = report_format


class SafetyLimitError(GPUBenchmarkError):
    """安全限制错误"""
    
    def __init__(self, message: str, limit_type: str, current_value: float, 
                 limit_value: float, device_id: Optional[int] = None):
        super().__init__(message, "SAFETY_LIMIT_ERROR")
        self.limit_type = limit_type
        self.current_value = current_value
        self.limit_value = limit_value
        self.device_id = device_id
        self.level = ErrorLevel.CRITICAL
        
        self.details.update({
            'limit_type': limit_type,
            'current_value': current_value,
            'limit_value': limit_value
        })
        
        if device_id is not None:
            self.details['device_id'] = device_id


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self):
        self.error_callbacks: Dict[str, list] = {}
        self.global_callbacks: list = []
    
    def register_callback(self, error_type: str, callback: Callable[[GPUBenchmarkError], None]):
        """注册错误回调函数"""
        if error_type not in self.error_callbacks:
            self.error_callbacks[error_type] = []
        self.error_callbacks[error_type].append(callback)
    
    def register_global_callback(self, callback: Callable[[GPUBenchmarkError], None]):
        """注册全局错误回调函数"""
        self.global_callbacks.append(callback)
    
    def handle_error(self, error: GPUBenchmarkError):
        """处理错误"""
        # 记录错误日志
        self._log_error(error)
        
        # 调用特定类型的回调函数
        error_type = error.__class__.__name__
        if error_type in self.error_callbacks:
            for callback in self.error_callbacks[error_type]:
                try:
                    callback(error)
                except Exception as e:
                    logger.error(f"错误回调函数执行失败: {e}")
        
        # 调用全局回调函数
        for callback in self.global_callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.error(f"全局错误回调函数执行失败: {e}")
    
    def _log_error(self, error: GPUBenchmarkError):
        """记录错误日志"""
        log_message = f"[{error.error_code}] {error.message}"
        
        if error.details:
            details_str = ", ".join([f"{k}={v}" for k, v in error.details.items()])
            log_message += f" (详情: {details_str})"
        
        if error.level == ErrorLevel.INFO:
            logger.info(log_message)
        elif error.level == ErrorLevel.WARNING:
            logger.warning(log_message)
        elif error.level == ErrorLevel.ERROR:
            logger.error(log_message)
        elif error.level == ErrorLevel.CRITICAL:
            logger.critical(log_message)
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """处理未捕获的异常"""
        if issubclass(exc_type, GPUBenchmarkError):
            self.handle_error(exc_value)
        else:
            # 转换为通用错误
            error_message = f"未处理的异常: {exc_value}"
            error = GPUBenchmarkError(
                message=error_message,
                error_code="UNHANDLED_EXCEPTION",
                details={
                    'exception_type': exc_type.__name__,
                    'traceback': ''.join(traceback.format_tb(exc_traceback))
                }
            )
            error.level = ErrorLevel.CRITICAL
            self.handle_error(error)


def safe_execute(func: Callable, *args, error_handler: Optional[ErrorHandler] = None, 
                default_return=None, **kwargs):
    """安全执行函数，捕获并处理异常"""
    try:
        return func(*args, **kwargs)
    except GPUBenchmarkError as e:
        if error_handler:
            error_handler.handle_error(e)
        else:
            logger.error(f"GPU基准测试错误: {e.message}")
        return default_return
    except Exception as e:
        # 转换为通用错误
        gpu_error = GPUBenchmarkError(
            message=f"执行函数 {func.__name__} 时发生错误: {str(e)}",
            error_code="FUNCTION_EXECUTION_ERROR",
            details={
                'function_name': func.__name__,
                'exception_type': type(e).__name__,
                'traceback': traceback.format_exc()
            }
        )
        
        if error_handler:
            error_handler.handle_error(gpu_error)
        else:
            logger.error(f"函数执行错误: {gpu_error.message}")
        
        return default_return


def validate_cuda_environment():
    """验证CUDA环境"""
    try:
        import cupy as cp
        
        # 检查CUDA设备数量
        device_count = cp.cuda.runtime.getDeviceCount()
        if device_count == 0:
            raise CUDAInitializationError("未检测到CUDA设备")
        
        # 检查每个设备
        for i in range(device_count):
            try:
                with cp.cuda.Device(i):
                    # 尝试分配少量内存
                    test_array = cp.zeros(1024, dtype=cp.float32)
                    del test_array
            except Exception as e:
                raise CUDADeviceError(f"设备 {i} 不可用: {str(e)}", device_id=i)
        
        return True
        
    except ImportError:
        raise DependencyError("CuPy未安装或不可用", dependency_name="cupy")
    except Exception as e:
        if isinstance(e, GPUBenchmarkError):
            raise
        else:
            raise CUDAInitializationError(f"CUDA环境验证失败: {str(e)}")


def validate_monitoring_environment():
    """验证监控环境"""
    try:
        import pynvml
        pynvml.nvmlInit()
        
        device_count = pynvml.nvmlDeviceGetCount()
        if device_count == 0:
            raise MonitoringError("未检测到可监控的GPU设备")
        
        # 测试获取设备信息
        for i in range(device_count):
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                pynvml.nvmlDeviceGetName(handle)
            except Exception as e:
                raise NVMLError(f"无法获取设备 {i} 信息: {str(e)}", device_id=i)
        
        return True
        
    except ImportError:
        try:
            import nvidia_ml_py3 as pynvml
            return validate_monitoring_environment()  # 递归调用使用nvidia_ml_py3
        except ImportError:
            raise DependencyError("NVML库未安装或不可用", dependency_name="pynvml")
    except Exception as e:
        if isinstance(e, GPUBenchmarkError):
            raise
        else:
            raise MonitoringError(f"监控环境验证失败: {str(e)}")


# 全局错误处理器实例
global_error_handler = ErrorHandler()


# 默认错误回调函数
def default_cuda_error_callback(error: CUDAError):
    """默认CUDA错误回调"""
    if error.level == ErrorLevel.CRITICAL:
        logger.critical("检测到严重CUDA错误，建议检查GPU驱动和CUDA安装")


def default_safety_limit_callback(error: SafetyLimitError):
    """默认安全限制错误回调"""
    logger.critical(f"GPU安全限制触发: {error.limit_type} = {error.current_value} > {error.limit_value}")
    logger.critical("为保护硬件，测试已停止")


def default_dependency_error_callback(error: DependencyError):
    """默认依赖错误回调"""
    logger.critical(f"缺少必要依赖: {error.dependency_name}")
    logger.critical("请安装所需依赖后重试")


# 注册默认回调函数
global_error_handler.register_callback("CUDAError", default_cuda_error_callback)
global_error_handler.register_callback("SafetyLimitError", default_safety_limit_callback)
global_error_handler.register_callback("DependencyError", default_dependency_error_callback)


# 设置全局异常处理器
def setup_global_exception_handler():
    """设置全局异常处理器"""
    sys.excepthook = global_error_handler.handle_exception


# 上下文管理器
class ErrorContext:
    """错误处理上下文管理器"""
    
    def __init__(self, error_handler: Optional[ErrorHandler] = None, 
                 suppress_errors: bool = False):
        self.error_handler = error_handler or global_error_handler
        self.suppress_errors = suppress_errors
        self.errors = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            if issubclass(exc_type, GPUBenchmarkError):
                self.errors.append(exc_value)
                self.error_handler.handle_error(exc_value)
            else:
                # 转换为通用错误
                error = GPUBenchmarkError(
                    message=f"上下文中发生异常: {exc_value}",
                    error_code="CONTEXT_EXCEPTION",
                    details={
                        'exception_type': exc_type.__name__,
                        'traceback': traceback.format_exc() if traceback else None
                    }
                )
                self.errors.append(error)
                self.error_handler.handle_error(error)
            
            return self.suppress_errors
        
        return False
    
    def get_errors(self):
        """获取收集的错误"""
        return self.errors.copy()