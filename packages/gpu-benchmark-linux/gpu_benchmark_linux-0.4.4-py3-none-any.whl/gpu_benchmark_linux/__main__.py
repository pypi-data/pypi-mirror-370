#!/usr/bin/env python3
"""
GPU基准测试工具命令行入口
"""

import argparse
import sys
import os
from datetime import datetime
from typing import List, Optional

from .benchmark import GPUBenchmark
from .utils import logger, setup_logger
from .gpu_profiles import gpu_profile_manager, list_supported_gpus
from .stress_test import GPUStressTester


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description='GPU基准测试工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 基本测试
  python -m gpu_benchmark_linux --test all
  
  # 指定GPU型号和测试类型
  python -m gpu_benchmark_linux --gpu-model A100 --test-type medium
  
  # 双GPU测试
  python -m gpu_benchmark_linux --gpu-model A10 --multi-gpu 2
  
  # 横向比较多个GPU
  python -m gpu_benchmark_linux --compare T4,A10,V100 --comparison-type horizontal
  
  # 自定义参数
  python -m gpu_benchmark_linux --gpu-model A100 --duration 600 --matrix-size 8192
        """
    )
    
    # 基本参数
    parser.add_argument('--test', 
                       choices=['all', 'env', 'cuda', 'model', 'stress', 'demo'], 
                       default='all',
                       help='指定要运行的测试类型')
    
    parser.add_argument('--duration', 
                       type=int, 
                       help='GPU烧机测试持续时间（秒）')
    
    parser.add_argument('--output', 
                       type=str, 
                       default='gpu_benchmark_linux_results',
                       help='测试结果输出目录')
    
    # GPU型号相关参数
    parser.add_argument('--gpu-model', 
                       type=str,
                       help='指定GPU型号 (如: T4, A10, A100, V100, L40, H20)')
    
    parser.add_argument('--list-gpus', 
                       action='store_true',
                       help='列出所有支持的GPU型号')
    
    parser.add_argument('--gpu-info', 
                       type=str,
                       help='显示指定GPU型号的详细信息')
    
    # 测试类型参数
    parser.add_argument('--test-type', 
                       choices=['short', 'medium', 'long'],
                       default='medium',
                       help='测试持续时间类型')
    
    # 多GPU参数
    parser.add_argument('--multi-gpu', 
                       type=int,
                       help='多GPU测试，指定GPU数量')
    
    parser.add_argument('--device-ids', 
                       type=str,
                       help='指定GPU设备ID，用逗号分隔 (如: 0,1,2)')
    
    # 比较测试参数
    parser.add_argument('--compare', 
                       type=str,
                       help='比较多个GPU型号，用逗号分隔 (如: T4,A10,V100)')
    
    parser.add_argument('--comparison-type', 
                       choices=['horizontal', 'vertical'],
                       default='vertical',
                       help='比较类型: horizontal(统一参数) 或 vertical(各自优化参数)')
    
    # 自定义参数
    parser.add_argument('--matrix-size', 
                       type=int,
                       help='矩阵大小')
    
    parser.add_argument('--memory-ratio', 
                       type=float,
                       help='内存使用比例 (0.1-1.0)')
    
    parser.add_argument('--temperature-limit', 
                       type=float,
                       help='温度限制 (摄氏度)')
    
    parser.add_argument('--power-limit-ratio', 
                       type=float,
                       help='功耗限制比例 (0.1-1.0)')
    
    # 其他选项
    parser.add_argument('--no-html', 
                       action='store_true',
                       help='不生成HTML报告')
    
    parser.add_argument('--enable-csv', 
                       action='store_true',
                       help='启用CSV数据记录')
    
    parser.add_argument('--enable-optimization', 
                       action='store_true', 
                       default=True,
                       help='启用内存和性能优化 (默认启用)')
    
    parser.add_argument('--disable-optimization', 
                       action='store_true',
                       help='禁用内存和性能优化')
    
    parser.add_argument('--enable-multi-precision', 
                       action='store_true', 
                       default=True,
                       help='启用多精度性能分析 (默认启用)')
    
    parser.add_argument('--disable-multi-precision', 
                       action='store_true',
                       help='禁用多精度性能分析')
    
    parser.add_argument('--verbose', '-v', 
                       action='store_true',
                       help='详细输出')
    
    return parser


def handle_list_gpus():
    """处理列出GPU型号命令"""
    print("支持的GPU型号:")
    print("=" * 50)
    
    gpus = list_supported_gpus()
    for gpu in gpus:
        profile = gpu_profile_manager.get_profile(gpu)
        if profile:
            print(f"• {gpu:<12} - {profile.name}")
            print(f"  显存: {profile.memory_gb}GB, 带宽: {profile.memory_bandwidth_gbps}GB/s")
            print(f"  CUDA核心: {profile.cuda_cores}, TDP: {profile.tdp_watts}W")
            print()


def handle_gpu_info(gpu_name: str):
    """处理显示GPU信息命令"""
    info = gpu_profile_manager.get_profile_info(gpu_name)
    if not info:
        print(f"错误: 未找到GPU型号 '{gpu_name}'")
        print("使用 --list-gpus 查看支持的GPU型号")
        return False
    
    print(f"GPU型号: {info['name']}")
    print("=" * 50)
    print(f"计算能力: {info['compute_capability']}")
    print(f"显存大小: {info['memory_gb']} GB")
    print(f"内存带宽: {info['memory_bandwidth_gbps']} GB/s")
    print(f"CUDA核心: {info['cuda_cores']}")
    if info['tensor_cores']:
        print(f"Tensor核心: {info['tensor_cores']}")
    print(f"基础时钟: {info['base_clock_mhz']} MHz")
    print(f"加速时钟: {info['boost_clock_mhz']} MHz")
    print(f"TDP功耗: {info['tdp_watts']} W")
    print()
    print("推荐测试参数:")
    print(f"• 矩阵大小: {info['recommended_matrix_size']}")
    print(f"• 内存使用比例: {info['memory_usage_ratio']}")
    print(f"• 温度限制: {info['temperature_limit']}°C")
    print(f"• 短测试时长: {info['test_duration_short']}秒")
    print(f"• 中等测试时长: {info['test_duration_medium']}秒")
    print(f"• 长测试时长: {info['test_duration_long']}秒")
    
    return True


def handle_comparison_test(gpu_names: List[str], comparison_type: str, test_type: str, output_dir: str):
    """处理比较测试"""
    print(f"开始{comparison_type}比较测试...")
    print(f"GPU型号: {', '.join(gpu_names)}")
    print(f"比较类型: {comparison_type}")
    print(f"测试类型: {test_type}")
    print("=" * 50)
    
    # 创建比较配置
    configs = gpu_profile_manager.create_comparison_configs(
        gpu_names, test_type, comparison_type
    )
    
    if not configs:
        print("错误: 无法创建比较配置")
        return False
    
    # 运行比较测试
    tester = GPUStressTester()
    results = {}
    
    for gpu_name, config in configs.items():
        print(f"\n开始测试 {gpu_name}...")
        try:
            result = tester.run_stress_test(config)
            results[gpu_name] = result
            
            if result.success:
                gflops = result.performance_metrics.get('total_gflops', 0) if result.performance_metrics else 0
                print(f"✅ {gpu_name} 测试完成 - GFLOPS: {gflops:.2f}")
            else:
                print(f"❌ {gpu_name} 测试失败: {result.error_message}")
                
        except Exception as e:
            print(f"❌ {gpu_name} 测试异常: {e}")
            results[gpu_name] = None
    
    # 生成比较报告
    print(f"\n比较测试结果:")
    print("=" * 50)
    
    for gpu_name, result in results.items():
        if result and result.success:
            metrics = result.performance_metrics
            gflops = metrics.get('total_gflops', 0)
            temp_stats = metrics.get('temperature_stats', {})
            power_stats = metrics.get('power_stats', {})
            
            print(f"{gpu_name}:")
            print(f"  GFLOPS: {gflops:.2f}")
            if temp_stats:
                print(f"  温度: {temp_stats.get('avg', 0):.1f}°C (最高: {temp_stats.get('max', 0):.1f}°C)")
            if power_stats:
                print(f"  功耗: {power_stats.get('avg', 0):.1f}W (最高: {power_stats.get('max', 0):.1f}W)")
            print(f"  测试时长: {result.duration:.1f}秒")
        else:
            print(f"{gpu_name}: 测试失败")
        print()
    
    return True


def setup_custom_logging(log_file=None, level='INFO'):
    """设置自定义日志"""
    import logging
    
    # 创建新的logger
    custom_logger = logging.getLogger("gpu_benchmark_main")
    custom_logger.setLevel(getattr(logging, level.upper()))
    
    # 清除现有处理器
    custom_logger.handlers.clear()
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # 格式化器
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    custom_logger.addHandler(console_handler)
    
    # 文件处理器
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        custom_logger.addHandler(file_handler)
    
    return custom_logger


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 处理特殊命令
    if args.list_gpus:
        handle_list_gpus()
        return 0
    
    if args.gpu_info:
        if handle_gpu_info(args.gpu_info):
            return 0
        else:
            return 1
    
    # 处理比较测试
    if args.compare:
        gpu_names = [name.strip() for name in args.compare.split(',')]
        if handle_comparison_test(gpu_names, args.comparison_type, args.test_type, args.output):
            return 0
        else:
            return 1
    
    # 显示工具信息
    print("=" * 60)
    print("      GPU基准测试工具 v0.1.9")
    print("=" * 60)
    print(f"测试类型: {args.test}")
    print(f"输出目录: {args.output}")
    
    if args.gpu_model:
        print(f"GPU型号: {args.gpu_model}")
        print(f"测试类型: {args.test_type}")
    
    if args.multi_gpu:
        print(f"多GPU测试: {args.multi_gpu}个GPU")
    
    print()
    
    # 创建输出目录
    os.makedirs(args.output, exist_ok=True)
    
    # 设置日志文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(args.output, f"benchmark_{timestamp}.log")
    
    # 设置自定义日志
    main_logger = setup_custom_logging(
        log_file=log_file, 
        level='DEBUG' if args.verbose else 'INFO'
    )
    
    main_logger.info("")
    main_logger.info("===== 初始化测试环境 =====")
    main_logger.info(f"测试结果将保存至：{os.path.abspath(log_file)}")
    main_logger.info("")
    
    try:
        # 根据参数选择测试方式
        if args.gpu_model:
            # 使用GPU型号配置
            return run_gpu_model_test(args, main_logger)
        else:
            # 使用传统测试方式
            return run_traditional_test(args, main_logger)
            
    except KeyboardInterrupt:
        main_logger.info("用户中断测试")
        return 1
    except Exception as e:
        main_logger.error(f"测试执行失败: {e}")
        return 1


def run_gpu_model_test(args, main_logger):
    """运行基于GPU型号的测试"""
    # 解析设备ID
    device_ids = None
    if args.device_ids:
        try:
            device_ids = [int(x.strip()) for x in args.device_ids.split(',')]
        except ValueError:
            main_logger.error("设备ID格式错误，应为数字，用逗号分隔")
            return 1
    elif args.multi_gpu:
        device_ids = list(range(args.multi_gpu))
    
    # 创建自定义参数
    custom_params = {}
    if args.duration:
        custom_params['duration'] = args.duration
    if args.matrix_size:
        custom_params['matrix_size'] = args.matrix_size
    if args.memory_ratio:
        custom_params['memory_usage_ratio'] = args.memory_ratio
    if args.temperature_limit:
        custom_params['temperature_limit'] = args.temperature_limit
    if args.power_limit_ratio:
        custom_params['power_limit_ratio'] = args.power_limit_ratio
    
    # 创建测试配置
    config = gpu_profile_manager.create_stress_config(
        args.gpu_model,
        args.test_type,
        device_ids,
        custom_params
    )
    
    if not config:
        main_logger.error(f"未找到GPU型号 '{args.gpu_model}' 的配置")
        main_logger.info("使用 --list-gpus 查看支持的GPU型号")
        return 1
    
    # 显示配置信息
    profile = gpu_profile_manager.get_profile(args.gpu_model)
    if profile:
        main_logger.info(f"使用 {profile.name} 的优化配置:")
        main_logger.info(f"• 矩阵大小: {config.matrix_size}")
        main_logger.info(f"• 内存使用比例: {config.memory_usage_ratio}")
        main_logger.info(f"• 温度限制: {config.temperature_limit}°C")
        main_logger.info(f"• 测试持续时间: {config.duration}秒")
        if device_ids:
            main_logger.info(f"• 设备ID: {device_ids}")
    
    # 运行压力测试
    main_logger.info("开始GPU压力测试...")
    tester = GPUStressTester()
    result = tester.run_stress_test(config)
    
    # 输出结果
    if result.success:
        main_logger.info("✅ GPU压力测试成功完成")
        
        # 显示性能指标
        metrics = result.performance_metrics
        if 'total_gflops' in metrics:
            main_logger.info(f"总计算性能: {metrics['total_gflops']:.2f} GFLOPS")
        
        if 'temperature_stats' in metrics:
            temp_stats = metrics['temperature_stats']
            main_logger.info(f"温度范围: {temp_stats['min']:.1f}°C - {temp_stats['max']:.1f}°C (平均: {temp_stats['avg']:.1f}°C)")
        
        if 'power_stats' in metrics:
            power_stats = metrics['power_stats']
            main_logger.info(f"功耗范围: {power_stats['min']:.1f}W - {power_stats['max']:.1f}W (平均: {power_stats['avg']:.1f}W)")
        
        # 导出结果
        json_file = os.path.join(args.output, f"stress_test_{int(result.start_time)}.json")
        tester.export_result(result, json_file)
        main_logger.info(f"详细测试结果已保存至: {json_file}")
        
        return 0
    else:
        main_logger.error("❌ GPU压力测试失败")
        if result.error_message:
            main_logger.error(f"错误信息: {result.error_message}")
        return 1


def run_traditional_test(args, main_logger):
    """运行传统测试方式"""
    if args.test == 'stress':
        # 运行压力测试
        return run_stress_test(args, main_logger)
    elif args.test == 'demo':
        # 运行演示测试
        return run_demo_test_cmd(args, main_logger)
    
    # 确定是否启用多精度分析（默认启用）
    enable_multi_precision = args.enable_multi_precision and not args.disable_multi_precision
    enable_optimization = args.enable_optimization and not args.disable_optimization
    
    benchmark = GPUBenchmark(
        device_id=0, 
        enable_optimization=enable_optimization,
        enable_multi_precision=enable_multi_precision
    )
    
    if enable_multi_precision:
        main_logger.info("✅ 多精度性能分析已启用 - 将显示FP64/FP32/FP16/FP8/INT8/INT4指标")
    else:
        main_logger.info("⚠️ 多精度性能分析已禁用")
    
    if args.test == 'all':
        success = benchmark.run_all_tests()
    elif args.test == 'env':
        success = benchmark.check_environment()
    elif args.test == 'cuda':
        # 使用正确的方法名
        benchmark.check_environment()
        benchmark.install_python_deps()
        benchmark.test_cuda_basics()
        success = True
    elif args.test == 'model':
        # 使用正确的方法名
        benchmark.check_environment()
        benchmark.install_python_deps()
        benchmark.test_model_inference()
        success = True
    else:
        main_logger.error(f"未知的测试类型: {args.test}")
        return 1
    
    return 0 if success else 1


def run_stress_test(args, main_logger):
    """运行压力测试"""
    from .stress_test import StressTestConfig, GPUStressTester
    
    # 确定是否启用优化
    enable_optimization = args.enable_optimization and not args.disable_optimization
    
    # 解析设备ID
    device_ids = None
    if args.device_ids:
        try:
            device_ids = [int(x.strip()) for x in args.device_ids.split(',')]
        except ValueError:
            main_logger.error("设备ID格式错误，应为数字，用逗号分隔")
            return 1
    elif args.multi_gpu:
        device_ids = list(range(args.multi_gpu))
    
    # 创建测试配置
    config = StressTestConfig(
        duration=args.duration or 60,
        device_ids=device_ids or [],
        matrix_size=args.matrix_size or 4096,
        memory_usage_ratio=args.memory_ratio or 0.8,
        temperature_limit=args.temperature_limit or 90.0,
        power_limit_ratio=args.power_limit_ratio or 0.95,
        test_types=['matrix_multiply', 'compute_intensive', 'memory_bandwidth']
    )
    
    main_logger.info("开始GPU压力测试...")
    main_logger.info(f"测试配置:")
    main_logger.info(f"• 持续时间: {config.duration}秒")
    main_logger.info(f"• 矩阵大小: {config.matrix_size}")
    main_logger.info(f"• 内存使用比例: {config.memory_usage_ratio}")
    main_logger.info(f"• 温度限制: {config.temperature_limit}°C")
    main_logger.info(f"• 内存和性能优化: {'已启用' if enable_optimization else '已禁用'}")
    if device_ids:
        main_logger.info(f"• 设备ID: {device_ids}")
    if hasattr(args, 'enable_csv') and args.enable_csv:
        main_logger.info("• CSV数据记录: 已启用")
    
    # 根据优化设置选择测试器
    if enable_optimization:
        try:
            from .optimized_stress_test import OptimizedStressTest
            tester = OptimizedStressTest(device_id=device_ids[0] if device_ids else 0)
            main_logger.info("✅ 使用优化版压力测试器")
        except ImportError as e:
            main_logger.warning(f"无法导入优化版测试器，使用标准版: {e}")
            tester = GPUStressTester(enable_csv_logging=getattr(args, 'enable_csv', False))
    else:
        tester = GPUStressTester(enable_csv_logging=getattr(args, 'enable_csv', False))
    
    try:
        result = tester.run_stress_test(config)
        
        if result.success:
            main_logger.info("✅ GPU压力测试成功完成")
            
            # 显示性能指标
            metrics = result.performance_metrics
            if 'total_gflops' in metrics:
                main_logger.info(f"总计算性能: {metrics['total_gflops']:.2f} GFLOPS")
            
            if 'temperature_stats' in metrics:
                temp_stats = metrics['temperature_stats']
                main_logger.info(f"温度范围: {temp_stats['min']:.1f}°C - {temp_stats['max']:.1f}°C (平均: {temp_stats['avg']:.1f}°C)")
            
            if 'power_stats' in metrics:
                power_stats = metrics['power_stats']
                main_logger.info(f"功耗范围: {power_stats['min']:.1f}W - {power_stats['max']:.1f}W (平均: {power_stats['avg']:.1f}W)")
            
            # 导出结果
            json_file = os.path.join(args.output, f"stress_test_{int(result.start_time)}.json")
            tester.export_result(result, json_file)
            main_logger.info(f"详细测试结果已保存至: {json_file}")
            
            # 如果启用了CSV记录，显示CSV文件信息
            if hasattr(tester, 'csv_logger') and tester.csv_logger:
                csv_file = tester.csv_logger.get_filepath()
                record_count = tester.csv_logger.get_record_count()
                main_logger.info(f"CSV数据文件: {csv_file}")
                main_logger.info(f"记录数据条数: {record_count}")
            
            return 0
        else:
            main_logger.error("❌ GPU压力测试失败")
            if result.error_message:
                main_logger.error(f"错误信息: {result.error_message}")
            return 1
            
    except Exception as e:
        main_logger.error(f"压力测试执行异常: {e}")
        return 1


def run_demo_test_cmd(args, main_logger):
    """运行演示测试命令"""
    from .demo_test import DemoTestConfig, DemoGPUTester
    
    main_logger.info("开始演示GPU压力测试（模拟数据）...")
    
    # 创建演示测试配置
    config = DemoTestConfig(
        duration=args.duration or 30,
        device_count=args.multi_gpu or 2,
        sample_interval=1.0,
        enable_csv=getattr(args, 'enable_csv', False)
    )
    
    main_logger.info(f"演示测试配置:")
    main_logger.info(f"• 持续时间: {config.duration}秒")
    main_logger.info(f"• 模拟设备数: {config.device_count}")
    main_logger.info(f"• 采样间隔: {config.sample_interval}秒")
    if config.enable_csv:
        main_logger.info("• CSV数据记录: 已启用")
    
    # 运行演示测试
    tester = DemoGPUTester()
    
    try:
        result = tester.run_demo_test(config)
        
        if result['success']:
            main_logger.info("✅ 演示测试成功完成")
            main_logger.info(f"实际运行时间: {result['duration']:.1f}秒")
            main_logger.info(f"总采样数: {result['total_samples']}")
            
            # 显示统计信息
            stats = result.get('statistics', {})
            for device_key, device_stats in stats.items():
                main_logger.info(f"{device_key} 统计:")
                temp_stats = device_stats.get('temperature', {})
                if temp_stats:
                    main_logger.info(f"  温度: {temp_stats['min']:.1f}°C - {temp_stats['max']:.1f}°C (平均: {temp_stats['avg']:.1f}°C)")
                
                power_stats = device_stats.get('power_usage', {})
                if power_stats:
                    main_logger.info(f"  功耗: {power_stats['min']:.1f}W - {power_stats['max']:.1f}W (平均: {power_stats['avg']:.1f}W)")
            
            # 如果启用了CSV记录，显示CSV文件信息和分析
            csv_file = tester.get_csv_filepath()
            if csv_file and config.enable_csv:
                main_logger.info(f"CSV数据文件: {csv_file}")
                
                # 演示CSV数据分析
                try:
                    from .demo_test import demo_csv_analysis
                    main_logger.info("开始CSV数据分析...")
                    demo_csv_analysis(str(csv_file))
                except Exception as e:
                    main_logger.warning(f"CSV数据分析失败: {e}")
            
            return 0
        else:
            main_logger.error("❌ 演示测试失败")
            if 'error' in result:
                main_logger.error(f"错误信息: {result['error']}")
            return 1
            
    except Exception as e:
        main_logger.error(f"演示测试执行异常: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
