# Purchase Order & Shipment Management - Frontend

React 前端應用程式，使用 Material-UI 和 Vite。

## 功能特色

- **使用者認證**: 登入/登出功能
- **角色權限控制**: 管理者和一般使用者
- **購買訂單管理**: CRUD 操作
- **貨運管理**: 追蹤和狀態更新
- **使用者管理**: 管理者可管理使用者和權限
- **響應式設計**: 支援各種螢幕尺寸

## 技術棧

- React 19
- Material-UI (MUI)
- React Router DOM
- Axios (HTTP 客戶端)
- Vite (建置工具)

## 本地開發

### 前置需求
- Node.js 18+
- npm

### 安裝依賴
```bash
npm install
```

### 開發服務器
```bash
npm run dev
```
應用程式將在 http://localhost:3000 啟動

### 建構生產版本
```bash
npm run build
```

### 建構 Cloudflare Pages 版本
```bash
npm run build:pages
```

### 預覽生產版本
```bash
# 標準預覽
npm run preview

# Cloudflare Pages 本地預覽
npm run preview:pages
```

## 部署

### 部署到 Cloudflare Pages
```bash
# 手動部署
npm run deploy:pages

# 或使用 GitHub Actions 自動部署
git push origin main
```

## 環境變數

建立 `.env.local` 檔案：
```
VITE_API_BASE_URL=http://localhost:3001
```

## 專案結構

```
src/
├── components/          # 可重用元件
│   ├── Layout.jsx      # 主要佈局
│   └── ProtectedRoute.jsx  # 路由保護
├── contexts/           # React Context
│   └── AuthContext.jsx # 認證上下文
├── pages/             # 頁面元件
│   ├── LoginPage.jsx
│   ├── DashboardPage.jsx
│   ├── PurchaseOrdersPage.jsx
│   ├── ShipmentsPage.jsx
│   └── UsersPage.jsx
├── services/          # API 服務
│   └── api.js
└── utils/            # 工具函數
```

## 路由

- `/` - 重新導向到儀表板
- `/login` - 登入頁面
- `/dashboard` - 儀表板
- `/purchase-orders` - 購買訂單管理
- `/shipments` - 貨運管理
- `/users` - 使用者管理（僅管理者）

## 權限系統

### 角色
- **管理者 (admin)**: 完整系統存取權限
- **一般使用者 (user)**: 基於權限的存取控制

### 一般使用者權限
- `purchase_order_create`: 建立購買訂單
- `purchase_order_edit`: 編輯購買訂單
- `purchase_order_delete`: 刪除購買訂單
- `shipment_create`: 建立貨運
- `shipment_edit`: 編輯貨運
- `shipment_delete`: 刪除貨運

## API 整合

前端透過 Axios 與後端 API 通訊，包含：
- 自動認證 token 處理
- 錯誤處理和重新導向
- 請求/回應攔截器