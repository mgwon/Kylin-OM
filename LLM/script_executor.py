import asyncio
import logging
import subprocess
import os
from typing import Optional

logger = logging.getLogger(__name__)

async def execute_script_remotely(script_name: str, user_name: str, host_name: str) -> str:
    """
    远程执行脚本工具
    
    Args:
        script_name: 脚本文件名
        user_name: 远程用户名
        host_name: 远程主机名
        
    Returns:
        脚本执行结果
    """
    try:
        # 获取当前工作目录
        current_dir = os.getcwd()
        logger.info(f"当前工作目录: {current_dir}")
        
        # 检查脚本文件是否存在
        script_path = os.path.join("generated_scripts", script_name)
        absolute_script_path = os.path.abspath(script_path)
        logger.info(f"脚本路径: {script_path}")
        logger.info(f"绝对脚本路径: {absolute_script_path}")
        
        if not os.path.exists(script_path):
            # 尝试列出generated_scripts目录的内容
            try:
                if os.path.exists("generated_scripts"):
                    files = os.listdir("generated_scripts")
                    logger.info(f"generated_scripts目录内容: {files}")
                    return f"错误: 脚本文件 {script_name} 不存在\n可用文件: {files}"
                else:
                    return f"错误: generated_scripts目录不存在"
            except Exception as e:
                return f"错误: 脚本文件 {script_name} 不存在，且无法列出目录内容: {str(e)}"
        
        # 检查文件权限
        if not os.access(script_path, os.R_OK):
            return f"错误: 脚本文件 {script_name} 没有读取权限"
        
        # 确定脚本类型和对应的执行命令
        if script_name.endswith('.sh'):
            # Bash脚本
            remote_command = f"cat {script_name} | ssh {user_name}@{host_name} 'bash -s'"
        elif script_name.endswith('.py'):
            # Python脚本
            remote_command = f"cat {script_name} | ssh {user_name}@{host_name} 'python3 -'"
        else:
            return f"错误: 不支持的脚本类型 {script_name}"
        
        logger.info(f"执行远程命令: {remote_command}")
        logger.info(f"当前用户: {os.getuid() if hasattr(os, 'getuid') else 'unknown'}")
        logger.info(f"脚本文件权限: {oct(os.stat(script_path).st_mode)[-3:]}")
        
        # 执行远程命令
        process = await asyncio.create_subprocess_shell(
            remote_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="generated_scripts"  # 设置工作目录为脚本所在目录
        )
        
        stdout, stderr = await process.communicate()
        
        # 构建结果报告
        result = f"脚本执行报告\n"
        result += f"脚本名称: {script_name}\n"
        result += f"执行用户: {user_name}\n"
        result += f"目标主机: {host_name}\n"
        result += f"执行命令: {remote_command}\n"
        result += f"退出代码: {process.returncode}\n\n"
        
        if stdout:
            result += f"标准输出:\n{stdout.decode('utf-8', errors='ignore')}\n\n"
        
        if stderr:
            result += f"错误输出:\n{stderr.decode('utf-8', errors='ignore')}\n\n"
        
        if process.returncode == 0:
            result += "脚本执行成功！"
        else:
            result += f"脚本执行失败 (退出代码: {process.returncode})"
        
        return result
        
    except FileNotFoundError:
        return f"错误: 脚本文件 {script_name} 不存在"
    except subprocess.TimeoutExpired:
        return f"错误: 脚本执行超时"
    except Exception as e:
        return f"脚本执行过程中发生错误: {str(e)}"

async def execute_script_locally(script_name: str) -> str:
    """
    本地执行脚本工具（备用方案）
    
    Args:
        script_name: 脚本文件名
        
    Returns:
        脚本执行结果
    """
    try:
        # 获取当前工作目录
        current_dir = os.getcwd()
        logger.info(f"当前工作目录: {current_dir}")
        
        # 检查脚本文件是否存在
        script_path = os.path.join("generated_scripts", script_name)
        absolute_script_path = os.path.abspath(script_path)
        logger.info(f"脚本路径: {script_path}")
        logger.info(f"绝对脚本路径: {absolute_script_path}")
        
        if not os.path.exists(script_path):
            # 尝试列出generated_scripts目录的内容
            try:
                if os.path.exists("generated_scripts"):
                    files = os.listdir("generated_scripts")
                    logger.info(f"generated_scripts目录内容: {files}")
                    return f"错误: 脚本文件 {script_name} 不存在\n可用文件: {files}"
                else:
                    return f"错误: generated_scripts目录不存在"
            except Exception as e:
                return f"错误: 脚本文件 {script_name} 不存在，且无法列出目录内容: {str(e)}"
        
        # 检查文件权限
        if not os.access(script_path, os.R_OK):
            return f"错误: 脚本文件 {script_name} 没有读取权限"
        
        # 确定脚本类型和对应的执行命令
        if script_name.endswith('.sh'):
            # Bash脚本
            command = f"bash {script_name}"
        elif script_name.endswith('.py'):
            # Python脚本
            command = f"python3 {script_name}"
        else:
            return f"错误: 不支持的脚本类型 {script_name}"
        
        logger.info(f"执行本地命令: {command}")
        logger.info(f"当前用户: {os.getuid() if hasattr(os, 'getuid') else 'unknown'}")
        logger.info(f"脚本文件权限: {oct(os.stat(script_path).st_mode)[-3:]}")
        
        # 执行本地命令
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="generated_scripts"  # 设置工作目录为脚本所在目录
        )
        
        stdout, stderr = await process.communicate()
        
        # 构建结果报告
        result = f"本地脚本执行报告\n"
        result += f"脚本名称: {script_name}\n"
        result += f"执行命令: {command}\n"
        result += f"退出代码: {process.returncode}\n\n"
        
        if stdout:
            result += f"标准输出:\n{stdout.decode('utf-8', errors='ignore')}\n\n"
        
        if stderr:
            result += f"错误输出:\n{stderr.decode('utf-8', errors='ignore')}\n\n"
        
        if process.returncode == 0:
            result += "脚本执行成功！"
        else:
            result += f"脚本执行失败 (退出代码: {process.returncode})"
        
        return result
        
    except FileNotFoundError:
        return f"错误: 脚本文件 {script_name} 不存在"
    except subprocess.TimeoutExpired:
        return f"错误: 脚本执行超时"
    except Exception as e:
        return f"脚本执行过程中发生错误: {str(e)}" 