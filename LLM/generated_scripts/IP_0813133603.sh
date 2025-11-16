#!/bin/bash
# 自动生成的运维脚本
# 生成时间: 2025-08-13 13:36:03
# 用途: 系统运维操作
# 注意: 请在执行前仔细检查脚本内容

set -e  # 遇到错误时退出
set -u  # 使用未定义的变量时退出

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "开始执行运维脚本: IP_0813133603.sh"

#!/bin/bash

# 查询系统时间和IP地址的运维脚本
# 安全说明：此脚本仅执行只读操作，无系统修改风险

function get_system_time() {
    echo "当前系统时间: $(date '+%Y-%m-%d %H:%M:%S %Z')"
}

function get_ip_address() {
    local ip=$(hostname -I 2>/dev/null | awk '{print $1}')
    
    if [ -z "$ip" ]; then
        ip=$(ip route get 1 2>/dev/null | awk '{print $7; exit}')
    fi
    
    if [ -n "$ip" ]; then
        echo "本机IP地址: $ip"
    else
        echo "无法获取IP地址" >&2
        return 1
    fi
}

# 主执行逻辑
echo "====== 系统信息查询 ======"
get_system_time
get_ip_address
echo "========================="

exit 0

log "脚本执行完成"
