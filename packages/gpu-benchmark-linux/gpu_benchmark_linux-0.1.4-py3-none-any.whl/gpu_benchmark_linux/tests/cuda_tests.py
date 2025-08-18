"""
CUDA测试模块 - 提供CUDA相关的测试功能
"""

import os
import subprocess
import time
from pathlib import Path

from ..utils import logger, run_command

def test_device_info():
    """测试设备信息"""
    logger.info("获取GPU设备信息...")
    
    # 使用nvidia-smi获取详细信息
    if os.path.exists("/usr/bin/nvidia-smi"):
        run_command("nvidia-smi -q")
    else:
        logger.warning("未找到nvidia-smi，无法获取详细设备信息")
        return False
    
    return True

def test_cuda_version():
    """测试CUDA版本"""
    logger.info("检查CUDA版本...")
    
    # 使用nvcc获取CUDA版本
    if os.path.exists("/usr/local/cuda/bin/nvcc") or os.path.exists("/usr/bin/nvcc"):
        run_command("nvcc --version")
    else:
        logger.warning("未找到nvcc，无法获取CUDA版本")
        return False
    
    return True

def test_memory_bandwidth(cuda_samples_dir=None):
    """测试内存带宽"""
    logger.info("测试GPU内存带宽...")
    
    # 查找bandwidthTest
    bandwidth_test_path = None
    
    # 如果提供了CUDA样例目录
    if cuda_samples_dir:
        test_path = Path(cuda_samples_dir) / "1_Utilities" / "bandwidthTest" / "bandwidthTest"
        if test_path.exists():
            bandwidth_test_path = test_path
    
    # 如果没有找到，尝试编译
    if not bandwidth_test_path:
        logger.warning("未找到bandwidthTest，尝试编译...")
        
        # 查找CUDA样例目录
        if not cuda_samples_dir:
            cuda_samples_dir = "/usr/local/cuda/samples"
            if not os.path.exists(cuda_samples_dir):
                # 尝试查找其他版本
                for cuda_dir in Path("/usr/local").glob("cuda-*"):
                    if (cuda_dir / "samples").exists():
                        cuda_samples_dir = cuda_dir / "samples"
                        break
        
        if os.path.exists(f"{cuda_samples_dir}/1_Utilities/bandwidthTest"):
            # 编译
            current_dir = os.getcwd()
            os.chdir(f"{cuda_samples_dir}/1_Utilities/bandwidthTest")
            run_command("make")
            os.chdir(current_dir)
            
            bandwidth_test_path = Path(f"{cuda_samples_dir}/1_Utilities/bandwidthTest/bandwidthTest")
    
    # 运行测试
    if bandwidth_test_path and bandwidth_test_path.exists():
        run_command(str(bandwidth_test_path))
        return True
    else:
        logger.warning("未找到bandwidthTest，跳过内存带宽测试")
        return False

def test_compute_capability(cuda_samples_dir=None):
    """测试计算能力"""
    logger.info("测试GPU计算能力...")
    
    # 查找deviceQuery
    device_query_path = None
    
    # 如果提供了CUDA样例目录
    if cuda_samples_dir:
        test_path = Path(cuda_samples_dir) / "1_Utilities" / "deviceQuery" / "deviceQuery"
        if test_path.exists():
            device_query_path = test_path
    
    # 如果没有找到，尝试编译
    if not device_query_path:
        logger.warning("未找到deviceQuery，尝试编译...")
        
        # 查找CUDA样例目录
        if not cuda_samples_dir:
            cuda_samples_dir = "/usr/local/cuda/samples"
            if not os.path.exists(cuda_samples_dir):
                # 尝试查找其他版本
                for cuda_dir in Path("/usr/local").glob("cuda-*"):
                    if (cuda_dir / "samples").exists():
                        cuda_samples_dir = cuda_dir / "samples"
                        break
        
        if os.path.exists(f"{cuda_samples_dir}/1_Utilities/deviceQuery"):
            # 编译
            current_dir = os.getcwd()
            os.chdir(f"{cuda_samples_dir}/1_Utilities/deviceQuery")
            run_command("make")
            os.chdir(current_dir)
            
            device_query_path = Path(f"{cuda_samples_dir}/1_Utilities/deviceQuery/deviceQuery")
    
    # 运行测试
    if device_query_path and device_query_path.exists():
        run_command(str(device_query_path))
        return True
    else:
        logger.warning("未找到deviceQuery，跳过计算能力测试")
        return False

def test_gpu_burn(duration=60, gpu_burn_path=None):
    """使用gpu-burn测试GPU计算性能与稳定性"""
    logger.info(f"使用gpu-burn测试GPU计算性能与稳定性（{duration}秒）...")
    
    # 查找gpu_burn
    if not gpu_burn_path:
        gpu_burn_path = "./gpu-burn/gpu_burn"
    
    # 运行测试
    if os.path.exists(gpu_burn_path):
        run_command(f"{gpu_burn_path} {duration}")
        return True
    else:
        logger.warning(f"未找到gpu_burn: {gpu_burn_path}，跳过计算性能测试")
        return False