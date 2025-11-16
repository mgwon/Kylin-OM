import os
import re
from flask import Blueprint, jsonify

# 1. 创建名为 'asset_logs' 的蓝图
asset_logs_bp = Blueprint('asset_logs_bp', __name__)

# --- 配置 ---
LOG_DIRECTORY = '../../data/api_data/asset-logs'


# --- API 端点定义 ---

# 2. 使用蓝图注册路由，并简化路径
@asset_logs_bp.route('/files', methods=['GET'])
def get_log_files():
    """API端点: 获取日志文件列表"""
    try:
        if not os.path.exists(LOG_DIRECTORY):
            return jsonify({"error": f"日志目录 '{LOG_DIRECTORY}' 未找到"}), 404
        files = [f for f in os.listdir(LOG_DIRECTORY) if f.endswith(('.log', '.txt'))]
        return jsonify(files)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@asset_logs_bp.route('/content/<filename>', methods=['GET'])
def get_log_content(filename):
    """API端点: 获取并解析指定日志文件的内容"""
    if '..' in filename or filename.startswith('/'):
        return jsonify({"error": "无效的文件名"}), 400

    file_path = os.path.join(LOG_DIRECTORY, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "文件未找到"}), 404

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        marker_indices = [i for i, line in enumerate(lines) if '-- Logs begin at' in line]
        content_to_process = []
        if not marker_indices:
            content_to_process = lines
        else:
            last_marker_index = marker_indices[-1]
            content_to_process.extend(lines[last_marker_index + 1:])
            for i in range(len(marker_indices) - 2, -1, -1):
                current_marker_index, next_marker_index = marker_indices[i], marker_indices[i + 1]
                if lines[current_marker_index].strip() != lines[next_marker_index].strip():
                    chunk = lines[current_marker_index + 1: next_marker_index]
                    content_to_process = chunk + content_to_process

        log_regex = re.compile(r'^(.+?\s+\d+\s+\d{2}:\d{2}:\d{2})\s+([\w.-]+)\s+([^:]+):\s+(.*)$')
        parsed_logs = []
        for index, line in enumerate(content_to_process):
            line = line.strip()
            if not line: continue
            match = log_regex.match(line)
            if match:
                parsed_logs.append({
                    "id": f"{filename}-{index}", "timestamp": match.group(1).strip(),
                    "hostname": match.group(2), "name": match.group(3).strip(),
                    "content": match.group(4).strip()
                })
            else:
                parsed_logs.append({
                    "id": f"{filename}-{index}", "timestamp": 'N/A', "hostname": 'N/A',
                    "name": 'Unknown', "content": line
                })
        return jsonify(parsed_logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3. 同样，移除原有的 app 实例和启动代码