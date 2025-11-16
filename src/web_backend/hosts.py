import json
import time
from flask import Blueprint, jsonify, request, abort

# 1. 不再导入 Flask，而是导入 Blueprint
hosts_bp = Blueprint('hosts_bp', __name__)

DB_FILE = '../../data/api_data/hosts.json'

def read_data():
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def write_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==================================================================
# --- 主机管理的 API 端点 ---
# ==================================================================

# 2. 使用蓝图对象 hosts_bp 来注册路由
@hosts_bp.route('/hosts', methods=['GET'])
def get_hosts():
    data = read_data()
    all_hosts = []
    for group in data:
        for host in group.get('hosts', []):
            host_with_group = host.copy()
            host_with_group['group'] = group.get('name')
            all_hosts.append(host_with_group)
    return jsonify(all_hosts)

@hosts_bp.route('/hosts/add', methods=['POST'])
def add_host():
    print("breakpoint")
    if not request.json:
        abort(400, "请求体必须是JSON格式")
    new_host_data = request.json
    required_fields = ['name', 'ip', 'ssh', 'group', 'isMgmt', 'status']
    if not all(field in new_host_data for field in required_fields):
        abort(400, "缺少必要的字段")
    data = read_data()
    target_group_name = new_host_data['group']
    group_found = False
    for group in data:
        if group['name'] == target_group_name:
            new_host = {
                "id": f"host-{int(time.time() * 1000)}",
                "name": new_host_data.get('name'),
                "ip": new_host_data.get('ip'),
                "ssh": int(new_host_data.get('ssh')),
                "isMgmt": new_host_data.get('isMgmt'),
                "status": new_host_data.get('status')
            }
            group.setdefault('hosts', []).insert(0, new_host)
            group_found = True
            break
    if not group_found:
        abort(404, f"名为 '{target_group_name}' 的主机组未找到")
    write_data(data)
    return jsonify(
        {"message": f"主机 '{new_host_data['name']}' 已成功添加到 '{target_group_name}'", "host": new_host}), 201

@hosts_bp.route('/hosts/delete', methods=['POST'])
def delete_host():

    """API端点: 从其所在的主机组中删除一个主机"""
    print("breakpoint")
    if not request.json or 'id' not in request.json:
        abort(400, "请求体必须包含 'id'")

    host_id_to_delete = request.json['id']
    data = read_data()

    host_deleted = False
    for group in data:
        hosts_in_group = group.get('hosts', [])
        original_count = len(hosts_in_group)
        # 过滤掉要删除的主机
        group['hosts'] = [host for host in hosts_in_group if host['id'] != host_id_to_delete]
        if len(group['hosts']) < original_count:
            host_deleted = True
            break

    if not host_deleted:
        abort(404, f"ID为 {host_id_to_delete} 的主机未找到")

    write_data(data)
    return jsonify({"message": f"主机ID {host_id_to_delete} 已成功删除"})

@hosts_bp.route('/host-groups', methods=['GET'])
def get_host_groups():
    # ... 函数体不变 ...
    data = read_data()
    groups_with_count = []
    for group in data:
        group_info = {
            "id": group.get('id'),
            "name": group.get('name'),
            "description": group.get('description'),
            "hostCount": len(group.get('hosts', []))
        }
        groups_with_count.append(group_info)
    return jsonify(groups_with_count)

@hosts_bp.route('/host-groups/add', methods=['POST'])
def add_host_group():
    """API端点: 添加一个新主机组"""
    if not request.json or 'groupName' not in request.json:
        abort(400, "请求体必须是JSON格式且包含 'groupName'")

    data = read_data()
    new_group_name = request.json.get('groupName').strip()

    if not new_group_name:
        abort(400, "'groupName' 不能为空")
    if any(g['name'] == new_group_name for g in data):
        abort(409, f"名为 '{new_group_name}' 的主机组已存在")  # 409 Conflict

    new_group = {
        "id": f"g-{int(time.time() * 1000)}",
        "name": new_group_name,
        "description": request.json.get('description', ''),
        "hosts": []  # 新增的主机组总是从0个主机开始
    }

    data.insert(0, new_group)
    write_data(data)
    return jsonify({"message": f"主机组 '{new_group['name']}' 添加成功", "group": new_group}), 201


@hosts_bp.route('/host-groups/delete', methods=['POST'])
def delete_host_group():
    """API端点: 删除一个主机组 (及其包含的所有主机)"""
    if not request.json or 'id' not in request.json:
        abort(400, "请求体必须包含 'id'")

    group_id_to_delete = request.json['id']
    data = read_data()

    if not any(g['id'] == group_id_to_delete for g in data):
        abort(404, f"ID为 {group_id_to_delete} 的主机组未找到")

    updated_data = [group for group in data if group['id'] != group_id_to_delete]

    write_data(updated_data)
    return jsonify({"message": f"主机组ID {group_id_to_delete} 已成功删除"})