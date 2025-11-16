#!/bin/bash
# 自动生成的运维脚本
# 生成时间: 2025-08-13 13:24:41
# 用途: 系统运维操作
# 注意: 请在执行前仔细检查脚本内容

set -e  # 遇到错误时退出
set -u  # 使用未定义的变量时退出

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "开始执行运维脚本: IP_0813132441.sh"

#!/bin/bash

# 查询系统时间和IP地址的脚本
# 安全说明：只读操作，无系统修改风险

# 获取当前系统时间（包含时区信息）
echo "===== 系统时间 ====="
date "+%Y-%m-%d %H:%M:%S %Z"

# 获取主要网络接口的IP地址
echo -e "\n===== IP地址信息 ====="
ip -o -4 addr show | awk '{print $2": "$4}' | grep -v '127.0.0.1'

# 错误处理：如果ip命令不存在则使用ifconfig
if [ $? -ne 0 ]; then
    echo "检测到旧版系统，使用备用命令获取IP信息"
    ifconfig | grep -E 'inet (addr:)?' | awk '{print $2}' | grep -v '127.0.0.1'
fi

echo -e "\n查询完成"

log "脚本执行完成"
