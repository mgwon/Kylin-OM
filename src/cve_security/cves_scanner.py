# scanner.py
import subprocess
import os

# --- [新增] 动态计算脚本路径 ---
# 获取当前脚本 (scanner.py) 所在的目录的绝对路径
# 例如: /home/user/kylin-OM/kylin/src/cve_security
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 从当前目录向上回溯两级，找到项目的根目录 'kylin'
# .../cve_security -> .../src -> .../kylin
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

# 基于项目根目录，构建 dependency-check.sh 脚本的最终绝对路径
# 结果: /home/user/kylin-OM/kylin/scripts/dependency-check.sh
DEPENDENCY_CHECK_SCRIPT_PATH = os.path.join(PROJECT_ROOT, "scripts", "dependency-check.sh")
# --- [新增结束] ---


def run_dependency_check(project_path, report_directory):
    # [修改] 使用我们动态计算出的脚本路径变量
    dependency_check_script = DEPENDENCY_CHECK_SCRIPT_PATH
    
    report_formats = ["HTML", "JSON"]
    format_args = [arg for format in report_formats for arg in ["--format", format]]
    command_parts = [
        dependency_check_script, "--project", "My Python Project",
        "--scan", project_path, "--out", report_directory,
        "--enableExperimental", "--noupdate"
    ] + format_args

    # 为确保脚本有执行权限，在执行前添加权限
    try:
        os.chmod(dependency_check_script, 0o755)
    except Exception as e:
        print(f"警告: 无法设置脚本 '{dependency_check_script}' 的执行权限: {e}")

    print(f"项目根目录: {PROJECT_ROOT}")
    print(f"将要执行的脚本: {dependency_check_script}")
    print(f"正在准备执行命令: {subprocess.list2cmdline(command_parts)}")
    
    try:
        process = subprocess.Popen(
            command_parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding='utf-8'
        )
        stdout, stderr = process.communicate()
        if stdout: print(f"--- 输出 ---\n{stdout.strip()}")
        if stderr: print(f"--- 错误信息 ---\n{stderr.strip()}")

        if process.returncode != 0:
            return False, f"扫描失败，返回代码: {process.returncode}。错误详情: {stderr.strip()}"
        else:
            return True, f"扫描成功完成。报告已生成在: {report_directory}"

    except FileNotFoundError:
        return False, f"错误: 未找到Dependency-Check脚本 '{dependency_check_script}'。请确认路径是否正确。"
    except Exception as e:
        return False, f"执行Dependency-Check期间发生错误: {e}"

def start_scan(project_dir, report_dir):
    project_to_scan_abs = os.path.abspath(project_dir)
    reports_folder_abs = os.path.abspath(report_dir)
    
    # [修改] 使用我们动态计算出的脚本路径变量
    dependency_check_script_path = DEPENDENCY_CHECK_SCRIPT_PATH

    if not os.path.isfile(dependency_check_script_path):
         return {"status": "error", "message": f"脚本文件未找到: '{dependency_check_script_path}'"}
    if not os.path.isdir(project_to_scan_abs):
        return {"status": "error", "message": f"项目路径不存在: '{project_to_scan_abs}'"}
    if not os.path.exists(reports_folder_abs):
        try:
            os.makedirs(reports_folder_abs)
        except Exception as e:
            return {"status": "error", "message": f"无法创建报告目录: {e}"}

    success, message = run_dependency_check(project_to_scan_abs, reports_folder_abs)
    
    if success:
        return {"status": "success", "message": message, "report_path": reports_folder_abs}
    else:
        return {"status": "error", "message": message}