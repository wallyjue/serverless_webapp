#!/usr/bin/env node

/**
 * Cloudflare Pages 建置腳本
 * 處理環境變數並建置專案
 */

import { execSync } from 'child_process';
import { copyFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('🚀 開始建置 Cloudflare Pages 版本...');

try {
  // 複製環境特定的配置檔案
  const envFiles = [
    '.env.production',
    '.env.pages',
    '.env'
  ];

  for (const envFile of envFiles) {
    const envPath = join(__dirname, envFile);
    if (existsSync(envPath)) {
      console.log(`📄 使用環境檔案: ${envFile}`);
      copyFileSync(envPath, join(__dirname, '.env.local'));
      break;
    }
  }

  // 執行建置
  console.log('🔨 執行 Vite 建置...');
  execSync('npm run build', { 
    stdio: 'inherit',
    cwd: __dirname 
  });

  // 複製 Pages 特定檔案到建置目錄
  const pagesToCopy = [
    '_headers',
    '_redirects'
  ];

  for (const file of pagesToCopy) {
    const srcPath = join(__dirname, file);
    const destPath = join(__dirname, 'dist', file);
    
    if (existsSync(srcPath)) {
      copyFileSync(srcPath, destPath);
      console.log(`📋 複製 ${file} 到建置目錄`);
    }
  }

  console.log('✅ Cloudflare Pages 建置完成！');
  console.log('📁 建置檔案位於 dist/ 目錄');

} catch (error) {
  console.error('❌ 建置失敗:', error.message);
  process.exit(1);
}