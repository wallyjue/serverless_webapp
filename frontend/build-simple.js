#!/usr/bin/env node

/**
 * 簡化版 Cloudflare Pages 建置腳本
 * 使用最基本的 Node.js 語法，確保兼容性
 */

var execSync = require('child_process').execSync;
var fs = require('fs');
var path = require('path');

console.log('🚀 開始建置 Cloudflare Pages 版本（簡化版）...');

try {
  // 檢查並複製環境變數檔案
  var envFiles = ['.env.production', '.env.pages', '.env'];
  var envFound = false;
  
  for (var i = 0; i < envFiles.length; i++) {
    var envFile = envFiles[i];
    var envPath = path.join(__dirname, envFile);
    
    if (fs.existsSync(envPath)) {
      console.log('📄 使用環境檔案: ' + envFile);
      var envContent = fs.readFileSync(envPath, 'utf8');
      fs.writeFileSync(path.join(__dirname, '.env.local'), envContent);
      envFound = true;
      break;
    }
  }
  
  if (!envFound) {
    console.log('⚠️  未找到環境變數檔案，使用預設設定');
  }

  // 執行 Vite 建置
  console.log('🔨 執行 Vite 建置...');
  execSync('npm run build', { 
    stdio: 'inherit',
    cwd: __dirname 
  });

  // 複製 Cloudflare Pages 特定檔案
  var filesToCopy = ['_headers', '_redirects'];
  var distPath = path.join(__dirname, 'dist');
  
  for (var j = 0; j < filesToCopy.length; j++) {
    var file = filesToCopy[j];
    var srcPath = path.join(__dirname, file);
    var destPath = path.join(distPath, file);
    
    if (fs.existsSync(srcPath)) {
      fs.copyFileSync(srcPath, destPath);
      console.log('📋 複製 ' + file + ' 到建置目錄');
    } else {
      console.log('⚠️  找不到檔案: ' + file);
    }
  }

  console.log('✅ Cloudflare Pages 建置完成！');
  console.log('📁 建置檔案位於 dist/ 目錄');
  console.log('');
  console.log('下一步：');
  console.log('- 本地預覽: npm run preview:pages');
  console.log('- 手動部署: npm run deploy:pages');
  console.log('- 或推送到 GitHub 觸發自動部署');

} catch (error) {
  console.error('❌ 建置失敗:');
  console.error(error.message);
  process.exit(1);
}