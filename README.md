# Purchase Order & Shipment Management System

## 系統概述
一個基於 AWS Serverless 架構的採購訂單和貨運管理系統，提供完整的 CRUD 操作、使用者權限管理和角色控制功能。

## 技術架構
- **前端**: React 19 + Material-UI + Vite (部署於 Cloudflare Pages)
- **後端**: AWS Lambda (Python 3.13) + AWS SAM
- **資料庫**: AWS DynamoDB
- **認證**: AWS Cognito
- **部署**: AWS SAM (後端) + Cloudflare Pages (前端)

## 功能特色

### 🔐 認證與授權
- JWT 基礎的使用者認證
- 角色權限控制（管理者/一般使用者）
- 細粒度權限管理

### 📋 購買訂單管理
- 建立、查看、編輯、刪除購買訂單
- 多項目商品管理
- 訂單狀態追蹤（草稿/待處理/已批准/已取消）
- 供應商管理

### 🚚 貨運管理
- 建立和追蹤貨運
- 承運商資訊管理
- 貨運狀態更新（待發貨/運送中/已送達/已取消）
- 預計和實際送達日期追蹤

### 👥 使用者管理
- 管理者可建立和管理使用者帳戶
- 權限分配和角色管理
- 使用者活動追蹤

### 📊 儀表板
- 系統統計概覽
- 快速操作入口
- 實時資料更新

## 專案結構
```
serverless_webapp/
├── backend/           # AWS Lambda 後端
│   ├── src/          # Python 原始碼
│   ├── tests/        # 單元測試
│   ├── events/       # 測試事件
│   └── template.yaml # SAM 模板
├── frontend/          # React 前端
│   ├── src/          # React 原始碼
│   ├── public/       # 靜態資源
│   └── package.json  # 依賴配置
├── docs/             # 文檔
├── scripts/          # 開發腳本
└── docker-compose.yml # Docker 配置
```

## 快速開始

### 方法 1: 使用開發腳本（推薦）
```bash
# 進入腳本目錄
cd scripts/

# 啟動開發環境（會自動建置並啟動前後端）
./start-dev.sh
```

### 方法 2: 手動啟動

#### 後端設置
```bash
cd backend/

# 安裝依賴
pip install -r requirements.txt

# 建置 SAM 應用程式
sam build

# 啟動本地 API
sam local start-api --port 3001
```

#### 前端設置
```bash
cd frontend/

# 安裝依賴
npm install

# 建立環境變數檔案
cp .env.example .env.local

# 啟動開發服務器
npm run dev
```

### 方法 3: 使用 Docker Compose
```bash
# 啟動所有服務（包括 LocalStack）
docker-compose up -d

# 查看記錄
docker-compose logs -f
```

## 服務端點
- **前端**: http://localhost:3000
- **後端 API**: http://localhost:3001
- **LocalStack**: http://localhost:4566 (如使用 Docker Compose)

## 初始登入
系統部署後需要手動建立第一個管理者帳戶。請參考 `docs/deployment.md` 中的詳細說明。

預設測試帳戶：
- **Email**: admin@example.com
- **Password**: AdminPass123
- **Role**: admin

## API 文檔

### 認證端點
- `POST /auth/login` - 使用者登入
- `POST /auth/logout` - 使用者登出
- `POST /auth/register` - 註冊使用者（管理者功能）

### 購買訂單端點
- `GET /purchase-orders` - 取得訂單列表
- `POST /purchase-orders` - 建立新訂單
- `GET /purchase-orders/{id}` - 取得特定訂單
- `PUT /purchase-orders/{id}` - 更新訂單
- `DELETE /purchase-orders/{id}` - 刪除訂單

### 貨運端點
- `GET /shipments` - 取得貨運列表
- `POST /shipments` - 建立新貨運
- `GET /shipments/{id}` - 取得特定貨運
- `PUT /shipments/{id}` - 更新貨運
- `DELETE /shipments/{id}` - 刪除貨運

### 使用者管理端點（管理者專用）
- `GET /users` - 取得使用者列表
- `POST /users` - 建立新使用者
- `PUT /users/{id}` - 更新使用者
- `DELETE /users/{id}` - 刪除使用者

## 測試

### 後端測試
```bash
cd backend/
python -m pytest tests/
```

### 前端測試
```bash
cd frontend/
npm test
```

## 部署

### 完整部署（後端 + 前端）
使用 GitHub Actions 自動部署（推薦）：
```bash
# 設定 GitHub Secrets 後推送程式碼
git push origin main
```

### 個別部署

#### 後端部署到 AWS
```bash
cd backend/
sam build
sam deploy
```

#### 前端部署到 Cloudflare Pages
```bash
cd frontend/
npm run build:pages
npm run deploy:pages
```

### LocalStack 本地部署
```bash
# 啟動 LocalStack
docker-compose up localstack -d

# 部署後端到 LocalStack
cd backend/
sam build
sam deploy --resolve-s3
```

詳細部署指南請參考：
- `docs/deployment.md` - 完整部署指南
- `docs/cloudflare-pages-setup.md` - Cloudflare Pages 專用指南

## 環境變數

### 後端環境變數
- `USERS_TABLE` - DynamoDB 使用者表名稱
- `PURCHASE_ORDERS_TABLE` - DynamoDB 購買訂單表名稱
- `SHIPMENTS_TABLE` - DynamoDB 貨運表名稱
- `COGNITO_USER_POOL_ID` - Cognito 使用者池 ID
- `COGNITO_USER_POOL_CLIENT_ID` - Cognito 使用者池客戶端 ID

### 前端環境變數
- `VITE_API_BASE_URL` - 後端 API 基礎 URL

## 權限系統

### 角色
- **管理者 (admin)**: 完整系統存取權限
- **一般使用者 (user)**: 基於權限的存取控制

### 可分配權限
- `purchase_order_create` - 建立購買訂單
- `purchase_order_edit` - 編輯購買訂單
- `purchase_order_delete` - 刪除購買訂單
- `shipment_create` - 建立貨運
- `shipment_edit` - 編輯貨運
- `shipment_delete` - 刪除貨運

## 疑難排解

### 常見問題
1. **端口被佔用**: 確認 3000 和 3001 端口未被其他應用程式使用
2. **CORS 錯誤**: 檢查前端 API URL 設定是否正確
3. **認證失敗**: 確認後端服務已正常啟動並可存取

更多疑難排解資訊請參考 `docs/deployment.md`。

## 貢獻指南
1. Fork 專案
2. 建立功能分支
3. 提交變更
4. 建立 Pull Request

## 授權
MIT License

## 技術支援
如有問題請查看 `docs/` 目錄下的文檔或建立 Issue。