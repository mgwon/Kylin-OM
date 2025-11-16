"""
进程监控工具 - 从AOPS最新拓扑数据中提取进程监控信息
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import aiofiles

logger = logging.getLogger(__name__)

AOPS_TOPOLOGY_FILE = "/tmp/aops_latest_topology.json"

async def get_process_monitoring_report(
    process_name: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 10,
    sort_by: str = "resource_usage"
) -> str:
    """
    从AOPS拓扑数据中获取进程监控报告
    
    Args:
        process_name: 指定进程名进行筛选，None表示获取所有进程
        status_filter: 按状态筛选，可选值：running, faulty, stopped
        limit: 返回进程数量限制，默认10个
        sort_by: 排序字段，可选：resource_usage(资源占用), memory(内存), cpu(CPU使用)
    
    Returns:
        格式化的进程监控报告
    """
    try:
        async with aiofiles.open(AOPS_TOPOLOGY_FILE, 'r', encoding='utf-8') as f:
            content = await f.read()
            topology_data = json.loads(content)
        
        processes = topology_data.get("processes", [])
        timestamp = topology_data.get("timestamp", "未知时间")
        
        if not processes:
            return "❌ 未找到任何进程监控数据"
        
        # 筛选进程
        filtered_processes = processes
        if process_name:
            filtered_processes = [
                p for p in filtered_processes 
                if process_name.lower() in p.get("进程名", "").lower()
            ]
        
        if status_filter:
            filtered_processes = [
                p for p in filtered_processes 
                if p.get("状态", "").lower() == status_filter.lower()
            ]
        
        # 排序
        sort_key_map = {
            "resource_usage": "资源占用（RCS综合得分）",
            "memory": "物理内存",
            "cpu": "cpu使用率"
        }
        
        sort_field = sort_key_map.get(sort_by, "资源占用（RCS综合得分）")
        
        def get_sort_value(process, field):
            if field == "物理内存":
                value = process.get(field, "0 MB").split()[0]
                return float(value)
            elif field == "cpu使用率":
                value = process.get(field, "0.00%").replace("%", "")
                return float(value)
            else:  # RCS综合得分
                return float(process.get(field, 0))
        
        try:
            filtered_processes.sort(
                key=lambda p: get_sort_value(p, sort_field),
                reverse=True
            )
        except (ValueError, IndexError):
            logger.warning("排序失败，使用默认排序")
        
        limited_processes = filtered_processes[:limit]
        
        # 生成报告
        report = f"📊 进程监控报告\n"
        report += f"数据时间: {timestamp}\n"
        report += f"总进程数: {len(processes)}\n"
        report += f"显示进程数: {len(limited_processes)}\n"
        
        if process_name:
            report += f"进程筛选: {process_name}\n"
        if status_filter:
            report += f"状态筛选: {status_filter}\n"
        
        report += "=" * 50 + "\n\n"
        
        if not limited_processes:
            report += "⚠️ 没有符合条件的进程"
            return report
        
        # 统计信息
        status_counts = {}
        for p in processes:
            status = p.get("状态", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        report += "📈 状态统计:\n"
        for status, count in status_counts.items():
            report += f" {status}: {count} 个\n"
        report += "\n"
        
        # 进程详情
        report += "🔍 进程详情 (按资源占用排序):\n\n"
        
        for i, process in enumerate(limited_processes, 1):
            name = process.get("进程名", "unknown")
            pid = process.get("pid", "unknown")
            status = process.get("状态", "unknown")
            cpu = process.get("cpu使用率", "0.00%")
            memory = process.get("物理内存", "0 MB")
            io = process.get("磁盘i/o", "0.00 MB/s")
            network = process.get("网络链接数", 0)
            rcs_score = process.get("资源占用（RCS综合得分）", 0)
            
            # 状态标识
            status_icon = {
                "running": "✅",
                "faulty": "❌",
                "stopped": "⏹️"
            }.get(status.lower(), "⚪")
            
            report += f"{i}. {status_icon} {name} (PID: {pid})\n"
            report += f"   状态: {status}\n"
            report += f"   CPU: {cpu} | 内存: {memory} | 磁盘I/O: {io}\n"
            report += f"   网络连接: {network} | RCS得分: {rcs_score}\n"
            
            # 异常进程额外提示
            if status.lower() == "faulty":
                report += f"   ⚠️ 注意: 该进程状态异常，建议检查\n"
            
            report += "\n"
        
        # 告警信息
        faulty_processes = [p for p in processes if p.get("状态", "").lower() == "faulty"]
        if faulty_processes:
            report += "🚨 异常进程告警:\n"
            for p in faulty_processes:
                report += f"   • {p.get('进程名', 'unknown')} (PID: {p.get('pid', 'unknown')})\n"
            report += "\n"
        
        # 资源占用最高的进程
        if processes:
            top_process = max(processes, key=lambda p: float(p.get("资源占用（RCS综合得分）", 0)))
            report += f"💾 资源占用最高: {top_process.get('进程名', 'unknown')} (RCS: {top_process.get('资源占用（RCS综合得分）', 0)})\n"
        
        return report
        
    except FileNotFoundError:
        return f"❌ 找不到进程监控数据文件: {AOPS_TOPOLOGY_FILE}"
    except json.JSONDecodeError as e:
        return f"❌ JSON文件解析错误: {str(e)}"
    except Exception as e:
        logger.error(f"获取进程监控报告失败: {e}")
        return f"❌ 获取进程监控报告失败: {str(e)}"
