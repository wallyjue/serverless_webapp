# Purchase Order & Shipment Management - Backend

AWS Serverless 後端服務，使用 Python 3.13 和 AWS SAM 框架。

## 架構

- **Lambda Functions**: 處理 API 請求
- **DynamoDB**: 資料儲存
- **Cognito**: 使用者認證
- **API Gateway**: RESTful API 端點

## API 端點

### 認證
- `POST /auth/login` - 使用者登入
- `POST /auth/logout` - 使用者登出
- `POST /auth/register` - 註冊新使用者（管理者功能）

### 使用者管理
- `GET /users` - 取得所有使用者（管理者）
- `POST /users` - 建立新使用者（管理者）
- `PUT /users/{user_id}` - 更新使用者（管理者）
- `DELETE /users/{user_id}` - 刪除使用者（管理者）

### 購買訂單
- `GET /purchase-orders` - 取得購買訂單列表
- `POST /purchase-orders` - 建立新購買訂單
- `GET /purchase-orders/{po_id}` - 取得特定購買訂單
- `PUT /purchase-orders/{po_id}` - 更新購買訂單
- `DELETE /purchase-orders/{po_id}` - 刪除購買訂單

### 貨運
- `GET /shipments` - 取得貨運列表
- `POST /shipments` - 建立新貨運
- `GET /shipments/{shipment_id}` - 取得特定貨運
- `PUT /shipments/{shipment_id}` - 更新貨運
- `DELETE /shipments/{shipment_id}` - 刪除貨運

## 本地開發

### 前置需求
- AWS CLI
- AWS SAM CLI
- Python 3.13
- Docker

### 安裝依賴
```bash
pip install -r requirements.txt
```

### 本地測試
```bash
# 建置應用程式
sam build

# 本地執行 API
sam local start-api --port 3001

# 測試特定函數
sam local invoke AuthFunction --event events/test-auth.json
```

### 部署到 AWS
```bash
# 首次部署
sam deploy --guided

# 後續部署
sam deploy
```

## 環境變數
- `USERS_TABLE`: DynamoDB 使用者表名稱
- `PURCHASE_ORDERS_TABLE`: DynamoDB 購買訂單表名稱
- `SHIPMENTS_TABLE`: DynamoDB 貨運表名稱
- `COGNITO_USER_POOL_ID`: Cognito 使用者池 ID
- `COGNITO_USER_POOL_CLIENT_ID`: Cognito 使用者池客戶端 ID

## 資料模型

### 使用者 (Users)
- user_id (主鍵)
- email
- role (admin/user)
- permissions (列表)
- created_at, updated_at

### 購買訂單 (PurchaseOrders)
- po_id (主鍵)
- supplier
- items (商品列表)
- total_amount
- status (draft/pending/approved/cancelled)
- created_by, created_at, updated_at
- notes

### 貨運 (Shipments)
- shipment_id (主鍵)
- po_id (關聯購買訂單)
- tracking_number
- carrier
- status (pending/in_transit/delivered/cancelled)
- estimated_delivery, actual_delivery
- created_by, created_at, updated_at
- notes