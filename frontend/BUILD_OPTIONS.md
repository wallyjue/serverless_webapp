# 建置選項指南

## 概述
本專案提供多種建置選項，適用於不同的環境和需求。

## 🎯 建置腳本選項

### 1. `npm run build` - 標準 Vite 建置
```bash
npm run build
```
- **用途**: 基本的 Vite 建置
- **適用**: 熟悉 Vite 的開發者
- **輸出**: `dist/` 目錄
- **注意**: 需要手動複製 `_headers` 和 `_redirects`

### 2. `npm run build:pages` - Cloudflare Pages 建置
```bash
npm run build:pages
```
- **用途**: 為 Cloudflare Pages 優化的建置
- **適用**: 大多數情況
- **特色**: 自動處理環境變數和 Pages 配置檔案
- **輸出**: 包含 `_headers` 和 `_redirects` 的完整 `dist/` 目錄

### 3. `npm run build:pages:simple` - 簡化版建置
```bash
npm run build:pages:simple
```
- **用途**: 相容性最佳的建置選項
- **適用**: 舊版 Node.js 或遇到語法錯誤時
- **特色**: 使用最基本的 JavaScript 語法

### 4. `npm run build:production` - 生產環境建置 ⭐ 推薦
```bash
npm run build:production
```
- **用途**: 新 Linux 環境的完整建置流程
- **適用**: CI/CD、新服務器、生產部署
- **特色**: 
  - 自動檢查和安裝依賴
  - 驗證關鍵套件
  - 環境變數處理
  - 完整的錯誤診斷
  - 建置結果驗證

## 🔧 選擇建議

### 開發環境
```bash
# 本地開發
npm run dev

# 快速建置測試
npm run build
```

### 生產部署
```bash
# 第一次部署或新環境（推薦）
npm run build:production

# 熟悉的環境
npm run build:pages
```

### CI/CD 環境
```bash
# GitHub Actions 中使用
npm run build:production
```

### 遇到問題時
```bash
# 如果遇到 ES6 語法錯誤
npm run build:pages:simple

# 如果遇到依賴問題
rm -rf node_modules package-lock.json
npm install
npm run build:production
```

## 🚀 自動化部署腳本

### Linux 環境完整部署
```bash
# 執行完整的 Linux 環境設置和建置
./scripts/deploy-linux.sh

# 清理模式（重新安裝所有依賴）
./scripts/deploy-linux.sh --clean
```

## 📊 建置輸出比較

| 腳本 | 依賴檢查 | 環境變數 | Pages 檔案 | 錯誤診斷 | 適用場景 |
|------|----------|----------|------------|----------|----------|
| `build` | ❌ | ❌ | ❌ | ❌ | 基本建置 |
| `build:pages` | ❌ | ✅ | ✅ | ❌ | 一般部署 |
| `build:pages:simple` | ❌ | ✅ | ✅ | ❌ | 相容性 |
| `build:production` | ✅ | ✅ | ✅ | ✅ | 生產環境 |

## 🛠️ 環境需求

### 最低要求
- Node.js 18+
- npm 6+

### 推薦配置
- Node.js 18-20 (LTS)
- npm 8+
- 4GB+ 可用記憶體

## 🐛 疑難排解

### 常見錯誤與解決方案

#### `vite: not found`
```bash
# 使用 npx 或生產建置腳本
npx vite build
# 或
npm run build:production
```

#### 依賴問題
```bash
# 清理並重新安裝
rm -rf node_modules package-lock.json
npm install
```

#### 記憶體不足
```bash
# 增加 Node.js 記憶體限制
NODE_OPTIONS="--max-old-space-size=4096" npm run build:production
```

#### 權限問題（Linux）
```bash
# 修復 npm 權限
sudo chown -R $(whoami) ~/.npm
sudo chown -R $(whoami) node_modules
```

## 🎯 最佳實踐

### 開發工作流程
1. **本地開發**: `npm run dev`
2. **測試建置**: `npm run build:pages`
3. **生產部署**: `npm run build:production`

### CI/CD 工作流程
1. **檢查環境**: 確保 Node.js 18+
2. **安裝依賴**: `npm ci`
3. **建置**: `npm run build:production`
4. **部署**: 使用建置輸出

### 新環境設置
1. **使用自動化腳本**: `./scripts/deploy-linux.sh`
2. **或手動執行**: `npm run build:production`

## 📁 輸出結構

所有建置腳本都會產生以下結構：
```
dist/
├── index.html              # 主頁面
├── assets/                 # 靜態資源
│   ├── index-*.js         # 主應用程式
│   ├── react-vendor-*.js  # React 相關
│   ├── mui-vendor-*.js    # Material-UI
│   ├── utils-vendor-*.js  # 工具函數
│   └── *.css             # 樣式檔案
├── _headers               # Cloudflare Pages 標頭
└── _redirects            # Cloudflare Pages 重導向
```

## 🚦 部署檢查清單

建置完成後，請確認：
- [ ] `dist/` 目錄存在
- [ ] `dist/index.html` 存在
- [ ] `dist/_headers` 存在
- [ ] `dist/_redirects` 存在
- [ ] 檔案大小合理（總計 < 2MB）
- [ ] 無建置錯誤或警告

完成以上檢查後，即可進行部署！