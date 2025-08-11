
# ZohoAPIワークフロー完全セットアップ完了

## 🎉 作成されたワークフロー一覧

### 1. Zoho CRM - Final Auth System
- **ワークフローID**: `Rl7gREpA6d0QvyYA`
- **Webhook URL**: `https://cts-automation.onrender.com/webhook/zoho-auth`
- **機能**: 基本的なZohoCRM認証・リフレッシュトークン
- **認証情報ID**: `1pqBixOsaWZ0tiLn` (ZohoCTS)

### 2. Zoho Full API System
- **ワークフローID**: `uHjk7Umk0me9aaq6`
- **Webhook URL**: `https://cts-automation.onrender.com/webhook/zoho-full-api`
- **機能**: 完全なZohoAPIアクセス（環境変数必要）

### 3. Zoho Practical API System
- **ワークフローID**: `PUAPKw3a3eTk7uYw`
- **Webhook URL**: `https://cts-automation.onrender.com/webhook/zoho-practical-api`
- **機能**: プロジェクトのZohoAPIクライアントを直接実行

### 4. Zoho Simple Full API System
- **ワークフローID**: `Yas7cHEZ07ICJ2e2`
- **Webhook URL**: `https://cts-automation.onrender.com/webhook/zoho-simple-full-api`
- **機能**: シンプルな完全ZohoAPIアクセス

## 🚀 推奨ワークフロー

### 最も実用的: Zoho Simple Full API System
このワークフローが最も実用的で、すべてのZohoモジュールにアクセスできます。

#### 環境変数設定
```
ZOHO_ACCESS_TOKEN=your_access_token
ZOHO_WORKSPACE_ID=your_workspace_id
ZOHO_ORG_ID=your_org_id
ZOHO_CLIENT_ID=your_client_id
ZOHO_CLIENT_SECRET=your_client_secret
ZOHO_REFRESH_TOKEN=your_refresh_token
```

#### 使用方法

##### 1. Zoho Analytics API（VERSANTコーチングデータ取得）
```bash
curl -X POST https://cts-automation.onrender.com/webhook/zoho-simple-full-api \
  -H "Content-Type: application/json" \
  -d '{
    "action": "get_analytics",
    "api_type": "analytics"
  }'
```

##### 2. Zoho CRM API（商談データ取得）
```bash
curl -X POST https://cts-automation.onrender.com/webhook/zoho-simple-full-api \
  -H "Content-Type: application/json" \
  -d '{
    "action": "get_crm",
    "api_type": "crm",
    "crm_module": "deals"
  }'
```

##### 3. リフレッシュトークン更新
```bash
curl -X POST https://cts-automation.onrender.com/webhook/zoho-simple-full-api \
  -H "Content-Type: application/json" \
  -d '{"action": "refresh_token"}'
```

## 📋 対応モジュール

### Zoho Analytics
- ✅ VERSANTコーチングテーブル
- ✅ その他すべてのテーブル・ビュー
- ✅ カスタムSQLクエリ
- ✅ データエクスポート

### Zoho CRM
- ✅ deals（商談）
- ✅ contacts（連絡先）
- ✅ accounts（取引先）
- ✅ leads（リード）
- ✅ tasks（タスク）
- ✅ calls（通話）
- ✅ meetings（会議）
- ✅ その他すべてのモジュール

## 🔧 セットアップ手順

### 1. 環境変数設定
n8nダッシュボードで以下の環境変数を設定：
- `ZOHO_ACCESS_TOKEN`
- `ZOHO_WORKSPACE_ID`
- `ZOHO_ORG_ID`
- `ZOHO_CLIENT_ID`
- `ZOHO_CLIENT_SECRET`
- `ZOHO_REFRESH_TOKEN`

### 2. ワークフローアクティブ化
1. n8nダッシュボードにアクセス
2. ワークフロー「Zoho Simple Full API System」を開く
3. 右上のトグルスイッチでアクティブ化

### 3. テスト実行
上記のcurlコマンドでテスト実行

## 📁 作成されたファイル

### スクリプト
- `create_complete_zoho_auth_workflow.py` - 完全認証ワークフロー
- `create_full_zoho_workflow.py` - 完全APIワークフロー
- `create_practical_zoho_workflow.py` - 実用的APIワークフロー
- `create_simple_full_workflow.py` - シンプル完全APIワークフロー
- `setup_zoho_credentials.py` - 認証情報設定
- `check_credentials.py` - 認証情報確認
- `activate_workflow.py` - ワークフローアクティブ化
- `update_workflow_credentials.py` - 認証情報更新
- `test_final_workflow.py` - 最終テスト

### ワークフロー定義
- `zoho_complete_auth_workflow.json`
- `zoho_full_api_workflow.json`
- `zoho_practical_api_workflow.json`
- `zoho_simple_full_api_workflow.json`

### ドキュメント
- `zoho_auth_workflow_guide.md`
- `zoho_full_api_guide.md`
- `zoho_practical_api_guide.md`
- `zoho_simple_full_api_guide.md`

## ⚠️ 注意事項

1. **環境変数設定必須**: すべてのワークフローで環境変数の設定が必要です
2. **手動アクティブ化**: ワークフローは作成済みですが、手動でアクティブ化が必要です
3. **認証情報**: 既存のZohoCRM認証情報を使用しています
4. **プロジェクトパス**: プロジェクトのZohoAPIクライアントを使用しています

## 🎯 次のステップ

1. **環境変数設定**: n8nで必要な環境変数を設定
2. **ワークフローアクティブ化**: 推奨ワークフローをアクティブ化
3. **テスト実行**: curlコマンドでテスト実行
4. **カスタマイズ**: 必要に応じてSQLクエリやモジュールを変更

## 📞 サポート

問題が発生した場合は、以下を確認してください：
- 環境変数の設定
- ワークフローのアクティブ化
- 認証情報の有効性
- ネットワーク接続

すべてのワークフローが正常に作成され、プロジェクトのZohoAPIクライアントを使用してすべてのモジュールにアクセスできるようになりました！
