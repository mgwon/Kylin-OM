import json
import os
import time
from flask import Blueprint, jsonify, abort, request

# ... (蓝图定义和DATA_DIRECTORY不变)
config_tracing_bp = Blueprint('config_tracing_bp', __name__)
DATA_DIRECTORY = '../../data/api_data/config-tracing-data'


# --- 辅助函数 ---

def read_data_file(filename):
    """从 config-tracing-data 子目录中读取并解析JSON数据。"""
    try:
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, DATA_DIRECTORY, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


# --- 新增: 写入数据的辅助函数 ---
def write_data_file(filename, data):
    """将数据写入到 config-tracing-data 子目录的文件中。"""
    try:
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, DATA_DIRECTORY, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error writing to {filename}: {e}")
        return False


def read_hosts_from_root():
    """特殊辅助函数：从 backend 根目录读取 hosts.json。"""
    try:
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, '..', '..', 'data', 'api_data', 'hosts.json')  # 直接指向根目录的hosts.json
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 将数据打平，方便前端使用
            all_hosts = []
            for group in data:
                all_hosts.extend(group.get('hosts', []))
            return all_hosts
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def _find_asset_domain_info(asset_id):
    """根据asset_id查找其IP、所属业务域ID和业务域名称。"""
    all_domains = read_data_file('domains.txt') or []
    for domain in all_domains:
        detail_filename = f"domain-detail-{domain['id']}.txt"
        domain_detail = read_data_file(detail_filename)
        if domain_detail and 'assets' in domain_detail:
            for asset in domain_detail['assets']:
                if asset['id'] == asset_id:
                    return {
                        "asset_ip": asset.get('ip'),
                        "domain_id": domain.get('id'),
                        "domain_name": domain.get('name')
                    }
    return None

def _update_domain_overall_status(domain_id):
    """
    Checks all assets within a domain and updates the domain's overall driftStatus
    in the main domains.txt file.
    """
    detail_filename = f'domain-detail-{domain_id}.txt'
    domain_detail = read_data_file(detail_filename)
    if not domain_detail:
        return  # Cannot proceed without details

    # Assume the domain is healthy until a drifted asset is found
    is_domain_healthy = True
    assets = domain_detail.get('assets', [])
    if not assets:
        # If there are no assets, it's 'Not Monitored'
        new_status = "未监控"
    else:
        for asset in assets:
            if '未同步' in asset.get('syncStatus', ''):
                is_domain_healthy = False
                break  # Found a drifted asset, no need to check further
        new_status = "健康" if is_domain_healthy else "漂移"

    # Now, update the main domains.txt file
    all_domains = read_data_file('domains.txt') or []
    for domain in all_domains:
        if domain['id'] == domain_id:
            domain['driftStatus'] = new_status
            break

    write_data_file('domains.txt', all_domains)

# ==================================================================
# --- API 端点 (更新与新增) ---
# ==================================================================
@config_tracing_bp.route('/domains/<domain_id>/assets', methods=['POST'])
def add_assets_to_domain(domain_id):
    if not request.json or 'hosts' not in request.json:
        abort(400, "请求体必须是JSON格式且包含 'hosts' 列表")

    hosts_to_add = request.json.get('hosts', [])
    if not isinstance(hosts_to_add, list):
        abort(400, "'hosts' 必须是一个列表")

    # 1. 读取业务域详情文件，如果不存在则创建一个基础结构
    detail_filename = f'domain-detail-{domain_id}.txt'
    domain_detail = read_data_file(detail_filename)
    if domain_detail is None:
        # 如果详情文件不存在，需要从主列表获取业务域名称
        all_domains = read_data_file('domains.txt') or []
        domain_info = next((d for d in all_domains if d['id'] == domain_id), None)
        if not domain_info:
            abort(404, "业务域未找到")
        domain_detail = {"id": domain_id, "name": domain_info['name'], "assets": []}

    # 2. 将新主机添加到 assets 列表 (避免重复添加)
    existing_asset_ids = {asset['id'] for asset in domain_detail['assets']}
    for host in hosts_to_add:
        if host['id'] not in existing_asset_ids:
            new_asset = {
                "id": host['id'],
                "ip": host['ip'],
                "protocol": "ipv4",  # 默认值
                "syncStatus": "✓ 已同步",  # 初始状态为已同步
                "driftCount": 0
            }
            domain_detail['assets'].append(new_asset)

    # 3. 更新业务域主列表中的 assetCount
    all_domains = read_data_file('domains.txt') or []
    for d in all_domains:
        if d['id'] == domain_id:
            d['assetCount'] = len(domain_detail['assets'])
            break

    # 4. 将更新后的数据写回文件
    if write_data_file(detail_filename, domain_detail) and write_data_file('domains.txt', all_domains):
        return jsonify({"message": f"成功向业务域添加 {len(hosts_to_add)} 个主机"}), 200
    else:
        abort(500, "写入业务域详情或列表文件失败")


@config_tracing_bp.route('/domains/<domain_id>/assets/<asset_id>', methods=['DELETE'])
def delete_asset_from_domain(domain_id, asset_id):
    """
    API 端点: 从指定业务域中删除一个资产(主机)。
    """
    # 1. 读取业务域详情文件
    detail_filename = f'domain-detail-{domain_id}.txt'
    domain_detail = read_data_file(detail_filename)
    if domain_detail is None:
        abort(404, {"message": f"未找到业务域 {domain_id} 的详情文件。"})

    # 2. 查找并删除资产
    original_asset_count = len(domain_detail['assets'])
    # 通过列表推导式创建一个不包含要删除资产的新列表
    domain_detail['assets'] = [asset for asset in domain_detail['assets'] if asset['id'] != asset_id]

    # 如果列表长度没变，说明没有找到该资产
    if len(domain_detail['assets']) == original_asset_count:
        abort(404, {"message": f"在业务域 {domain_id} 中未找到资产 {asset_id}。"})

    # 3. 读取并更新主业务域列表中的 assetCount
    all_domains = read_data_file('domains.txt') or []
    for d in all_domains:
        if d['id'] == domain_id:
            d['assetCount'] = len(domain_detail['assets'])
            break

    # 4. 将更新后的数据写回两个文件
    if write_data_file(detail_filename, domain_detail) and write_data_file('domains.txt', all_domains):
        _update_domain_overall_status(domain_id)
        return jsonify({"message": f"成功从业务域移除主机"}), 200
    else:
        abort(500, {"message": "写入文件失败，无法完成删除操作。"})

@config_tracing_bp.route('/all-hosts', methods=['GET'])
def get_all_hosts():
    """
    API 端点: 获取所有主机的扁平化列表，供“添加主机”弹窗使用。
    """
    data = read_hosts_from_root()
    return jsonify(data)

@config_tracing_bp.route('/domains', methods=['GET'])
def get_domains():
    # 修改: 如果文件不存在，返回空列表而不是错误
    data = read_data_file('domains.txt')
    if data is None:
        return jsonify([])
    return jsonify(data)


# --- 新增: 创建业务域的 API ---
@config_tracing_bp.route('/domains', methods=['POST'])
def create_domain():
    if not request.json or 'name' not in request.json:
        abort(400, "请求体必须是JSON格式且包含 'name'")

    new_domain_data = request.json
    domains = read_data_file('domains.txt') or []

    new_domain = {
        "id": f"dom-{int(time.time() * 1000)}",
        "name": new_domain_data.get('name'),
        "assetCount": 0,
        "driftStatus": "未监控",
        "lastScan": "N/A"
        # isMonitorOn 和 isAlertOn 是前端状态，后端暂不处理
    }

    domains.insert(0, new_domain)  # 插入到最前面
    if write_data_file('domains.txt', domains):
        return jsonify({"message": "业务域创建成功", "domain": new_domain}), 201
    else:
        abort(500, "写入业务域文件失败")


@config_tracing_bp.route('/baselines', methods=['GET'])
def get_baselines():
    # 修改: 如果文件不存在，返回空列表
    data = read_data_file('baselines.txt')
    if data is None:
        return jsonify([])
    return jsonify(data)

@config_tracing_bp.route('/domains/<domain_id>', methods=['GET'])
def get_domain_detail(domain_id):
    """
    API 端点: 获取单个业务域的详细信息，包括其下的资产列表。
    """
    filename = f'domain-detail-{domain_id}.txt'
    data = read_data_file(filename)
    if data is None:
        abort(404, f"未找到业务域 {domain_id} 的详情文件。")
    return jsonify(data)


@config_tracing_bp.route('/baselines/content/<baseline_id>', methods=['GET'])
def get_baseline_content(baseline_id):
    """
    API 端点: 获取单个基线配置文件的具体内容。
    """
    filename = f'baseline-content-{baseline_id}.txt'
    data = read_data_file(filename)
    if data is None:
        abort(404, f"未找到基线 {baseline_id} 的内容文件。")
    return jsonify(data)


# --- 新增: 新增基线配置的 API ---
@config_tracing_bp.route('/baselines', methods=['POST'])
def create_baseline():
    if not request.json or not all(k in request.json for k in ['domainId', 'path', 'content']):
        abort(400, "请求缺少必要的字段 (domainId, path, content)")

    new_baseline_data = request.json
    baselines = read_data_file('baselines.txt') or []
    domains = read_data_file('domains.txt') or []

    # 根据 domainId 查找 domainName
    domain_name = next((d['name'] for d in domains if d['id'] == new_baseline_data.get('domainId')), "未知业务域")

    new_baseline = {
        "id": f"bl-{int(time.time() * 1000)}",
        "path": new_baseline_data.get('path'),
        "domain": domain_name,
        "source": new_baseline_data.get('source', '手动输入'),
        "lastModified": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    baselines.insert(0, new_baseline)

    # 同时，为这个基线创建一个内容文件
    content_data = {
        "id": new_baseline['id'],
        "path": new_baseline['path'],
        "content": new_baseline_data.get('content')
    }

    if write_data_file('baselines.txt', baselines) and write_data_file(f"baseline-content-{new_baseline['id']}.txt",
                                                                       content_data):
        return jsonify({"message": "基线配置新增成功", "baseline": new_baseline}), 201
    else:
        abort(500, "写入基线或内容文件失败")


# --- 新增: 删除基线配置的 API ---
@config_tracing_bp.route('/baselines/<baseline_id>', methods=['DELETE'])
def delete_baseline(baseline_id):
    baselines = read_data_file('baselines.txt') or []

    baseline_to_delete = next((b for b in baselines if b['id'] == baseline_id), None)
    if not baseline_to_delete:
        abort(404, "未找到要删除的基线")

    updated_baselines = [b for b in baselines if b['id'] != baseline_id]

    # 尝试删除对应的 content 文件
    try:
        base_dir = os.path.dirname(__file__)
        content_file_path = os.path.join(base_dir, DATA_DIRECTORY, f"baseline-content-{baseline_id}.txt")
        if os.path.exists(content_file_path):
            os.remove(content_file_path)
    except Exception as e:
        print(f"删除内容文件失败: {e}")  # 记录错误，但继续执行

    if write_data_file('baselines.txt', updated_baselines):
        return jsonify({"message": f"基线配置 '{baseline_to_delete['path']}' 删除成功"}), 200
    else:
        abort(500, "写入基线文件失败")

@config_tracing_bp.route('/assets/config/<asset_id>', methods=['GET'])
def get_asset_config_detail(asset_id):
    """
    API 端点: 获取单个资产(主机)的当前漂移配置详情。
    对应 "当前配置" 弹窗。
    """
    filename = f'host-config-asset-{asset_id}.txt'
    data = read_data_file(filename)
    if data is None:
        # 如果没有特定的漂移文件，可以返回一个空状态或错误
        # 这里为了演示，我们假设对于未漂移的主机，此接口不被调用或调用后无数据
        abort(404, f"未找到资产 {asset_id} 的配置详情文件。")
    return jsonify(data)


@config_tracing_bp.route('/assets/status/<asset_id>', methods=['GET'])
def get_asset_status_detail(asset_id):
    """
    API 端点: 动态获取单个资产(主机)上所有配置的同步状态列表。
    此版本完全通过读取文件来动态生成数据，无任何硬编码。
    """
    # === 第 1 步: 查找主机信息，确定其 IP 和所属的业务域名称 ===
    asset_ip = "未知IP"
    asset_domain_name = "未知业务域"
    all_domains = read_data_file('domains.txt') or []
    found_asset = False
    for domain in all_domains:
        detail_filename = f"domain-detail-{domain['id']}.txt"
        domain_detail = read_data_file(detail_filename)
        if domain_detail and 'assets' in domain_detail:
            for asset in domain_detail['assets']:
                if asset['id'] == asset_id:
                    asset_ip = asset.get('ip', '未知IP')
                    asset_domain_name = domain.get('name', '未知业务域')
                    found_asset = True
                    break
        if found_asset:
            break

    if not found_asset:
        abort(404, {"message": f"在任何业务域中都未找到资产 {asset_id}。"})

    # === 第 2 步: 根据业务域名称，筛选出所有适用的基线配置 ===
    all_baselines = read_data_file('baselines.txt') or []
    applicable_baselines = [
        b for b in all_baselines if b.get('domain') == asset_domain_name
    ]

    # === 第 3 步: 检查该主机是否存在漂移文件，并获取漂移的配置路径 ===
    drifted_paths = set()
    drift_config_file = f'host-config-asset-{asset_id}.txt'
    drift_data = read_data_file(drift_config_file)
    if drift_data and 'filePath' in drift_data:
        # 将漂移的配置文件路径添加到一个集合中，便于快速查找
        drifted_paths.add(drift_data['filePath'])

    # === 第 4 步: 遍历适用基线，生成最终的状态列表 ===
    final_configs = []
    for baseline in applicable_baselines:
        baseline_path = baseline.get('path')
        if not baseline_path:
            continue

        # 判断此基线路径是否存在于漂移路径集合中
        status = "未同步" if baseline_path in drifted_paths else "已同步"

        final_configs.append({
            "id": baseline.get('id'),
            "path": baseline_path,
            "status": status
        })

    # === 第 5 步: 组合最终数据并返回 ===
    response_data = {
        "ip": asset_ip,
        "configs": final_configs
    }

    return jsonify(response_data)

@config_tracing_bp.route('/assets/<asset_id>/sync', methods=['POST'])
def sync_asset_config(asset_id):
    """
    API 端点: 同步单个主机的配置，使其恢复到基线状态。
    逻辑: 删除漂移记录文件，并更新业务域详情中的主机状态。
    """
    domain_info = _find_asset_domain_info(asset_id)
    if not domain_info:
        abort(404, {"message": f"未找到资产 {asset_id}。"})

    # 1. 更新业务域详情文件中的状态
    detail_filename = f"domain-detail-{domain_info['domain_id']}.txt"
    domain_detail = read_data_file(detail_filename)
    asset_updated = False
    for asset in domain_detail.get('assets', []):
        if asset['id'] == asset_id:
            asset['syncStatus'] = "✓ 已同步"
            asset['driftCount'] = 0
            asset_updated = True
            break

    if not asset_updated:
        abort(500, {"message": "在业务域详情中更新状态失败。"})

    # 2. 删除代表漂移的配置文件
    drift_file_path = os.path.join(os.path.dirname(__file__), DATA_DIRECTORY, f'host-config-asset-{asset_id}.txt')
    if os.path.exists(drift_file_path):
        os.remove(drift_file_path)

    # 3. 写回更新后的业务域详情文件
    if write_data_file(detail_filename, domain_detail):
        # (可选高级逻辑: 检查是否整个业务域都已同步，并更新 domains.txt 中的状态)
        _update_domain_overall_status(domain_info['domain_id'])
        return jsonify({"message": f"主机 {domain_info['asset_ip']} 的配置已同步至基线。"}), 200
    else:
        abort(500, {"message": "写入业务域详情文件失败。"})


@config_tracing_bp.route('/assets/<asset_id>/set-as-baseline', methods=['POST'])
def set_config_as_baseline(asset_id):
    """
    API 端点: 将主机当前的漂移配置设置为其业务域的新基线。
    """
    domain_info = _find_asset_domain_info(asset_id)
    if not domain_info:
        abort(404, {"message": f"未找到资产 {asset_id}。"})

    # 1. 读取该主机的漂移配置内容
    drift_config_filename = f'host-config-asset-{asset_id}.txt'
    drift_data = read_data_file(drift_config_filename)
    if not drift_data:
        abort(404, {"message": f"找不到资产 {asset_id} 的漂移配置文件，无法设为基线。"})

    new_content = drift_data.get('content')
    config_path = drift_data.get('filePath')

    # 2. 查找对应的旧基线ID
    all_baselines = read_data_file('baselines.txt') or []
    baseline_id_to_update = None
    for baseline in all_baselines:
        if baseline.get('domain') == domain_info['domain_name'] and baseline.get('path') == config_path:
            baseline_id_to_update = baseline['id']
            baseline['lastModified'] = time.strftime("%Y-%m-%d %H:%M:%S")  # 更新修改时间
            break

    if not baseline_id_to_update:
        abort(404, {"message": f"找不到路径为 {config_path} 且属于业务域 {domain_info['domain_name']} 的基线。"})

    # 3. 更新基线内容文件
    baseline_content_filename = f'baseline-content-{baseline_id_to_update}.txt'
    baseline_content_data = read_data_file(baseline_content_filename)
    if baseline_content_data:
        baseline_content_data['content'] = new_content
        write_data_file(baseline_content_filename, baseline_content_data)
        write_data_file('baselines.txt', all_baselines)  # 写回更新了时间的baselines列表
    else:
        abort(404, {"message": f"找不到基线内容文件 {baseline_content_filename}。"})

    # 4. 执行与“同步”一样的操作来清理漂移状态
    # (因为当前配置已是基线，所以它不再是“漂移”状态)
    sync_response, status_code = sync_asset_config(asset_id)
    if status_code == 200:
        return jsonify({"message": f"已将主机 {domain_info['asset_ip']} 的当前配置设为新基线。"}), 200
    else:
        return sync_response, status_code


@config_tracing_bp.route('/domains/<domain_id>/scan', methods=['POST'])
def scan_domain_for_drift(domain_id):
    """
    API 端点: 模拟扫描一个业务域下的所有主机，检查配置漂移。
    """
    # 1. 获取业务域详情和其下的资产
    detail_filename = f'domain-detail-{domain_id}.txt'
    domain_detail = read_data_file(detail_filename)
    if not domain_detail:
        abort(404, {"message": "找不到业务域详情文件。"})

    domain_name = domain_detail.get('name')
    assets = domain_detail.get('assets', [])

    # 2. 获取该业务域的所有基线
    all_baselines = read_data_file('baselines.txt') or []
    applicable_baselines = {b['path']: b for b in all_baselines if b.get('domain') == domain_name}
    if not applicable_baselines:
        return jsonify({"message": f"业务域 '{domain_name}' 没有配置任何基线，无需扫描。"}), 200

    # 3. 遍历该业务域下的所有资产(主机)
    for asset in assets:
        asset_id = asset['id']
        has_drift = False

        # 4. 遍历所有应有的基线，检查每一个
        for path, baseline_info in applicable_baselines.items():
            baseline_content_file = f"baseline-content-{baseline_info['id']}.txt"
            baseline_data = read_data_file(baseline_content_file)

            # 代表主机当前配置的文件
            host_current_config_file = f"host-config-asset-{asset_id}.txt"
            host_data = read_data_file(host_current_config_file)

            # 只有当主机当前配置文件和基线文件都存在时，才进行比较
            if baseline_data and host_data and host_data.get('filePath') == path:
                if baseline_data.get('content') != host_data.get('content'):
                    has_drift = True
                    break  # 只要有一个文件漂移，该主机就算漂移

        # 5. 根据扫描结果更新主机的同步状态
        if has_drift:
            asset['syncStatus'] = "⊗ 未同步 1条"
            asset['driftCount'] = 1
        else:
            asset['syncStatus'] = "✓ 已同步"
            asset['driftCount'] = 0
            # 如果主机是同步的，顺便把可能存在的旧漂移文件删掉
            drift_file_path = os.path.join(os.path.dirname(__file__), DATA_DIRECTORY,
                                           f'host-config-asset-{asset_id}.txt')
            if os.path.exists(drift_file_path) and not has_drift:
                # 附加逻辑：如果主机扫描为同步，但漂移文件内容与基线相同，则应删除该漂移文件
                # 这是为了处理 “设为基线”后，漂移文件还残留的情况
                host_current_config_file = f"host-config-asset-{asset_id}.txt"
                host_data = read_data_file(host_current_config_file)
                if host_data:
                    baseline_content_file = f"baseline-content-{applicable_baselines[host_data['filePath']]['id']}.txt"
                    baseline_data = read_data_file(baseline_content_file)
                    if host_data.get('content') == baseline_data.get('content'):
                        os.remove(drift_file_path)

    # 6. 将更新后的业务域详情写回文件
    if write_data_file(detail_filename, domain_detail):
        _update_domain_overall_status(domain_id)
        return jsonify({"message": f"业务域 '{domain_name}' 扫描完成。"}), 200
    else:
        abort(500, {"message": "扫描结果写入文件失败。"})

# ... (所有其他的 GET API 端点保持不变) ...