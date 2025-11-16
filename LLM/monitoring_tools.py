"""
智能运维监控数据检索工具
基于JSON文件的监控数据智能检索和分析
"""

import json
import logging
import os
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio

import aiofiles
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient

logger = logging.getLogger(__name__)

# 监控数据文件路径
MONITORING_DATA_DIR = "../data"

# 查询关键字
QUERY_MAPPING = {

    "CPU": ["panel_3_CPU.json", "panel_20_CPU Busy.json", "panel_305_CPU Saturation per Core.json"],
    "CPU使用率": ["panel_3_CPU.json"],
    "CPU负载": ["panel_155_Sys Load.json"],
    "CPU饱和度": ["panel_305_CPU Saturation per Core.json"],
    
    "内存": ["panel_16_RAM Used.json", "panel_24_Memory.json"],
    "RAM": ["panel_16_RAM Used.json"],
    "内存使用率": ["panel_16_RAM Used.json"],
    "内存占用": ["panel_16_RAM Used.json"],
    "内存详情": ["panel_24_Memory.json"],
    
    "磁盘": ["panel_152_Disk Space Used Basic.json", "panel_33_Disk Read_Write Data.json"],
    "磁盘空间": ["panel_152_Disk Space Used Basic.json"],
    "磁盘IO": ["panel_33_Disk Read_Write Data.json", "panel_229_Disk IOps.json"],
    "磁盘读写": ["panel_33_Disk Read_Write Data.json"],
    "磁盘IOPS": ["panel_229_Disk IOps.json"],
    
    "网络": ["panel_141_Network Traffic Compressed.json", "panel_142_Network Traffic Errors.json"],
    "网络流量": ["panel_141_Network Traffic Compressed.json"],
    "网络错误": ["panel_142_Network Traffic Errors.json"],
    "网络丢包": ["panel_143_Network Traffic Drop.json"],
    "TCP连接": ["panel_299_TCP In _ Out.json"],
    "UDP连接": ["panel_109_UDP Errors.json"],

    "服务": ["panel_157_Node Exporter Scrape.json"],
    "进程": ["panel_149_Exporter Processes Memory.json"],
    "系统负载": ["panel_155_Sys Load.json"],
    "系统运行时间": ["panel_15_Uptime.json"],
    "文件描述符": ["panel_28_File Descriptor.json"],
    
    "漏洞": ["dependency-check-report.json"],
    "安全": ["dependency-check-report.json"],
    "CVE": ["dependency-check-report.json"],
    "安全扫描": ["dependency-check-report.json"],
    
    "系统状态": ["panel_15_Uptime.json", "panel_155_Sys Load.json", "panel_16_RAM Used.json"],
    "系统概览": ["panel_15_Uptime.json", "panel_155_Sys Load.json", "panel_16_RAM Used.json", "panel_152_Disk Space Used Basic.json"],
}

# 时间范围映射
TIME_RANGE_MAPPING = {
    "1h": 1,
    "6h": 6, 
    "24h": 24,
    "7d": 168,
    "1小时": 1,
    "6小时": 6,
    "24小时": 24,
    "7天": 168,
    "1天": 24,
    "1周": 168
}

def get_host_data_path(host_name: str = "localhost") -> str:
    """
    获取指定主机的数据路径
    
    Args:
        host_name: 主机名称，默认为localhost
    
    Returns:
        主机数据目录的完整路径
    """
    return os.path.join(MONITORING_DATA_DIR, host_name)

def get_prometheus_data_path(host_name: str = "localhost") -> str:
    """
    获取指定主机的Prometheus数据路径
    
    Args:
        host_name: 主机名称，默认为localhost
    
    Returns:
        Prometheus数据目录的完整路径
    """
    return os.path.join(get_host_data_path(host_name), "prometheus_data")

async def search_monitoring_data(query: str, time_range: str = "1h", host_name: str = "localhost") -> str:
    """
    智能搜索监控数据
    
    Args:
        query: 查询关键词，支持以下类型：
            - CPU相关: "CPU", "CPU使用率", "CPU负载"
            - 内存相关: "内存", "RAM", "内存使用率"
            - 磁盘相关: "磁盘", "磁盘空间", "磁盘IO"
            - 网络相关: "网络", "网络流量", "网络错误"
            - 服务相关: "服务", "进程", "系统负载"
            - 安全相关: "漏洞", "安全", "CVE"
        time_range: 时间范围，支持 "1h", "6h", "24h", "7d" 或中文描述
        host_name: 主机名称，默认为localhost
    
    Returns:
        格式化的监控数据报告
    """
    try:
        # 1. 检查主机数据目录是否存在
        host_data_path = get_host_data_path(host_name)
        if not os.path.exists(host_data_path):
            return f"错误: 主机 '{host_name}' 的数据目录不存在。请检查 {host_data_path} 路径。"
        
        # 2. 解析时间范围
        hours = TIME_RANGE_MAPPING.get(time_range, 1)
        
        # 3. 查找匹配的文件
        matched_files = []
        for keyword, files in QUERY_MAPPING.items():
            if keyword.lower() in query.lower():
                matched_files.extend(files)
        
        if not matched_files:
            return f"未找到与 '{query}' 相关的监控数据。支持的查询类型包括：CPU、内存、磁盘、网络、服务、安全等。"
        
        # 4. 读取和分析数据
        results = []
        prometheus_data_path = get_prometheus_data_path(host_name)
        
        for file_name in matched_files:
            # 确定文件路径
            if "dependency-check-report.json" in file_name:
                file_path = os.path.join(host_data_path, file_name)
            else:
                file_path = os.path.join(prometheus_data_path, file_name)
            
            logger.debug(f"尝试读取文件: {file_path}")
            
            if os.path.exists(file_path):
                logger.debug(f"文件存在，开始读取: {file_path}")
                data = await read_monitoring_file(file_path)
                if data:
                    analysis = analyze_monitoring_data(data, hours)
                    results.append(analysis)
            else:
                logger.warning(f"文件不存在: {file_path}")
                try:
                    if os.path.exists(prometheus_data_path):
                        available_files = os.listdir(prometheus_data_path)
                        logger.debug(f"可用文件: {available_files[:10]}")
                except Exception as e:
                    logger.error(f"无法列出目录内容: {e}")
        
        if not results:
            return f"无法读取主机 '{host_name}' 的监控数据文件，请检查文件路径是否正确。"
        
        # 5. 生成报告
        return generate_comprehensive_report(query, results, time_range, host_name)
        
    except Exception as e:
        logger.error(f"搜索监控数据时出错: {e}")
        return f"搜索监控数据时发生错误: {str(e)}"

async def read_monitoring_file(file_path: str) -> Optional[Dict]:
    """读取监控数据文件"""
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)
    except Exception as e:
        logger.error(f"读取文件 {file_path} 失败: {e}")
        return None

def analyze_monitoring_data(data: Dict, hours: int) -> Dict:
    """分析监控数据"""
    try:
        panel_title = data.get("panel_title", "未知面板")
        description = data.get("description", "")
        
        # 提取时间序列数据
        time_series_data = []
        if "targets" in data:
            for target in data["targets"]:
                if "result" in target and "data" in target["result"]:
                    for result in target["result"]["data"].get("result", []):
                        if "values" in result:
                            time_series_data.extend(result["values"])
        
        # 分析数据趋势
        if time_series_data:
            # 按时间排序
            time_series_data.sort(key=lambda x: x[0])
            
            # 计算统计信息
            values = [float(v[1]) for v in time_series_data if v[1] != "NaN"]
            if values:
                current_value = values[-1]
                avg_value = sum(values) / len(values)
                max_value = max(values)
                min_value = min(values)
                
                # 计算趋势
                if len(values) > 1:
                    trend = "上升" if values[-1] > values[0] else "下降" if values[-1] < values[0] else "稳定"
                else:
                    trend = "数据不足"
                
                return {
                    "panel_title": panel_title,
                    "description": description,
                    "current_value": current_value,
                    "average_value": avg_value,
                    "max_value": max_value,
                    "min_value": min_value,
                    "trend": trend,
                    "data_points": len(values),
                    "time_range_hours": hours
                }
        
        return {
            "panel_title": panel_title,
            "description": description,
            "error": "无法解析数据"
        }
        
    except Exception as e:
        logger.error(f"分析监控数据失败: {e}")
        return {"error": f"数据分析失败: {str(e)}"}

def generate_comprehensive_report(query: str, results: List[Dict], time_range: str, host_name: str = "localhost") -> str:
    """生成综合监控报告"""
    if not results:
        return "未找到相关监控数据。"
    
    report = f" 监控数据报告 - {query}\n"
    report += f" 主机: {host_name}\n"
    report += f" 时间范围: {time_range}\n"
    report += "=" * 50 + "\n\n"
    
    for i, result in enumerate(results, 1):
        if "error" in result:
            report += f"❌ {result['panel_title']}: {result['error']}\n\n"
            continue
            
        report += f" {result['panel_title']}\n"
        report += f" {result['description']}\n"
        report += f" 当前值: {result['current_value']:.2f}\n"
        report += f" 平均值: {result['average_value']:.2f}\n"
        report += f" 最大值: {result['max_value']:.2f}\n"
        report += f" 最小值: {result['min_value']:.2f}\n"
        report += f" 趋势: {result['trend']}\n"
        report += f" 数据点: {result['data_points']} 个\n"
        report += "-" * 30 + "\n\n"
    
    # 添加总体评估
    report += " 总体评估:\n"
    critical_issues = []
    warnings = []
    
    for result in results:
        if "error" not in result:
            current = result['current_value']
            if current > 90:
                critical_issues.append(f"{result['panel_title']}: {current:.1f}%")
            elif current > 80:
                warnings.append(f"{result['panel_title']}: {current:.1f}%")
    
    if critical_issues:
        report += " 严重问题:\n"
        for issue in critical_issues:
            report += f"   • {issue}\n"
        report += "\n"
    
    if warnings:
        report += " 需要注意:\n"
        for warning in warnings:
            report += f"   • {warning}\n"
        report += "\n"
    
    if not critical_issues and not warnings:
        report += " 系统状态良好，各项指标正常。\n"
    
    return report
