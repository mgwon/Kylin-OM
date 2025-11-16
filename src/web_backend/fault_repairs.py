import json
import os
from flask import Blueprint, jsonify, abort

# 1. 创建一个名为 'fault_repairs' 的蓝图
fault_repairs_bp = Blueprint('fault_repairs_bp', __name__)

# 定义数据文件所在的子目录
DATA_DIRECTORY = '../../data/api_data/faults_data'


# --- 辅助函数 ---
def read_data_file(filename):
    """从 faults-data 子目录中读取并解析JSON数据。"""
    try:
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, DATA_DIRECTORY, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


# ==================================================================
# --- API 端点定义 ---
# ==================================================================

@fault_repairs_bp.route('/records', methods=['GET'])
def get_fault_records():
    """API端点: 获取所有故障修复记录的列表。"""
    data = read_data_file('records.txt')
    if data is None:
        abort(404, "故障修复记录列表文件 (records.txt) 未找到或格式错误。")
    return jsonify(data)


@fault_repairs_bp.route('/records/<record_id>', methods=['GET'])
def get_fault_record_detail(record_id):
    """API端点: 根据ID获取单条故障修复记录的详细信息。"""
    # 安全检查，防止路径遍历攻击
    if '..' in record_id or record_id.startswith('/'):
        abort(400, "无效的记录ID。")

    filename = f"{record_id}.txt"
    data = read_data_file(filename)

    if data is None:
        abort(404, f"ID为 {record_id} 的故障详情文件 ({filename}) 未找到。")

    return jsonify(data)