# 🚀 快速開始指南

## 本地開發環境設定

### 1. 克隆專案
```bash
git clone <your-repo-url>
cd serverless_webapp
```

### 2. 使用自動化腳本（推薦）
```bash
# 進入腳本目錄
cd scripts/

# 啟動完整開發環境
./start-dev.sh
```

這個腳本會自動：
- 建置後端 SAM 應用程式
- 啟動本地 API 服務器 (port 3001)
- 啟動前端開發服務器 (port 3000)

### 3. 手動設定（可選）

#### 後端設定
```bash
cd backend/
pip install -r requirements.txt
sam build
sam local start-api --port 3001
```

#### 前端設定
```bash
cd frontend/
npm install
cp .env.example .env.local
npm run dev
```

## 生產環境部署

### 自動部署（推薦）

#### 1. 設定 GitHub Secrets
在您的 GitHub Repository Settings > Secrets 中新增：
```
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
```

#### 2. 推送程式碼
```bash
git push origin main
```

GitHub Actions 會自動部署後端到 AWS 和前端到 Cloudflare Pages。

### 手動部署

#### 1. 部署後端到 AWS
```bash
cd backend/
sam build
sam deploy --guided  # 第一次部署
# sam deploy  # 後續部署
```

#### 2. 部署前端到 Cloudflare Pages
```bash
cd frontend/

# 設定環境變數
cp .env.example .env.production
# 編輯 .env.production，填入 AWS API Gateway URL

# 建置並部署
npm run build:pages
npm run deploy:pages
```

## 服務端點

### 本地開發
- 前端：http://localhost:3000
- 後端 API：http://localhost:3001

### 生產環境
- 前端：https://your-project.pages.dev
- 後端 API：https://your-api-id.execute-api.us-east-1.amazonaws.com/Prod

## 初始設定

### 建立管理者帳戶
部署完成後，需要在 AWS Cognito 中手動建立第一個管理者帳戶：

1. 進入 AWS Cognito Console
2. 建立使用者：
   - Email: admin@example.com
   - 設定 `custom:role` 屬性為 `admin`
3. 在 DynamoDB Users 表中新增對應記錄

## 疑難排解

### 常見問題
1. **Port 3000/3001 被佔用**：請確認沒有其他服務使用這些端口
2. **CORS 錯誤**：檢查環境變數中的 API URL 設定
3. **認證失敗**：確認後端服務已啟動且可存取

### 詳細文檔
- [完整部署指南](docs/deployment.md)
- [Cloudflare Pages 設定](docs/cloudflare-pages-setup.md)
- [後端 API 文檔](backend/README.md)
- [前端開發指南](frontend/README.md)

## 支援
如有問題請查看相關文檔或建立 GitHub Issue。