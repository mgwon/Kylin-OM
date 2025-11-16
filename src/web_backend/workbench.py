import json
from flask import Blueprint, jsonify

# 1. 创建名为 'workbench' 的蓝图
workbench_bp = Blueprint('workbench_bp', __name__)

# 定义文件路径
HOSTS_DB_FILE = '../../data/api_data/hosts.json'
SUMMARY_FILE = '../../data/api_data/workbench_summary.json'
RECORDS_FILE = '../../data/api_data/workbench_records.json'


def read_hosts_data():
    try:
        with open(HOSTS_DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def read_summary_data():
    try:
        with open(SUMMARY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"summary_base": {}}


def read_records_data():
    try:
        with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# --- API 端点定义 ---

# 2. 使用蓝图注册路由，并简化路径 (前缀将在主应用中添加)
@workbench_bp.route('/summary', methods=['GET'])
def get_workbench_summary():
    """API端点: 获取工作台的摘要信息"""
    summary_data = read_summary_data()
    summary_response = summary_data.get('summary_base', {})

    hosts_data = read_hosts_data()
    host_count = sum(len(group.get('hosts', [])) for group in hosts_data)

    summary_response['hostCount'] = host_count
    return jsonify(summary_response)


@workbench_bp.route('/records', methods=['GET'])
def get_workbench_records():
    """API端点: 获取工作台的异常检测记录"""
    records = read_records_data()
    return jsonify(records)

# 3. 注意：原有的 app 实例和 if __name__ == '__main__' 部分被移除