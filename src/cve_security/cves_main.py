import cves_scanner
import cves_processor
import os
import logging
from datetime import datetime

# --- [新] 动态路径配置区 ---

# 1. 动态计算项目根目录
# 假设此脚本位于 kylin/src/cve_security/main.py
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    # 从 .../src/cve_security/ 向上回溯两级到 kylin/
    PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
except NameError:
    # 为交互式环境提供备用方案
    PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd(), "../.."))

# 2. 基于项目根目录定义所有路径
# 扫描目标：整个项目文件夹
PROJECT_TO_SCAN = PROJECT_ROOT
# 原始报告存放目录 (未处理的 JSON/HTML)
REPORTS_DIRECTORY = os.path.join(PROJECT_ROOT, "data", "cve_reports")
# 最终输出目录 (处理后的 all.txt, CVE-xxxx.txt)
FINAL_OUTPUT_DIRECTORY = os.path.join(PROJECT_ROOT, "data", "api_data", "cves")
# 日志文件存放目录
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")

# 3. 确保所有输出目录都存在
os.makedirs(REPORTS_DIRECTORY, exist_ok=True)
os.makedirs(FINAL_OUTPUT_DIRECTORY, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


# --- [新] 日志配置 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        # 将日志文件也存放在项目内部的 logs/ 目录下
        logging.FileHandler(os.path.join(LOG_DIR, "cve_scan.log")),
        logging.StreamHandler()
    ]
)

def main():
    """主执行函数"""
    logging.info("=============================================")
    logging.info(f"服务启动，开始扫描任务 @ {datetime.now()}")
    
    # --- 阶段 1: 执行依赖扫描 ---
    logging.info(f"开始扫描项目: {PROJECT_TO_SCAN}")
    scan_result = cves_scanner.start_scan(PROJECT_TO_SCAN, REPORTS_DIRECTORY)
    
    if scan_result.get("status") != "success":
        logging.error(f"扫描阶段失败: {scan_result.get('message')}")
        logging.info("任务因扫描失败而终止。")
        logging.info("=============================================\n")
        return

    logging.info(f"扫描成功: {scan_result.get('message')}")

    # --- 阶段 2: 处理扫描报告 ---
    json_report_path = os.path.join(REPORTS_DIRECTORY, "dependency-check-report.json")
    
    if not os.path.exists(json_report_path):
        logging.error(f"找不到扫描报告: {json_report_path}。无法进行处理。")
        logging.info("任务终止。")
        logging.info("=============================================\n")
        return

    logging.info("开始处理扫描报告...")
    
    # 直接调用 processor 函数，并把输入文件路径和最终输出目录作为参数传递
    # （这要求 cves_processor.py 中的 process_report 函数已按我们之前的讨论修改过）
    process_result = cves_processor.process_report(
        input_filename=json_report_path,
        final_output_dir=FINAL_OUTPUT_DIRECTORY
    )
    
    if process_result.get("status") == "success":
        logging.info(f"报告处理成功: {process_result.get('message')}")
    else:
        logging.error(f"处理阶段失败: {process_result.get('message')}")

    logging.info(f"所有任务完成 @ {datetime.now()}")
    logging.info("=============================================\n")

if __name__ == '__main__':
    main()