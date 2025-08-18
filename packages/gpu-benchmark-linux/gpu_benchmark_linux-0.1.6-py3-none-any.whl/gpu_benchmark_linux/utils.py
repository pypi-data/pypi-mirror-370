"""
工具函数模块 - 提供日志、系统检查和依赖安装等功能
"""

import os
import sys
import logging
import subprocess
import platform
import shutil
import time
from datetime import datetime
from pathlib import Path
import pkg_resources
from tqdm import tqdm
import colorama

# 初始化颜色支持
colorama.init()

# 定义颜色
GREEN = colorama.Fore.GREEN
RED = colorama.Fore.RED
YELLOW = colorama.Fore.YELLOW
BLUE = colorama.Fore.BLUE
RESET = colorama.Fore.RESET

# 配置
RESULT_DIR = Path("./gpu_benchmark_linux_results")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = RESULT_DIR / f"benchmark_{TIMESTAMP}.log"
GPU_BURN_REPO = "https://github.com/wilicc/gpu-burn.git"

# 配置日志
def setup_logger():
    """设置日志系统"""
    RESULT_DIR.mkdir(exist_ok=True)
    
    # 创建日志处理器
    logger = logging.getLogger("gpu_benchmark_linux")
    logger.setLevel(logging.INFO)
    
    # 文件处理器
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.INFO)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 格式化器
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 获取日志实例
logger = setup_logger()

def log_section(title):
    """记录带格式的章节标题"""
    logger.info("")
    logger.info(f"===== {title} =====")

def log_subsection(title):
    """记录带格式的子章节标题"""
    logger.info(f"=== {title} ===")

def run_command(cmd, shell=False, check=True, capture_output=True, env=None):
    """运行系统命令并返回结果"""
    try:
        if isinstance(cmd, str) and not shell:
            cmd = cmd.split()
        
        # 如果提供了环境变量，与当前环境合并
        command_env = None
        if env:
            command_env = os.environ.copy()
            command_env.update(env)
        
        result = subprocess.run(
            cmd, 
            shell=shell, 
            check=check, 
            text=True,
            capture_output=capture_output,
            env=command_env
        )
        
        if capture_output:
            if result.stdout:
                logger.info(result.stdout.strip())
            if result.stderr:
                logger.warning(result.stderr.strip())
        
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"命令执行失败: {e}")
        if e.stdout:
            logger.info(e.stdout.strip())
        if e.stderr:
            logger.error(e.stderr.strip())
        if check:
            raise
        return e
    except Exception as e:
        logger.error(f"执行命令时出错: {e}")
        if check:
            raise
        return None

def check_command(cmd):
    """检查命令是否存在"""
    return shutil.which(cmd) is not None

def install_system_package(package):
    """安装系统包"""
    if platform.system() == "Linux":
        # 检测包管理器
        if check_command("apt"):
            logger.info(f"使用apt安装: {package}")
            run_command(f"sudo apt update -y", shell=True, check=False)
            return run_command(f"sudo apt install -y {package}", shell=True, check=False)
        elif check_command("yum"):
            logger.info(f"使用yum安装: {package}")
            return run_command(f"sudo yum install -y {package}", shell=True, check=False)
        else:
            logger.warning(f"未找到支持的包管理器，请手动安装: {package}")
            return False
    else:
        logger.warning(f"不支持在当前系统({platform.system()})自动安装系统包: {package}")
        return False

def install_python_package(package):
    """安装Python包"""
    try:
        logger.info(f"安装Python包: {package}")
        result = run_command([sys.executable, "-m", "pip", "install", package], check=False)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"安装Python包失败: {e}")
        return False

def check_python_package(package):
    """检查Python包是否已安装"""
    try:
        pkg_resources.get_distribution(package)
        return True
    except pkg_resources.DistributionNotFound:
        return False

def clone_repository(repo_url, target_dir):
    """克隆Git仓库"""
    import git
    try:
        if os.path.exists(target_dir):
            logger.info(f"目录已存在，清理: {target_dir}")
            shutil.rmtree(target_dir)
        
        logger.info(f"克隆仓库: {repo_url} 到 {target_dir}")
        git.Repo.clone_from(repo_url, target_dir)
        return True
    except Exception as e:
        logger.error(f"克隆仓库失败: {e}")
        return False

def find_cuda_samples_dir():
    """查找CUDA样例目录"""
    # 常见的CUDA样例路径
    common_paths = [
        "/usr/local/cuda/samples",
        "/usr/local/cuda-*/samples",
    ]
    
    # 扩展通配符路径
    expanded_paths = []
    for path in common_paths:
        if "*" in path:
            import glob
            expanded_paths.extend(glob.glob(path))
        else:
            expanded_paths.append(path)
    
    # 检查路径是否存在
    for path in expanded_paths:
        if os.path.isdir(path):
            return path
    
    return None