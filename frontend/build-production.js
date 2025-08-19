#!/usr/bin/env node

/**
 * 生產環境建置腳本 - 適用於新的 Linux 環境
 * 自動檢查和安裝依賴，確保建置成功
 */

const { execSync } = require('child_process');
const { copyFileSync, existsSync } = require('fs');
const { join } = require('path');

// 輔助函數：執行命令並顯示輸出
function runCommand(command, description) {
  console.log(`🔄 ${description}...`);
  try {
    execSync(command, { 
      stdio: 'inherit',
      cwd: __dirname 
    });
    console.log(`✅ ${description} 完成`);
  } catch (error) {
    console.error(`❌ ${description} 失敗:`, error.message);
    throw error;
  }
}

// 檢查檔案是否存在
function checkFileExists(filePath, description) {
  if (existsSync(filePath)) {
    console.log(`✅ ${description} 存在`);
    return true;
  } else {
    console.log(`⚠️  ${description} 不存在: ${filePath}`);
    return false;
  }
}

console.log('🚀 開始生產環境建置流程...');
console.log('📍 目標: Cloudflare Pages 部署');
console.log('');

try {
  // 1. 檢查 Node.js 環境
  console.log('1️⃣ 檢查 Node.js 環境');
  runCommand('node --version', '檢查 Node.js 版本');
  runCommand('npm --version', '檢查 npm 版本');
  console.log('');

  // 2. 檢查 package.json
  console.log('2️⃣ 檢查專案配置');
  if (!checkFileExists(join(__dirname, 'package.json'), 'package.json')) {
    throw new Error('package.json 不存在，請在正確的專案目錄執行');
  }
  console.log('');

  // 3. 安裝依賴
  console.log('3️⃣ 安裝依賴套件');
  
  // 檢查是否需要安裝依賴
  const nodeModulesExists = existsSync(join(__dirname, 'node_modules'));
  const packageLockExists = existsSync(join(__dirname, 'package-lock.json'));
  
  if (!nodeModulesExists) {
    console.log('📦 node_modules 不存在，執行完整安裝');
    runCommand('npm install', '安裝所有依賴套件');
  } else if (packageLockExists) {
    console.log('🔄 使用 npm ci 進行清潔安裝');
    runCommand('npm ci', '清潔安裝依賴套件');
  } else {
    console.log('📦 node_modules 存在，跳過安裝');
  }
  console.log('');

  // 4. 驗證關鍵依賴
  console.log('4️⃣ 驗證關鍵依賴');
  const criticalDeps = [
    'node_modules/.bin/vite',
    'node_modules/react',
    'node_modules/@mui/material'
  ];
  
  let missingDeps = false;
  for (const dep of criticalDeps) {
    if (!checkFileExists(join(__dirname, dep), dep)) {
      missingDeps = true;
    }
  }
  
  if (missingDeps) {
    console.log('⚠️  有依賴缺失，重新安裝...');
    runCommand('npm install --force', '強制重新安裝依賴');
  }
  console.log('');

  // 5. 處理環境變數
  console.log('5️⃣ 處理環境變數');
  const envFiles = ['.env.production', '.env.pages', '.env'];
  let envFound = false;
  
  for (const envFile of envFiles) {
    const envPath = join(__dirname, envFile);
    if (existsSync(envPath)) {
      console.log(`📄 使用環境檔案: ${envFile}`);
      copyFileSync(envPath, join(__dirname, '.env.local'));
      envFound = true;
      break;
    }
  }
  
  if (!envFound) {
    console.log('⚠️  未找到環境變數檔案，建立預設配置');
    const defaultEnv = 'VITE_API_BASE_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/Prod\nVITE_DEPLOY_TARGET=production\n';
    require('fs').writeFileSync(join(__dirname, '.env.local'), defaultEnv);
  }
  console.log('');

  // 6. 執行建置
  console.log('6️⃣ 執行 Vite 建置');
  
  // 使用 npx 確保使用本地安裝的 vite
  runCommand('npx vite build', 'Vite 建置');
  console.log('');

  // 7. 驗證建置輸出
  console.log('7️⃣ 驗證建置輸出');
  const distPath = join(__dirname, 'dist');
  if (!checkFileExists(distPath, 'dist 目錄')) {
    throw new Error('建置失敗：dist 目錄不存在');
  }
  
  if (!checkFileExists(join(distPath, 'index.html'), 'index.html')) {
    throw new Error('建置失敗：index.html 不存在');
  }
  console.log('');

  // 8. 複製 Cloudflare Pages 特定檔案
  console.log('8️⃣ 複製 Cloudflare Pages 配置');
  const pagesToCopy = ['_headers', '_redirects'];
  
  for (const file of pagesToCopy) {
    const srcPath = join(__dirname, file);
    const destPath = join(distPath, file);
    
    if (existsSync(srcPath)) {
      copyFileSync(srcPath, destPath);
      console.log(`📋 複製 ${file} 到建置目錄`);
    } else {
      console.log(`⚠️  警告: ${file} 不存在，將建立預設版本`);
      
      if (file === '_headers') {
        const defaultHeaders = `/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-XSS-Protection: 1; mode=block

/assets/*
  Cache-Control: public, max-age=31536000, immutable

/*.html
  Cache-Control: no-cache`;
        require('fs').writeFileSync(destPath, defaultHeaders);
      } else if (file === '_redirects') {
        const defaultRedirects = `/*    /index.html   200`;
        require('fs').writeFileSync(destPath, defaultRedirects);
      }
      console.log(`📋 建立預設 ${file}`);
    }
  }
  console.log('');

  // 9. 最終檢查
  console.log('9️⃣ 最終檢查');
  const finalChecks = [
    'dist/index.html',
    'dist/_headers', 
    'dist/_redirects'
  ];
  
  let allChecksPass = true;
  for (const check of finalChecks) {
    if (!checkFileExists(join(__dirname, check), check)) {
      allChecksPass = false;
    }
  }
  
  if (!allChecksPass) {
    throw new Error('最終檢查失敗，請檢查建置輸出');
  }

  // 10. 顯示建置統計
  console.log('');
  console.log('📊 建置統計:');
  try {
    runCommand('ls -lh dist/assets/', '資源檔案大小');
  } catch (e) {
    console.log('⚠️  無法顯示檔案統計');
  }

  console.log('');
  console.log('🎉 建置完成！');
  console.log('📁 建置檔案位於 dist/ 目錄');
  console.log('');
  console.log('📋 下一步：');
  console.log('  • 本地預覽: npm run preview');
  console.log('  • 部署到 Cloudflare Pages: npm run deploy:pages');
  console.log('  • 或推送到 GitHub 觸發自動部署');

} catch (error) {
  console.log('');
  console.error('❌ 建置失敗！');
  console.error('錯誤訊息:', error.message);
  console.log('');
  console.log('🔧 疑難排解建議：');
  console.log('1. 檢查 Node.js 版本 (建議 18+): node --version');
  console.log('2. 清理依賴並重新安裝: rm -rf node_modules package-lock.json && npm install');
  console.log('3. 檢查磁碟空間是否足夠');
  console.log('4. 檢查網路連線（下載依賴時需要）');
  console.log('5. 參考: BUILD_TROUBLESHOOTING.md');
  
  process.exit(1);
}