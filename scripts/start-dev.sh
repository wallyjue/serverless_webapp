#!/bin/bash

# 開發環境啟動腳本

echo "啟動 Purchase Order & Shipment Management 開發環境..."

# 檢查是否安裝了必要的工具
command -v sam >/dev/null 2>&1 || { echo >&2 "需要安裝 AWS SAM CLI. 請參考: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo >&2 "需要安裝 Node.js 和 npm."; exit 1; }

# 設定變數
BACKEND_DIR="../backend"
FRONTEND_DIR="../frontend"
API_PORT=3001
FRONTEND_PORT=3000

echo "1. 建置後端..."
cd "$BACKEND_DIR"
sam build

echo "2. 啟動後端 API (Port: $API_PORT)..."
sam local start-api --port $API_PORT --host 0.0.0.0 &
BACKEND_PID=$!

# 等待後端啟動
echo "等待後端服務啟動..."
sleep 10

echo "3. 啟動前端 (Port: $FRONTEND_PORT)..."
cd "$FRONTEND_DIR"

# 建立本地環境變數檔案
if [ ! -f .env.local ]; then
    echo "建立 .env.local 檔案..."
    echo "VITE_API_BASE_URL=http://localhost:$API_PORT" > .env.local
fi

# 啟動前端開發服務器
npm run dev &
FRONTEND_PID=$!

echo ""
echo "🎉 開發環境已啟動！"
echo "📍 前端: http://localhost:$FRONTEND_PORT"
echo "📍 後端 API: http://localhost:$API_PORT"
echo ""
echo "按 Ctrl+C 停止所有服務"

# 等待中斷信號
trap 'echo "停止服務中..."; kill $BACKEND_PID $FRONTEND_PID; exit' INT

# 保持腳本運行
wait