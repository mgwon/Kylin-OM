#!/usr/bin/env python3
"""
主机管理工具测试脚本
"""

import asyncio
import json
from host_management_tools import (
    list_hosts_and_groups, add_host_to_group, remove_host_from_group,
    update_host_info, add_host_group, remove_host_group,
    check_host_connectivity, get_hosts_by_group, search_hosts_by_criteria
)

async def test_host_management():
    """测试主机管理工具的各项功能"""
    
    print("=== 主机管理工具测试 ===\n")
    
    # 1. 测试列出主机和主机组
    print("1. 测试列出主机和主机组:")
    result = await list_hosts_and_groups()
    print(result)
    print("-" * 50)
    
    # 2. 测试添加主机组
    print("\n2. 测试添加主机组:")
    new_group = {
        "id": "g6",
        "name": "Test Group",
        "description": "测试主机组"
    }
    result = await add_host_group(new_group)
    print(result)
    print("-" * 50)
    
    # 3. 测试添加主机
    print("\n3. 测试添加主机:")
    new_host = {
        "id": "host-test-001",
        "name": "test-server-01",
        "ip": "192.168.1.100",
        "ssh": 22,
        "isMgmt": "否",
        "status": "运行中"
    }
    result = await add_host_to_group("g6", new_host)
    print(result)
    print("-" * 50)
    
    # 4. 测试获取主机组信息
    print("\n4. 测试获取主机组信息:")
    result = await get_hosts_by_group("g6")
    print(result)
    print("-" * 50)
    
    # 5. 测试搜索主机
    print("\n5. 测试搜索主机:")
    result = await search_hosts_by_criteria("name", "test")
    print(result)
    print("-" * 50)
    
    # 6. 测试更新主机信息
    print("\n6. 测试更新主机信息:")
    updated_info = {
        "status": "维护中",
        "ssh": 2222
    }
    result = await update_host_info("host-test-001", updated_info)
    print(result)
    print("-" * 50)
    
    # 7. 测试连接状态检查（模拟）
    print("\n7. 测试连接状态检查:")
    result = await check_host_connectivity("host-test-001")
    print(result)
    print("-" * 50)
    
    # 8. 测试移除主机
    print("\n8. 测试移除主机:")
    result = await remove_host_from_group("host-test-001")
    print(result)
    print("-" * 50)
    
    # 9. 测试移除主机组
    print("\n9. 测试移除主机组:")
    result = await remove_host_group("g6")
    print(result)
    print("-" * 50)
    
    # 10. 最终状态检查
    print("\n10. 最终状态检查:")
    result = await list_hosts_and_groups()
    print(result)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_host_management())
