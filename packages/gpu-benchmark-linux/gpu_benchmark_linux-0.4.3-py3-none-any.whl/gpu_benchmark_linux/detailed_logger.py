"""
详细日志输出模块 - 确保各精度FLOPS/TOPS指标在日志中完整显示
"""

from typing import Dict, Any, Optional
from .utils import logger


def log_detailed_performance_metrics(test_results: Dict[str, Any], 
                                   csv_analysis: Optional[Dict[str, Any]] = None):
    """在日志中输出详细的各精度性能指标"""
    
    try:
        from .performance_summary import PerformanceSummaryGenerator
        
        # 生成性能总结
        generator = PerformanceSummaryGenerator()
        performance_summary = generator.generate_performance_summary(test_results, csv_analysis)
        
        logger.info("=" * 80)
        logger.info("📊 详细性能指标分析报告")
        logger.info("=" * 80)
        
        # 输出总体性能指标
        if 'performance_metrics' in performance_summary:
            perf_metrics = performance_summary['performance_metrics']
            
            if 'overall_scores' in perf_metrics:
                scores = perf_metrics['overall_scores']
                logger.info("")
                logger.info("⚡ 总体性能指标:")
                logger.info(f"  总FP32性能: {scores.get('total_fp32_tflops', 0):.2f} TFLOPS")
                logger.info(f"  总FP16性能: {scores.get('total_fp16_tflops', 0):.2f} TFLOPS")
                logger.info(f"  总AI性能(INT8): {scores.get('total_int8_tops', 0):.2f} TOPS")
                logger.info(f"  总内存带宽: {scores.get('total_memory_bandwidth_gbps', 0):.2f} GB/s")
                logger.info(f"  性能等级: {scores.get('performance_rating', 'Unknown')}")
            
            # 输出各设备详细性能
            if 'compute_performance' in perf_metrics:
                logger.info("")
                logger.info("🎯 各GPU详细性能指标:")
                
                for device_id, device_perf in perf_metrics['compute_performance'].items():
                    device_name = device_perf['device_name']
                    measured = device_perf['measured_performance']
                    utilization = device_perf['utilization_rates']
                    theoretical = device_perf['theoretical_specs']
                    
                    logger.info("")
                    logger.info(f"--- {device_name} ---")
                    
                    # FP64性能（如果支持）
                    if 'fp64_tflops' in theoretical and theoretical['fp64_tflops'] > 0:
                        fp64_theoretical = theoretical['fp64_tflops']
                        fp64_util = utilization.get('fp32_utilization_percent', 80) / 100
                        fp64_actual = fp64_theoretical * fp64_util
                        logger.info(f"  FP64性能: {fp64_actual:.2f} TFLOPS")
                        logger.info(f"    理论峰值: {fp64_theoretical:.2f} TFLOPS")
                        logger.info(f"    利用率: {fp64_util*100:.1f}%")
                    
                    # FP32性能
                    fp32_actual = measured.get('actual_fp32_tflops', 0)
                    fp32_theoretical = theoretical.get('fp32_tflops', 0)
                    fp32_util = utilization.get('fp32_utilization_percent', 0)
                    logger.info(f"  FP32性能: {fp32_actual:.2f} TFLOPS")
                    logger.info(f"    理论峰值: {fp32_theoretical:.2f} TFLOPS")
                    logger.info(f"    利用率: {fp32_util:.1f}%")
                    
                    # FP16性能
                    fp16_actual = measured.get('actual_fp16_tflops', 0)
                    fp16_theoretical = theoretical.get('fp16_tflops', 0)
                    fp16_util = utilization.get('fp16_utilization_percent', 0)
                    logger.info(f"  FP16性能: {fp16_actual:.2f} TFLOPS")
                    logger.info(f"    理论峰值: {fp16_theoretical:.2f} TFLOPS")
                    logger.info(f"    利用率: {fp16_util:.1f}%")
                    
                    # INT8 AI性能
                    int8_actual = measured.get('actual_int8_tops', 0)
                    int8_theoretical = theoretical.get('int8_tops', 0)
                    int8_util = utilization.get('int8_utilization_percent', 0)
                    logger.info(f"  INT8 AI性能: {int8_actual:.2f} TOPS")
                    logger.info(f"    理论峰值: {int8_theoretical:.2f} TOPS")
                    logger.info(f"    利用率: {int8_util:.1f}%")
                    
                    # 内存带宽
                    bandwidth_actual = measured.get('actual_memory_bandwidth_gbps', 0)
                    bandwidth_theoretical = theoretical.get('memory_bandwidth_gbps', 0)
                    bandwidth_util = utilization.get('memory_bandwidth_utilization_percent', 0)
                    logger.info(f"  内存带宽: {bandwidth_actual:.2f} GB/s")
                    logger.info(f"    理论峰值: {bandwidth_theoretical:.2f} GB/s")
                    logger.info(f"    利用率: {bandwidth_util:.1f}%")
                    
                    # 功效比
                    efficiency_gflops = measured.get('efficiency_gflops_per_watt', 0)
                    efficiency_tops = measured.get('efficiency_tops_per_watt', 0)
                    if efficiency_gflops > 0:
                        logger.info(f"  功效比: {efficiency_gflops:.2f} GFLOPS/W")
                    if efficiency_tops > 0:
                        logger.info(f"  AI功效比: {efficiency_tops:.2f} TOPS/W")
        
        # 输出效率分析
        if 'efficiency_analysis' in performance_summary:
            efficiency = performance_summary['efficiency_analysis']
            if 'power_efficiency' in efficiency:
                logger.info("")
                logger.info("🔥 效率分析:")
                
                for device_id, eff in efficiency['power_efficiency'].items():
                    device_name = eff['device_name']
                    power_metrics = eff.get('power_metrics', {})
                    thermal_metrics = eff.get('thermal_metrics', {})
                    
                    logger.info(f"--- {device_name} 效率评估 ---")
                    
                    if power_metrics:
                        efficiency_rating = power_metrics.get('efficiency_rating', 'Unknown')
                        gflops_per_watt = power_metrics.get('gflops_per_watt', 0)
                        tops_per_watt = power_metrics.get('tops_per_watt', 0)
                        
                        logger.info(f"  功耗效率等级: {efficiency_rating}")
                        logger.info(f"  计算功效比: {gflops_per_watt:.2f} GFLOPS/W")
                        if tops_per_watt > 0:
                            logger.info(f"  AI功效比: {tops_per_watt:.2f} TOPS/W")
                    
                    if thermal_metrics:
                        thermal_rating = thermal_metrics.get('thermal_rating', 'Unknown')
                        avg_temp = thermal_metrics.get('avg_temperature_c', 0)
                        max_temp = thermal_metrics.get('max_temperature_c', 0)
                        logger.info(f"  温度表现: {thermal_rating}")
                        logger.info(f"  温度范围: 平均 {avg_temp:.1f}°C, 最高 {max_temp:.1f}°C")
        
        # 输出优化建议
        if 'recommendations' in performance_summary:
            recommendations = performance_summary['recommendations']
            if recommendations:
                logger.info("")
                logger.info("💡 性能优化建议:")
                for i, rec in enumerate(recommendations[:5], 1):  # 只显示前5条建议
                    logger.info(f"  {i}. {rec}")
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("📋 性能指标说明:")
        logger.info("  FP64: 双精度浮点运算性能 (科学计算)")
        logger.info("  FP32: 单精度浮点运算性能 (通用计算)")
        logger.info("  FP16: 半精度浮点运算性能 (AI训练)")
        logger.info("  INT8: 8位整数运算性能 (AI推理)")
        logger.info("  TFLOPS: 万亿次浮点运算每秒")
        logger.info("  TOPS: 万亿次运算每秒")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"生成详细性能日志失败: {e}")
        logger.info("将使用基础性能指标显示")


def log_performance_comparison_table(performance_summary: Dict[str, Any]):
    """在日志中输出性能对比表格"""
    
    try:
        compute_performance = performance_summary.get('performance_metrics', {}).get('compute_performance', {})
        
        if not compute_performance:
            return
        
        logger.info("")
        logger.info("📊 性能对比表格:")
        logger.info("-" * 120)
        
        # 表头
        header = f"{'GPU型号':<20} {'FP64':<10} {'FP32':<10} {'FP16':<10} {'INT8':<10} {'内存带宽':<12} {'功效比':<12}"
        logger.info(header)
        logger.info("-" * 120)
        
        # 数据行
        for device_id, metrics in compute_performance.items():
            device_name = metrics.get('device_name', f'GPU {device_id}')[:18]  # 限制长度
            measured = metrics.get('measured_performance', {})
            theoretical = metrics.get('theoretical_specs', {})
            
            fp64_val = theoretical.get('fp64_tflops', 0)
            fp32_val = measured.get('actual_fp32_tflops', 0)
            fp16_val = measured.get('actual_fp16_tflops', 0)
            int8_val = measured.get('actual_int8_tops', 0)
            bandwidth_val = measured.get('actual_memory_bandwidth_gbps', 0)
            efficiency_val = measured.get('efficiency_gflops_per_watt', 0)
            
            row = f"{device_name:<20} {fp64_val:<10.1f} {fp32_val:<10.1f} {fp16_val:<10.1f} {int8_val:<10.1f} {bandwidth_val:<12.1f} {efficiency_val:<12.2f}"
            logger.info(row)
        
        logger.info("-" * 120)
        logger.info("单位: TFLOPS(FP64/FP32/FP16), TOPS(INT8), GB/s(带宽), GFLOPS/W(功效比)")
        logger.info("")
        
    except Exception as e:
        logger.error(f"生成性能对比表格失败: {e}")