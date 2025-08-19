# Cloudflare Pages 部署設定指南

## 概述
本指南將詳細說明如何將前端應用程式部署到 Cloudflare Pages，並與 AWS 後端整合。

## 前置作業

### 1. Cloudflare 帳戶設定
1. 註冊 [Cloudflare 帳戶](https://dash.cloudflare.com/sign-up)
2. 取得 API Token：
   - 進入 "My Profile" > "API Tokens"
   - 點擊 "Create Token"
   - 使用 "Custom token" 模板
   - 權限設定：
     - `Zone:Zone:Read`
     - `Zone:Page Rules:Edit`
     - `Account:Cloudflare Pages:Edit`

### 2. 取得帳戶資訊
```bash
# 使用 Wrangler CLI 取得帳戶 ID
wrangler whoami
```

## 部署方式

### 方式 1: GitHub Actions 自動部署（推薦）

#### 步驟 1: 設定 GitHub Secrets
在您的 GitHub Repository 中設定以下 Secrets：

```
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id
VITE_API_BASE_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/Prod
```

#### 步驟 2: 推送程式碼
```bash
git add .
git commit -m "Deploy to Cloudflare Pages"
git push origin main
```

GitHub Actions 將自動：
1. 建置前端應用程式
2. 部署到 Cloudflare Pages
3. 設定自訂網域（如果已配置）

### 方式 2: Cloudflare Dashboard 設定

#### 步驟 1: 建立 Pages 專案
1. 登入 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 選擇 "Pages" 分頁
3. 點擊 "Create a project"
4. 選擇 "Connect to Git"

#### 步驟 2: 連接 GitHub Repository
1. 授權 Cloudflare 存取您的 GitHub 帳戶
2. 選擇包含專案的 Repository
3. 設定部署分支為 `main`

#### 步驟 3: 配置建置設定
```yaml
Project name: po-shipment-frontend
Production branch: main
Build command: npm run build:pages
Build output directory: dist
Root directory: frontend
Node.js version: 18
```

#### 步驟 4: 設定環境變數
在 "Settings" > "Environment variables" 中新增：
```
VITE_API_BASE_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/Prod
NODE_ENV=production
VITE_DEPLOY_TARGET=cloudflare-pages
```

### 方式 3: Wrangler CLI 手動部署

#### 步驟 1: 安裝和設定 Wrangler
```bash
# 全域安裝 Wrangler
npm install -g wrangler

# 登入 Cloudflare
wrangler login

# 驗證登入狀態
wrangler whoami
```

#### 步驟 2: 建立 Pages 專案
```bash
cd frontend/
wrangler pages project create po-shipment-frontend
```

#### 步驟 3: 建置和部署
```bash
# 設定環境變數
cp .env.example .env.production
# 編輯 .env.production，設定正確的 API URL

# 建置應用程式
npm run build:pages

# 部署到 Cloudflare Pages
wrangler pages deploy dist --project-name po-shipment-frontend
```

## 自訂網域設定

### 1. 在 Cloudflare Pages 中新增自訂網域
1. 進入您的 Pages 專案
2. 選擇 "Custom domains" 分頁
3. 點擊 "Set up a custom domain"
4. 輸入您的網域名稱

### 2. 設定 DNS 記錄
如果您的網域已在 Cloudflare 管理：
```
Type: CNAME
Name: @ (或 www)
Target: your-project.pages.dev
```

如果網域在其他 DNS 提供商：
1. 新增 CNAME 記錄指向 `your-project.pages.dev`
2. 或依照 Cloudflare 提供的 DNS 記錄設定

## 環境變數管理

### 生產環境變數
在 Cloudflare Pages Dashboard 設定：
```
VITE_API_BASE_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/Prod
NODE_ENV=production
```

### 預覽環境變數
為 Pull Request 預覽設定不同的 API URL：
```
VITE_API_BASE_URL=https://your-staging-api-id.execute-api.us-east-1.amazonaws.com/Staging
NODE_ENV=staging
```

## 效能優化

### 1. 建置優化
前端建置腳本 `build-for-pages.js` 會自動：
- 複製 `_headers` 檔案設定快取策略
- 複製 `_redirects` 檔案支援 SPA 路由
- 優化建置輸出

### 2. 快取設定
`_headers` 檔案包含：
```
# 靜態資源長期快取
/assets/*
  Cache-Control: public, max-age=31536000, immutable

# HTML 檔案不快取
/*.html
  Cache-Control: no-cache
```

### 3. 壓縮設定
Cloudflare Pages 自動提供：
- Gzip 壓縮
- Brotli 壓縮
- 自動最小化 CSS/JS

## 監控和分析

### 1. Cloudflare Analytics
- 在 Pages Dashboard 查看流量統計
- 監控載入時間和錯誤率
- 分析地理分佈

### 2. Web Vitals
Cloudflare Pages 提供：
- Core Web Vitals 指標
- 效能建議
- 真實使用者監控 (RUM)

## 疑難排解

### 常見問題

#### 建置失敗
```bash
# 檢查 Node.js 版本
node --version  # 應該是 18.x

# 檢查建置命令
npm run build:pages

# 檢查環境變數
echo $VITE_API_BASE_URL
```

#### CORS 錯誤
確保 AWS API Gateway 已正確設定 CORS：
```yaml
# 在 SAM template.yaml 中
Cors:
  AllowOrigin: "'https://your-domain.pages.dev'"
  AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
  AllowHeaders: "'Content-Type,Authorization'"
```

#### 路由問題
確認 `_redirects` 檔案已正確設定：
```
/*    /index.html   200
```

### 除錯工具

#### 1. Wrangler 除錯
```bash
# 本地預覽
wrangler pages dev dist

# 檢查專案狀態
wrangler pages project list
```

#### 2. 建置記錄
- 在 Cloudflare Dashboard 查看建置記錄
- 檢查環境變數是否正確設定
- 查看建置輸出和錯誤訊息

## 最佳實踐

### 1. 分支部署策略
- `main` 分支：生產環境
- `develop` 分支：預覽環境
- Pull Request：自動預覽部署

### 2. 環境隔離
```bash
# 生產環境
VITE_API_BASE_URL=https://prod-api.example.com

# 預覽環境
VITE_API_BASE_URL=https://staging-api.example.com
```

### 3. 安全性
- 使用 HTTPS
- 設定適當的 CSP headers
- 定期更新依賴套件

### 4. 效能
- 啟用 Cloudflare 的所有效能功能
- 使用 Cloudflare Images 優化圖片
- 實施資源提示 (preload, prefetch)

## 進階設定

### 1. 函數 (Functions)
Cloudflare Pages 支援 Edge Functions：
```javascript
// functions/api/hello.js
export function onRequest() {
  return new Response('Hello from Cloudflare Pages Functions!');
}
```

### 2. 中介軟體
```javascript
// functions/_middleware.js
export function onRequest({ request, next }) {
  // 新增安全標頭
  const response = next();
  response.headers.set('X-Frame-Options', 'DENY');
  return response;
}
```

這個指南涵蓋了 Cloudflare Pages 部署的所有重要面向。如有其他問題，請參考 [Cloudflare Pages 官方文檔](https://developers.cloudflare.com/pages/)。