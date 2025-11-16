#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import glob
import subprocess
import time
from datetime import datetime
from flask import Blueprint, jsonify

# 导入 Flask 相关模块
from flask import Flask, jsonify, request, abort, send_from_directory
from crontab import CronTab

assetbackup_bp = Blueprint('assetbackup_bp', __name__)
# --- 核心配置 (与之前版本保持一致) ---
current_script_path = os.path.abspath(__file__)

# 2. 从当前脚本路径向上追溯，找到项目的根目录 "kylin"
# (从 web_backend -> src -> kylin)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))

# --- 使用 os.path.join 构建跨平台的、绝对的脚本路径 ---

# 这样做可以自动使用正确的路径分隔符（Linux下是'/'）
DO_BACKUP_SCRIPT = os.path.join(project_root, 'src', 'daily_maintenance', 'do_backup.py')
RESTORE_BACKUP_SCRIPT = os.path.join(project_root, 'src', 'fault_recovery', 'restore_backup.py')

CONFIG_DIR = "/etc/backup_jobs"
BACKUP_ROOT = "/var/backups/openeuler_style_backups"




# --- Cron 任务管理辅助函数 (与之前版本保持一致) ---
def schedule_to_cron(schedule_str):
    # 这个函数是框架无关的，所以不需要任何修改
    parts = schedule_str.split()
    if len(parts) != 2 or parts[0] not in ['每日', '每周日']:
        try:
            cron_parts = schedule_str.split()
            if len(cron_parts) == 5:
                return cron_parts
            return None, None, None, None, None
        except:
            return None, None, None, None, None

    time_parts = parts[1].split(':')
    minute, hour = time_parts[0], time_parts[1]
    day_of_week = '*'
    if parts[0] == '每周日':
        day_of_week = '0'
    return minute, hour, '*', '*', day_of_week


def update_cron_job(policy: dict):
    # 这个函数也是框架无关的，不需要修改
    job_id = policy.get('id')
    schedule = policy.get('schedule')
    job_comment = f"Backup Policy ID: {job_id}"
    try:
        # 假设在Linux环境下运行，且有权限
        cron = CronTab(user='root')
        cron.remove_all(comment=job_comment)
        if schedule:
            cron_schedule = schedule_to_cron(schedule)
            if all(part is not None for part in cron_schedule):
                command = f"{sys.executable} {DO_BACKUP_SCRIPT} {job_id} >> /var/log/backup_{job_id}.log 2>&1"
                job = cron.new(command=command, comment=job_comment)
                job.setall(*cron_schedule)
        cron.write()
    except Exception as e:
        # 在生产环境中，应该使用更完善的日志记录
        print(f"Error updating cron for job {job_id}: {e}", file=sys.stderr)


# --- API Endpoints (Flask 风格) ---

@assetbackup_bp.route("/api/policies", methods=['GET'])
def get_policies():
    """获取所有备份策略"""
    policies = []
    os.makedirs(CONFIG_DIR, exist_ok=True)
    for filename in sorted(glob.glob(os.path.join(CONFIG_DIR, "*.json"))):
        try:
            with open(filename, 'r') as f:
                policies.append(json.load(f))
        except:
            continue
    return jsonify(policies)


@assetbackup_bp.route("/api/policies", methods=['POST'])
def create_policy():
    """新建备份策略"""
    data = request.get_json()
    if not data or 'name' not in data or 'content' not in data:
        abort(400, description="请求数据无效，缺少必须的字段。")

    new_id = f"p{int(time.time() * 1000)}"
    new_policy_data = {
        "id": new_id,
        "name": data.get("name"),
        "target": data.get("target"),
        "type": data.get("type", "文件"),
        "content": data.get("content"),
        "schedule": data.get("schedule"),
        "retention": data.get("retention"),
        "description": data.get("description"),
        "lastStatus": "未执行",
        "lastBackupTime": "N/A"
    }

    filepath = os.path.join(CONFIG_DIR, f"{new_id}.json")
    with open(filepath, 'w') as f:
        json.dump(new_policy_data, f, indent=4, ensure_ascii=False)

    update_cron_job(new_policy_data)
    # 对于POST请求，返回创建的资源和201状态码是标准实践
    return jsonify(new_policy_data), 201


@assetbackup_bp.route("/api/policies/<string:policy_id>", methods=['PUT'])
def edit_policy(policy_id):
    """编辑指定的备份策略"""
    data = request.get_json()
    filepath = os.path.join(CONFIG_DIR, f"{policy_id}.json")
    if not os.path.exists(filepath):
        abort(404, description="策略未找到")

    with open(filepath, 'r') as f:
        current_policy = json.load(f)

    # 用新数据更新旧字典
    current_policy.update(data)

    with open(filepath, 'w') as f:
        json.dump(current_policy, f, indent=4, ensure_ascii=False)

    update_cron_job(current_policy)
    return jsonify(current_policy)


@assetbackup_bp.route("/api/policies/<string:policy_id>", methods=['DELETE'])
def delete_policy(policy_id):
    """删除指定的备份策略"""
    filepath = os.path.join(CONFIG_DIR, f"{policy_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
        update_cron_job({'id': policy_id, 'schedule': None})
        # DELETE成功通常返回一个空响应和204状态码
        return '', 204
    else:
        abort(404, description="策略未找到")


@assetbackup_bp.route("/api/policies/<string:policy_id>/execute", methods=['POST'])
def execute_policy_now(policy_id):
    """立即执行一个备份任务"""
    if not os.path.exists(os.path.join(CONFIG_DIR, f"{policy_id}.json")):
        abort(404, description="策略未找到")

    # 假设在Linux下运行，并且配置了sudo权限
    command = ['sudo', sys.executable, DO_BACKUP_SCRIPT, policy_id]
    subprocess.Popen(command)

    # 接受请求后立即返回，表示任务已在后台触发
    return jsonify({"message": f"策略 {policy_id} 已触发执行"}), 202


@assetbackup_bp.route("/api/policies/<string:policy_id>/history", methods=['GET'])
def get_policy_history(policy_id):
    """查看指定策略的备份历史"""
    history = []
    job_backup_dir = os.path.join(BACKUP_ROOT, policy_id)
    if not os.path.isdir(job_backup_dir):
        return jsonify([])

    backup_files = glob.glob(os.path.join(job_backup_dir, f"{policy_id}-*.tar.gz"))
    for f_path in sorted(backup_files, key=os.path.getmtime, reverse=True):
        try:
            stat = os.stat(f_path)
            history.append({
                "id": os.path.basename(f_path),
                "timestamp": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                "duration": "N/A",
                "size": f"{stat.st_size / (1024 * 1024):.2f} MB",
                "status": "成功",
                "filePath": f_path
            })
        except OSError:
            continue
    return jsonify(history)


@assetbackup_bp.route("/api/restore", methods=['POST'])
def restore_from_backup():
    """从指定的备份文件恢复"""
    data = request.get_json()
    file_path = data.get('filePath')

    if not file_path or not os.path.abspath(file_path).startswith(os.path.abspath(BACKUP_ROOT)):
        abort(403, description="禁止的路径")

    if not os.path.exists(file_path):
        abort(404, description="备份文件未找到")

    command = ['sudo', sys.executable, RESTORE_BACKUP_SCRIPT, file_path]
    subprocess.Popen(command)
    return jsonify({"message": f"已触发从 {os.path.basename(file_path)} 的恢复"}), 202


# 定义新数据文件夹的基础路径
# 我们利用已经计算好的 project_root 来准确定位
DATA_DIR = os.path.join(project_root, 'data')

@assetbackup_bp.route("/data/<path:filepath>")
def serve_data_file(filepath):
    """
    提供位于 /data/ 目录下的静态文件。
    例如，前端请求 /data/api_data/backup/policies.txt 时，
    'filepath' 的值会是 'api_data/backup/policies.txt'。
    """
    # 使用 send_from_directory 从 DATA_DIR 目录安全地发送文件
    # DATA_DIR 会被解析为 C:\Users\31311\Desktop\kkkyyy\kylin\data
    return send_from_directory(DATA_DIR, filepath)

# --- 运行 Flask App ---
if __name__ == '__main__':
    # Flask默认只监听本地回环地址，设置host='0.0.0.0'使其可以从网络访问
    # debug=True 会在代码变动时自动重载，并提供详细的错误页面，生产环境应设为False
    app = Flask(__name__)

   

    # 这样 app 才知道 /api/policies 这些路由的存在
    app.register_blueprint(assetbackup_bp)

    app.run(host='0.0.0.0', port=5001, debug=True)