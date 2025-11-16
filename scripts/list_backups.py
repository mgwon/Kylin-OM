#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import glob
from datetime import datetime

# --- 核心配置 ---
BACKUP_ROOT = "/var/backups/openeuler_style_backups"

def main():
    if not os.path.isdir(BACKUP_ROOT):
        print(f"备份根目录 '{BACKUP_ROOT}' 不存在。")
        sys.exit(1)

    print(f"--- 备份仓库列表 ({BACKUP_ROOT}) ---\n")
    
    job_dirs = sorted([d for d in os.listdir(BACKUP_ROOT) if os.path.isdir(os.path.join(BACKUP_ROOT, d))])
    
    if not job_dirs:
        print("未找到任何备份任务。")
        return

    for job_id in job_dirs:
        job_backup_dir = os.path.join(BACKUP_ROOT, job_id)
        backups = sorted(glob.glob(os.path.join(job_backup_dir, "*.tar.gz")), key=os.path.getmtime, reverse=True)
        
        print(f"任务ID: {job_id} ({len(backups)} 个版本)")
        
        if not backups:
            print("  -> 此任务下没有找到备份文件。")
            continue

        for f_path in backups:
            try:
                stat = os.stat(f_path)
                size_mb = stat.st_size / (1024 * 1024)
                mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                filename = os.path.basename(f_path)
                print(f"  - {filename:<45} | 大小: {size_mb:>7.2f} MB | 创建时间: {mtime}")
            except Exception as e:
                print(f"  - 无法获取文件信息: {os.path.basename(f_path)} ({e})")
        print("-" * 80)

if __name__ == "__main__":
    main()