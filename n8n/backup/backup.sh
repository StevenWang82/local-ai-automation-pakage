#!/bin/sh
# 備份目錄
BACKUP_DIR="/backup"
# 建立備份目錄，如果不存在
mkdir -p "$BACKUP_DIR"

# 產生時間戳記
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')  # 使用單引號

# 匯出工作流程
n8n export:workflow --all --output="$BACKUP_DIR/workflows/workflows_$TIMESTAMP.json"

# 匯出憑證
# n8n export:credential --all --output="$BACKUP_DIR/credentials/credentials_$TIMESTAMP.json"
n8n export:credential --all --output=/backup/credentials/credentials.json

echo "n8n 工作流程和憑證已備份到 $BACKUP_DIR"