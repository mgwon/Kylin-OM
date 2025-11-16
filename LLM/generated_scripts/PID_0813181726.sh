#!/bin/bash
# 自动生成的运维脚本
# 生成时间: 2025-08-13 18:17:26
# 用途: 系统运维操作
# 注意: 请在执行前仔细检查脚本内容

set -e  # 遇到错误时退出
set -u  # 使用未定义的变量时退出

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "开始执行运维脚本: PID_0813181726.sh"

#!/bin/bash
# 进程终止脚本 v1.0
# 功能：通过PID安全终止指定进程
# 用法：./kill_process.sh <PID>

# 验证参数存在
if [ -z "$1" ]; then
    echo "错误：必须提供PID参数"
    echo "用法：$0 <PID>"
    exit 1
fi

PID=$1
LOG_FILE="/var/log/process_termination.log"

# 验证PID有效性
if ! ps -p $PID > /dev/null 2>&1; then
    echo "错误：PID $PID 对应的进程不存在"
    exit 2
fi

# 获取进程信息
process_info=$(ps -p $PID -o comm=)

# 操作确认
echo "即将终止进程："
echo "  PID:    $PID"
echo "  名称:   $process_info"
read -p "确认终止？(y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "操作已取消"
    exit 0
fi

# 执行终止
if kill -9 $PID; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 成功终止进程: PID=$PID, Name=$process_info" >> $LOG_FILE
    echo "进程已成功终止"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 终止失败: PID=$PID" >> $LOG_FILE
    echo "错误：进程终止失败"
    exit 3
fi

log "脚本执行完成"
