#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess

def main():
    if len(sys.argv) != 2:
        print(f"用法: sudo python3 {sys.argv[0]} <备份归档文件的完整路径>")
        print(f"示例: sudo python3 {sys.argv[0]} /var/backups/openeuler_style_backups/p02/p02-2025-07-27_103000.tar.gz")
        sys.exit(1)

    archive_path = sys.argv[1]

    if os.geteuid() != 0:
        print("❌ 错误: 恢复操作需要 sudo 权限，以确保文件权限和所有权被正确还原。")
        sys.exit(1)

    if not os.path.exists(archive_path) or not archive_path.endswith('.tar.gz'):
        print(f"❌ 错误: 提供的路径 '{archive_path}' 不是一个有效的备份归档文件。")
        sys.exit(1)
        
    print(f"警告: 您即将从以下备份文件恢复数据：")
    print(f"  -> {archive_path}")
    print("此操作将覆盖系统中与备份文件路径相同的现有文件！")
    
    try:
        confirm = input("请输入 'yes' 以确认恢复: ")
        if confirm.lower() != 'yes':
            print("操作已取消。")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\n操作已取消。")
        sys.exit(0)
        
    command = ["tar", "-xvpzf", archive_path, "-C", "/", "--numeric-owner"]
    
    print(f"🔩 执行恢复命令: {' '.join(command)}")
    
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        return_code = process.poll()
        if return_code == 0:
            print("\n✅ 恢复操作成功完成。")
        else:
            print(f"\n❌ 恢复操作失败! 返回码: {return_code}")

    except Exception as e:
        print(f"\n❌ 执行恢复时发生未知错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()