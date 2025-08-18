"""
命令行入口点 - 提供命令行界面
"""

import sys
import argparse
from pathlib import Path

from .benchmark import GPUBenchmark
from .utils import GREEN, RED, YELLOW, BLUE, RESET

def main():
    """主函数，处理命令行参数并运行测试"""
    parser = argparse.ArgumentParser(description="GPU基准测试工具")
    
    # 添加参数
    parser.add_argument("--test", choices=["all", "env", "cuda", "model"], default="all",
                        help="指定要运行的测试类型")
    parser.add_argument("--duration", type=int, default=60,
                        help="GPU烧机测试持续时间（秒）")
    parser.add_argument("--output", type=str, default="./gpu_benchmark_linux_results",
                        help="测试结果输出目录")
    
    # 解析参数
    args = parser.parse_args()
    
    # 创建输出目录
    Path(args.output).mkdir(exist_ok=True)
    
    # 打印欢迎信息
    print(f"{GREEN}===================================={RESET}")
    print(f"{BLUE}      GPU基准测试工具 v0.1.0        {RESET}")
    print(f"{GREEN}===================================={RESET}")
    print(f"测试类型: {args.test}")
    print(f"输出目录: {args.output}")
    print()
    
    # 创建测试实例
    benchmark = GPUBenchmark()
    
    # 运行测试
    success = False
    if args.test == "all":
        success = benchmark.run_all_tests()
    else:
        success = benchmark.run_specific_test(args.test)
    
    # 返回状态码
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())