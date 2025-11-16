#!/usr/bin/env python3
"""
进程监控工具测试脚本
"""

import asyncio
import json
import os
import tempfile
from process_monitor import get_process_monitoring_report

async def test_process_monitor():
    """测试进程监控工具"""
    print("🧪 开始测试进程监控工具...\n")
    
    # 创建临时测试数据文件
    test_data = {
        "timestamp": "2025-08-10 15:30:00",
        "processes": [
            {
                "进程名": "test_process_1",
                "pid": 1234,
                "状态": "running",
                "cpu使用率": "15.50%",
                "物理内存": "128.50 MB",
                "磁盘i/o": "2.30 MB/s",
                "网络链接数": 5,
                "cpu得分": "0.1550",
                "内存得分": "0.1285",
                "磁盘得分": "0.0230",
                "网络得分": "1.0000",
                "资源占用（RCS综合得分）": "0.3267"
            },
            {
                "进程名": "test_process_2",
                "pid": 5678,
                "状态": "faulty",
                "cpu使用率": "0.00%",
                "物理内存": "256.00 MB",
                "磁盘i/o": "0.00 MB/s",
                "网络链接数": 0,
                "cpu得分": "0.0000",
                "内存得分": "0.2560",
                "磁盘得分": "0.0000",
                "网络得分": "0.0000",
                "资源占用（RCS综合得分）": "0.2560"
            }
        ]
    }
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
        temp_file = f.name
    
    # 修改process_monitor.py中的文件路径
    import process_monitor
    original_path = process_monitor.AOPS_TOPOLOGY_FILE
    process_monitor.AOPS_TOPOLOGY_FILE = temp_file
    
    try:
        # 测试1: 获取所有进程
        print("📋 测试1: 获取所有进程")
        result1 = await get_process_monitoring_report()
        print(result1)
        print("-" * 50)
        
        # 测试2: 按状态筛选
        print("📋 测试2: 获取异常进程")
        result2 = await get_process_monitoring_report(status_filter="faulty")
        print(result2)
        print("-" * 50)
        
        # 测试3: 按进程名搜索
        print("📋 测试3: 搜索特定进程")
        result3 = await get_process_monitoring_report(process_name="test_process_1")
        print(result3)
        print("-" * 50)
        
        # 测试4: 排序和限制
        print("📋 测试4: 按内存排序，限制1个")
        result4 = await get_process_monitoring_report(sort_by="memory", limit=1)
        print(result4)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    
    finally:
        # 清理
        os.unlink(temp_file)
        process_monitor.AOPS_TOPOLOGY_FILE = original_path
    
    print("✅ 测试完成！")
    return True

if __name__ == "__main__":
    asyncio.run(test_process_monitor())