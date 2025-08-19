"""
GPU型号配置文件 - 为不同GPU型号提供优化的测试配置
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from .stress_test import StressTestConfig


@dataclass
class GPUProfile:
    """GPU型号配置文件"""
    name: str  # GPU型号名称
    compute_capability: str  # 计算能力版本
    memory_gb: int  # 显存大小(GB)
    memory_bandwidth_gbps: int  # 内存带宽(GB/s)
    cuda_cores: int  # CUDA核心数
    tensor_cores: Optional[int] = None  # Tensor核心数
    base_clock_mhz: int = 1000  # 基础时钟频率
    boost_clock_mhz: int = 1500  # 加速时钟频率
    tdp_watts: int = 250  # 热设计功耗
    
    # 测试配置参数
    recommended_matrix_size: int = 4096  # 推荐矩阵大小
    memory_usage_ratio: float = 0.8  # 内存使用比例
    temperature_limit: float = 83.0  # 温度限制
    power_limit_ratio: float = 0.95  # 功耗限制比例
    test_duration_short: int = 60  # 短测试时长
    test_duration_medium: int = 300  # 中等测试时长
    test_duration_long: int = 1800  # 长测试时长
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


class GPUProfileManager:
    """GPU配置管理器"""
    
    def __init__(self):
        self.profiles = self._initialize_profiles()
    
    def _initialize_profiles(self) -> Dict[str, GPUProfile]:
        """初始化GPU配置文件"""
        profiles = {}
        
        # NVIDIA Tesla T4
        profiles['T4'] = GPUProfile(
            name='Tesla T4',
            compute_capability='7.5',
            memory_gb=16,
            memory_bandwidth_gbps=320,
            cuda_cores=2560,
            tensor_cores=320,
            base_clock_mhz=585,
            boost_clock_mhz=1590,
            tdp_watts=70,
            recommended_matrix_size=2048,  # T4适合较小矩阵
            memory_usage_ratio=0.85,
            temperature_limit=80.0,
            power_limit_ratio=0.9,
            test_duration_short=60,
            test_duration_medium=300,
            test_duration_long=1200
        )
        
        # NVIDIA A10
        profiles['A10'] = GPUProfile(
            name='A10',
            compute_capability='8.6',
            memory_gb=24,
            memory_bandwidth_gbps=600,
            cuda_cores=9216,
            tensor_cores=288,
            base_clock_mhz=885,
            boost_clock_mhz=1695,
            tdp_watts=150,
            recommended_matrix_size=4096,
            memory_usage_ratio=0.8,
            temperature_limit=83.0,
            power_limit_ratio=0.95,
            test_duration_short=90,
            test_duration_medium=450,
            test_duration_long=1800
        )
        
        # NVIDIA A100 40GB
        profiles['A100-40GB'] = GPUProfile(
            name='A100-40GB',
            compute_capability='8.0',
            memory_gb=40,
            memory_bandwidth_gbps=1555,
            cuda_cores=6912,
            tensor_cores=432,
            base_clock_mhz=765,
            boost_clock_mhz=1410,
            tdp_watts=400,
            recommended_matrix_size=8192,  # A100适合大矩阵
            memory_usage_ratio=0.9,
            temperature_limit=85.0,
            power_limit_ratio=0.98,
            test_duration_short=120,
            test_duration_medium=600,
            test_duration_long=3600
        )
        
        # NVIDIA A100 80GB
        profiles['A100-80GB'] = GPUProfile(
            name='A100-80GB',
            compute_capability='8.0',
            memory_gb=80,
            memory_bandwidth_gbps=1935,
            cuda_cores=6912,
            tensor_cores=432,
            base_clock_mhz=765,
            boost_clock_mhz=1410,
            tdp_watts=400,
            recommended_matrix_size=8192,
            memory_usage_ratio=0.9,
            temperature_limit=85.0,
            power_limit_ratio=0.98,
            test_duration_short=120,
            test_duration_medium=600,
            test_duration_long=3600
        )
        
        # NVIDIA V100
        profiles['V100'] = GPUProfile(
            name='V100',
            compute_capability='7.0',
            memory_gb=32,
            memory_bandwidth_gbps=900,
            cuda_cores=5120,
            tensor_cores=640,
            base_clock_mhz=1245,
            boost_clock_mhz=1380,
            tdp_watts=300,
            recommended_matrix_size=6144,
            memory_usage_ratio=0.85,
            temperature_limit=84.0,
            power_limit_ratio=0.95,
            test_duration_short=90,
            test_duration_medium=450,
            test_duration_long=2400
        )
        
        # NVIDIA L40
        profiles['L40'] = GPUProfile(
            name='L40',
            compute_capability='8.9',
            memory_gb=48,
            memory_bandwidth_gbps=864,
            cuda_cores=18176,
            tensor_cores=568,
            base_clock_mhz=735,
            boost_clock_mhz=2520,
            tdp_watts=300,
            recommended_matrix_size=6144,
            memory_usage_ratio=0.85,
            temperature_limit=83.0,
            power_limit_ratio=0.95,
            test_duration_short=90,
            test_duration_medium=450,
            test_duration_long=2400
        )
        
        # NVIDIA H20 (假设规格，实际可能需要调整)
        profiles['H20'] = GPUProfile(
            name='H20',
            compute_capability='9.0',
            memory_gb=96,
            memory_bandwidth_gbps=4000,
            cuda_cores=16896,
            tensor_cores=528,
            base_clock_mhz=1200,
            boost_clock_mhz=1980,
            tdp_watts=700,
            recommended_matrix_size=8192,
            memory_usage_ratio=0.9,
            temperature_limit=89.0,
            power_limit_ratio=0.98,
            test_duration_short=120,
            test_duration_medium=600,
            test_duration_long=3600
        )
        
        return profiles
    
    def get_profile(self, gpu_name: str) -> Optional[GPUProfile]:
        """获取GPU配置文件"""
        # 支持模糊匹配
        gpu_name_upper = gpu_name.upper()
        
        # 直接匹配
        if gpu_name_upper in self.profiles:
            return self.profiles[gpu_name_upper]
        
        # 模糊匹配
        for key, profile in self.profiles.items():
            if gpu_name_upper in key or key in gpu_name_upper:
                return profile
        
        return None
    
    def list_profiles(self) -> List[str]:
        """列出所有可用的GPU配置"""
        return list(self.profiles.keys())
    
    def get_profile_info(self, gpu_name: str) -> Optional[Dict[str, Any]]:
        """获取GPU配置信息"""
        profile = self.get_profile(gpu_name)
        return profile.to_dict() if profile else None
    
    def create_stress_config(self, 
                           gpu_name: str, 
                           test_type: str = 'medium',
                           device_ids: Optional[List[int]] = None,
                           custom_params: Optional[Dict[str, Any]] = None) -> Optional[StressTestConfig]:
        """根据GPU型号创建压力测试配置"""
        profile = self.get_profile(gpu_name)
        if not profile:
            return None
        
        # 根据测试类型选择持续时间
        duration_map = {
            'short': profile.test_duration_short,
            'medium': profile.test_duration_medium,
            'long': profile.test_duration_long
        }
        duration = duration_map.get(test_type, profile.test_duration_medium)
        
        # 创建基础配置
        config = StressTestConfig(
            duration=duration,
            device_ids=device_ids or [],
            matrix_size=profile.recommended_matrix_size,
            memory_usage_ratio=profile.memory_usage_ratio,
            test_types=['matrix_multiply', 'compute_intensive', 'memory_bandwidth'],
            monitor_interval=1.0,
            temperature_limit=profile.temperature_limit,
            power_limit_ratio=profile.power_limit_ratio,
            auto_stop_on_limit=True
        )
        
        # 应用自定义参数
        if custom_params:
            for key, value in custom_params.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        return config
    
    def create_comparison_configs(self, 
                                gpu_names: List[str], 
                                test_type: str = 'medium',
                                comparison_type: str = 'horizontal') -> Dict[str, StressTestConfig]:
        """创建用于比较的测试配置
        
        Args:
            gpu_names: GPU型号列表
            test_type: 测试类型 (short/medium/long)
            comparison_type: 比较类型 (horizontal/vertical)
                - horizontal: 横向比较，使用统一参数
                - vertical: 纵向比较，使用各自优化参数
        """
        configs = {}
        
        if comparison_type == 'horizontal':
            # 横向比较：使用统一的测试参数
            base_config = {
                'matrix_size': 4096,
                'memory_usage_ratio': 0.8,
                'temperature_limit': 85.0,
                'test_types': ['matrix_multiply', 'compute_intensive']
            }
            
            for gpu_name in gpu_names:
                config = self.create_stress_config(
                    gpu_name, 
                    test_type, 
                    custom_params=base_config
                )
                if config:
                    configs[gpu_name] = config
        
        else:  # vertical comparison
            # 纵向比较：使用各自优化的参数
            for gpu_name in gpu_names:
                config = self.create_stress_config(gpu_name, test_type)
                if config:
                    configs[gpu_name] = config
        
        return configs
    
    def get_multi_gpu_config(self, 
                           gpu_name: str, 
                           gpu_count: int,
                           test_type: str = 'medium') -> Optional[StressTestConfig]:
        """获取多GPU配置"""
        config = self.create_stress_config(gpu_name, test_type)
        if not config:
            return None
        
        # 设置多GPU设备ID
        config.device_ids = list(range(gpu_count))
        
        # 根据GPU数量调整参数
        if gpu_count >= 2:
            # 多GPU时可以使用更大的矩阵
            profile = self.get_profile(gpu_name)
            if profile:
                config.matrix_size = min(8192, profile.recommended_matrix_size * 2)
                # 多GPU时降低单卡内存使用率，避免冲突
                config.memory_usage_ratio = max(0.6, profile.memory_usage_ratio - 0.2)
        
        return config


# 全局GPU配置管理器实例
gpu_profile_manager = GPUProfileManager()


# 便捷函数
def get_gpu_config(gpu_name: str, test_type: str = 'medium', **kwargs) -> Optional[StressTestConfig]:
    """获取GPU测试配置的便捷函数"""
    return gpu_profile_manager.create_stress_config(gpu_name, test_type, custom_params=kwargs)


def create_benchmark_suite(gpu_names: List[str], 
                         test_type: str = 'medium',
                         comparison_type: str = 'vertical') -> Dict[str, StressTestConfig]:
    """创建基准测试套件"""
    return gpu_profile_manager.create_comparison_configs(gpu_names, test_type, comparison_type)


def get_dual_gpu_config(gpu_name: str, test_type: str = 'medium') -> Optional[StressTestConfig]:
    """获取双GPU配置"""
    return gpu_profile_manager.get_multi_gpu_config(gpu_name, 2, test_type)


def list_supported_gpus() -> List[str]:
    """列出支持的GPU型号"""
    return gpu_profile_manager.list_profiles()