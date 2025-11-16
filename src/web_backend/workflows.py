import os
import json
import uuid
from flask import Blueprint, jsonify, request
from filelock import FileLock

# --- 蓝图和配置 ---
# 创建一个名为 'workflows' 的蓝图
workflows_bp = Blueprint('workflows', __name__)

# 基础路径配置
DATA_DIR = '../../data/api_data'
HOSTS_DB_FILE = '../../data/api_data/hosts.json'


# ==================================================================
# 辅助函数 (读写文件)
# ==================================================================
def read_json_file(path):
    """安全地读取一个JSON文件"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # 根据不同的文件名返回不同的默认空结构
        basename = os.path.basename(path)
        if basename in ['all.txt', 'applications.txt', 'all_models.txt']:
            return []
        if basename == 'records.txt':
            return {'records': []}
        if basename == 'statistics.txt':
            return {'statistics': []}
        return None


def write_json_file(path, data):
    """安全地写入一个JSON文件，使用文件锁防止冲突"""
    lock_path = path + ".lock"
    lock = FileLock(lock_path)
    with lock:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def read_hosts_data():
    """专门用于读取 hosts.json 的函数"""
    try:
        with open(HOSTS_DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# ==================================================================
#  工作流 (Workflow) 相关的 API
# ==================================================================

@workflows_bp.route('/workflows', methods=['GET'])
def get_workflows():
    filepath = os.path.join(DATA_DIR, 'workflows', 'all.txt')
    return jsonify(read_json_file(filepath))


@workflows_bp.route('/workflows/<workflow_id>', methods=['GET'])
def get_workflow_detail(workflow_id):
    filepath = os.path.join(DATA_DIR, 'workflows', 'details', f'{workflow_id}.txt')
    data = read_json_file(filepath)
    if data:
        return jsonify(data)
    return jsonify({"error": "Workflow not found"}), 404


@workflows_bp.route('/workflows/cluster-diag/<workflow_id>', methods=['GET'])
def get_cluster_diagnosis_detail(workflow_id):
    filename = f'cluster-diag-{workflow_id}.txt'
    filepath = os.path.join(DATA_DIR, 'workflows', 'details', filename)
    data = read_json_file(filepath)
    if data:
        return jsonify(data)
    return jsonify({"error": "Cluster diagnosis report not found"}), 404


@workflows_bp.route('/workflows/delete', methods=['POST'])
def delete_workflow():
    workflow_id = request.get_json().get('id')
    all_path = os.path.join(DATA_DIR, 'workflows', 'all.txt')
    workflows = read_json_file(all_path)
    new_workflows = [wf for wf in workflows if wf.get('id') != workflow_id]
    write_json_file(all_path, new_workflows)
    detail_path = os.path.join(DATA_DIR, 'workflows', 'details', f'{workflow_id}.txt')
    if os.path.exists(detail_path):
        os.remove(detail_path)
    return jsonify({"message": "Workflow deleted."})


@workflows_bp.route('/workflows/update_status', methods=['POST'])
def update_workflow_status():
    data = request.get_json()
    workflow_id, new_status = data.get('id'), data.get('status')
    all_path = os.path.join(DATA_DIR, 'workflows', 'all.txt')
    workflows = read_json_file(all_path)
    for wf in workflows:
        if wf.get('id') == workflow_id:
            wf['status'] = new_status
            break
    write_json_file(all_path, workflows)
    detail_path = os.path.join(DATA_DIR, 'workflows', 'details', f'{workflow_id}.txt')
    detail_data = read_json_file(detail_path)
    if detail_data:
        detail_data['status'] = new_status
        write_json_file(detail_path, detail_data)
    return jsonify({"message": "Status updated."})


@workflows_bp.route('/workflows/toggle_recommend', methods=['POST'])
def toggle_recommend_status():
    data = request.get_json()
    workflow_id = data.get('id')
    all_path = os.path.join(DATA_DIR, 'workflows', 'all.txt')
    workflows = read_json_file(all_path)
    target_wf = next((wf for wf in workflows if wf.get('id') == workflow_id), None)
    if not target_wf:
        return jsonify({"error": "Workflow not found"}), 404
    target_wf['isRecommended'] = not target_wf.get('isRecommended', False)
    write_json_file(all_path, workflows)
    return jsonify({"message": "Recommend status updated.", "workflow": target_wf})


@workflows_bp.route('/workflows/add', methods=['POST'])
def add_workflow():
    data = request.get_json()
    if not data or not data.get('workflowName'):
        return jsonify({"error": "Missing workflowName"}), 400
    new_id = f"wf-{uuid.uuid4().hex[:8]}"
    workflow_summary = {
        "id": new_id,
        "name": data.get("workflowName"),
        "description": data.get("description", ""),
        "hostGroup": data.get("hostGroupId"),
        "application": data.get("appName"),
        "status": "已暂停",
        "isRecommended": data.get("isRecommended", False)
    }
    all_path = os.path.join(DATA_DIR, 'workflows', 'all.txt')
    all_workflows = read_json_file(all_path)
    all_workflows.insert(0, workflow_summary)
    write_json_file(all_path, all_workflows)
    workflow_detail = {
        "id": new_id,
        "name": data.get("workflowName"),
        "hostGroup": data.get("hostGroupId"),
        "hostCount": len(data.get("hostIds", [])),
        "application": data.get("appName"),
        "description": data.get("description", ""),
        "status": "已暂停",
        "hosts": []
    }
    detail_path = os.path.join(DATA_DIR, 'workflows', 'details', f'{new_id}.txt')
    write_json_file(detail_path, workflow_detail)
    return jsonify({"message": "Workflow created successfully!", "workflow": workflow_summary}), 201


@workflows_bp.route('/workflows/update_indicator', methods=['POST'])
def update_workflow_indicator():
    data = request.get_json()
    workflow_id, host_id, indicator_id, new_model_info = data.get('workflowId'), data.get('hostId'), data.get(
        'indicatorId'), data.get('newModel')
    if not all([workflow_id, host_id, indicator_id, new_model_info]):
        return jsonify({"error": "Missing required parameters"}), 400
    detail_path = os.path.join(DATA_DIR, 'workflows', 'details', f'{workflow_id}.txt')
    workflow_data = read_json_file(detail_path)
    if not workflow_data:
        return jsonify({"error": "Workflow detail file not found"}), 404
    target_host = next((h for h in workflow_data.get('hosts', []) if h.get('id') == host_id), None)
    if not target_host:
        return jsonify({"error": "Host not found in workflow"}), 404
    target_indicator = next((i for i in target_host.get('indicators', []) if i.get('id') == indicator_id), None)
    if not target_indicator:
        return jsonify({"error": "Indicator not found in host"}), 404
    target_indicator['model'] = new_model_info.get('name')
    target_indicator['algorithm'] = new_model_info.get('algorithm')
    write_json_file(detail_path, workflow_data)
    return jsonify({"message": "Indicator updated successfully."})


@workflows_bp.route('/workflows/save_rule', methods=['POST'])
def save_multi_metric_rule():
    data = request.get_json()
    workflow_id, host_id, rule_data = data.get('workflowId'), data.get('hostId'), data.get('ruleData')
    if not all([workflow_id, host_id, rule_data]):
        return jsonify({"error": "Missing required parameters"}), 400
    detail_path = os.path.join(DATA_DIR, 'workflows', 'details', f'{workflow_id}.txt')
    workflow_data = read_json_file(detail_path)
    if not workflow_data:
        return jsonify({"error": "Workflow detail file not found"}), 404
    target_host = next((h for h in workflow_data.get('hosts', []) if h.get('id') == host_id), None)
    if not target_host:
        return jsonify({"error": "Host not found"}), 404
    if 'multiMetricRules' not in target_host:
        target_host['multiMetricRules'] = []
    rule_id = rule_data.get('id')
    if rule_id:
        rule_index = next((i for i, r in enumerate(target_host['multiMetricRules']) if r.get('id') == rule_id), -1)
        if rule_index != -1:
            target_host['multiMetricRules'][rule_index].update(rule_data)
        else:
            return jsonify({"error": f"Rule with id {rule_id} not found"}), 404
    else:
        rule_data['id'] = f"rule-{uuid.uuid4().hex[:6]}"
        target_host['multiMetricRules'].append(rule_data)
    write_json_file(detail_path, workflow_data)
    return jsonify({"message": "Rule saved successfully.", "rule": rule_data})


@workflows_bp.route('/workflows/delete_rule', methods=['POST'])
def delete_multi_metric_rule():
    data = request.get_json()
    workflow_id, host_id, rule_id = data.get('workflowId'), data.get('hostId'), data.get('ruleId')
    if not all([workflow_id, host_id, rule_id]):
        return jsonify({"error": "Missing required parameters"}), 400
    detail_path = os.path.join(DATA_DIR, 'workflows', 'details', f'{workflow_id}.txt')
    workflow_data = read_json_file(detail_path)
    if not workflow_data: return jsonify({"error": "Workflow detail file not found"}), 404
    target_host = next((h for h in workflow_data.get('hosts', []) if h.get('id') == host_id), None)
    if not target_host or 'multiMetricRules' not in target_host:
        return jsonify({"error": "Host or rules not found"}), 404
    original_count = len(target_host['multiMetricRules'])
    target_host['multiMetricRules'] = [r for r in target_host['multiMetricRules'] if r.get('id') != rule_id]
    if len(target_host['multiMetricRules']) == original_count:
        return jsonify({"error": "Rule not found for deletion"}), 404
    write_json_file(detail_path, workflow_data)
    return jsonify({"message": "Rule deleted successfully."})


# ==================================================================
#  应用 (Application) 和模型 (Model) 相关的 API
# ==================================================================

@workflows_bp.route('/applications', methods=['GET'])
def get_applications():
    filepath = os.path.join(DATA_DIR, 'workflows', 'applications.txt')
    return jsonify(read_json_file(filepath))


@workflows_bp.route('/applications/<app_id>', methods=['GET'])
def get_application_detail(app_id):
    filepath = os.path.join(DATA_DIR, 'workflows', 'apps', f'{app_id}.txt')
    return jsonify(read_json_file(filepath))


@workflows_bp.route('/models', methods=['GET'])
def get_models():
    filepath = os.path.join(DATA_DIR, 'workflows', 'all_models.txt')
    return jsonify(read_json_file(filepath))


@workflows_bp.route('/applications/add', methods=['POST'])
def add_application():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('version'):
        return jsonify({"error": "应用名称和版本是必填项"}), 400
    new_id = data.get('name').lower().replace(' ', '_')
    processed_flow = [{"id": f"step-{i + 1}", "name": step.get("name")} for i, step in enumerate(data.get('flow', []))]
    new_app = {"id": new_id, "name": data.get('name'), "version": data.get('version'),
               "description": data.get('description', '')}
    apps_path = os.path.join(DATA_DIR, 'workflows', 'applications.txt')
    all_apps = read_json_file(apps_path)
    if any(app.get('id') == new_id for app in all_apps):
        return jsonify({"error": f"ID为 '{new_id}' 的应用已存在"}), 409
    all_apps.insert(0, new_app)
    write_json_file(apps_path, all_apps)
    app_detail_path = os.path.join(DATA_DIR, 'workflows', 'apps', f'{new_id}.txt')
    new_app_detail = new_app.copy()
    new_app_detail['flow'] = processed_flow
    write_json_file(app_detail_path, new_app_detail)
    return jsonify({"message": "应用添加成功!", "application": new_app}), 201


# ==================================================================
#  告警 (Alarms) 相关的 API
# ==================================================================

@workflows_bp.route('/alarms/records', methods=['GET'])
def get_alarm_records():
    filepath = os.path.join(DATA_DIR, 'alarms', 'records.txt')
    data = read_json_file(filepath)
    if data is None or 'records' not in data:
        return jsonify({"records": []})
    return jsonify(data)


@workflows_bp.route('/alarms/statistics', methods=['GET'])
def get_alarm_statistics():
    filepath = os.path.join(DATA_DIR, 'alarms', 'statistics.txt')
    data = read_json_file(filepath)
    if data is None or 'statistics' not in data:
        return jsonify({"statistics": []})
    return jsonify(data)


@workflows_bp.route('/alarms/confirm', methods=['POST'])
def confirm_alarm():
    alarm_id = request.get_json().get('id')
    records_path = os.path.join(DATA_DIR, 'alarms', 'records.txt')
    records_data = read_json_file(records_path)
    if records_data is None or 'records' not in records_data:
        records_data = {'records': []}
    original_count = len(records_data['records'])
    records_data['records'] = [rec for rec in records_data['records'] if rec.get('id') != alarm_id]
    if len(records_data['records']) == original_count:
        return jsonify({"error": f"Alarm ID {alarm_id} not found."}), 404
    write_json_file(records_path, records_data)
    stats = {group: sum(1 for r in records_data["records"] if r.get("host_group") == group) for group in
             {rec.get("host_group") for rec in records_data["records"]} if group}
    sorted_stats = sorted(stats.items(), key=lambda item: item[1], reverse=True)
    statistics_data = {
        "statistics": [{"rank": i + 1, "host_group": g, "alert_count": c} for i, (g, c) in enumerate(sorted_stats)]}
    stats_path = os.path.join(DATA_DIR, 'alarms', 'statistics.txt')
    write_json_file(stats_path, statistics_data)
    return jsonify({"message": "Alarm confirmed."})


# ==================================================================
#  主机 (Host) 和主机组 (Host Group) 相关的 API
# ==================================================================

@workflows_bp.route('/hosts', methods=['GET'])
def get_hosts():
    data = read_hosts_data()
    all_hosts = []
    for group in data:
        for host in group.get('hosts', []):
            host_with_group = host.copy()
            host_with_group['group'] = group.get('name')
            all_hosts.append(host_with_group)
    return jsonify(all_hosts)


@workflows_bp.route('/host-groups', methods=['GET'])
def get_host_groups():
    data = read_hosts_data()
    groups_with_count = []
    for group in data:
        groups_with_count.append({
            "id": group.get('id'),
            "name": group.get('name'),
            "description": group.get('description'),
            "hostCount": len(group.get('hosts', []))
        })
    return jsonify(groups_with_count)