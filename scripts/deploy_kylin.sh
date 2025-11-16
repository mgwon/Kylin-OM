#!/bin/bash

# --- 配置 ---
PROJECT_SOURCE_DIR=$(pwd) # 假设在kylin-OM根目录运行此脚本
DEPLOY_DIR="/opt/a-ops"
SERVICE_NAME="aops-topology"
SOURCE_SCRIPT="src/web_backend/topology_service.py"
# systemd 服务期望的目标文件名
TARGET_SCRIPT="aops_backend_service.py"

echo "=== 开始部署 A-Ops 后端服务 ==="

# 1. 创建部署目录
echo "--> 1. 创建部署目录 ${DEPLOY_DIR}"
sudo mkdir -p ${DEPLOY_DIR}

# 2. 安装 Python 依赖
echo "--> 2. 安装 Python 依赖库..."
sudo pip3 install -r "${PROJECT_SOURCE_DIR}/requirements.txt"
if [ $? -ne 0 ]; then
    echo "❌ 错误：Python 依赖安装失败！"
    exit 1
fi

# 3. 复制核心服务脚本 (*** 这是关键的修正 ***)
echo "--> 3. 复制并重命名拓扑服务脚本到 ${DEPLOY_DIR}"
# 确保在复制时，将源文件明确地命名为目标文件名
sudo cp "${PROJECT_SOURCE_DIR}/${SOURCE_SCRIPT}" "${DEPLOY_DIR}/${TARGET_SCRIPT}"
if [ $? -ne 0 ]; then
    echo "❌ 错误：复制脚本文件失败！"
    exit 1
fi


# 4. 复制和配置 systemd 服务文件
echo "--> 4. 安装 systemd 服务..."
sudo cp "${PROJECT_SOURCE_DIR}/deployment/${SERVICE_NAME}.service" "/etc/systemd/system/"

# 5. 启动服务
echo "--> 5. 重新加载、启动并启用服务..."
sudo systemctl daemon-reload
sudo systemctl restart ${SERVICE_NAME}.service
sudo systemctl enable ${SERVICE_NAME}.service

echo "🚀 部署完成！"
echo "使用 'sudo systemctl status ${SERVICE_NAME}.service' 来检查服务状态。"