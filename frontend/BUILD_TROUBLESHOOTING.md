# 建置疑難排解指南

## 常見建置錯誤解決方案

### 1. `SyntaxError: Cannot use import statement outside a module`

**錯誤原因**: Node.js 預設使用 CommonJS 模組系統，但腳本使用了 ES6 import 語法。

**解決方案**:
```bash
# 方法 1: 使用修正後的腳本（推薦）
npm run build:pages

# 方法 2: 使用簡化版腳本
npm run build:pages:simple

# 方法 3: 直接使用 Vite 建置 + 手動複製檔案
npm run build
# 然後手動複製 _headers 和 _redirects 到 dist/ 目錄
```

### 2. `NODE_ENV=production is not supported in the .env file`

**錯誤原因**: Vite 不允許在 .env 檔案中設定 NODE_ENV。

**解決方案**:
```bash
# 檢查並移除 .env.production 中的 NODE_ENV 設定
# ❌ 錯誤
NODE_ENV=production

# ✅ 正確 - 不設定 NODE_ENV，Vite 會自動處理
VITE_API_BASE_URL=https://your-api-url
```

### 3. `Some chunks are larger than 500 kB after minification`

**錯誤原因**: 打包後的檔案過大。

**解決方案**: 已在 `vite.config.js` 中配置了程式碼分割：
```javascript
// vite.config.js 已包含優化配置
manualChunks: {
  'react-vendor': ['react', 'react-dom'],
  'mui-vendor': ['@mui/material', '@mui/icons-material'],
  // ... 其他分割配置
}
```

### 4. `vite: not found` 錯誤

**錯誤原因**: Vite 未正確安裝或不在 PATH 中。

**解決方案**:
```bash
# 方法 1: 使用 npx 運行本地安裝的 vite
npx vite build

# 方法 2: 檢查 vite 是否安裝
ls -la node_modules/.bin/vite

# 方法 3: 重新安裝依賴
rm -rf node_modules package-lock.json
npm install

# 方法 4: 使用生產環境建置腳本（推薦）
npm run build:production
```

### 5. 找不到 `_headers` 或 `_redirects` 檔案

**錯誤原因**: Cloudflare Pages 特定檔案不存在。

**解決方案**:
```bash
# 檢查檔案是否存在
ls -la _headers _redirects

# 如果不存在，重新建立
echo "/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff" > _headers

echo "/*    /index.html   200" > _redirects
```

### 5. Wrangler 相關錯誤

**錯誤原因**: Wrangler CLI 未安裝或未登入。

**解決方案**:
```bash
# 安裝 Wrangler CLI
npm install -g wrangler

# 登入 Cloudflare
wrangler login

# 檢查登入狀態
wrangler whoami
```

## 建置流程詳解

### 正常建置流程
1. 檢查環境變數檔案（.env.production, .env.pages, .env）
2. 複製環境變數到 .env.local
3. 執行 `vite build`
4. 複製 `_headers` 和 `_redirects` 到 dist 目錄
5. 完成建置

### 手動建置步驟
如果自動腳本失敗，可以手動執行：

```bash
# 1. 設定環境變數
cp .env.production .env.local

# 2. 執行 Vite 建置
npm run build

# 3. 複製 Cloudflare Pages 檔案
cp _headers dist/
cp _redirects dist/

# 4. 預覽建置結果
npm run preview
```

## 環境變數配置

### 本地開發
```bash
# .env.local
VITE_API_BASE_URL=http://localhost:3001
```

### 生產環境
```bash
# .env.production
VITE_API_BASE_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/Prod
VITE_DEPLOY_TARGET=production
```

## Linux/CI 環境特定問題

### Node.js 版本問題
```bash
# 檢查 Node.js 版本
node --version  # 應該 >= 18

# Ubuntu/Debian 安裝 Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# CentOS/RHEL 安裝 Node.js 18
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs
```

### 權限問題
```bash
# 如果遇到權限錯誤
sudo chown -R $(whoami) ~/.npm
sudo chown -R $(whoami) node_modules

# 或使用 npm 配置避免 sudo
npm config set prefix ~/.local
export PATH=~/.local/bin:$PATH
```

### 記憶體不足
```bash
# 增加 Node.js 記憶體限制
NODE_OPTIONS="--max-old-space-size=4096" npm run build:production

# 檢查可用記憶體
free -h
```

### CI/CD 環境建置
```bash
# 在 CI 環境中使用
npm ci                          # 快速安裝
npm run build:production        # 包含所有檢查的建置
```

## 建置輸出檢查

### 檢查建置結果
```bash
# 查看建置檔案
ls -la dist/

# 應該包含
# - index.html
# - assets/ 目錄
# - _headers
# - _redirects
```

### 檔案大小分析
```bash
# 查看各個 chunk 的大小
ls -lh dist/assets/

# 預期輸出：
# react-vendor-*.js    ~12KB (React 相關)
# mui-vendor-*.js      ~276KB (Material-UI)
# utils-vendor-*.js    ~68KB (工具函數)
# index-*.js           ~202KB (主要應用程式)
```

## 效能優化建議

### 1. 程式碼分割已配置
- React 和 React-DOM 獨立打包
- Material-UI 組件獨立打包
- 工具函數獨立打包

### 2. 快取策略
`_headers` 檔案設定了適當的快取：
- 靜態資源（assets/）：1年快取
- HTML 檔案：不快取

### 3. 壓縮
Vite 自動啟用：
- JavaScript 最小化
- CSS 最小化
- Gzip 壓縮準備

## 部署前檢查清單

- [ ] 建置成功無錯誤
- [ ] `dist/` 目錄包含所有必要檔案
- [ ] 環境變數正確設定
- [ ] `_headers` 和 `_redirects` 檔案存在
- [ ] 檔案大小合理（總計 < 1MB）

## 聯絡支援

如果問題持續存在：

1. **檢查 Node.js 版本**: `node --version` （建議 18+）
2. **檢查 npm 版本**: `npm --version`
3. **清理快取**: `npm ci` （重新安裝依賴）
4. **查看詳細錯誤**: 使用 `--verbose` 選項

```bash
# 詳細建置資訊
npm run build -- --mode development
```