# Zoho Analytics API 接続ガイド

## 📋 概要

このドキュメントは、Zoho Analytics APIへの接続方法と、プロジェクト内で使用されているAPIクライアントコードの使用方法を説明します。

## 🔑 認証・トークン管理

### 1. アクセストークン取得方法

#### 方法1: リフレッシュトークンから取得（推奨）
```bash
python3 get_access_token.py
```
選択肢で「1」を選択し、以下を入力：
- **リフレッシュトークン**: 以前取得したリフレッシュトークン
- **クライアントID**: Zoho Developer Consoleで取得したクライアントID
- **クライアントシークレット**: Zoho Developer Consoleで取得したクライアントシークレット

#### 方法2: 認証コードから取得（初回）
```bash
python3 get_access_token.py
```
選択肢で「2」を選択し、以下を入力：
- **認証コード**: Zoho Developer Consoleで取得した認証コード
- **クライアントID**: アプリケーションのクライアントID
- **クライアントシークレット**: アプリケーションのクライアントシークレット
- **リダイレクトURI**: 設定したリダイレクトURI

#### 方法3: 手動でトークンを入力
```bash
python3 get_access_token.py
```
選択肢で「3」を選択し、以下を入力：
- **アクセストークン**: 既に取得したアクセストークン
- **ワークスペースID**: Zoho AnalyticsのワークスペースID

### 2. 自動トークン更新

既存の設定ファイルを使用した自動更新：
```bash
python3 auto_refresh_token.py
```

### 3. 既存トークンの使用

保存されたトークンを使用：
```bash
python3 use_existing_token.py
```

## 🏗️ APIクライアント

### メインAPIクライアント

#### `zoho_analytics_api_client.py`
- **用途**: VERSANTコーチングレポート実行用のメインAPIクライアント
- **機能**: 
  - SQLクエリ実行
  - ワークスペース・テーブル取得
  - 非同期ジョブ管理
  - 結果保存

#### `zoho_analytics_api_client_v2.py`
- **用途**: APIクライアントのバージョン2
- **機能**: 改良されたエラーハンドリングとレスポンス処理

#### `zoho_analytics_api_client_v3.py`
- **用途**: APIクライアントのバージョン3
- **機能**: 最新の機能と改善されたパフォーマンス

#### `zoho_analytics_api_client_final.py`
- **用途**: 最終版APIクライアント
- **機能**: 安定版の機能セット

### ヘルパー関数

#### `zoho_analytics_helper.py`
- **用途**: APIクライアントの補助機能
- **機能**: 共通ユーティリティ関数

## 🔧 設定ファイル

### 環境変数設定
```bash
# .env ファイル
ZOHO_ANALYTICS_ACCESS_TOKEN=your_access_token
ZOHO_ANALYTICS_WORKSPACE_ID=your_workspace_id
ZOHO_ANALYTICS_ORG_ID=your_org_id
```

### トークンファイル
- `zoho_tokens.json`: 基本トークン情報
- `zoho_tokens_updated_YYYYMMDD_HHMMSS.json`: 更新されたトークン情報

## 🧪 テスト・検証

### API接続テスト
```bash
python3 test_actual_api.py
```

### 修正版テスト（推奨）
```bash
python3 test_actual_api_fixed.py
```

### データ取得テスト
```bash
python3 test_api_data_retrieval.py
```

### 直接クエリテスト
```bash
python3 direct_query_test.py
```

## 📊 スキーマ情報

### スキーマ取得
```bash
python3 get_schema_info.py
```

### テーブル構造確認
```bash
python3 check_table_structure.py
```

### カラム情報確認
```bash
python3 check_columns.py
```

## 🔍 トラブルシューティング

### よくある問題

#### 1. 認証エラー（401 Unauthorized）
**原因**: アクセストークンの期限切れまたは無効
**解決方法**: 
```bash
python3 auto_refresh_token.py
```

#### 2. ワークスペースアクセスエラー
**原因**: ワークスペースIDの誤り
**解決方法**: 
```bash
python3 test_actual_api_fixed.py
```
で利用可能なワークスペースを確認

#### 3. クエリ実行エラー
**原因**: SQL構文エラーまたはテーブル名のエンコーディング問題
**解決方法**: 
```bash
python3 check_table_structure.py
```
でテーブル構造を確認

### デバッグ方法

#### 詳細ログの有効化
```bash
export DEBUG=1
python3 test_actual_api_fixed.py
```

#### ジョブステータス確認
```bash
python3 check_job_status.py
python3 check_detailed_job_status.py
python3 check_simple_job_status.py
python3 check_final_job_status.py
```

## 📁 ファイル構成

```
Zoho_API/
├── 認証・トークン/
│   ├── get_access_token.py
│   ├── auto_refresh_token.py
│   ├── use_existing_token.py
│   └── token_manager.py
├── APIクライアント/
│   ├── zoho_analytics_api_client.py
│   ├── zoho_analytics_api_client_v2.py
│   ├── zoho_analytics_api_client_v3.py
│   ├── zoho_analytics_api_client_final.py
│   └── zoho_analytics_helper.py
├── テスト・検証/
│   ├── test_actual_api.py
│   ├── test_actual_api_fixed.py
│   ├── test_api_data_retrieval.py
│   ├── direct_query_test.py
│   └── check_*.py
├── 設定ファイル/
│   ├── zoho_tokens.json
│   ├── zoho_tokens_updated_*.json
│   └── .env
└── ドキュメント/
    ├── アクセストークン取得手順.md
    └── VERSANT_レポート_API使用説明.md
```

## 🚀 使用例

### 基本的な使用手順

1. **環境設定**
```bash
source .env
```

2. **APIクライアント初期化**
```python
from zoho_analytics_api_client import ZohoAnalyticsAPI

client = ZohoAnalyticsAPI()
```

3. **クエリ実行**
```python
query = "SELECT * FROM 連絡先 LIMIT 10"
result = client.execute_query(query)
```

4. **結果保存**
```python
import json
with open('result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
```

## 📞 サポート

問題が発生した場合は、以下を確認してください：

1. **ネットワーク接続**: インターネット接続が安定しているか
2. **認証情報**: クライアントIDとクライアントシークレットが正しいか
3. **スコープ設定**: Zoho Analytics APIのスコープが設定されているか
4. **リダイレクトURI**: 正確に一致しているか

## 📚 参考資料

- [Zoho Analytics API v2 ドキュメント](https://www.zoho.com/analytics/api/v2/introduction.html)
- [Zoho Developer Console](https://api-console.zoho.com/)
- [OAuth 2.0 認証ガイド](https://www.zoho.com/analytics/api/v2/oauth-guide.html)

---

*最終更新: 2025年8月9日*
*バージョン: 1.0* 