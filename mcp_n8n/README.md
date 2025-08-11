# N8N Custom MCP Server for Claude Desktop

N8N ワークフロー自動化プラットフォームへの完全なアクセスを提供するMCP（Model Context Protocol）サーバーです。

## 機能

- **ワークフロー管理**: 作成、更新、削除、アクティブ化/非アクティブ化
- **ワークフロー実行**: 手動実行とWebhookトリガー
- **実行履歴管理**: 実行状況の確認と詳細な結果取得
- **WebhookURL生成**: 自動的なWebhookエンドポイント生成
- **正しいAPIパス**: `/api/v1/`エンドポイントを使用した安定した接続

## セットアップ

### 1. 依存関係のインストール

```bash
cd mcp_n8n
python3 -m pip install -r requirements.txt
```

### 2. Claude Desktopの設定

Claude Desktopの設定ファイルに以下を追加：

```json
{
  "mcpServers": {
    "n8n-custom": {
      "command": "node",
      "args": [
        "/path/to/mcp_n8n/index.js"
      ],
      "env": {
        "N8N_API_URL": "your_n8n_server_url",
        "N8N_API_KEY": "your_n8n_api_key"
      }
    }
  }
}
```

### 3. 動作確認

テストスクリプトを実行して接続を確認：

```bash
python3 test_n8n_mcp.py
```

## 利用可能なツール

### ワークフロー管理
- **list_workflows** - ワークフロー一覧を取得
- **get_workflow** - ワークフローの詳細を取得
- **create_workflow** - 新規ワークフローを作成
- **update_workflow** - ワークフローを更新
- **delete_workflow** - ワークフローを削除

### ワークフロー制御
- **activate_workflow** - ワークフローをアクティブ化
- **deactivate_workflow** - ワークフローを非アクティブ化
- **execute_workflow** - ワークフローを手動実行

### 実行管理
- **get_executions** - 実行履歴を取得
- **get_execution** - 実行結果の詳細を取得

### ユーティリティ
- **get_webhook_url** - WebhookURLを生成

## 使用例

Claude Desktopで以下のような質問ができます：

- 「N8Nのワークフロー一覧を表示して」
- 「アクティブなワークフローを確認して」
- 「特定のワークフローを実行して」
- 「実行履歴を確認して」
- 「新しいWebhookワークフローを作成して」

## トラブルシューティング

### API接続エラー
- N8N_API_URLが正しく設定されているか確認
- N8N_API_KEYが有効か確認
- N8Nサーバーが稼働しているか確認

### 既存の n8n-mcp との競合
このサーバーは独自実装のため、既存のn8n-mcpパッケージと併用可能です。設定では`n8n-custom`として区別されています。

## セキュリティ注意事項

- **APIキー管理**: N8N APIキーは安全に管理してください
- **環境変数**: 本番環境では環境変数を使用してAPIキーを管理
- **アクセス制御**: N8Nサーバーへのアクセス制御を適切に設定してください