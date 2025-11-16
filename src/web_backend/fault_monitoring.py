import json
import os
from flask import Blueprint, jsonify, abort

fault_monitoring_bp = Blueprint('fault_monitoring_bp', __name__)


# --- 辅助函数 ---
def read_data_file(filename):
    """
    从 fault-monitoring 子目录中读取并解析JSON数据。
    """
    try:
        base_dir = os.path.dirname(__file__)

        # --- MODIFICATION ---
        # 告诉 os.path.join 在基础路径和文件名之间，
        # 插入 'fault-monitoring' 这个目录名。
        data_folder = '../../data/api_data/fault-monitoring'
        file_path = os.path.join(base_dir, data_folder, filename)

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


# ==================================================================
# --- API 端点 (这部分代码无需任何改动) ---
# ==================================================================

@fault_monitoring_bp.route('/global-health', methods=['GET'])
def get_global_health():
    """API端点: 获取全局健康度数据。"""
    data = read_data_file('global-health.txt')
    if data is None:
        abort(404, "全局健康度数据文件 (global-health.txt) 未找到或格式错误。")
    return jsonify(data)


@fault_monitoring_bp.route('/timeline-events', methods=['GET'])
def get_timeline_events():
    """API端点: 获取时间轴事件数据。"""
    data = read_data_file('timeline-events.txt')
    if data is None:
        abort(404, "时间轴事件数据文件 (timeline-events.txt) 未找到或格式错误。")
    return jsonify(data)


@fault_monitoring_bp.route('/anomalies', methods=['GET'])
def get_anomalies():
    """API端点: 获取智能异常聚合列表数据。"""
    data = read_data_file('anomalies.txt')
    if data is None:
        abort(404, "异常聚合列表数据文件 (anomalies.txt) 未找到或格式错误。")
    return jsonify(data)


@fault_monitoring_bp.route('/anomaly-detail/<anomaly_id>', methods=['GET'])
def get_anomaly_detail(anomaly_id):
    """API端点: 根据ID获取单个异常的详细信息。"""
    filename = f"anomaly-detail-{anomaly_id}.txt"
    data = read_data_file(filename)
    if data is None:
        abort(404, f"ID为 {anomaly_id} 的异常详情文件 ({filename}) 未找到。")
    return jsonify(data)