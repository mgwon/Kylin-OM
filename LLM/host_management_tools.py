"""
主机管理工具
提供主机和主机组信息的CRUD操作、连接状态检查等功能
"""

import json
import logging
import os
import subprocess
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import aiofiles

logger = logging.getLogger(__name__)

# 主机配置文件路径
HOSTS_CONFIG_PATH = "../data/api_data/hosts.json"

def get_hosts_data() -> Dict:
    """
    读取主机配置文件
    
    Returns:
        主机配置数据字典
    """
    try:
        if not os.path.exists(HOSTS_CONFIG_PATH):
            # 如果文件不存在，创建默认配置
            default_config = [
                {
                    "id": "g1",
                    "name": "Default Group",
                    "description": "默认主机组",
                    "hosts": []
                }
            ]
            os.makedirs(os.path.dirname(HOSTS_CONFIG_PATH), exist_ok=True)
            with open(HOSTS_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=4)
            return {"groups": default_config}
        
        with open(HOSTS_CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {"groups": data}
    except Exception as e:
        logger.error(f"读取主机配置文件失败: {e}")
        return {"groups": [], "error": str(e)}

def save_hosts_data(data: Dict) -> bool:
    """
    保存主机配置数据
    
    Args:
        data: 主机配置数据
        
    Returns:
        保存是否成功
    """
    try:
        os.makedirs(os.path.dirname(HOSTS_CONFIG_PATH), exist_ok=True)
        with open(HOSTS_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data["groups"], f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logger.error(f"保存主机配置文件失败: {e}")
        return False

def find_host_by_id(host_id: str, groups: List[Dict]) -> Tuple[Optional[Dict], Optional[Dict]]:
    """
    根据主机ID查找主机和所属组
    
    Args:
        host_id: 主机ID
        groups: 主机组列表
        
    Returns:
        (主机信息, 所属组信息) 的元组
    """
    for group in groups:
        for host in group.get("hosts", []):
            if host.get("id") == host_id:
                return host, group
    return None, None

def find_group_by_id(group_id: str, groups: List[Dict]) -> Optional[Dict]:
    """
    根据组ID查找主机组
    
    Args:
        group_id: 组ID
        groups: 主机组列表
        
    Returns:
        主机组信息
    """
    for group in groups:
        if group.get("id") == group_id:
            return group
    return None

async def list_hosts_and_groups() -> str:
    """
    列出所有主机和主机组信息
    
    Returns:
        主机和主机组信息的格式化字符串
    """
    try:
        data = get_hosts_data()
        if "error" in data:
            return f"获取主机信息失败: {data['error']}"
        
        groups = data["groups"]
        if not groups:
            return "暂无主机组配置"
        
        result = "主机组和主机信息:\n\n"
        
        for group in groups:
            result += f"组ID: {group['id']}\n"
            result += f"组名称: {group['name']}\n"
            result += f"描述: {group['description']}\n"
            result += f"主机数量: {len(group.get('hosts', []))}\n"
            
            hosts = group.get("hosts", [])
            if hosts:
                result += "主机列表:\n"
                for host in hosts:
                    result += f"  - ID: {host['id']}\n"
                    result += f"    名称: {host['name']}\n"
                    result += f"    IP: {host['ip']}\n"
                    result += f"    SSH端口: {host['ssh']}\n"
                    result += f"    管理节点: {host['isMgmt']}\n"
                    result += f"    状态: {host['status']}\n"
                    result += "\n"
            else:
                result += "  暂无主机\n"
            
            result += "-" * 50 + "\n\n"
        
        return result
        
    except Exception as e:
        return f"列出主机信息时发生错误: {str(e)}"

async def add_host_to_group(group_id: str, host_info: Dict) -> str:
    """
    向指定主机组添加主机
    
    Args:
        group_id: 主机组ID
        host_info: 主机信息字典，包含id, name, ip, ssh, isMgmt, status等字段
        
    Returns:
        操作结果报告
    """
    try:
        data = get_hosts_data()
        if "error" in data:
            return f"获取主机信息失败: {data['error']}"
        
        groups = data["groups"]
        target_group = find_group_by_id(group_id, groups)
        
        if not target_group:
            return f"错误: 未找到ID为 '{group_id}' 的主机组"
        
        # 检查主机ID是否已存在
        existing_host, _ = find_host_by_id(host_info["id"], groups)
        if existing_host:
            return f"错误: 主机ID '{host_info['id']}' 已存在"
        
        # 添加主机到组
        if "hosts" not in target_group:
            target_group["hosts"] = []
        
        target_group["hosts"].append(host_info)
        
        # 保存更新
        if save_hosts_data(data):
            return f"成功添加主机 '{host_info['name']}' 到组 '{target_group['name']}'"
        else:
            return "保存主机信息失败"
            
    except Exception as e:
        return f"添加主机时发生错误: {str(e)}"

async def remove_host_from_group(host_id: str) -> str:
    """
    从主机组中移除指定主机
    
    Args:
        host_id: 要移除的主机ID
        
    Returns:
        操作结果报告
    """
    try:
        data = get_hosts_data()
        if "error" in data:
            return f"获取主机信息失败: {data['error']}"
        
        groups = data["groups"]
        host, group = find_host_by_id(host_id, groups)
        
        if not host:
            return f"错误: 未找到ID为 '{host_id}' 的主机"
        
        # 从组中移除主机
        group["hosts"].remove(host)
        
        # 保存更新
        if save_hosts_data(data):
            return f"成功移除主机 '{host['name']}' 从组 '{group['name']}'"
        else:
            return "保存主机信息失败"
            
    except Exception as e:
        return f"移除主机时发生错误: {str(e)}"

async def update_host_info(host_id: str, updated_info: Dict) -> str:
    """
    更新指定主机的信息
    
    Args:
        host_id: 主机ID
        updated_info: 更新的主机信息
        
    Returns:
        操作结果报告
    """
    try:
        data = get_hosts_data()
        if "error" in data:
            return f"获取主机信息失败: {data['error']}"
        
        groups = data["groups"]
        host, group = find_host_by_id(host_id, groups)
        
        if not host:
            return f"错误: 未找到ID为 '{host_id}' 的主机"
        
        # 更新主机信息
        host.update(updated_info)
        
        # 保存更新
        if save_hosts_data(data):
            return f"成功更新主机 '{host['name']}' 的信息"
        else:
            return "保存主机信息失败"
            
    except Exception as e:
        return f"更新主机信息时发生错误: {str(e)}"

async def add_host_group(group_info: Dict) -> str:
    """
    添加新的主机组
    
    Args:
        group_info: 主机组信息，包含id, name, description等字段
        
    Returns:
        操作结果报告
    """
    try:
        data = get_hosts_data()
        if "error" in data:
            return f"获取主机信息失败: {data['error']}"
        
        groups = data["groups"]
        
        # 检查组ID是否已存在
        existing_group = find_group_by_id(group_info["id"], groups)
        if existing_group:
            return f"错误: 主机组ID '{group_info['id']}' 已存在"
        
        # 添加新组
        groups.append(group_info)
        
        # 保存更新
        if save_hosts_data(data):
            return f"成功添加主机组 '{group_info['name']}'"
        else:
            return "保存主机信息失败"
            
    except Exception as e:
        return f"添加主机组时发生错误: {str(e)}"

async def remove_host_group(group_id: str) -> str:
    """
    移除指定的主机组
    
    Args:
        group_id: 要移除的主机组ID
        
    Returns:
        操作结果报告
    """
    try:
        data = get_hosts_data()
        if "error" in data:
            return f"获取主机信息失败: {data['error']}"
        
        groups = data["groups"]
        target_group = find_group_by_id(group_id, groups)
        
        if not target_group:
            return f"错误: 未找到ID为 '{group_id}' 的主机组"
        
        # 检查组中是否有主机
        if target_group.get("hosts"):
            return f"错误: 主机组 '{target_group['name']}' 中还有主机，无法删除"
        
        # 移除组
        groups.remove(target_group)
        
        # 保存更新
        if save_hosts_data(data):
            return f"成功移除主机组 '{target_group['name']}'"
        else:
            return "保存主机信息失败"
            
    except Exception as e:
        return f"移除主机组时发生错误: {str(e)}"

async def check_host_connectivity(host_id: str) -> str:
    """
    检查指定主机的连接状态
    
    Args:
        host_id: 主机ID
        
    Returns:
        连接状态检查结果
    """
    try:
        data = get_hosts_data()
        if "error" in data:
            return f"获取主机信息失败: {data['error']}"
        
        groups = data["groups"]
        host, group = find_host_by_id(host_id, groups)
        
        if not host:
            return f"错误: 未找到ID为 '{host_id}' 的主机"
        
        result = f"主机连接状态检查\n"
        result += f"主机ID: {host['id']}\n"
        result += f"主机名称: {host['name']}\n"
        result += f"IP地址: {host['ip']}\n"
        result += f"SSH端口: {host['ssh']}\n"
        result += f"所属组: {group['name']}\n\n"
        
        # ping测试
        try:
            ping_process = await asyncio.create_subprocess_shell(
                f"ping -c 3 {host['ip']}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            ping_stdout, ping_stderr = await ping_process.communicate()
            
            if ping_process.returncode == 0:
                result += "Ping测试: 成功\n"
            else:
                result += "Ping测试: 失败\n"
                result += f"错误信息: {ping_stderr.decode('utf-8', errors='ignore')}\n"
        except Exception as e:
            result += f"Ping测试: 执行失败 - {str(e)}\n"
        
        # SSH连接测试
        try:
            ssh_process = await asyncio.create_subprocess_shell(
                f"ssh -o ConnectTimeout=10 -o BatchMode=yes -p {host['ssh']} {host['ip']} 'echo connection_test'",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            ssh_stdout, ssh_stderr = await ssh_process.communicate()
            
            if ssh_process.returncode == 0:
                result += "SSH连接: 成功\n"
            else:
                result += "SSH连接: 失败\n"
                result += f"错误信息: {ssh_stderr.decode('utf-8', errors='ignore')}\n"
        except Exception as e:
            result += f"SSH连接测试: 执行失败 - {str(e)}\n"
        
        result += f"\n检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return result
        
    except Exception as e:
        return f"检查主机连接状态时发生错误: {str(e)}"

async def get_hosts_by_group(group_id: str) -> str:
    """
    获取指定主机组的所有主机信息
    
    Args:
        group_id: 主机组ID
        
    Returns:
        主机组信息报告
    """
    try:
        data = get_hosts_data()
        if "error" in data:
            return f"获取主机信息失败: {data['error']}"
        
        groups = data["groups"]
        target_group = find_group_by_id(group_id, groups)
        
        if not target_group:
            return f"错误: 未找到ID为 '{group_id}' 的主机组"
        
        result = f"主机组信息: {target_group['name']}\n"
        result += f"组ID: {target_group['id']}\n"
        result += f"描述: {target_group['description']}\n"
        result += f"主机数量: {len(target_group.get('hosts', []))}\n\n"
        
        hosts = target_group.get("hosts", [])
        if hosts:
            result += "主机列表:\n"
            for host in hosts:
                result += f"  - ID: {host['id']}\n"
                result += f"    名称: {host['name']}\n"
                result += f"    IP: {host['ip']}\n"
                result += f"    SSH端口: {host['ssh']}\n"
                result += f"    管理节点: {host['isMgmt']}\n"
                result += f"    状态: {host['status']}\n"
                result += "\n"
        else:
            result += "该组暂无主机\n"
        
        return result
        
    except Exception as e:
        return f"获取主机组信息时发生错误: {str(e)}"

async def search_hosts_by_criteria(criteria: str, value: str) -> str:
    """
    根据条件搜索主机
    
    Args:
        criteria: 搜索条件 (id, name, ip, status, group)
        value: 搜索值
        
    Returns:
        搜索结果报告
    """
    try:
        data = get_hosts_data()
        if "error" in data:
            return f"获取主机信息失败: {data['error']}"
        
        groups = data["groups"]
        results = []
        
        for group in groups:
            for host in group.get("hosts", []):
                match = False
                
                if criteria == "id" and value.lower() in host.get("id", "").lower():
                    match = True
                elif criteria == "name" and value.lower() in host.get("name", "").lower():
                    match = True
                elif criteria == "ip" and value.lower() in host.get("ip", "").lower():
                    match = True
                elif criteria == "status" and value.lower() in host.get("status", "").lower():
                    match = True
                elif criteria == "group" and value.lower() in group.get("name", "").lower():
                    match = True
                
                if match:
                    results.append({
                        "host": host,
                        "group": group
                    })
        
        if not results:
            return f"未找到符合条件 '{criteria}={value}' 的主机"
        
        result = f"搜索结果 (条件: {criteria}={value}, 找到 {len(results)} 个主机):\n\n"
        
        for item in results:
            host = item["host"]
            group = item["group"]
            result += f"主机ID: {host['id']}\n"
            result += f"主机名称: {host['name']}\n"
            result += f"IP地址: {host['ip']}\n"
            result += f"SSH端口: {host['ssh']}\n"
            result += f"管理节点: {host['isMgmt']}\n"
            result += f"状态: {host['status']}\n"
            result += f"所属组: {group['name']} ({group['id']})\n"
            result += "-" * 40 + "\n\n"
        
        return result
        
    except Exception as e:
        return f"搜索主机时发生错误: {str(e)}"
