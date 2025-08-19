# 部署指南

## AWS 環境設置

### 前置需求
1. AWS CLI 已安裝並配置
2. AWS SAM CLI 已安裝
3. 具有適當權限的 AWS 帳戶

### 部署後端

1. 進入後端目錄：
```bash
cd backend/
```

2. 建置應用程式：
```bash
sam build
```

3. 首次部署（會提示設定參數）：
```bash
sam deploy --guided
```

4. 後續部署：
```bash
sam deploy
```

5. 記錄輸出的 API Gateway URL 和 Cognito 配置

### 部署前端到 Cloudflare Pages

#### 方法 1: 自動部署（推薦）

1. **設定 GitHub Repository**
   - 將專案推送到 GitHub
   - 設定必要的 GitHub Secrets（見下方）

2. **配置 GitHub Secrets**
   在 GitHub Repository Settings > Secrets and variables > Actions 中新增：
   ```
   CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
   CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id
   VITE_API_BASE_URL=https://your-api-gateway-url.amazonaws.com/Prod
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   ```

3. **推送程式碼觸發部署**
   ```bash
   git push origin main
   ```

#### 方法 2: 手動部署

1. **安裝 Wrangler CLI**
   ```bash
   npm install -g wrangler
   ```

2. **登入 Cloudflare**
   ```bash
   wrangler login
   ```

3. **建立 Cloudflare Pages 專案**
   ```bash
   wrangler pages project create po-shipment-frontend
   ```

4. **設定環境變數**
   ```bash
   cd frontend/
   cp .env.example .env.production
   # 編輯 .env.production，設定正確的 API URL
   ```

5. **建置並部署**
   ```bash
   npm run build:pages
   npm run deploy:pages
   ```

#### 方法 3: Cloudflare Dashboard 部署

1. **登入 Cloudflare Dashboard**
   - 進入 https://dash.cloudflare.com
   - 選擇 "Pages"

2. **連接 GitHub Repository**
   - 點擊 "Create a project"
   - 選擇 "Connect to Git"
   - 選擇您的 GitHub repository

3. **設定建置配置**
   ```
   Build command: npm run build:pages
   Build output directory: dist
   Root directory: frontend
   ```

4. **設定環境變數**
   在 Pages 專案設定中新增：
   ```
   VITE_API_BASE_URL=https://your-api-gateway-url.amazonaws.com/Prod
   NODE_ENV=production
   ```

5. **部署**
   - 儲存設定後會自動觸發第一次部署
   - 後續推送到 main 分支會自動重新部署

## LocalStack 本地開發

### 使用 LocalStack 模擬 AWS 服務

1. 安裝 LocalStack：
```bash
pip install localstack
```

2. 啟動 LocalStack：
```bash
localstack start
```

3. 設定本地端點：
```bash
export AWS_ENDPOINT_URL=http://localhost:4566
```

4. 部署到 LocalStack：
```bash
sam build
sam deploy --region us-east-1 --resolve-s3 --s3-prefix localstack
```

### Docker Compose 設定

建立 `docker-compose.yml`：
```yaml
version: '3.8'
services:
  localstack:
    image: localstack/localstack
    ports:
      - "4566:4566"
    environment:
      - SERVICES=lambda,apigateway,dynamodb,cognito-idp,s3
      - DEBUG=1
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock"
      - "${TMPDIR:-/tmp}/localstack:/tmp/localstack"
```

## 初始設定

### 建立管理者帳戶

部署完成後，需要手動在 Cognito 建立第一個管理者帳戶：

1. 進入 AWS Cognito Console
2. 選擇您的 User Pool
3. 建立新使用者：
   - Username: admin@example.com
   - Password: 設定臨時密碼
   - 設定屬性 `custom:role` 為 `admin`

4. 在 DynamoDB Users 表中新增對應記錄：
```json
{
  "user_id": "cognito-user-id",
  "email": "admin@example.com",
  "role": "admin",
  "permissions": [],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## 環境變數設定

### 後端環境變數
Lambda 函數會自動從 CloudFormation 模板取得環境變數。

### 前端環境變數
根據部署環境設定不同的 `.env` 檔案：

開發環境 (`.env.local`)：
```
VITE_API_BASE_URL=http://localhost:3001
```

生產環境 (`.env.production`)：
```
VITE_API_BASE_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/Prod
NODE_ENV=production
VITE_DEPLOY_TARGET=cloudflare-pages
```

Cloudflare Pages 環境變數可在 Cloudflare Dashboard 中設定：
- `VITE_API_BASE_URL`: 您的 AWS API Gateway URL
- `NODE_ENV`: `production`

## 監控和記錄

### CloudWatch 記錄
- Lambda 函數的記錄會自動寫入 CloudWatch
- 可在 AWS Console 查看執行記錄和錯誤

### 監控指標
- API Gateway 請求數量和延遲
- Lambda 函數執行時間和錯誤率
- DynamoDB 讀寫容量使用情況

## 疑難排解

### 常見問題

1. **CORS 錯誤**：
   - 確認 API Gateway 已正確設定 CORS
   - 檢查前端 API URL 設定

2. **認證失敗**：
   - 檢查 Cognito 設定
   - 確認 JWT token 格式正確

3. **DynamoDB 存取錯誤**：
   - 檢查 Lambda 執行角色權限
   - 確認表名稱正確

4. **Lambda 冷啟動**：
   - 考慮使用 Provisioned Concurrency
   - 優化函數大小和依賴