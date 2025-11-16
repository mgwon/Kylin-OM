#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""
智能运维团队 WebUI - 简化启动脚本
最小可运行框架
"""

import os
import sys
import subprocess

def check_basic_deps():
    """检查基本依赖"""
    """try:
        import fastapi
        import uvicorn
        import aiofiles
        import yaml
        print("✅ 基本依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install fastapi uvicorn aiofiles pyyaml")
        return False"""

def check_autogen_deps():
    """检查AutoGen依赖"""
    try:
        import autogen_agentchat
        import autogen_core
        print("✅ AutoGen依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少AutoGen依赖: {e}")
        print("请运行: pip install autogen-agentchat autogen-core")
        return False

def check_files():
    """检查必要文件"""
    required_files = ["ops_webui.py"]
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            missing_files.append(file)
            print(f"❌ {file} - 文件不存在")
    
    if missing_files:
        print(f"\n缺少文件: {', '.join(missing_files)}")
        return False
    
    return True

def create_simple_config():
    """创建简单的配置文件"""
    config_content = """provider: autogen_ext.models.ollama.OllamaChatCompletionClient
config:
  model: qwen3:8b
  host: http://localhost:11434
  model_info:
    vision: false
    function_calling: true
    json_output: false
    family: r1
    structured_output: false
  options:
    num_ctx: 25000
    temperature: 0.3
    top_p: 0.8
    repeat_penalty: 1.1"""
    
    if not os.path.exists("model_config.yaml"):
        with open("model_config.yaml", "w", encoding="utf-8") as f:
            f.write(config_content)
        print("✅ 已创建配置文件: model_config.yaml")
    else:
        print("✅ 配置文件已存在")
    
    return True

def start_server():
    """启动服务器"""
    print("\n🚀 启动智能运维团队 WebUI...")
    print("服务地址: http://localhost:8003")
    print("按 Ctrl+C 停止服务")
    print("-" * 50)
    
    try:
        import uvicorn
        uvicorn.run("ops_webui:app", host="0.0.0.0", port=8003, reload=False)
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("请检查:")
        print("1. Ollama服务是否运行: ollama serve")
        print("3. 端口8003是否被占用")

def main():
    """主函数"""
    print("智能运维团队 WebUI - 简化启动")
    print("=" * 40)
    
    # 检查基本依赖
    print("\n1. 检查基本依赖...")
    if not check_basic_deps():
        return
    
    # 检查AutoGen依赖
    print("\n2. 检查AutoGen依赖...")
    if not check_autogen_deps():
        return
    
    # 检查文件
    print("\n3. 检查必要文件...")
    if not check_files():
        return
    
    # 创建配置
    print("\n4. 检查配置文件...")
    if not create_simple_config():
        return
    
    print("\n✅ 所有检查通过!")
    print("\n📋 使用说明:")
    print("1. 确保Ollama服务运行: ollama serve")
    print("2. 确保模型已下载: ollama pull qwen3:8b")
    print("3. 打开浏览器访问: http://localhost:8003")
    print("4. 描述您的运维问题")
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main() 
