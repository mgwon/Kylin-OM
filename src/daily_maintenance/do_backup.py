#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import subprocess
import glob
from datetime import datetime

# --- 核心配置 ---
# 备份文件存储的根目录
BACKUP_ROOT = "/var/backups/openeuler_style_backups"
# 备份任务配置文件的存放目录
CONFIG_DIR = "/etc/backup_jobs"

def load_job_config(job_id):
    """根据任务ID加载并返回JSON配置"""
    config_path = os.path.join(CONFIG_DIR, f"{job_id}.json")
    if not os.path.exists(config_path):
        print(f"❌ 错误: 配置文件 {config_path} 不存在。")
        sys.exit(1)
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"❌ 错误: 配置文件 {config_path} 格式无效。")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: 读取配置文件时发生未知错误: {e}")
        sys.exit(1)

def run_prune(job_id, retention_count):
    """清理旧的备份，只保留指定数量的最新备份"""
    job_backup_dir = os.path.join(BACKUP_ROOT, job_id)
    if not os.path.isdir(job_backup_dir):
        return

    print(f"🧹 开始为任务 '{job_id}' 清理旧备份，保留数量: {retention_count}...")
    
    backups = glob.glob(os.path.join(job_backup_dir, f"{job_id}-*.tar.gz"))
    backups.sort(key=os.path.getmtime)
    
    files_to_delete = backups[:-retention_count]
    
    if not files_to_delete:
        print("✅ 没有需要清理的旧备份。")
        return

    for f in files_to_delete:
        try:
            os.remove(f)
            print(f"  - 已删除旧备份: {os.path.basename(f)}")
        except Exception as e:
            print(f"  - 删除失败: {os.path.basename(f)} ({e})")

def main():
    if len(sys.argv) != 2:
        print(f"用法: sudo python3 {sys.argv[0]} <任务ID>")
        print(f"示例: sudo python3 {sys.argv[0]} p02")
        sys.exit(1)
    
    job_id = sys.argv[1]
    
    if os.geteuid() != 0:
        print("❌ 错误: 此脚本需要使用 sudo 权限运行，以确保可以备份系统文件。")
        sys.exit(1)
        
    config = load_job_config(job_id)
    
    print(f"---==[ 开始执行备份任务: {config.get('name', job_id)} ]==---")

    job_backup_dir = os.path.join(BACKUP_ROOT, job_id)
    os.makedirs(job_backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    archive_filename = f"{job_id}-{timestamp}.tar.gz"
    archive_path = os.path.join(job_backup_dir, archive_filename)

    paths_to_backup = [path.strip() for path in config.get('content', '').split('\n') if path.strip()]
    if not paths_to_backup:
        print("❌ 错误: 配置文件中没有定义任何有效的 'content' (备份路径)。")
        sys.exit(1)
    
    print(f"📦 目标归档文件: {archive_path}")
    print(f"🗂️ 将要备份的路径: {', '.join(paths_to_backup)}")

    command = ["tar", "-cpzf", archive_path, "--absolute-names"] + paths_to_backup
    
    print(f"🔩 执行命令: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"\n✅ 备份任务 '{job_id}' 成功完成!")
        if result.stderr:
            print(f"命令输出(stderr):\n{result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 备份失败! 返回码: {e.returncode}")
        print(f"错误信息:\n{e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 执行tar命令时发生未知错误: {e}")
        sys.exit(1)

    retention_count = config.get("retention")
    if isinstance(retention_count, int) and retention_count > 0:
        run_prune(job_id, retention_count)
    else:
        print("未配置有效的保留策略 (retention)，将跳过清理。")

if __name__ == "__main__":
    main()