"""
基准测试模块 - 提供GPU基准测试的核心功能
"""

import os
import sys
import time
from pathlib import Path

from .utils import (
    logger, log_section, log_subsection, run_command,
    check_command, install_system_package, install_python_package,
    check_python_package, clone_repository, find_cuda_samples_dir,
    GPU_BURN_REPO, GREEN, RED, YELLOW, BLUE, RESET
)

class GPUBenchmark:
    """GPU基准测试类，提供完整的测试流程"""
    
    def __init__(self):
        """初始化基准测试环境"""
        self.cuda_samples_dir = find_cuda_samples_dir()
        self.gpu_burn_dir = Path("./gpu-burn")
    
    def init(self):
        """初始化测试环境"""
        log_section("初始化测试环境")
        # 获取日志文件路径，使用类型安全的方式
        log_file_path = ""
        for handler in logger.handlers:
            # 检查是否为FileHandler类型的处理器
            if hasattr(handler, 'baseFilename') and handler.baseFilename:
                log_file_path = handler.baseFilename
                break
        
        if log_file_path:
            logger.info(f"测试结果将保存至：{log_file_path}")
        else:
            logger.info("未找到日志文件路径")
    
    def install_system_deps(self):
        """检查并安装系统依赖"""
        log_section("检查系统依赖")
        
        # 检查并安装必要工具
        deps = ["gcc", "make", "git", "python3"]
        for dep in deps:
            if not check_command(dep):
                logger.info(f"安装缺失的系统工具: {dep}")
                install_system_package(dep)
    
    def check_environment(self):
        """检查GPU环境"""
        log_section("环境检查")
        
        # 检查NVIDIA显卡状态
        log_subsection("NVIDIA显卡状态")
        if check_command("nvidia-smi"):
            run_command("nvidia-smi")
        else:
            logger.error("错误: 未找到nvidia-smi，请安装NVIDIA驱动")
            return False
        
        # 检查CUDA
        log_subsection("CUDA版本检查")
        if check_command("nvcc"):
            run_command("nvcc --version")
        else:
            logger.warning("警告: 未找到nvcc (CUDA编译器)，某些测试将受限")
            logger.warning("请确保已安装CUDA Toolkit: https://developer.nvidia.com/cuda-toolkit")
        
        # 检查PyTorch
        log_subsection("PyTorch CUDA检查")
        if not check_python_package("torch"):
            logger.info("安装PyTorch...")
            install_python_package("torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        
        # 检查PyTorch CUDA可用性
        try:
            import torch
            logger.info(f"Torch version: {torch.__version__}")
            logger.info(f"CUDA available: {torch.cuda.is_available()}")
            logger.info(f"GPU count: {torch.cuda.device_count()}")
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    logger.info(f"GPU {i}: {torch.cuda.get_device_name(i)}")
        except ImportError:
            logger.error("无法导入PyTorch，请检查安装")
            return False
        
        return True
    
    def install_python_deps(self):
        """安装Python依赖"""
        log_section("安装Python依赖")
        
        deps = ["transformers", "diffusers", "accelerate", "sentencepiece", "numpy", "tqdm", "colorama", "gitpython"]
        for dep in deps:
            if not check_python_package(dep):
                logger.info(f"安装缺失的Python包: {dep}")
                install_python_package(dep)
    
    def install_gpu_burn(self):
        """安装gpu_burn"""
        if not self.gpu_burn_dir.joinpath("gpu_burn").exists():
            log_section("安装gpu_burn")
            
            # 克隆仓库
            if clone_repository(GPU_BURN_REPO, self.gpu_burn_dir):
                # 编译（添加-allow-unsupported-compiler标志以支持新版GCC）
                os.chdir(self.gpu_burn_dir)
                
                # 修改Makefile以添加-allow-unsupported-compiler标志
                try:
                    # 读取Makefile
                    with open("Makefile", "r") as f:
                        makefile_content = f.read()
                    
                    # 检查是否已经包含-allow-unsupported-compiler标志
                    if "-allow-unsupported-compiler" not in makefile_content:
                        # 添加-allow-unsupported-compiler标志
                        modified_content = makefile_content.replace(
                            "$(NVCC) -I$(CUDA_PATH)/include -arch=compute_$(CUDA_ARCH) -ptx compare.cu -o compare.ptx",
                            "$(NVCC) -I$(CUDA_PATH)/include -arch=compute_$(CUDA_ARCH) -allow-unsupported-compiler -ptx compare.cu -o compare.ptx"
                        )
                        
                        # 写回Makefile
                        with open("Makefile", "w") as f:
                            f.write(modified_content)
                        
                        logger.info("已修改Makefile以支持新版GCC编译器")
                    else:
                        logger.info("Makefile已包含-allow-unsupported-compiler标志")
                except Exception as e:
                    logger.warning(f"修改Makefile失败: {e}")
                
                # 尝试编译
                try:
                    # 使用环境变量传递-allow-unsupported-compiler标志
                    custom_env = {"NVCC_EXTRA_FLAGS": "-allow-unsupported-compiler"}
                    run_command("make", env=custom_env)
                except Exception as e:
                    logger.warning(f"使用make编译失败: {e}")
                    logger.info("尝试使用手动命令编译...")
                    
                    # 手动编译命令 - 添加-D__FLOAT32=float定义来解决_Float32未定义的问题
                    try:
                        # 第一步：编译C++驱动文件
                        run_command("g++ -O3 -Wno-unused-result -I/usr/local/cuda/include -std=c++11 -DIS_JETSON=false -c gpu_burn-drv.cpp", check=False)
                        
                        # 第二步：使用nvcc编译CUDA文件，添加-D__FLOAT32=float和-D__FLOAT64=double定义
                        run_command("/usr/local/cuda/bin/nvcc -I/usr/local/cuda/include -arch=compute_50 -allow-unsupported-compiler -D__FLOAT32=float -D__FLOAT64=double -ptx compare.cu -o compare.ptx", check=False)
                        
                        # 第三步：链接生成最终可执行文件
                        run_command("g++ -O3 -Wno-unused-result -o gpu_burn gpu_burn-drv.o -L/usr/local/cuda/lib64 -lcuda -lcudart -lcublas", check=False)
                        
                        if os.path.exists("gpu_burn"):
                            logger.info("gpu_burn编译成功")
                        else:
                            logger.warning("gpu_burn编译失败，跳过此测试")
                    except Exception as e:
                        logger.warning(f"手动编译失败: {e}")
                
                os.chdir("..")
    
    def test_cuda_basics(self):
        """基础CUDA能力测试"""
        log_section("基础CUDA能力测试")
        
        # deviceQuery测试
        log_subsection("deviceQuery（设备信息）")
        if self.cuda_samples_dir:
            devicequery_dir = Path(self.cuda_samples_dir) / "1_Utilities" / "deviceQuery"
            if devicequery_dir.exists():
                os.chdir(devicequery_dir)
                run_command("make")
                run_command("./deviceQuery")
                os.chdir(os.path.expanduser("~"))  # 返回主目录
            else:
                logger.warning(f"警告: 未找到deviceQuery目录: {devicequery_dir}")
        else:
            logger.warning("警告: 未找到CUDA Samples目录，跳过deviceQuery测试")
        
        # bandwidthTest测试
        log_subsection("bandwidthTest（内存带宽）")
        if self.cuda_samples_dir:
            bandwidth_dir = Path(self.cuda_samples_dir) / "1_Utilities" / "bandwidthTest"
            if bandwidth_dir.exists():
                os.chdir(bandwidth_dir)
                run_command("make")
                run_command("./bandwidthTest")
                os.chdir(os.path.expanduser("~"))  # 返回主目录
            else:
                logger.warning(f"警告: 未找到bandwidthTest目录: {bandwidth_dir}")
        else:
            logger.warning("警告: 未找到CUDA Samples目录，跳过bandwidthTest测试")
        
        # gpu_burn测试
        log_subsection("gpu_burn（计算性能与稳定性）")
        if self.gpu_burn_dir.joinpath("gpu_burn").exists():
            run_command(f"{self.gpu_burn_dir}/gpu_burn 60")  # 测试60秒
        else:
            logger.warning("警告: 未找到gpu_burn，跳过此测试")
    
    def test_model_inference(self):
        """大模型推理测试"""
        log_section("大模型推理能力测试")
        
        # 检查测试脚本
        script_path = Path("model_inference_test.py")
        if not script_path.exists():
            # 如果脚本不存在，创建一个
            from .tests.model_tests import create_model_test_script
            script_path = create_model_test_script()
            logger.info(f"已创建模型测试脚本: {script_path}")
        
        # 运行测试
        log_subsection("开始模型推理测试（Stable Diffusion/LLaMA）")
        run_command([sys.executable, str(script_path)])
    
    def run_all_tests(self):
        """运行所有测试"""
        self.init()
        self.install_system_deps()
        if not self.check_environment():
            logger.error("环境检查失败，无法继续测试")
            return False
        
        self.install_python_deps()
        self.install_gpu_burn()
        self.test_cuda_basics()
        self.test_model_inference()
        
        log_section("所有测试完成")
        logger.info(f"完整结果见：{logger.handlers[0].baseFilename}")
        return True
    
    def run_specific_test(self, test_name):
        """运行特定测试"""
        self.init()
        
        if test_name == "env":
            self.check_environment()
        elif test_name == "cuda":
            self.install_gpu_burn()
            self.test_cuda_basics()
        elif test_name == "model":
            self.check_environment()
            self.install_python_deps()
            self.test_model_inference()
        else:
            logger.error(f"未知的测试类型: {test_name}")
            return False
        
        log_section(f"{test_name}测试完成")
        logger.info(f"完整结果见：{logger.handlers[0].baseFilename}")
        return True