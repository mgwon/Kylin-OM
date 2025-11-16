"""
脚本生成工具
将代码块转换为可执行的bash或python脚本文件
"""

import os
import logging
import re
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# 脚本输出目录
SCRIPTS_DIR = "generated_scripts"

def ensure_scripts_directory():
    """确保脚本输出目录存在"""
    if not os.path.exists(SCRIPTS_DIR):
        os.makedirs(SCRIPTS_DIR)
        logger.info(f"创建脚本目录: {SCRIPTS_DIR}")

def extract_code_blocks(content: str) -> Dict[str, str]:
    """
    从内容中提取代码块
    
    Args:
        content: 包含代码块的内容
        
    Returns:
        包含语言类型和代码内容的字典
    """
    code_blocks = {}
    
    # 匹配 ```language 和 ``` 之间的内容
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        language = match[0].lower() if match[0] else 'bash'
        code = match[1].strip()
        
        if code:
            code_blocks[language] = code
    
    # 如果没有找到代码块，尝试提取单行代码
    if not code_blocks:
        # 匹配以 #!/ 开头的脚本
        shebang_pattern = r'(#!/[^\n]+\n.*)'
        shebang_match = re.search(shebang_pattern, content, re.DOTALL)
        if shebang_match:
            code_blocks['bash'] = shebang_match.group(1)
    
    return code_blocks

def generate_script_filename(language: str, purpose: str = "script") -> str:
    """
    生成脚本文件名
    
    Args:
        language: 脚本语言 (bash/python)
        purpose: 脚本用途描述
        
    Returns:
        生成的文件名
    """
    # 生成短时间戳
    timestamp = datetime.now().strftime("%m%d%H%M%S")
    
    # 简化用途名称，只保留关键字符
    safe_purpose = re.sub(r'[^a-zA-Z0-9]', '', purpose)
    # 限制长度，避免文件名过长
    if len(safe_purpose) > 10:
        safe_purpose = safe_purpose[:10]
    
    # 如果用途为空，使用默认名称
    if not safe_purpose:
        safe_purpose = "script"
    
    extension = '.sh' if language == 'bash' else '.py'
    
    return f"{safe_purpose}_{timestamp}{extension}"

def create_bash_script(code: str, filename: str) -> str:
    """
    创建bash脚本文件
    
    Args:
        code: bash代码内容
        filename: 文件名
        
    Returns:
        脚本文件的完整路径
    """
    ensure_scripts_directory()
    filepath = os.path.join(SCRIPTS_DIR, filename)
    
    # 确保脚本有执行权限的shebang
    if not code.startswith('#!/'):
        code = '#!/bin/bash\n\n' + code
    
    # 头部信息
    header = f"""#!/bin/bash
# 自动生成的运维脚本
# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# 用途: 系统运维操作
# 注意: 请在执行前仔细检查脚本内容

set -e  # 遇到错误时退出
set -u  # 使用未定义的变量时退出

# 日志函数
log() {{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}}

log "开始执行运维脚本: {filename}"

"""
    
    # 添加尾部
    footer = """

log "脚本执行完成"
"""
    
    full_script = header + code + footer
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_script)
        
        # 设置执行权限
        os.chmod(filepath, 0o755)
        
        logger.info(f"Bash脚本已生成: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"创建bash脚本失败: {e}")
        raise

def create_python_script(code: str, filename: str) -> str:
    """
    创建python脚本文件
    
    Args:
        code: python代码内容
        filename: 文件名
        
    Returns:
        脚本文件的完整路径
    """
    ensure_scripts_directory()
    filepath = os.path.join(SCRIPTS_DIR, filename)
    
    # 头部信息
    header = f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
自动生成的运维脚本
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
用途: 系统运维操作
注意: 请在执行前仔细检查脚本内容
\"\"\"

import os
import sys
import subprocess
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def log(message):
    logger.info(message)

log(f"开始执行运维脚本: {filename}")
"""
    
    # 尾部
    footer = """

log("脚本执行完成")
"""
    
    full_script = header + code + footer
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_script)
        
        # 设置执行权限
        os.chmod(filepath, 0o755)
        
        logger.info(f"Python脚本已生成: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"创建python脚本失败: {e}")
        raise

def generate_script_from_code_blocks(content: str, purpose: str = "运维脚本") -> Dict[str, Any]:
    """
    从代码块生成脚本文件
    
    Args:
        content: 包含代码块的内容
        purpose: 脚本用途描述
        
    Returns:
        包含生成结果的字典
    """
    try:
        # 提取代码块
        code_blocks = extract_code_blocks(content)
        
        if not code_blocks:
            return {
                "success": False,
                "error": "未找到有效的代码块",
                "content": content
            }
        
        results = []
        
        for language, code in code_blocks.items():
            try:
                # 生成文件名
                filename = generate_script_filename(language, purpose)
                
                # 创建脚本文件
                if language == 'bash':
                    filepath = create_bash_script(code, filename)
                elif language == 'python':
                    filepath = create_python_script(code, filename)
                else:
                    logger.warning(f"不支持的语言类型: {language}")
                    continue
                
                results.append({
                    "language": language,
                    "filename": filename,
                    "filepath": filepath,
                    "code_preview": code[:200] + "..." if len(code) > 200 else code
                })
                
            except Exception as e:
                logger.error(f"生成{language}脚本失败: {e}")
                results.append({
                    "language": language,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "results": results,
            "total_scripts": len(results)
        }
        
    except Exception as e:
        logger.error(f"脚本生成失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "content": content
        }

def get_script_content(filepath: str) -> str:
    """
    获取脚本文件内容
    
    Args:
        filepath: 脚本文件路径
        
    Returns:
        脚本文件内容
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"读取脚本文件失败: {e}")
        return f"读取文件失败: {str(e)}"

def list_generated_scripts() -> Dict[str, Any]:
    """
    列出已生成的脚本文件
    
    Returns:
        脚本文件列表
    """
    try:
        ensure_scripts_directory()
        scripts = []
        
        for filename in os.listdir(SCRIPTS_DIR):
            filepath = os.path.join(SCRIPTS_DIR, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                scripts.append({
                    "filename": filename,
                    "filepath": filepath,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                    "executable": os.access(filepath, os.X_OK)
                })
        
        return {
            "success": True,
            "scripts": scripts,
            "total": len(scripts)
        }
        
    except Exception as e:
        logger.error(f"列出脚本文件失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }
