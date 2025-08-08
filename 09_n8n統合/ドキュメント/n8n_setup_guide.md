# n8n ZohoCRM統合セットアップガイド

## 📋 概要

このガイドでは、n8nを使用してZohoCRMにアクセスし、Cursorから統合する方法を説明します。

## 🚀 n8nセットアップ

### 1. n8nインスタンスの起動

#### Dockerを使用する場合
```bash
# n8nをDockerで起動
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

#### npmを使用する場合
```bash
# n8nをグローバルにインストール
npm install n8n -g

# n8nを起動
n8n start
```

### 2. n8nにアクセス
- URL: `http://localhost:5678`
- 初回アクセス時にアカウントを作成

### 3. APIキーの生成
1. n8nダッシュボードにログイン
2. 設定 → API Keys
3. 新しいAPIキーを生成
4. 生成されたキーを保存

## 🔧 ZohoCRMワークフロー作成

### 1. ワークフローの作成

#### 商談取得ワークフロー
1. **Webhook Trigger** ノードを追加
   - HTTP Method: POST
   - Path: `zoho-deals`
   - Response Mode: responseNode

2. **Zoho CRM** ノードを追加
   - Operation: getAll
   - Resource: deals
   - Filters: `from: {{ $json.date_from }}`

3. **Filter** ノードを追加
   - 条件: `Close_Date >= {{ $json.date_from }}`

4. **Set** ノードを追加（データ変換）
   - 必要なフィールドをマッピング

5. **Respond to Webhook** ノードを追加
   - Response Body: `{{ $json }}`

### 2. ZohoCRM認証設定
1. ZohoCRMノードを選択
2. 認証情報を設定
   - Client ID
   - Client Secret
   - Refresh Token

## 🔗 Cursor統合

### 1. 統合スクリプトの使用

#### 接続テスト
```bash
python3 test_n8n_connection.py
```

#### 商談データ取得
```bash
python3 n8n_zoho_integration.py
```

### 2. カスタム統合

#### Pythonスクリプト例
```python
from n8n_zoho_integration import N8nZohoIntegration

# n8n統合インスタンスを作成
n8n = N8nZohoIntegration(
    base_url="http://localhost:5678",
    api_key="your_api_key"
)

# 商談データを取得
deals = n8n.get_current_period_deals_via_n8n(
    workflow_id="your_workflow_id",
    from_date="2025-04-01"
)
```

## 📊 ワークフロー例

### 1. 今期商談取得ワークフロー
```json
{
  "name": "Get Current Period Deals",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "httpMethod": "POST",
        "path": "zoho-deals"
      }
    },
    {
      "name": "Zoho CRM",
      "type": "n8n-nodes-base.zohoCrm",
      "parameters": {
        "operation": "getAll",
        "resource": "deals",
        "filters": {
          "from": "={{ $json.date_from }}"
        }
      }
    }
  ]
}
```

### 2. 商品内訳取得ワークフロー
```json
{
  "name": "Get Products",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "httpMethod": "POST",
        "path": "zoho-products"
      }
    },
    {
      "name": "Zoho CRM",
      "type": "n8n-nodes-base.zohoCrm",
      "parameters": {
        "operation": "getAll",
        "resource": "products",
        "filters": {
          "parentId": "={{ $json.deal_id }}"
        }
      }
    }
  ]
}
```

## 🔐 認証設定

### 1. ZohoCRM OAuth2設定
1. Zoho Developer Consoleでアプリを作成
2. 必要なスコープを設定
3. リダイレクトURIを設定
4. Client IDとClient Secretを取得

### 2. n8nでの認証設定
1. ZohoCRMノードを選択
2. 認証方法をOAuth2に設定
3. 認証情報を入力
4. 認証を実行

## 📈 データフロー

### 1. 基本的なフロー
```
Cursor → Python Script → n8n Webhook → Zoho CRM → データ処理 → 結果返却
```

### 2. エラーハンドリング
- 接続エラーの処理
- データ変換エラーの処理
- レスポンス検証

## 🛠️ トラブルシューティング

### 1. 接続エラー
- n8nインスタンスが起動しているか確認
- URLとポート番号が正しいか確認
- ファイアウォール設定を確認

### 2. 認証エラー
- APIキーが有効か確認
- ZohoCRM認証情報が正しいか確認
- スコープが適切に設定されているか確認

### 3. データ取得エラー
- ワークフローがアクティブか確認
- Webhookエンドポイントが有効か確認
- フィルター条件が正しいか確認

## 📝 使用例

### 1. 定期実行
```python
import schedule
import time
from n8n_zoho_integration import N8nZohoIntegration

def daily_deals_update():
    n8n = N8nZohoIntegration(base_url, api_key)
    deals = n8n.get_current_period_deals_via_n8n(workflow_id)
    # データ処理

# 毎日午前9時に実行
schedule.every().day.at("09:00").do(daily_deals_update)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 2. リアルタイム処理
```python
# Webhookを使用したリアルタイム処理
@app.route('/webhook/zoho-update', methods=['POST'])
def handle_zoho_update():
    data = request.json
    # データ処理
    return {"status": "success"}
```

## 🔄 自動化

### 1. スケジュール実行
- n8nのスケジュール機能を使用
- 定期的なデータ取得と処理

### 2. トリガー実行
- ZohoCRMの変更をトリガーに実行
- リアルタイムデータ同期

### 3. 条件実行
- 特定の条件を満たした場合のみ実行
- 効率的なデータ処理

## 📚 参考資料

- [n8n公式ドキュメント](https://docs.n8n.io/)
- [ZohoCRM APIドキュメント](https://www.zoho.com/crm/developer/docs/api/)
- [n8n ZohoCRMノード](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.zohoCrm/) 