#!/bin/bash
# 自动生成的运维脚本
# 生成时间: 2025-08-13 18:50:36
# 用途: 系统运维操作
# 注意: 请在执行前仔细检查脚本内容

set -e  # 遇到错误时退出
set -u  # 使用未定义的变量时退出

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "开始执行运维脚本: GDB_0813185036.sh"

#!/bin/bash
# GDB调试进程终止脚本
# 功能：终止附加到指定进程的所有GDB实例
# 用法：./kill_attached_gdb.sh <进程名>

if [ $# -eq 0 ]; then
    echo "错误：必须提供进程名称参数"
    echo "用法：$0 <进程名>"
    exit 1
fi

TARGET_PROCESS="$1"
LOG_FILE="/var/log/gdb_termination.log"

# 获取目标进程PID
PIDS=$(pgrep -x "$TARGET_PROCESS")

if [ -z "$PIDS" ]; then
    echo "错误：未找到名为 '$TARGET_PROCESS' 的进程" | tee -a "$LOG_FILE"
    exit 2
fi

# 查找并终止附加的GDB进程
gdb_killed=0
for pid in $PIDS; do
    # 查找附加到该PID的GDB进程
    gdb_pids=$(ps aux | awk -v pid="$pid" \
        '$11 ~ /gdb/ && $0 ~ "attach "pid || $0 ~ "-p "pid {print $2}')
    
    for gdb_pid in $gdb_pids; do
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 终止GDB进程 $gdb_pid (附加到 $TARGET_PROCESS[$pid])" | tee -a "$LOG_FILE"
        kill -9 "$gdb_pid"
        ((gdb_killed++))
    done
done

if [ $gdb_killed -eq 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 未找到附加到 $TARGET_PROCESS 的GDB进程" | tee -a "$LOG_FILE"
    exit 3
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 已终止 $gdb_killed 个GDB进程" | tee -a "$LOG_FILE"
    exit 0
fi

log "脚本执行完成"
