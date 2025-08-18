# MCP 验证码生成工具

## 项目概述
这是一个基于FastMCP构建的验证码生成工具包，提供多种类型的验证码生成功能，可以轻松集成到各种Python项目中。

## 功能特性
- 生成纯数字验证码
- 生成纯字母验证码（包含大小写）
- 生成字母和数字混合验证码
- 支持自定义验证码长度

## 安装方法

### 从PyPI安装（推荐）
```bash
# 使用pip安装（清华源）
pip install mcp-verification-code -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用官方源
pip install mcp-verification-code
```

### 从源码安装
```bash
# 克隆代码库
git clone https://github.com/yourusername/mcp-verification-code.git
cd mcp-verification-code

# 安装依赖
pip install -e .
```

## 使用方法

### 作为MCP服务器
```python
# 启动MCP服务器
from mcp_verification_code.verification_code import run_server

run_server()
```

### 直接在代码中使用
```python
# 导入验证码生成函数
from mcp_verification_code import (
    generate_numeric_verification_code,
    generate_alphabetic_verification_code,
    generate_mixed_verification_code
)

# 生成6位数字验证码
num_code = generate_numeric_verification_code()
print(f"数字验证码: {num_code}")

# 生成8位字母验证码
alpha_code = generate_alphabetic_verification_code(length=8)
print(f"字母验证码: {alpha_code}")

# 生成10位混合验证码
mixed_code = generate_mixed_verification_code(length=10)
print(f"混合验证码: {mixed_code}")
```

## 开发指南

### 安装开发依赖
```bash
pip install -e ".[dev]"
```

### 构建并上传到PyPI
```bash
# 使用提供的脚本
python build_and_upload.py
```

## 许可证
[MIT License](LICENSE)
