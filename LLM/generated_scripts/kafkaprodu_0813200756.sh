#!/bin/bash
# 自动生成的运维脚本
# 生成时间: 2025-08-13 20:07:56
# 用途: 系统运维操作
# 注意: 请在执行前仔细检查脚本内容

set -e  # 遇到错误时退出
set -u  # 使用未定义的变量时退出

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "开始执行运维脚本: kafkaprodu_0813200756.sh"

#!/bin/bash
# kafka-producer服务安全重启脚本
# 功能：执行kafka-producer服务的完整重启流程
# 日志：/var/log/kafka_producer_restart.log

SERVICE_NAME="kafka-producer"
LOG_FILE="/var/log/kafka_producer_restart.log"
TIMEOUT=60  # 操作超时时间（秒）

# 创建日志目录
mkdir -p $(dirname $LOG_FILE)
touch $LOG_FILE

# 记录日志函数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

# 检查root权限
if [ $(id -u) -ne 0 ]; then
    log "错误：需要root权限执行此脚本"
    exit 1
fi

# 检查服务是否存在
if ! systemctl list-unit-files | grep -q "^$SERVICE_NAME.service"; then
    log "错误：服务 $SERVICE_NAME 不存在"
    exit 2
fi

# 获取当前服务状态
current_status=$(systemctl is-active $SERVICE_NAME)
log "当前服务状态: $current_status"

# 停止服务（如果正在运行）
if [ "$current_status" = "active" ]; then
    log "正在停止 $SERVICE_NAME 服务..."
    systemctl stop $SERVICE_NAME
    
    # 等待停止完成
    elapsed=0
    while [ $(systemctl is-active $SERVICE_NAME) = "active" ] && [ $elapsed -lt $TIMEOUT ]; do
        sleep 1
        ((elapsed++))
    done
    
    if [ $elapsed -ge $TIMEOUT ]; then
        log "错误：停止服务超时（超过 ${TIMEOUT}秒）"
        exit 3
    fi
    log "服务已成功停止"
fi

# 启动服务
log "正在启动 $SERVICE_NAME 服务..."
systemctl start $SERVICE_NAME

# 验证启动结果
elapsed=0
while [ $(systemctl is-active $SERVICE_NAME) != "active" ] && [ $elapsed -lt $TIMEOUT ]; do
    sleep 1
    ((elapsed++))
done

if [ $(systemctl is-active $SERVICE_NAME) = "active" ]; then
    log "服务已成功启动"
    exit 0
else
    log "错误：服务启动失败！当前状态：$(systemctl is-active $SERVICE_NAME)"
    exit 4
fi

log "脚本执行完成"
