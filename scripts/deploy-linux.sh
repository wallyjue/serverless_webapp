#!/bin/bash

# =============================================================================
# Linux 環境部署腳本
# 適用於新的 Linux 伺服器或 CI/CD 環境
# =============================================================================

set -e  # 遇到錯誤立即退出

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 輔助函數
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 檢查命令是否存在
check_command() {
    if command -v $1 >/dev/null 2>&1; then
        log_success "$1 已安裝"
        return 0
    else
        log_error "$1 未安裝"
        return 1
    fi
}

# 檢查 Node.js 版本
check_node_version() {
    if check_command node; then
        NODE_VERSION=$(node --version | sed 's/v//')
        MAJOR_VERSION=$(echo $NODE_VERSION | cut -d. -f1)
        
        if [ $MAJOR_VERSION -ge 18 ]; then
            log_success "Node.js 版本 $NODE_VERSION (符合要求 >= 18)"
        else
            log_error "Node.js 版本 $NODE_VERSION 過舊，需要 >= 18"
            return 1
        fi
    else
        return 1
    fi
}

echo "🚀 開始 Linux 環境部署流程"
echo "======================================"

# 1. 檢查系統環境
log_info "檢查系統環境"
echo "系統資訊:"
uname -a
echo ""

# 檢查可用空間
AVAILABLE_SPACE=$(df -h . | awk 'NR==2 {print $4}')
log_info "可用磁碟空間: $AVAILABLE_SPACE"

# 2. 檢查必要工具
log_info "檢查必要工具"

if ! check_node_version; then
    log_error "Node.js 安裝或版本不符合要求"
    log_info "請安裝 Node.js 18+ 或使用以下命令:"
    echo "  curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -"
    echo "  sudo apt-get install -y nodejs"
    exit 1
fi

if ! check_command npm; then
    log_error "npm 未安裝"
    exit 1
fi

if ! check_command git; then
    log_warning "git 未安裝，可能無法進行版本控制操作"
fi

echo ""

# 3. 進入前端目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/../frontend"

if [ ! -d "$FRONTEND_DIR" ]; then
    log_error "前端目錄不存在: $FRONTEND_DIR"
    exit 1
fi

cd "$FRONTEND_DIR"
log_info "切換到前端目錄: $(pwd)"

# 4. 檢查專案檔案
log_info "檢查專案檔案"

if [ ! -f "package.json" ]; then
    log_error "package.json 不存在"
    exit 1
fi

if [ ! -f "vite.config.js" ]; then
    log_error "vite.config.js 不存在"
    exit 1
fi

log_success "專案檔案檢查完成"
echo ""

# 5. 清理舊的建置
log_info "清理舊的建置檔案"
if [ -d "dist" ]; then
    rm -rf dist
    log_success "清理 dist 目錄"
fi

if [ -d "node_modules" ] && [ "$1" == "--clean" ]; then
    rm -rf node_modules package-lock.json
    log_success "清理 node_modules（--clean 模式）"
fi

echo ""

# 6. 安裝依賴
log_info "安裝依賴套件"

if [ -f "package-lock.json" ] && [ -d "node_modules" ]; then
    log_info "使用 npm ci 進行快速安裝"
    npm ci
else
    log_info "使用 npm install 進行完整安裝"
    npm install
fi

log_success "依賴安裝完成"
echo ""

# 7. 驗證關鍵依賴
log_info "驗證關鍵依賴"

CRITICAL_DEPS=("node_modules/.bin/vite" "node_modules/react" "node_modules/@mui/material")

for dep in "${CRITICAL_DEPS[@]}"; do
    if [ -e "$dep" ]; then
        log_success "$dep 存在"
    else
        log_error "$dep 缺失"
        exit 1
    fi
done

echo ""

# 8. 檢查環境變數
log_info "檢查環境變數配置"

if [ -f ".env.production" ]; then
    log_success "找到 .env.production"
elif [ -f ".env.pages" ]; then
    log_success "找到 .env.pages"
elif [ -f ".env" ]; then
    log_success "找到 .env"
else
    log_warning "未找到環境變數檔案，將使用預設值"
    echo "VITE_API_BASE_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/Prod" > .env.production
    echo "VITE_DEPLOY_TARGET=production" >> .env.production
    log_info "已建立預設 .env.production"
fi

echo ""

# 9. 執行建置
log_info "執行建置"

if [ -f "build-production.js" ]; then
    log_info "使用生產環境建置腳本"
    npm run build:production
else
    log_info "使用標準建置流程"
    
    # 複製環境變數
    if [ -f ".env.production" ]; then
        cp .env.production .env.local
    fi
    
    # 使用 npx 確保使用本地 vite
    npx vite build
    
    # 複製 Cloudflare Pages 檔案
    if [ -f "_headers" ]; then
        cp _headers dist/
        log_success "複製 _headers"
    fi
    
    if [ -f "_redirects" ]; then
        cp _redirects dist/
        log_success "複製 _redirects"
    fi
fi

echo ""

# 10. 驗證建置結果
log_info "驗證建置結果"

if [ ! -d "dist" ]; then
    log_error "建置失敗: dist 目錄不存在"
    exit 1
fi

if [ ! -f "dist/index.html" ]; then
    log_error "建置失敗: index.html 不存在"
    exit 1
fi

# 檢查檔案大小
DIST_SIZE=$(du -sh dist | cut -f1)
log_success "建置目錄大小: $DIST_SIZE"

# 列出建置檔案
log_info "建置檔案:"
ls -la dist/

echo ""

# 11. 完成
log_success "🎉 Linux 環境部署完成！"
echo ""
echo "📋 下一步選項:"
echo "  • 本地預覽: npm run preview"
echo "  • 部署到 Cloudflare Pages: npm run deploy:pages"
echo "  • 手動上傳 dist/ 目錄內容到您的主機"
echo ""

# 如果是 CI 環境，顯示額外資訊
if [ "$CI" = "true" ]; then
    log_info "偵測到 CI 環境"
    echo "建置檔案已準備好進行自動部署"
fi

echo "======================================"
log_success "部署腳本執行完成"