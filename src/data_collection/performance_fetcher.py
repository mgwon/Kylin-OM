import requests
import json
import os

def fetch_and_save_dashboard_data(grafana_url: str, token: str, dashboard_uid: str, output_dir: str, output_filename: str):
    """
    通过API获取指定仪表盘的JSON定义，并将其保存到指定目录的文件中。

    返回:
        一个包含操作状态和信息的字典。
    """
    print(f"--- [性能报告] 步骤 1: 开始从Grafana获取仪表盘 (UID: {dashboard_uid}) 数据 ---")
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    full_output_path = os.path.join(output_dir, output_filename)
    url = f"{grafana_url}/api/dashboards/uid/{dashboard_uid}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        dashboard_data = response.json()
        
        with open(full_output_path, 'w', encoding='utf-8') as json_file:
            json.dump(dashboard_data, json_file, ensure_ascii=False, indent=2)

        abs_path = os.path.abspath(full_output_path)
        message = f"成功获取并保存仪表盘数据到: {abs_path}"
        print(f"--- {message} ---")
        return {"status": "success", "message": message, "output_file": abs_path}

    except requests.exceptions.HTTPError as http_err:
        message = f"HTTP请求失败: {http_err} - 响应: {http_err.response.text}"
        print(f"--- [错误] {message} ---")
        return {"status": "error", "message": message}
    except Exception as e:
        message = f"发生未知错误: {e}"
        print(f"--- [错误] {message} ---")
        return {"status": "error", "message": message}