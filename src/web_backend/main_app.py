# -*- coding: utf-8 -*-

'''
from flask import Flask
from flask_cors import CORS
'''


import os
import json
import time
import random
import uuid
import threading
from flask import Flask, jsonify
from flask_cors import CORS
from filelock import FileLock

# 从其他路由文件中导入蓝图对象 (这些不变)
from hosts import hosts_bp
from workbench import workbench_bp
from asset_logs import asset_logs_bp
from fault_monitoring import fault_monitoring_bp
from fault_repairs import fault_repairs_bp
from config_tracing import config_tracing_bp
from workflows import workflows_bp
from vulnerability import vulnerability_bp
from assetbackup import assetbackup_bp

# 创建主 Flask 应用
app = Flask(__name__)
# 将原来的这行:
# CORS(app)

CORS(app, resources={r"/api/*": {
    "origins": "http://localhost:8000",  # 关键：必须与您前端的源完全匹配
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], # 必须包含 OPTIONS 和 POST
    "allow_headers": ["Content-Type", "Authorization"] # 允许前端发送的请求头
}})


# 注册所有蓝图 (这部分逻辑不变)
app.register_blueprint(hosts_bp, url_prefix='/api')
app.register_blueprint(workbench_bp, url_prefix='/api/workbench')
app.register_blueprint(asset_logs_bp, url_prefix='/api/logs')
app.register_blueprint(fault_monitoring_bp, url_prefix='/api/fault-monitoring')
app.register_blueprint(fault_repairs_bp, url_prefix='/api/fault-repairs')
app.register_blueprint(config_tracing_bp, url_prefix='/api/config-tracing')
app.register_blueprint(workflows_bp, url_prefix='/api')
app.register_blueprint(vulnerability_bp, url_prefix='/api/vulnerability')
app.register_blueprint(assetbackup_bp)
#模拟生成告警
DATA_DIR = '../../data/api_data'

def read_json_file(path):
    """安全地读取一个JSON文件 (后台任务也需要)"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        if os.path.basename(path) in ['all.txt', 'applications.txt', 'records.txt', 'all_models.txt']:
             return []
        if os.path.basename(path) == 'records.txt':
            return {'records': []}
        return None

def write_json_file(path, data):
    """安全地写入一个JSON文件 (后台任务也需要)"""
    lock_path = path + ".lock"
    lock = FileLock(lock_path)
    with lock:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def run_single_workflow_diagnosis(workflow):
    """模拟诊断并生成告警"""
    print(f"[{time.ctime()}] [Engine Thread] Running diagnosis for: '{workflow['name']}'...")
    if random.random() < 0.01: # 1%的概率出问题
        print(f"  -> [Engine Thread] ABNORMALITY DETECTED!")
        return {
            "id": f"alert_{uuid.uuid4().hex[:6]}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "host_group": workflow.get("hostGroup", "N/A"),
            "abnormal_host_count": 1,
            "message": f"'{workflow['name']}' detected an issue.",
            "level": random.choice(["P1", "P2", "P3", "P4"]),
            "details": {
                "abnormal_hosts": [{"host_id": "h_sim", "host_name": "simulated-host", "ip": "1.2.3.4", "abnormal_item_count": 1, "is_root_cause_node": "是"}],
                "abnormal_metrics": [{"metric_id": "m_sim", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "data_item": "simulated_metric", "tags": "simulated, generated", "is_root_cause": "是", "level": "P1"}]
            }
        }
    print(f"  -> [Engine Thread] Status: OK")
    return None

def update_alarms_and_stats(new_alarm):
    """写入告警和统计文件"""
    records_path = os.path.join(DATA_DIR, 'alarms', 'records.txt')
    records_data = read_json_file(records_path)
    if records_data is None or 'records' not in records_data or not isinstance(records_data.get('records'), list):
        records_data = {'records': []}
    records_data['records'].insert(0, new_alarm)
    write_json_file(records_path, records_data)
    print(f"  -> [Engine Thread] New alarm '{new_alarm['id']}' written.")
    stats = {}
    for record in records_data["records"]:
        group = record.get("host_group")
        if group: stats[group] = stats.get(group, 0) + 1
    sorted_stats = sorted(stats.items(), key=lambda item: item[1], reverse=True)
    statistics_data = {"statistics": [{"rank": i + 1, "host_group": g, "alert_count": c} for i, (g, c) in enumerate(sorted_stats)]}
    stats_path = os.path.join(DATA_DIR, 'alarms', 'statistics.txt')
    write_json_file(stats_path, statistics_data)
    print(f"  -> [Engine Thread] Statistics updated.")

def background_engine_loop():
    """将在后台线程中运行的循环函数"""
    while True:
        print(f"\n[{time.ctime()}] [Engine Thread] Check...")
        all_workflows = read_json_file(os.path.join(DATA_DIR, 'workflows', 'all.txt'))
        if all_workflows:
            running_workflows = [wf for wf in all_workflows if wf.get('status') == '运行中']
            print(f"  -> [Engine Thread] Found {len(running_workflows)} running workflows.")
            for workflow in running_workflows:
                new_alarm = run_single_workflow_diagnosis(workflow)
                if new_alarm:
                    update_alarms_and_stats(new_alarm)
        time.sleep(30) # 每30秒检查一次


if __name__ == '__main__':
    # 1. 创建并启动后台告警引擎线程(模拟？）
    engine_thread = threading.Thread(target=background_engine_loop, daemon=True)
    engine_thread.start()
    print("Background alarm generation engine started.")

    # 2. 打印已注册的蓝图信息
    print("Backend server is running. Access APIs at http://localhost:5000")
    print("Registered Blueprints:")
    for bp_name, bp in app.blueprints.items():
        # 获取蓝图注册时设置的前缀
        prefix = app.blueprints[bp_name].url_prefix
        print(f"- Blueprint '{bp_name}' registered at prefix '{prefix}'")

    # 3. 启动 Flask API 服务
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)


'''
if __name__ == '__main__':
    print("Backend server is running. Access APIs at http://localhost:5000")
    print("Registered Blueprints:")
    for bp_name, bp in app.blueprints.items():
        print(f"- Blueprint '{bp_name}' registered at prefix '{bp.url_prefix}'")

    app.run(host='0.0.0.0', port=5000, debug=True)
'''
