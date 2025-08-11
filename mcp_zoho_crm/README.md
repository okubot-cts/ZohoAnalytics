# Zoho CRM MCP Server for Claude Desktop

Zoho CRM APIへの完全なアクセスを提供するMCP（Model Context Protocol）サーバーです。

## 機能

- **全モジュールアクセス**: Zoho CRMの全てのモジュール（標準・カスタム）へのアクセス
- **CRUD操作**: レコードの作成、読み取り、更新、削除
- **高度な検索**: Zoho CRM検索構文を使用した条件指定検索
- **関連レコード取得**: モジュール間の関連データ取得
- **完全自動認証**: リフレッシュトークン切れ時の自動再認証（ブラウザ認証）
- **トークン自動管理**: アクセス・リフレッシュトークンの自動更新・保存
- **バックアップ機能**: トークンファイルの自動バックアップ作成

## セットアップ

### 1. 依存関係のインストール

```bash
cd mcp_zoho_crm
python3 -m pip install -r requirements.txt
```

### 2. Claude Desktopの設定

Claude Desktopの設定ファイル（`~/Library/Application Support/Claude/claude_desktop_config.json`）に以下を追加：

```json
{
  "mcpServers": {
    "zoho-crm": {
      "command": "node",
      "args": [
        "/Users/ks1-utakashio/Desktop/CursorProjects/20250726_ZohoAnalytics/mcp_zoho_crm/index.js"
      ],
      "env": {
        "ZOHO_CLIENT_ID": "your_client_id",
        "ZOHO_CLIENT_SECRET": "your_client_secret",
        "ZOHO_REFRESH_TOKEN": "your_refresh_token"
      }
    }
  }
}
```

### 3. 動作確認

テストスクリプトを実行して接続を確認：

```bash
python3 test_server.py
```

## 利用可能なツール

### 1. list_modules
利用可能なZoho CRMモジュール一覧を取得

### 2. get_module_fields
指定モジュールのフィールド情報を取得

パラメータ:
- `module_name`: モジュール名（例: Leads, Contacts, Deals）

### 3. get_records
指定モジュールのレコードを取得

パラメータ:
- `module_name`: モジュール名
- `page`: ページ番号（オプション、デフォルト: 1）
- `per_page`: 1ページあたりのレコード数（オプション、最大200）
- `fields`: 取得するフィールド名のリスト（オプション）
- `sort_by`: ソートフィールド（オプション）
- `sort_order`: ソート順（"asc" または "desc"、オプション）

### 4. search_records
条件を指定してレコードを検索

パラメータ:
- `module_name`: モジュール名
- `criteria`: 検索条件（Zoho CRM検索構文）
- `page`: ページ番号（オプション）
- `per_page`: 1ページあたりのレコード数（オプション）

### 5. get_record
単一レコードの詳細を取得

パラメータ:
- `module_name`: モジュール名
- `record_id`: レコードID

### 6. create_record
新規レコードを作成

パラメータ:
- `module_name`: モジュール名
- `data`: レコードデータ（JSON形式）

### 7. update_record
既存レコードを更新

パラメータ:
- `module_name`: モジュール名
- `record_id`: レコードID
- `data`: 更新データ（JSON形式）

### 8. delete_record
レコードを削除

パラメータ:
- `module_name`: モジュール名
- `record_id`: レコードID

### 9. get_related_records
関連レコードを取得

パラメータ:
- `module_name`: 親モジュール名
- `record_id`: 親レコードID
- `related_module`: 関連モジュール名
- `page`: ページ番号（オプション）
- `per_page`: 1ページあたりのレコード数（オプション）

## 使用例

Claude Desktopで以下のような質問ができます：

- 「Zoho CRMの商談（Deals）一覧を表示して」
- 「今月クローズ予定の商談を検索して」
- 「新しい見込み客（Lead）を作成して」
- 「特定の顧客（Contact）の詳細情報を取得して」

## 自動再認証機能

### 動作概要
- **アクセストークン切れ**: 自動的にリフレッシュトークンで更新
- **リフレッシュトークン切れ**: 自動的にブラウザ認証を開始
- **トークン保存**: 新しいトークンを自動的にファイル保存
- **バックアップ**: 既存のトークンファイルを自動バックアップ

### 初回認証・再認証プロセス
1. リフレッシュトークンが無効/期限切れを検出
2. コールバックサーバー（localhost:8080）を自動起動
3. ブラウザでZoho認証ページを自動表示
4. ユーザーがZohoアカウントでログイン
5. 認証完了後、新しいトークンを自動取得・保存
6. APIアクセスを継続

### テスト方法
```bash
# 自動認証機能のテスト
python3 test_auto_auth.py
```

## トラブルシューティング

### 初回使用時・トークン期限切れ
- ブラウザが自動で開きます
- Zohoアカウントでログインして認証を完了してください
- 認証完了後、自動的にAPIアクセスが継続されます

### ポート8080が使用中の場合
- 他のアプリケーションがポート8080を使用している場合は一時的に停止してください
- または、コードを修正して別のポートを使用してください

### モジュールが見つからない場合
1. `list_modules`ツールを使用して利用可能なモジュール一覧を確認
2. モジュール名はAPI名（例: "Deals", "Contacts"）を使用してください

## セキュリティ注意事項

- **自動バックアップ**: トークンファイルは自動的にバックアップされます
- **環境変数**: 本番環境では環境変数を使用して認証情報を管理することを推奨
- **ローカルサーバー**: 認証時のみlocalhost:8080でコールバックサーバーが起動します
- **トークン暗号化**: 必要に応じてトークンファイルの暗号化を検討してください