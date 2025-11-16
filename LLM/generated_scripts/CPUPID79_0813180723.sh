#!/bin/bash
# 自动生成的运维脚本
# 生成时间: 2025-08-13 18:07:23
# 用途: 系统运维操作
# 注意: 请在执行前仔细检查脚本内容

set -e  # 遇到错误时退出
set -u  # 使用未定义的变量时退出

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "开始执行运维脚本: CPUPID79_0813180723.sh"

#!/bin/bash

TARGET_PID=79  # 需要终止的进程PID

# 验证当前用户权限
if [ "$(id -u)" -ne 0 ]; then
    echo "错误：此操作需要root权限！请使用sudo执行脚本" >&2
    exit 1
fi

# 检查目标进程是否存在
if ! ps -p "$TARGET_PID" > /dev/null; then
    echo "错误：PID $TARGET_PID 对应的进程不存在" >&2
    exit 2
fi

# 获取进程详情
PROCESS_INFO=$(ps -p "$TARGET_PID" -o comm=)
echo "即将终止进程："
echo "  PID: $TARGET_PID"
echo "  名称: $PROCESS_INFO"
echo "  状态: $(ps -p "$TARGET_PID" -o state=)"

# 用户确认
read -rp "确认终止此进程？(y/n) " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "操作已取消"
    exit 0
fi

# 尝试安全终止
echo "正在发送终止信号(SIGTERM)..."
if kill "$TARGET_PID"; then
    echo "终止信号已发送，等待进程退出..."
    sleep 3  # 等待进程处理退出信号
    
    # 检查进程是否已退出
    if ps -p "$TARGET_PID" > /dev/null; then
        echo "警告：进程未正常退出，将发送强制终止信号(SIGKILL)"
        kill -9 "$TARGET_PID"
        sleep 1
        if ps -p "$TARGET_PID" > /dev/null; then
            echo "错误：无法终止进程 $TARGET_PID" >&2
            exit 3
        else
            echo "进程已被强制终止"
            logger "进程终止成功: PID $TARGET_PID (强制终止)"
        fi
    else
        echo "进程已安全终止"
        logger "进程终止成功: PID $TARGET_PID (安全终止)"
    fi
else
    echo "错误：终止操作失败" >&2
    exit 4
fi

exit 0

log "脚本执行完成"
