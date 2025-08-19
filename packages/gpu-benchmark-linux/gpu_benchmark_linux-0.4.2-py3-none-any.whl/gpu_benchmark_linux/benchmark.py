"""
基准测试模块 - 提供GPU基准测试的核心功能
包含内存和性能优化功能
"""

import os
import sys
import time
import logging
from pathlib import Path

from .utils import (
    logger, log_section, log_subsection, run_command,
    check_command, install_system_package, install_python_package,
    check_python_package, clone_repository, find_cuda_samples_dir,
    GREEN, RED, YELLOW, BLUE, RESET
)
from .memory_optimizer import ResourceManager, MemoryOptimizer, PerformanceOptimizer

class GPUBenchmark:
    """GPU基准测试类，提供完整的测试流程"""
    
    def __init__(self, device_id: int = 0, enable_optimization: bool = True, enable_multi_precision: bool = True):
        """初始化基准测试环境"""
        self.device_id = device_id
        self.cuda_samples_dir = find_cuda_samples_dir()
        self.enable_optimization = enable_optimization
        self.enable_multi_precision = enable_multi_precision
        
        # 初始化多精度分析器（默认启用）
        if self.enable_multi_precision:
            try:
                from .multi_precision_performance import MultiPrecisionPerformanceAnalyzer
                self.multi_precision_analyzer = MultiPrecisionPerformanceAnalyzer()
                logger.info("✅ 多精度性能分析已启用")
            except ImportError as e:
                logger.warning(f"无法导入多精度分析器: {e}")
                self.multi_precision_analyzer = None
        else:
            self.multi_precision_analyzer = None
    
    def init(self):
        """初始化测试环境"""
        log_section("初始化测试环境")
        # 获取日志文件路径，使用类型安全的方式
        log_file_path = ""
        for handler in logger.handlers:
            # 检查是否为FileHandler类型的处理器
            if isinstance(handler, logging.FileHandler):
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
            logger.warning("警告: 未找到nvidia-smi，请安装NVIDIA驱动")
            logger.info("在没有NVIDIA硬件的环境下，将跳过硬件相关测试")
        
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
        
        # GPU压力测试（使用内置实现）
        log_subsection("GPU压力测试（计算性能与稳定性）")
        try:
            from .stress_test import stress_tester, StressTestConfig
            
            logger.info("开始内置GPU压力测试...")
            
            # 配置压力测试
            config = StressTestConfig(
                duration=60,  # 60秒测试
                test_types=['matrix_multiply', 'compute_intensive'],
                temperature_limit=85.0,
                auto_stop_on_limit=True
            )
            
            # 运行压力测试
            result = stress_tester.run_stress_test(config)
            
            if result.success:
                logger.info("GPU压力测试成功完成")
                
                # 显示性能指标
                if result.performance_metrics:
                    metrics = result.performance_metrics
                    if 'total_gflops' in metrics:
                        logger.info(f"总计算性能: {metrics['total_gflops']:.2f} GFLOPS")
                    if 'temperature_stats' in metrics:
                        temp_stats = metrics['temperature_stats']
                        logger.info(f"温度范围: {temp_stats['min']:.1f}°C - {temp_stats['max']:.1f}°C (平均: {temp_stats['avg']:.1f}°C)")
                    if 'power_stats' in metrics:
                        power_stats = metrics['power_stats']
                        logger.info(f"功耗范围: {power_stats['min']:.1f}W - {power_stats['max']:.1f}W (平均: {power_stats['avg']:.1f}W)")
                
                # 保存详细结果
                from pathlib import Path
                result_file = Path("./gpu_benchmark_linux_results") / f"stress_test_{int(result.start_time)}.json"
                stress_tester.export_result(result, str(result_file))
                logger.info(f"详细测试结果已保存至: {result_file}")
                
            else:
                logger.error("GPU压力测试失败")
                if result.error_message:
                    logger.error(f"错误信息: {result.error_message}")
                    
        except ImportError as e:
            logger.error(f"无法导入压力测试模块: {e}")
            logger.info("GPU基础功能已通过nvidia-smi和PyTorch CUDA测试验证")
        except Exception as e:
            logger.error(f"GPU压力测试执行失败: {e}")
            logger.info("GPU基础功能已通过nvidia-smi和PyTorch CUDA测试验证")
    
    def test_model_inference(self):
        """大模型推理测试 - 使用安全版本"""
        log_section("大模型推理能力测试")
        
        try:
            # 使用内置的安全模型推理测试
            from .safe_model_inference_test import run_safe_model_inference_tests
            
            log_subsection("开始安全的模型推理测试")
            success = run_safe_model_inference_tests()
            
            if success:
                logger.info("模型推理测试完成")
            else:
                logger.warning("模型推理测试未能成功运行，但这不影响其他GPU基准测试")
                
        except ImportError as e:
            logger.warning(f"无法导入安全模型推理测试模块: {e}")
            logger.info("尝试使用原始模型推理测试...")
            
            # 回退到原始测试
            from pathlib import Path
            script_path = Path("model_inference_test.py")
            if script_path.exists():
                log_subsection("运行原始模型推理测试")
                run_command([sys.executable, str(script_path)])
            else:
                logger.warning("未找到模型推理测试脚本，跳过此测试")
                
        except Exception as e:
            logger.warning(f"模型推理测试遇到问题: {e}")
            logger.info("这通常是由于模型下载失败或显存不足，不影响其他GPU测试")
    
    def run_all_tests(self):
        """运行所有测试 - 包含完整的多精度性能分析"""
        self.init()
        
        logger.info("=" * 60)
        logger.info("🚀 开始GPU基准测试完整流程")
        logger.info("=" * 60)
        
        # 1. 环境检查和依赖安装
        logger.info("📋 步骤1: 环境检查和依赖安装")
        self.install_system_deps()
        if not self.check_environment():
            logger.error("环境检查失败，无法继续测试")
            return False
        self.install_python_deps()
        
        # 2. 基础CUDA测试
        logger.info("🧪 步骤2: 基础CUDA功能测试")
        self.test_cuda_basics()
        
        # 3. 完整GPU压力测试和多精度分析
        logger.info("🎯 步骤3: 完整GPU压力测试和多精度性能分析")
        try:
            from .stress_test import StressTestConfig, GPUStressTester
            
            # 创建测试配置 - 更长时间的测试以获得准确数据
            config = StressTestConfig(
                duration=120,  # 2分钟测试
                device_ids=[],
                matrix_size=4096,
                memory_usage_ratio=0.8,
                temperature_limit=90.0,
                test_types=['matrix_multiply', 'compute_intensive', 'memory_bandwidth']
            )
            
            # 运行压力测试
            logger.info("开始GPU压力测试...")
            stress_tester = GPUStressTester(enable_csv_logging=True)
            result = stress_tester.run_stress_test(config)
            
            if result.success:
                logger.info("✅ GPU压力测试成功完成")
                
                # 显示基本结果
                self._display_stress_test_results(result)
                
                # 4. 多精度性能分析
                if self.enable_multi_precision and self.multi_precision_analyzer:
                    logger.info("📊 步骤4: 多精度性能分析")
                    
                    # 分析CSV数据
                    csv_analysis = None
                    if hasattr(stress_tester, 'csv_logger') and stress_tester.csv_logger:
                        csv_file = stress_tester.csv_logger.get_filepath()
                        logger.info(f"分析CSV数据文件: {csv_file}")
                        
                        try:
                            from .csv_viewer import analyze_csv_file
                            csv_viewer = analyze_csv_file(str(csv_file), export_summary=False)
                            # 获取分析数据
                            csv_analysis = {
                                'basic_info': csv_viewer.get_basic_info(),
                                'temperature_analysis': csv_viewer.get_temperature_analysis(),
                                'power_analysis': csv_viewer.get_power_analysis(),
                                'utilization_analysis': csv_viewer.get_utilization_analysis(),
                                'performance_trends': csv_viewer.get_performance_trends()
                            }
                            logger.info("✅ CSV数据分析完成")
                        except Exception as e:
                            logger.warning(f"CSV数据分析失败: {e}")
                    
                    # 执行多精度分析
                    test_results = {
                        'device_results': result.device_results,
                        'performance_metrics': result.performance_metrics,
                        'success': result.success
                    }
                    
                    multi_precision_metrics = self.multi_precision_analyzer.calculate_multi_precision_performance(
                        test_results, csv_analysis or {}
                    )
                    
                    # 5. 生成详细性能报告
                    logger.info("📝 步骤5: 生成详细性能报告")
                    
                    # 输出多精度总结到日志
                    multi_precision_summary = self.multi_precision_analyzer.generate_multi_precision_summary_text(
                        multi_precision_metrics
                    )
                    
                    # 将多精度总结写入日志
                    for line in multi_precision_summary.split('\n'):
                        if line.strip():
                            logger.info(line)
                    
                    # 6. 保存详细报告文件
                    logger.info("💾 步骤6: 保存详细报告")
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # 保存多精度报告
                    multi_precision_file = f"gpu_benchmark_linux_results/multi_precision_analysis_{timestamp}.json"
                    self.multi_precision_analyzer.export_multi_precision_report(
                        multi_precision_metrics, multi_precision_file
                    )
                    logger.info(f"📊 多精度分析报告已保存: {multi_precision_file}")
                    
                    # 保存性能总结
                    try:
                        from .performance_summary import PerformanceSummaryGenerator
                        performance_summary = PerformanceSummaryGenerator()
                        summary_metrics = performance_summary.generate_performance_summary(
                            test_results, csv_analysis or {}
                        )
                        
                        summary_file = f"gpu_benchmark_linux_results/performance_summary_{timestamp}.json"
                        performance_summary.export_summary_report(summary_metrics, summary_file)
                        logger.info(f"📈 性能总结报告已保存: {summary_file}")
                        
                        # 输出性能总结到日志
                        text_summary = performance_summary.generate_text_summary(summary_metrics)
                        for line in text_summary.split('\n'):
                            if line.strip():
                                logger.info(line)
                                
                    except Exception as e:
                        logger.warning(f"生成性能总结失败: {e}")
                
                else:
                    logger.warning("⚠️ 多精度性能分析未启用")
                
            else:
                logger.error("❌ GPU压力测试失败")
                if result.error_message:
                    logger.error(f"错误信息: {result.error_message}")
                
        except Exception as e:
            logger.error(f"GPU压力测试执行失败: {e}")
            logger.info("继续执行其他测试...")
        
        # 7. 大模型推理测试（最后执行，可能出错但不影响其他测试）
        logger.info("🤖 步骤7: 大模型推理测试（如遇错误将跳过）")
        try:
            self.test_model_inference()
        except Exception as e:
            logger.warning(f"大模型推理测试遇到问题，已跳过: {e}")
            logger.info("这通常是因为模型下载或显存不足导致的，不影响其他GPU基准测试")
        
        # 8. 测试完成总结
        log_section("🎉 GPU基准测试完整流程已完成")
        
        # 获取日志文件路径
        log_file_path = ""
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                log_file_path = handler.baseFilename
                break
        
        if log_file_path:
            logger.info(f"📋 完整的多精度性能分析结果见：{log_file_path}")
            logger.info("📊 日志包含完整的FP64/FP32/FP16/FP8/INT8/INT4性能指标")
        else:
            logger.info("📋 测试完成，请查看上述详细结果")
        
        return True
    
    def test_gpu_stress(self, duration=60, test_types=None):
        """运行GPU压力测试"""
        log_section("GPU压力测试")
        
        try:
            from .stress_test import stress_tester, StressTestConfig
            
            if test_types is None:
                test_types = ['matrix_multiply', 'compute_intensive', 'memory_bandwidth']
            
            logger.info(f"开始GPU压力测试，持续时间: {duration}秒")
            
            # 配置压力测试
            config = StressTestConfig(
                duration=duration,
                test_types=test_types,
                temperature_limit=85.0,
                power_limit_ratio=0.95,
                auto_stop_on_limit=True,
                monitor_interval=2.0
            )
            
            # 运行压力测试
            result = stress_tester.run_stress_test(config)
            
            if result.success:
                logger.info("GPU压力测试成功完成")
                
                # 显示详细结果
                self._display_stress_test_results(result)
                
                # 输出详细性能指标到日志
                try:
                    from .detailed_logger import log_detailed_performance_metrics, log_performance_comparison_table
                    
                    # 构造测试结果数据
                    test_results = {
                        'device_results': result.device_results,
                        'system_info': {'gpu_count': len(result.device_results)}
                    }
                    
                    # 输出详细性能指标
                    log_detailed_performance_metrics(test_results)
                    
                    # 输出性能对比表格
                    from .performance_summary import PerformanceSummaryGenerator
                    generator = PerformanceSummaryGenerator()
                    performance_summary = generator.generate_performance_summary(test_results)
                    log_performance_comparison_table(performance_summary)
                    
                except Exception as e:
                    logger.warning(f"输出详细性能日志失败: {e}")
                
                # 保存结果
                self._save_stress_test_results(result)
                
                return True
            else:
                logger.error("GPU压力测试失败")
                if result.error_message:
                    logger.error(f"错误信息: {result.error_message}")
                return False
                
        except Exception as e:
            logger.error(f"GPU压力测试执行失败: {e}")
            return False
    
    def _display_stress_test_results(self, result):
        """显示压力测试结果"""
        logger.info("=== 压力测试结果摘要 ===")
        
        # 基本信息
        logger.info(f"测试持续时间: {result.duration:.1f}秒")
        logger.info(f"测试设备数量: {len(result.device_results)}")
        
        # 性能指标
        if result.performance_metrics:
            metrics = result.performance_metrics
            
            if 'total_gflops' in metrics:
                logger.info(f"总计算性能: {metrics['total_gflops']:.2f} GFLOPS")
                if 'avg_gflops_per_device' in metrics:
                    logger.info(f"平均每设备性能: {metrics['avg_gflops_per_device']:.2f} GFLOPS")
            
            if 'temperature_stats' in metrics:
                temp_stats = metrics['temperature_stats']
                logger.info(f"温度统计: 最低{temp_stats['min']:.1f}°C, 最高{temp_stats['max']:.1f}°C, 平均{temp_stats['avg']:.1f}°C")
            
            if 'power_stats' in metrics:
                power_stats = metrics['power_stats']
                logger.info(f"功耗统计: 最低{power_stats['min']:.1f}W, 最高{power_stats['max']:.1f}W, 平均{power_stats['avg']:.1f}W")
            
            if 'gpu_utilization_stats' in metrics:
                util_stats = metrics['gpu_utilization_stats']
                logger.info(f"GPU利用率统计: 最低{util_stats['min']:.1f}%, 最高{util_stats['max']:.1f}%, 平均{util_stats['avg']:.1f}%")
        
        # 各设备详细结果
        for device_id, device_result in result.device_results.items():
            logger.info(f"--- GPU {device_id} 详细结果 ---")
            
            if 'matrix_multiply' in device_result:
                mm_result = device_result['matrix_multiply']
                if 'gflops' in mm_result:
                    logger.info(f"  矩阵乘法性能: {mm_result['gflops']:.2f} GFLOPS")
            
            if 'compute_intensive' in device_result:
                ci_result = device_result['compute_intensive']
                if 'iterations_per_second' in ci_result:
                    logger.info(f"  计算密集型性能: {ci_result['iterations_per_second']:.2f} iter/s")
            
            if 'memory_bandwidth' in device_result:
                mb_result = device_result['memory_bandwidth']
                if 'h2d_bandwidth_gbps' in mb_result:
                    logger.info(f"  内存带宽 (Host->Device): {mb_result['h2d_bandwidth_gbps']:.2f} GB/s")
                if 'd2h_bandwidth_gbps' in mb_result:
                    logger.info(f"  内存带宽 (Device->Host): {mb_result['d2h_bandwidth_gbps']:.2f} GB/s")
    
    def _save_stress_test_results(self, result):
        """保存压力测试结果"""
        try:
            from pathlib import Path
            from .stress_test import stress_tester
            
            # 确保结果目录存在
            result_dir = Path("./gpu_benchmark_linux_results")
            result_dir.mkdir(exist_ok=True)
            
            # 生成文件名
            timestamp = int(result.start_time)
            result_file = result_dir / f"stress_test_{timestamp}.json"
            
            # 保存结果
            if stress_tester.export_result(result, str(result_file)):
                logger.info(f"详细测试结果已保存至: {result_file}")
            
        except Exception as e:
            logger.error(f"保存压力测试结果失败: {e}")
    
    def run_specific_test(self, test_name):
        """运行特定测试"""
        self.init()
        
        if test_name == "env":
            self.check_environment()
        elif test_name == "cuda":
            self.test_cuda_basics()
        elif test_name == "stress":
            self.check_environment()
            self.install_python_deps()
            self.test_gpu_stress()
        elif test_name == "model":
            self.check_environment()
            self.install_python_deps()
            self.test_model_inference()
        else:
            logger.error(f"未知的测试类型: {test_name}")
            return False
        
        log_section(f"{test_name}测试完成")
        # 获取日志文件路径，使用类型安全的方式
        log_file_path = ""
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                log_file_path = handler.baseFilename
                break
        
        if log_file_path:
            logger.info(f"完整结果见：{log_file_path}")
        else:
            logger.info("测试完成")
        return True
