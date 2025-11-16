#!/bin/bash
# 自动生成的运维脚本
# 生成时间: 2025-08-13 18:34:26
# 用途: 系统运维操作
# 注意: 请在执行前仔细检查脚本内容

set -e  # 遇到错误时退出
set -u  # 使用未定义的变量时退出

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "开始执行运维脚本: mysqld_0813183426.sh"

#!/bin/bash
# mysqld进程监控与自动重启脚本
# 功能：检测mysqld进程状态，异常时自动重启服务
# 日志：/var/log/mysqld_monitor.log

LOG_FILE="/var/log/mysqld_monitor.log"
SERVICE_NAME="mysqld"

# 创建日志目录（如不存在）
mkdir -p $(dirname $LOG_FILE)
touch $LOG_FILE

# 记录日志函数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

# 检测进程是否存在
if pgrep -x "$SERVICE_NAME" >/dev/null; then
    log "检测正常：$SERVICE_NAME 进程正在运行"
    exit 0
fi

# 检测服务状态
service_status=$(systemctl is-active "$SERVICE_NAME" 2>/dev/null)

if [ "$service_status" == "active" ]; then
    log "检测正常：$SERVICE_NAME 服务状态为 active"
    exit 0
fi

# 执行重启操作
log "警告：$SERVICE_NAME 进程不存在且服务未激活，尝试重启..."
systemctl restart "$SERVICE_NAME"

# 验证重启结果
if systemctl is-active "$SERVICE_NAME" --quiet; then
    log "重启成功：$SERVICE_NAME 服务已恢复运行"
    exit 0
else
    log "错误：$SERVICE_NAME 重启失败！当前状态: $(systemctl is-active $SERVICE_NAME)"
    exit 1
fi

log "脚本执行完成"
