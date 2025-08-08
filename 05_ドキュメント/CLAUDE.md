# Claude Code設定メモ

## 自動実行設定
- **設定ファイル**: `~/.config/claude/settings.json`
  - 全ツールの自動実行許可設定済み
  - タイムアウト設定: 30秒（デフォルト）、300秒（最大）
- **環境変数**: `~/.zshrc`に追加済み
  - `CLAUDE_AUTO_EXECUTE=true`
  - `BASH_DEFAULT_TIMEOUT_MS=30000`
  - `BASH_MAX_TIMEOUT_MS=300000`
  - `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR=true`

## 通知設定
- **通知スクリプト**: `~/.config/claude/notify_completion.sh`
  - Macのダイアログボックス通知
  - ログ出力機能付き
- **Hooks設定**:
  - `Stop`: Claude Codeエージェント応答完了時に通知（修正済み）

## Excel計算機能
- **ファイル**: `excel_calculator.py`
- **機能**:
  - CSVをExcel形式に変換
  - 売上小計・原価小計の計算
  - 粗利（売上-原価）の自動計算
  - 粗利率（粗利/売上×100）の自動計算
  - 合計行の自動追加
  - ヘッダーと合計行のスタイリング

## 生成されたファイル
- `2025年1月以降_商談_商品内訳_レポート_計算式付き.xlsx` - 計算式付きExcelファイル

## 設定日時
2025年7月27日 - Claude Code自動実行と通知システム設定完了