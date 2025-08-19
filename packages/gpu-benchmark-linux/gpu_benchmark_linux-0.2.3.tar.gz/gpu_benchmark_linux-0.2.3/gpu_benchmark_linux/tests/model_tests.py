"""
模型测试模块 - 提供大模型推理测试功能
"""

import os
import time
import gc
from pathlib import Path

from ..utils import logger

def create_model_test_script():
    """创建模型测试脚本"""
    script_content = '''import torch
import time
import gc
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from diffusers import StableDiffusionPipeline

# 测试配置
TEST_CASES = {
    # 文本生成模型(LLaMA类，可替换为实际可用的模型)
    "text_model": {
        "model_name": "decapoda-research/llama-7b-hf",  # 7B模型，适合12GB+显存
        "input_texts": ["The future of AI is", "Explain quantum computing in simple terms"],
        "max_new_tokens": [32, 64],  # 测试不同生成长度
        "batch_sizes": [1, 2]  # 测试不同批量
    },
    # 图像生成模型(Stable Diffusion，ComfyUI常用)
    "image_model": {
        "model_name": "runwayml/stable-diffusion-v1-5",
        "prompts": ["a photo of a cat", "a futuristic cityscape"],
        "resolutions": [(512, 512), (768, 768)],  # 测试不同分辨率
        "batch_sizes": [1]  # 高分辨率下批量设为1，避免显存不足
    }
}

def test_text_generation(model_name, input_texts, max_new_tokens_list, batch_sizes):
    """测试文本生成模型推理性能"""
    print(f"\\n--- 文本生成模型测试：{model_name} ---")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,  # 用半精度节省显存
            device_map="auto"
        )
        generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
    except Exception as e:
        print(f"模型加载失败：{e}")
        return

    for batch_size in batch_sizes:
        for input_text in input_texts:
            for max_new_tokens in max_new_tokens_list:
                # 构造批量输入
                inputs = [input_text] * batch_size
                try:
                    # 预热(排除首次加载耗时)
                    generator(inputs, max_new_tokens=8, do_sample=False)
                    
                    # 正式测试
                    start_time = time.time()
                    outputs = generator(
                        inputs,
                        max_new_tokens=max_new_tokens,
                        do_sample=False,
                        num_return_sequences=1
                    )
                    end_time = time.time()
                    
                    # 计算指标
                    total_tokens = sum(len(output["generated_text"]) for output in outputs)
                    latency = (end_time - start_time) * 1000  # 延迟(毫秒)
                    throughput = (batch_size * max_new_tokens) / (end_time - start_time)  # 每秒生成token数
                    
                    print(f"批量大小: {batch_size}, 输入: '{input_text}', 生成长度: {max_new_tokens}")
                    print(f"  延迟: {latency:.2f} ms, 吞吐量: {throughput:.2f} tokens/sec")
                    print(f"  显存占用: {torch.cuda.max_memory_allocated() / 1024**3:.2f} GB")
                    
                except Exception as e:
                    print(f"测试失败(批量{batch_size}，长度{max_new_tokens})：{e}")
        
    # 清理显存
    del model, tokenizer, generator
    gc.collect()
    torch.cuda.empty_cache()

def test_image_generation(model_name, prompts, resolutions, batch_sizes):
    """测试图像生成模型推理性能(Stable Diffusion)"""
    print(f"\\n--- 图像生成模型测试：{model_name} ---")
    try:
        pipe = StableDiffusionPipeline.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        # 禁用安全检查(服务器环境无需)
        pipe.safety_checker = lambda images, clip_input: (images, False)
    except Exception as e:
        print(f"模型加载失败：{e}")
        return

    for batch_size in batch_sizes:
        for prompt in prompts:
            for (height, width) in resolutions:
                # 构造批量输入
                inputs = [prompt] * batch_size
                try:
                    # 预热
                    pipe(inputs, height=256, width=256, num_inference_steps=10)
                    
                    # 正式测试
                    start_time = time.time()
                    outputs = pipe(
                        inputs,
                        height=height,
                        width=width,
                        num_inference_steps=30,  # 标准步数
                        guidance_scale=7.5
                    )
                    end_time = time.time()
                    
                    # 计算指标
                    latency = (end_time - start_time) * 1000  # 延迟(毫秒)
                    throughput = batch_size / (end_time - start_time)  # 每秒生成图像数
                    
                    print(f"批量大小: {batch_size}, 提示词: '{prompt}', 分辨率: {width}x{height}")
                    print(f"  延迟: {latency:.2f} ms, 吞吐量: {throughput:.2f} images/sec")
                    print(f"  显存占用: {torch.cuda.max_memory_allocated() / 1024**3:.2f} GB")
                    
                except Exception as e:
                    print(f"测试失败(批量{batch_size}，分辨率{width}x{height})：{e}")
    
    # 清理显存
    del pipe
    gc.collect()
    torch.cuda.empty_cache()

if __name__ == "__main__":
    # 检查CUDA
    if not torch.cuda.is_available():
        print("ERROR: CUDA不可用，无法进行模型推理测试")
        exit(1)
    
    # 运行测试
    test_text_generation(**TEST_CASES["text_model"])
    test_image_generation(**TEST_CASES["image_model"])
'''
    
    # 写入脚本文件
    with open("model_inference_test.py", "w") as f:
        f.write(script_content)
    
    return Path("model_inference_test.py")

def run_model_tests():
    """运行模型测试"""
    try:
        import torch
        
        # 检查CUDA可用性
        if not torch.cuda.is_available():
            logger.error("CUDA不可用，无法进行模型推理测试")
            return False
        
        # 确保测试脚本存在
        script_path = Path("model_inference_test.py")
        if not script_path.exists():
            script_path = create_model_test_script()
        
        # 导入并运行测试
        import importlib.util
        spec = importlib.util.spec_from_file_location("model_test", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 运行测试
        if hasattr(module, "test_text_generation"):
            module.test_text_generation(**module.TEST_CASES["text_model"])
        
        if hasattr(module, "test_image_generation"):
            module.test_image_generation(**module.TEST_CASES["image_model"])
        
        return True
    
    except ImportError as e:
        logger.error(f"缺少必要的Python包: {e}")
        return False
    except Exception as e:
        logger.error(f"运行模型测试时出错: {e}")
        return False