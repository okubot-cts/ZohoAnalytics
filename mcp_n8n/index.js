#!/usr/bin/env node

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Python MCPサーバーを起動
const pythonScript = join(__dirname, 'n8n_mcp_server.py');

const pythonProcess = spawn('python3', [pythonScript], {
  stdio: 'inherit',
  env: {
    ...process.env,
    PYTHONPATH: join(__dirname, '..'),
    PYTHONIOENCODING: 'utf-8'
  }
});

pythonProcess.on('error', (error) => {
  console.error('N8N MCPサーバーエラー:', error);
  process.exit(1);
});

pythonProcess.on('exit', (code) => {
  process.exit(code);
});

// シグナルハンドリング
process.on('SIGTERM', () => {
  pythonProcess.kill('SIGTERM');
});

process.on('SIGINT', () => {
  pythonProcess.kill('SIGINT');
});