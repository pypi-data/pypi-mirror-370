# GPU基准测试工具

这是一个用于测试NVIDIA GPU性能的综合工具，可以评估GPU的各项性能指标。

## 功能特点

- 环境检查：自动检测NVIDIA驱动、CUDA和PyTorch环境
- 系统依赖安装：自动安装必要的系统依赖
- CUDA基础能力测试：包括设备信息查询和内存带宽测试
- GPU计算性能与稳定性测试：使用gpu-burn进行压力测试
- 大模型推理测试：测试Stable Diffusion和LLaMA等模型的推理性能

## 安装方法

```bash
# 从PyPI安装
pip install gpu-benchmark-linux

# 或者从源码安装
git clone https://github.com/yourusername/gpu-benchmark-linux.git
cd gpu-benchmark-linux
pip install -e .
```

## 使用方法

```bash
# 运行完整测试
gpu-benchmark-linux

# 或者使用Python模块方式运行
python -m gpu-benchmark-linux

# 运行特定测试
gpu-benchmark-linux --test cuda
gpu-benchmark-linux --test model
```

## 测试结果

测试结果将保存在`./gpu-benchmark-linux_results`目录下，包含详细的日志信息。

## 系统要求

- NVIDIA GPU
- NVIDIA驱动
- CUDA Toolkit（推荐）
- Python 3.7+