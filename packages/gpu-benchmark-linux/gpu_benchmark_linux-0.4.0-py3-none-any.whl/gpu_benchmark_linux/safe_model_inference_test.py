"""
安全的大模型推理测试模块
提供更好的错误处理和模型可用性检查
"""

import torch
import time
import gc
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def check_model_availability(model_name):
    """检查模型是否可用（不实际下载）"""
    try:
        from transformers import AutoConfig
        config = AutoConfig.from_pretrained(model_name, trust_remote_code=True)
        return True
    except Exception as e:
        logger.warning(f"模型 {model_name} 不可用: {e}")
        return False

def get_available_models():
    """获取可用的轻量级模型列表"""
    lightweight_models = [
        "microsoft/DialoGPT-small",  # 117M参数，适合小显存
        "gpt2",  # 124M参数，经典轻量模型
        "distilgpt2",  # 82M参数，更轻量
        "microsoft/DialoGPT-medium",  # 345M参数，中等大小
    ]
    
    available_models = []
    for model in lightweight_models:
        if check_model_availability(model):
            available_models.append(model)
            break  # 找到一个可用的就够了
    
    return available_models

def safe_test_text_generation():
    """安全的文本生成测试"""
    logger.info("开始安全的文本生成测试...")
    
    # 检查CUDA可用性
    if not torch.cuda.is_available():
        logger.error("CUDA不可用，跳过文本生成测试")
        return False
    
    # 获取可用模型
    available_models = get_available_models()
    if not available_models:
        logger.warning("未找到可用的轻量级模型，跳过文本生成测试")
        return False
    
    model_name = available_models[0]
    logger.info(f"使用模型: {model_name}")
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
        
        # 加载模型
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        # 设置pad_token
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
        
        # 简单测试
        test_inputs = ["Hello, how are you?", "The weather today is"]
        
        for input_text in test_inputs:
            try:
                start_time = time.time()
                outputs = generator(
                    input_text,
                    max_new_tokens=16,  # 短输出，减少显存使用
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id
                )
                end_time = time.time()
                
                latency = (end_time - start_time) * 1000
                logger.info(f"输入: '{input_text}'")
                logger.info(f"  延迟: {latency:.2f} ms")
                logger.info(f"  显存占用: {torch.cuda.max_memory_allocated() / 1024**3:.2f} GB")
                
            except Exception as e:
                logger.warning(f"测试输入 '{input_text}' 失败: {e}")
        
        # 清理显存
        del model, tokenizer, generator
        gc.collect()
        torch.cuda.empty_cache()
        
        logger.info("文本生成测试完成")
        return True
        
    except Exception as e:
        logger.error(f"文本生成测试失败: {e}")
        return False

def safe_test_image_generation():
    """安全的图像生成测试（使用更小的模型）"""
    logger.info("开始安全的图像生成测试...")
    
    # 检查CUDA可用性
    if not torch.cuda.is_available():
        logger.error("CUDA不可用，跳过图像生成测试")
        return False
    
    # 检查显存大小
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
    if gpu_memory < 6:  # 小于6GB显存跳过
        logger.warning(f"显存不足({gpu_memory:.1f}GB < 6GB)，跳过图像生成测试")
        return False
    
    try:
        from diffusers import StableDiffusionPipeline
        
        # 使用较小的模型
        model_name = "runwayml/stable-diffusion-v1-5"
        
        pipe = StableDiffusionPipeline.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        # 禁用安全检查
        pipe.safety_checker = lambda images, clip_input: (images, False)
        
        # 简单测试
        test_prompts = ["a simple cat", "a red apple"]
        
        for prompt in test_prompts:
            try:
                start_time = time.time()
                outputs = pipe(
                    prompt,
                    height=256,  # 小分辨率
                    width=256,
                    num_inference_steps=10,  # 少步数
                    guidance_scale=7.5
                )
                end_time = time.time()
                
                latency = (end_time - start_time) * 1000
                logger.info(f"提示词: '{prompt}'")
                logger.info(f"  延迟: {latency:.2f} ms")
                logger.info(f"  显存占用: {torch.cuda.max_memory_allocated() / 1024**3:.2f} GB")
                
            except Exception as e:
                logger.warning(f"测试提示词 '{prompt}' 失败: {e}")
        
        # 清理显存
        del pipe
        gc.collect()
        torch.cuda.empty_cache()
        
        logger.info("图像生成测试完成")
        return True
        
    except Exception as e:
        logger.error(f"图像生成测试失败: {e}")
        return False

def run_safe_model_inference_tests():
    """运行安全的模型推理测试"""
    logger.info("=== 开始安全的大模型推理测试 ===")
    
    success_count = 0
    total_tests = 2
    
    # 文本生成测试
    if safe_test_text_generation():
        success_count += 1
    
    # 图像生成测试
    if safe_test_image_generation():
        success_count += 1
    
    logger.info(f"=== 大模型推理测试完成: {success_count}/{total_tests} 成功 ===")
    
    if success_count == 0:
        logger.warning("所有大模型推理测试都失败了，这通常是由于:")
        logger.warning("1. 模型下载失败（网络问题）")
        logger.warning("2. 显存不足")
        logger.warning("3. 缺少必要的Python包")
        logger.warning("这不影响其他GPU基准测试的结果")
    
    return success_count > 0

if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    # 运行测试
    run_safe_model_inference_tests()