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


def check_cuda_availability():
    """检查CUDA可用性"""
    try:
        # 检查nvidia-smi
        if not check_command("nvidia-smi"):
            return False, "未找到nvidia-smi命令"
        
        # 检查CUDA运行时
        result = run_command("nvidia-smi --query-gpu=name --format=csv,noheader,nounits", 
                           capture_output=True, check=False)
        if result.returncode != 0:
            return False, "nvidia-smi执行失败"
        
        gpu_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        if gpu_count == 0:
            return False, "未检测到NVIDIA GPU"
        
        return True, f"检测到 {gpu_count} 个NVIDIA GPU"
        
    except Exception as e:
        return False, f"检查CUDA可用性时出错: {e}"


def get_gpu_info():
    """获取GPU基本信息"""
    gpu_info = []
    
    try:
        # 使用nvidia-smi获取GPU信息
        result = run_command([
            "nvidia-smi", 
            "--query-gpu=index,name,memory.total,temperature.gpu,power.draw,utilization.gpu",
            "--format=csv,noheader,nounits"
        ], capture_output=True, check=False)
        
        if result.returncode == 0 and result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    parts = [part.strip() for part in line.split(',')]
                    if len(parts) >= 6:
                        gpu_info.append({
                            'index': int(parts[0]) if parts[0].isdigit() else 0,
                            'name': parts[1],
                            'memory_total': parts[2],
                            'temperature': parts[3],
                            'power_draw': parts[4],
                            'utilization': parts[5]
                        })
    
    except Exception as e:
        logger.error(f"获取GPU信息失败: {e}")
    
    return gpu_info


def format_bytes(bytes_value):
    """格式化字节数为人类可读格式"""
    if bytes_value is None:
        return "N/A"
    
    try:
        bytes_value = float(bytes_value)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    except (ValueError, TypeError):
        return str(bytes_value)


def format_temperature(temp_value):
    """格式化温度值"""
    if temp_value is None:
        return "N/A"
    
    try:
        temp = float(temp_value)
        return f"{temp:.1f}°C"
    except (ValueError, TypeError):
        return str(temp_value)


def format_power(power_value):
    """格式化功耗值"""
    if power_value is None:
        return "N/A"
    
    try:
        power = float(power_value)
        return f"{power:.1f}W"
    except (ValueError, TypeError):
        return str(power_value)


def format_percentage(percent_value):
    """格式化百分比值"""
    if percent_value is None:
        return "N/A"
    
    try:
        percent = float(percent_value)
        return f"{percent:.1f}%"
    except (ValueError, TypeError):
        return str(percent_value)


def format_frequency(freq_value):
    """格式化频率值"""
    if freq_value is None:
        return "N/A"
    
    try:
        freq = float(freq_value)
        if freq >= 1000:
            return f"{freq/1000:.2f} GHz"
        else:
            return f"{freq:.0f} MHz"
    except (ValueError, TypeError):
        return str(freq_value)


def check_gpu_requirements():
    """检查GPU环境要求"""
    requirements = {
        'cuda_available': False,
        'gpu_count': 0,
        'min_memory': 4 * 1024 * 1024 * 1024,  # 4GB
        'cuda_version': None,
        'driver_version': None,
        'issues': []
    }
    
    try:
        # 检查CUDA可用性
        cuda_available, cuda_msg = check_cuda_availability()
        requirements['cuda_available'] = cuda_available
        
        if not cuda_available:
            requirements['issues'].append(cuda_msg)
            return requirements
        
        # 获取GPU数量
        gpu_info = get_gpu_info()
        requirements['gpu_count'] = len(gpu_info)
        
        if requirements['gpu_count'] == 0:
            requirements['issues'].append("未检测到可用的GPU设备")
        
        # 检查内存要求
        for gpu in gpu_info:
            try:
                memory_str = gpu.get('memory_total', '0')
                # 解析内存大小（假设格式为 "XXXX MiB"）
                if 'MiB' in memory_str:
                    memory_mb = float(memory_str.replace('MiB', '').strip())
                    memory_bytes = memory_mb * 1024 * 1024
                    if memory_bytes < requirements['min_memory']:
                        requirements['issues'].append(
                            f"GPU {gpu['index']} 内存不足: {memory_str} < 4GB"
                        )
            except (ValueError, TypeError):
                requirements['issues'].append(f"无法解析GPU {gpu['index']} 内存信息")
        
        # 获取CUDA版本
        try:
            result = run_command("nvcc --version", capture_output=True, check=False)
            if result.returncode == 0 and result.stdout:
                for line in result.stdout.split('\n'):
                    if 'release' in line.lower():
                        # 提取版本号
                        import re
                        match = re.search(r'release (\d+\.\d+)', line)
                        if match:
                            requirements['cuda_version'] = match.group(1)
                            break
        except Exception:
            pass
        
        # 获取驱动版本
        try:
            result = run_command([
                "nvidia-smi", 
                "--query-gpu=driver_version",
                "--format=csv,noheader,nounits"
            ], capture_output=True, check=False)
            
            if result.returncode == 0 and result.stdout:
                driver_version = result.stdout.strip().split('\n')[0].strip()
                requirements['driver_version'] = driver_version
        except Exception:
            pass
        
        # 检查CUDA版本要求
        if requirements['cuda_version']:
            try:
                cuda_major = int(float(requirements['cuda_version']))
                if cuda_major < 12:
                    requirements['issues'].append(
                        f"CUDA版本过低: {requirements['cuda_version']} < 12.0"
                    )
            except (ValueError, TypeError):
                requirements['issues'].append("无法解析CUDA版本")
        else:
            requirements['issues'].append("未找到CUDA编译器(nvcc)")
    
    except Exception as e:
        requirements['issues'].append(f"检查GPU要求时出错: {e}")
    
    return requirements


def display_gpu_requirements_check():
    """显示GPU环境要求检查结果"""
    log_section("GPU环境要求检查")
    
    requirements = check_gpu_requirements()
    
    # 显示基本信息
    logger.info(f"CUDA可用性: {'✓' if requirements['cuda_available'] else '✗'}")
    logger.info(f"GPU设备数量: {requirements['gpu_count']}")
    
    if requirements['cuda_version']:
        logger.info(f"CUDA版本: {requirements['cuda_version']}")
    
    if requirements['driver_version']:
        logger.info(f"驱动版本: {requirements['driver_version']}")
    
    # 显示GPU详细信息
    if requirements['gpu_count'] > 0:
        log_subsection("GPU设备详情")
        gpu_info = get_gpu_info()
        for gpu in gpu_info:
            logger.info(f"GPU {gpu['index']}: {gpu['name']}")
            logger.info(f"  内存: {gpu['memory_total']}")
            logger.info(f"  温度: {format_temperature(gpu['temperature'])}")
            logger.info(f"  功耗: {format_power(gpu['power_draw'])}")
            logger.info(f"  利用率: {format_percentage(gpu['utilization'])}")
    
    # 显示问题和建议
    if requirements['issues']:
        log_subsection("发现的问题")
        for issue in requirements['issues']:
            logger.warning(f"⚠ {issue}")
        
        log_subsection("建议解决方案")
        if not requirements['cuda_available']:
            logger.info("1. 安装NVIDIA驱动程序")
            logger.info("2. 安装CUDA Toolkit 12.0或更高版本")
        
        if requirements['gpu_count'] == 0:
            logger.info("1. 检查GPU硬件连接")
            logger.info("2. 确认GPU驱动正确安装")
        
        for issue in requirements['issues']:
            if "内存不足" in issue:
                logger.info("3. 考虑使用内存更大的GPU或降低测试参数")
                break
    else:
        logger.info(f"{GREEN}✓ GPU环境检查通过，满足所有要求{RESET}")
    
    return len(requirements['issues']) == 0


def create_benchmark_report(results, output_file=None):
    """创建基准测试报告"""
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = RESULT_DIR / f"benchmark_report_{timestamp}.html"
    
    try:
        # HTML报告模板
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GPU基准测试报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1, h2, h3 { color: #333; }
        .summary { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .gpu-card { background: #f9f9f9; border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin: 10px 0; }
        .metric { display: inline-block; margin: 5px 15px 5px 0; }
        .metric-label { font-weight: bold; color: #666; }
        .metric-value { color: #2196F3; font-weight: bold; }
        .status-success { color: #4CAF50; }
        .status-warning { color: #FF9800; }
        .status-error { color: #F44336; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .chart-placeholder { background: #f0f0f0; height: 200px; display: flex; align-items: center; justify-content: center; color: #666; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>GPU基准测试报告</h1>
        <div class="summary">
            <h2>测试摘要</h2>
            <div class="metric">
                <span class="metric-label">测试时间:</span>
                <span class="metric-value">{test_time}</span>
            </div>
            <div class="metric">
                <span class="metric-label">GPU数量:</span>
                <span class="metric-value">{gpu_count}</span>
            </div>
            <div class="metric">
                <span class="metric-label">测试状态:</span>
                <span class="metric-value {status_class}">{test_status}</span>
            </div>
        </div>
        
        <h2>GPU设备信息</h2>
        {gpu_info_html}
        
        <h2>性能测试结果</h2>
        {performance_results_html}
        
        <h2>监控数据</h2>
        {monitoring_data_html}
        
        <div class="chart-placeholder">
            性能图表 (需要JavaScript支持)
        </div>
        
        <h2>详细日志</h2>
        <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; font-size: 12px;">
{detailed_log}
        </pre>
    </div>
</body>
</html>
        """
        
        # 生成报告内容
        test_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        gpu_info = get_gpu_info()
        gpu_count = len(gpu_info)
        
        # GPU信息HTML
        gpu_info_html = ""
        for gpu in gpu_info:
            gpu_info_html += f"""
            <div class="gpu-card">
                <h3>GPU {gpu['index']}: {gpu['name']}</h3>
                <div class="metric">
                    <span class="metric-label">内存:</span>
                    <span class="metric-value">{gpu['memory_total']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">温度:</span>
                    <span class="metric-value">{format_temperature(gpu['temperature'])}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">功耗:</span>
                    <span class="metric-value">{format_power(gpu['power_draw'])}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">利用率:</span>
                    <span class="metric-value">{format_percentage(gpu['utilization'])}</span>
                </div>
            </div>
            """
        
        # 填充模板
        html_content = html_template.format(
            test_time=test_time,
            gpu_count=gpu_count,
            test_status="完成",
            status_class="status-success",
            gpu_info_html=gpu_info_html,
            performance_results_html="<p>性能测试结果将在此显示</p>",
            monitoring_data_html="<p>监控数据将在此显示</p>",
            detailed_log="详细日志将在此显示"
        )
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"基准测试报告已生成: {output_file}")
        return str(output_file)
        
    except Exception as e:
        logger.error(f"生成基准测试报告失败: {e}")
        return None
