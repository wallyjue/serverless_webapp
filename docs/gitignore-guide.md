# .gitignore 檔案指南

## 概述
本專案包含多層級的 .gitignore 檔案來管理版本控制忽略規則。

## 檔案結構

```
serverless_webapp/
├── .gitignore                    # 主要忽略規則
├── .gitignore.template          # 範本檔案
├── frontend/.gitignore          # 前端專用規則
├── backend/.gitignore           # 後端專用規則
└── docs/gitignore-guide.md      # 說明文檔（此檔案）
```

## 主要 .gitignore 檔案

### 🔒 敏感資訊保護
- **環境變數檔案**: `.env*` 檔案包含 API 金鑰、資料庫連線字串等敏感資訊
- **AWS 憑證**: `.aws/` 目錄包含 AWS 存取金鑰
- **Cloudflare Token**: 部署用的 API Token

### 🏗️ 建置產物
- **前端建置**: `frontend/dist/` - Vite 建置輸出
- **後端建置**: `backend/.aws-sam/` - SAM 建置快取
- **Docker**: 容器建置快取

### 📦 依賴套件
- **Node.js**: `node_modules/` - npm/yarn 套件
- **Python**: `__pycache__/`, `venv/` - Python 快取和虛擬環境

## 前端 .gitignore

### React + Vite 專用
```gitignore
# 建置輸出
dist/
dist-ssr/

# Vite 快取
vite.config.js.timestamp-*

# 環境變數
.env.local
.env.production.local
```

### Cloudflare Pages
```gitignore
# Wrangler 快取
.wrangler/

# Functions 建置
functions/
```

## 後端 .gitignore

### Python + AWS SAM
```gitignore
# SAM 建置
.aws-sam/

# Python 快取
__pycache__/
*.pyc

# 虛擬環境
venv/
.venv/
```

### AWS 相關
```gitignore
# 打包檔案
packaged.yaml

# AWS 憑證
.aws/
```

## 最佳實踐

### ✅ 應該忽略的檔案
1. **敏感資訊**: API 金鑰、密碼、憑證
2. **建置產物**: 可重新生成的檔案
3. **依賴套件**: 可通過套件管理器安裝
4. **快取檔案**: 開發工具生成的快取
5. **個人設定**: IDE 設定、作業系統檔案

### ⚠️ 不應該忽略的檔案
1. **原始碼**: 所有手寫的程式碼
2. **配置檔案**: 非敏感的配置（如 `package.json`）
3. **文檔**: README、API 文檔等
4. **測試檔案**: 單元測試、整合測試
5. **建置腳本**: Dockerfile、部署腳本

## 環境變數管理

### 檔案命名規範
```
.env.example          # 範本檔案（應提交）
.env                  # 本地開發（忽略）
.env.local           # 本地覆寫（忽略）
.env.production      # 生產環境（忽略）
.env.staging         # 測試環境（忽略）
```

### 敏感資訊處理
```bash
# ✅ 正確：使用範本檔案
cp .env.example .env.local
# 然後編輯 .env.local 填入實際值

# ❌ 錯誤：直接編輯 .env 檔案並提交
```

## 特殊情況處理

### 強制添加被忽略的檔案
```bash
# 如果需要提交被忽略的檔案
git add -f path/to/ignored/file
```

### 停止追蹤已提交的檔案
```bash
# 移除已追蹤但現在要忽略的檔案
git rm --cached filename
git commit -m "Stop tracking filename"
```

### 檢查忽略狀態
```bash
# 檢查檔案是否被忽略
git check-ignore -v filename

# 列出所有被忽略的檔案
git status --ignored
```

## 常見問題

### Q: .env 檔案不小心被提交了怎麼辦？
```bash
# 1. 立即從版本控制中移除
git rm --cached .env

# 2. 添加到 .gitignore（如果還沒有）
echo ".env" >> .gitignore

# 3. 提交變更
git commit -m "Remove .env from version control"

# 4. 立即更換所有敏感資訊
```

### Q: node_modules 資料夾太大，如何處理？
```bash
# 確保 node_modules 在 .gitignore 中
echo "node_modules/" >> .gitignore

# 如果已經被追蹤，移除它
git rm -r --cached node_modules/
git commit -m "Remove node_modules from version control"
```

### Q: 建置檔案應該提交嗎？
通常**不應該**提交建置檔案，因為：
- 它們可以從原始碼重新生成
- 會使 repository 變大
- 可能造成合併衝突
- CI/CD 會自動建置

## 維護建議

### 定期檢查
1. **每月檢查**: 查看是否有新的檔案類型需要忽略
2. **清理快取**: 定期清理開發工具產生的快取檔案
3. **更新規則**: 隨著專案發展更新忽略規則

### 團隊協作
1. **統一規則**: 確保團隊成員使用相同的 .gitignore
2. **文檔化**: 記錄特殊的忽略規則和原因
3. **審查變更**: .gitignore 的變更應該經過 code review

## 參考資源

- [GitHub .gitignore 範本](https://github.com/github/gitignore)
- [Git 官方文檔](https://git-scm.com/docs/gitignore)
- [gitignore.io](https://www.toptal.com/developers/gitignore) - 線上產生器