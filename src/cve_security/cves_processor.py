# processor.py
import json
import os
import random

def get_severity_chinese(severity):
    # ... (代码不变)
    mapping = { "CRITICAL": "高风险", "HIGH": "高风险", "MEDIUM": "中风险", "LOW": "低风险", "INFO": "信息" }
    return mapping.get(severity.upper(), "未知")

def process_report(input_filename="dependency-check-report.json"):
    output_dir = "static/api/cves"
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open(input_filename, 'r', encoding='utf-8') as f:
            report = json.load(f)
    except FileNotFoundError:
        return {"status": "error", "message": f"输入文件 '{input_filename}' 未找到。"}
    except json.JSONDecodeError:
        return {"status": "error", "message": f"文件 '{input_filename}' 不是有效的JSON格式。"}
    except Exception as e:
        return {"status": "error", "message": f"初始化时发生错误: {str(e)}"}

    cve_list_summary = []
    # ... (此处省略了所有数据处理和文件写入的内部逻辑，它们保持原样)
    for dependency in report.get('dependencies', []):
        if 'vulnerabilities' not in dependency: continue
        file_name = dependency.get('fileName', 'N/A')
        for vuln in dependency['vulnerabilities']:
            cve_id = vuln.get('name')
            if not cve_id or not cve_id.startswith('CVE-'): continue
            cvss_v3 = vuln.get('cvssv3', {})
            severity = get_severity_chinese(vuln.get('severity', '未知'))
            hosts_count = random.randint(1, 10)
            status = random.choice(["未修复", "已修复"])
            summary_item = {
                "id": cve_id, "date": report.get('projectInfo', {}).get('reportDate', 'N/A').split('T')[0],
                "package": file_name, "severity": severity, "cvss": cvss_v3.get('baseScore', 'N/A'),
                "hosts": hosts_count, "status": status,
            }
            cve_list_summary.append(summary_item)
            affected_hosts = []
            for i in range(1, hosts_count + 1):
                affected_hosts.append({ "id": f"host-{i:03d}", "name": f"server-{random.choice(['web', 'db', 'app'])}-{i:02d}", "ip": f"192.168.{random.randint(1, 10)}.{random.randint(10, 200)}", "group": random.choice(["Web Servers", "Database", "App Servers"]), "repo": "ky10.aarch64", "lastScan": "2025-07-26 10:30", "rpms": {"affected": f"{dependency.get('packages', [{}])[0].get('id', 'N/A').split('@')[0]}-{dependency.get('packages', [{}])[0].get('id', 'N/A').split('@')[1]}", "pending": "待定", "method": "热补丁", "count": 1} })
            detail_item = { "id": cve_id, "releaseDate": summary_item["date"], "cvss": summary_item["cvss"], "severity": severity, "relatedCveCount": len(vuln.get('references', [])), "description": vuln.get('description', '无详细描述。'), "affectedProducts": [{"product": report.get('projectInfo', {}).get('name', 'N/A'), "package": file_name}], "affectedHosts": affected_hosts }
            detail_filename = os.path.join(output_dir, f"{cve_id}.txt")
            with open(detail_filename, 'w', encoding='utf-8') as f_detail:
                json.dump(detail_item, f_detail, ensure_ascii=False, indent=2)

    summary_filename = os.path.join(output_dir, "all.txt")
    with open(summary_filename, 'w', encoding='utf-8') as f_summary:
        json.dump(cve_list_summary, f_summary, ensure_ascii=False, indent=2)

    return {
        "status": "success",
        "message": f"处理完成！生成了 {len(cve_list_summary)} 个CVE的详情文件。",
        "summary_file": f"/{summary_filename.replace(os.path.sep, '/')}",
        "details_directory": f"/{output_dir.replace(os.path.sep, '/')}/"
    }