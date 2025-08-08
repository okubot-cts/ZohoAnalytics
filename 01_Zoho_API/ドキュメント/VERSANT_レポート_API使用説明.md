# VERSANTコーチングレポート - Zoho Analytics API v2使用説明書

## 📋 概要

このドキュメントは、[Zoho Analytics API v2](https://www.zoho.com/analytics/api/v2/introduction.html)を使用してVERSANTコーチングレポートを実行する方法を説明します。

## 🚀 セットアップ

### 1. 必要なパッケージのインストール

```bash
pip install requests pandas
```

### 2. 環境変数の設定

#### 方法1: 設定スクリプトを使用
```bash
chmod +x setup_environment.sh
./setup_environment.sh
```

#### 方法2: 手動で環境変数を設定
```bash
export ZOHO_ANALYTICS_ACCESS_TOKEN="your_access_token"
export ZOHO_ANALYTICS_WORKSPACE_ID="your_workspace_id"
```

#### 方法3: .envファイルを使用
```bash
# .envファイルを作成
echo "ZOHO_ANALYTICS_ACCESS_TOKEN=your_access_token" > .env
echo "ZOHO_ANALYTICS_WORKSPACE_ID=your_workspace_id" >> .env

# 環境変数を読み込み
source .env
```

## 🔑 Zoho Analytics API アクセストークンの取得

1. [Zoho Developer Console](https://api-console.zoho.com/)にアクセス
2. 新しいクライアントを作成
3. Zoho Analytics APIを選択
4. アクセストークンを生成
5. ワークスペースIDを確認

## 📊 実行方法

### 基本的な実行

```bash
python3 zoho_analytics_api_client.py
```

### 特定のSQLファイルを実行

```python
from zoho_analytics_api_client import ZohoAnalyticsAPI, load_versant_query

# APIクライアントの初期化
client = ZohoAnalyticsAPI()

# SQLファイルの読み込み
query = load_versant_query('versant_coaching_report_zoho.sql')

# クエリ実行
results = client.execute_query(query, output_format='json')

# 結果の確認
if results and 'data' in results:
    print(f"取得件数: {len(results['data'])}件")
```

## 📁 ファイル構成

### SQLファイル
- `versant_coaching_report_zoho.sql` - ZohoAnalytics専用最適化版
- `versant_coaching_report_simple.sql` - 最も安全でシンプル版
- `versant_coaching_report_select_only.sql` - 完全版
- `versant_coaching_report_basic.sql` - 基本版

### Pythonファイル
- `zoho_analytics_api_client.py` - APIクライアント
- `setup_environment.sh` - 環境変数設定スクリプト

## 🔧 API機能

### ZohoAnalyticsAPI クラス

#### 初期化
```python
client = ZohoAnalyticsAPI(
    access_token="your_token",
    workspace_id="your_workspace"
)
```

#### クエリ実行
```python
results = client.execute_query(query, output_format='json')
```

#### ワークスペース取得
```python
workspaces = client.get_workspaces()
```

#### テーブル一覧取得
```python
tables = client.get_tables()
```

## 📈 出力形式

### JSON形式
```json
{
  "data": [
    {
      "受講生ID": "123456",
      "受講生名": "田中 太郎",
      "メールアドレス": "tanaka@example.com",
      "会社名": "株式会社サンプル",
      "学習開始日": "2025-01-15",
      "20日前": 5,
      "19日前": 3,
      ...
      "今日": 2,
      "3週間合計": 45,
      "1日平均": 2.1,
      "学習状況": "積極的"
    }
  ]
}
```

### CSV形式
```python
results = client.execute_query(query, output_format='csv')
```

## ⚠️ 注意事項

### エラーハンドリング
- APIリクエストエラーは自動的にキャッチされます
- ネットワークエラーや認証エラーが発生した場合はログに出力されます

### レート制限
- Zoho Analytics APIにはレート制限があります
- 大量のクエリを実行する場合は適切な間隔を空けてください

### セキュリティ
- アクセストークンは機密情報です
- .envファイルは.gitignoreに追加してください
- 本番環境では適切な認証情報管理を行ってください

## 🔍 トラブルシューティング

### よくあるエラー

#### 1. 認証エラー
```
APIリクエストエラー: 401 Unauthorized
```
**解決方法**: アクセストークンを確認し、再生成してください

#### 2. ワークスペースエラー
```
ワークスペースIDが必要です
```
**解決方法**: 正しいワークスペースIDを設定してください

#### 3. SQL構文エラー
```
SQLクエリの構文エラー
```
**解決方法**: SQLファイルの構文を確認してください

### デバッグ方法

```python
# 詳細なログを有効にする
import logging
logging.basicConfig(level=logging.DEBUG)

# APIクライアントを初期化
client = ZohoAnalyticsAPI()
```

## 📞 サポート

問題が発生した場合は、以下を確認してください：

1. **API認証情報**: アクセストークンとワークスペースIDが正しいか
2. **ネットワーク接続**: インターネット接続が安定しているか
3. **SQL構文**: SQLファイルの構文が正しいか
4. **権限**: APIクライアントに適切な権限があるか

## 📚 参考資料

- [Zoho Analytics API v2 ドキュメント](https://www.zoho.com/analytics/api/v2/introduction.html)
- [Zoho Developer Console](https://api-console.zoho.com/)
- [REST API ガイド](https://www.zoho.com/analytics/api/v2/rest-api-guide.html) 