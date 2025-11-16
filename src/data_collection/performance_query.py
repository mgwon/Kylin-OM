import json
import os
import re
import string
from datetime import datetime, timedelta
import requests


def sanitize_filename(name):
    """
    对字符串进行处理，使其可以安全地作为文件名。
    """
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c if c in valid_chars else '_' for c in name)
    filename = re.sub(r'_+', '_', filename)
    return filename[:100]

def parse_grafana_time(time_str):
    """
    解析 Grafana 风格的时间字符串 (例如 'now-24h') 并返回 datetime 对象。
    """
    now = datetime.utcnow()
    if time_str == 'now':
        return now
    match = re.match(r'now-(\d+)([hmsd])', time_str)
    if not match:
        raise ValueError(f"不支持的时间格式: {time_str}")
    value, unit = int(match.group(1)), match.group(2)
    if unit == 'h':
        return now - timedelta(hours=value)
    elif unit == 'm':
        return now - timedelta(minutes=value)
    elif unit == 's':
        return now - timedelta(seconds=value)
    elif unit == 'd':
        return now - timedelta(days=value)
    else:
        raise ValueError(f"不支持的时间单位: {unit}")

def query_prometheus(prometheus_url, query, start_time, end_time, step):
    """
    对 Prometheus 实例执行范围查询。
    """
    api_url = f"{prometheus_url.strip('/')}/api/v1/query_range"
    params = {
        'query': query,
        'start': start_time.isoformat() + "Z",
        'end': end_time.isoformat() + "Z",
        'step': step
    }
    try:
        print(f"    - 执行查询: {query[:100]}...")
        response = requests.get(api_url, params=params, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"错误: 查询 Prometheus 失败。 查询语句:\n'{query}'\n错误详情: {e}")
        return None
    except json.JSONDecodeError:
        print(f"错误: 解析 Prometheus 的 JSON 响应失败。 查询语句:\n'{query}'")
        print(f"响应内容: {response.text}")
        return None

def process_panels(panels, prometheus_url, template_vars, time_range, output_dir):
    """
    递归处理面板列表，提取并执行 PromQL 查询，然后保存结果。
    """
    for panel in panels:
        if panel.get('type') == 'row' and 'panels' in panel:
            print(f"进入 Row: {panel.get('title', '无标题 Row')}")
            if panel.get('collapsed', False) and panel.get('panels'):
                process_panels(panel['panels'], prometheus_url, template_vars, time_range, output_dir)
            elif not panel.get('collapsed', True) and panel.get('panels'):
                 process_panels(panel['panels'], prometheus_url, template_vars, time_range, output_dir)
            continue
        
        datasource = panel.get('datasource')
        is_prometheus_panel = isinstance(datasource, dict) and datasource.get('type') == 'prometheus'
        
        if not (panel.get('targets') and is_prometheus_panel):
            continue

        panel_title = panel.get('title', '无标题')
        panel_id = panel.get('id', 'no-id')
        print(f"  - 发现面板: '{panel_title}' (ID: {panel_id})")

        panel_results = {
            "panel_title": panel_title,
            "panel_id": panel_id,
            "description": panel.get('description', ''),
            "targets": []
        }

        has_queries = False
        for target in panel.get('targets', []):
            if not target.get('expr'):
                continue
            
            has_queries = True
            query = target['expr']
            
            for var, value in template_vars.items():
                query = query.replace(f'${var}', str(value))
                
            query = re.sub(r'\$\{([^}]+)\}', lambda m: str(template_vars.get(m.group(1).split(':')[0], f'${{{m.group(0)}}}')), query)

            result = query_prometheus(
                prometheus_url,
                query,
                time_range['start'],
                time_range['end'],
                time_range['step']
            )

            panel_results["targets"].append({
                "refId": target.get('refId', 'N/A'),
                "query": query,
                "legendFormat": target.get('legendFormat', ''),
                "hidden": target.get('hide', False),
                "result": result
            })

        if has_queries:
            filename = sanitize_filename(f"panel_{panel_id}_{panel_title}") + '.json'
            output_path = os.path.join(output_dir, filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(panel_results, f, indent=2, ensure_ascii=False)
            print(f"    => 结果已保存至: {output_path}")

def execute_dashboard_query(config):
    """
    这个函数包含了原来 main 函数的核心逻辑，但它接收一个配置字典作为参数。
    """
    dashboard_file_path = config.get("dashboard_file_path")
    prometheus_url = config.get("prometheus_url")
    output_dir = config.get("output_dir", "prometheus_data")

    if not dashboard_file_path or not prometheus_url:
        return {"error": "缺少 'dashboard_file_path' 或 'prometheus_url' 参数。"}, 400

    os.makedirs(output_dir, exist_ok=True)

    try:
        with open(dashboard_file_path, 'r', encoding='utf-8') as f:
            dashboard_json = json.load(f)
    except FileNotFoundError:
        return {"error": f"找不到仪表盘文件 {dashboard_file_path}"}, 404
    except json.JSONDecodeError:
        return {"error": f"无法解析 {dashboard_file_path} 的 JSON 内容"}, 400

    template_vars = {
        'job': config.get('job', 'node_exporter'),
        'nodename': config.get('nodename', 'localhost'),
        'node': config.get('node', 'localhost:9100'),
        '__rate_interval': config.get('rate-interval', '5m')
    }

    if 'templating' in dashboard_json.get('dashboard', {}) and 'list' in dashboard_json['dashboard']['templating']:
        for var in dashboard_json['dashboard']['templating']['list']:
            if var.get('name') == 'diskdevices' and var.get('name') not in template_vars:
                default_val = var.get('query', var.get('options', [{}])[0].get('value'))
                if default_val:
                    template_vars['diskdevices'] = default_val
                    print(f"使用 '$diskdevices' 的默认值: {default_val}")

    try:
        start_time = parse_grafana_time(config.get("start", "now-1h"))
        end_time = parse_grafana_time(config.get("end", "now"))
    except ValueError as e:
        return {"error": f"解析时间范围失败: {e}"}, 400

    time_range = {
        'start': start_time,
        'end': end_time,
        'step': config.get("step", "1m")
    }

    print("开始提取并执行查询...")
    print(f"Prometheus URL: {prometheus_url}")
    print(f"时间范围: 从 {time_range['start'].isoformat()}Z 到 {time_range['end'].isoformat()}Z")
    print(f"时间步长: {time_range['step']}")
    print(f"使用的模板变量: {template_vars}")
    print("-" * 40)

    if 'dashboard' in dashboard_json and 'panels' in dashboard_json['dashboard']:
        process_panels(
            dashboard_json['dashboard']['panels'],
            prometheus_url,
            template_vars,
            time_range,
            output_dir
        )
    else:
        print("错误: 无法在 JSON 文件中找到 'dashboard' 或 'panels' 键。")
        return {"error": "无法在 JSON 文件中找到 'dashboard' 或 'panels' 键。"}, 400
    
    print("-" * 40)
    print("脚本执行完毕。")
    return {"status": "success", "message": f"查询结果已保存到 '{output_dir}' 目录。"}, 200


