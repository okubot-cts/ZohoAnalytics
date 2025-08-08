# n8n ZohoCRM統合セットアップガイド

## 📋 概要

このガイドでは、n8nを使用してZohoCRMにアクセスし、Cursorから統合する完全なセットアップ手順を説明します。

## 🏗️ システム構成

```
Cursor → Python Script → n8n → Zoho CRM
                ↓
        認証管理・データ処理
```

## 📁 フォルダ構成

```
09_n8n統合/
├── ワークフロー/
│   ├── zoho_crm_deals_workflow.json
│   └── n8n_workflow_examples.json
├── スクリプト/
│   ├── n8n_zoho_integration.py
│   ├── zoho_crm_auth_manager.py
│   └── test_n8n_connection.py
├── 設定/
│   ├── zoho_crm_auth_config.json
│   └── zoho_crm_tokens.json (自動生成)
└── ドキュメント/
    └── n8n_zoho_setup_guide.md
```

## 🚀 セットアップ手順

### 1. n8nインスタンスの起動

#### Dockerを使用する場合（推奨）
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

### 2. n8nにアクセス・初期設定

1. ブラウザで `http://localhost:5678` にアクセス
2. 初回アクセス時にアカウントを作成
3. ダッシュボードにログイン

### 3. APIキーの生成

1. n8nダッシュボードで設定 → API Keys
2. 「新しいAPIキーを生成」をクリック
3. 生成されたキーをコピー
4. `設定/zoho_crm_auth_config.json` の `n8n_config.api_key` に設定

### 4. ZohoCRM認証設定

#### 4.1 Zoho Developer Consoleでの設定

1. [Zoho Developer Console](https://api-console.zoho.com/) にアクセス
2. 新しいアプリを作成
3. 以下の設定を行う：
   - **Client Name**: n8n-ZohoCRM-Integration
   - **Homepage URL**: `http://localhost:5678`
   - **Authorized Redirect URIs**: `https://www.zohoapis.com/oauth/v2/auth`
   - **Scope**: `ZohoCRM.modules.ALL,ZohoCRM.settings.ALL`

4. Client IDとClient Secretを取得

#### 4.2 設定ファイルの更新

`設定/zoho_crm_auth_config.json` を編集：

```json
{
  "zoho_crm_auth": {
    "client_id": "あなたのClient ID",
    "client_secret": "あなたのClient Secret",
    "redirect_uri": "https://www.zohoapis.com/oauth/v2/auth",
    "scope": "ZohoCRM.modules.ALL,ZohoCRM.settings.ALL"
  }
}
```

#### 4.3 初期認証の実行

```bash
cd 09_n8n統合/スクリプト
python3 zoho_crm_auth_manager.py
```

1. メニューから「1. 初期認証セットアップ」を選択
2. 表示されたURLにアクセス
3. ZohoCRMにログインして認証を実行
4. 認証コードをコピーして入力

### 5. n8nワークフローの作成

#### 5.1 ワークフローのインポート

1. n8nダッシュボードで「Workflows」→「Import from file」
2. `ワークフロー/zoho_crm_deals_workflow.json` を選択
3. ワークフローをインポート

#### 5.2 ZohoCRM認証の設定

1. ワークフロー内のZohoCRMノードを選択
2. 「Credentials」→「Create New」
3. 「Zoho CRM OAuth2 API」を選択
4. 以下の情報を入力：
   - **Client ID**: 設定ファイルの値
   - **Client Secret**: 設定ファイルの値
   - **Authorization URL**: `https://accounts.zoho.com/oauth/v2/auth`
   - **Token URL**: `https://accounts.zoho.com/oauth/v2/token`
   - **Scope**: `ZohoCRM.modules.ALL,ZohoCRM.settings.ALL`

5. 「Save」をクリック
6. 「Connect to Zoho CRM」をクリックして認証を実行

#### 5.3 ワークフローの有効化

1. ワークフローを保存
2. 「Active」スイッチをONにする
3. Webhookエンドポイントが有効になることを確認

### 6. 接続テスト

#### 6.1 n8n接続テスト

```bash
cd 09_n8n統合/スクリプト
python3 test_n8n_connection.py
```

#### 6.2 ZohoCRM接続テスト

```bash
cd 09_n8n統合/スクリプト
python3 zoho_crm_auth_manager.py
# メニューから「2. 接続テスト」を選択
```

#### 6.3 統合テスト

```bash
cd 09_n8n統合/スクリプト
python3 n8n_zoho_integration.py
```

## 🔧 ワークフロー詳細

### 商談取得ワークフロー

**ノード構成:**
1. **Webhook Trigger** - エントリーポイント
2. **Validate Input** - 入力データの検証
3. **Zoho CRM - Get Deals** - 商談データ取得
4. **Filter Current Period** - 今期データのフィルタリング
5. **Transform Deal Data** - データ変換
6. **Get Products for Deal** - 商品内訳取得
7. **Transform Product Data** - 商品データ変換
8. **Combine Deal & Products** - データ統合
9. **Save to File** - ファイル保存
10. **Success Response** - 成功レスポンス

**Webhook URL:**
```
http://localhost:5678/webhook/zoho-deals
```

**リクエスト例:**
```json
{
  "date_from": "2025-04-01",
  "include_products": true
}
```

## 📊 データフロー

### 1. 基本的なフロー
```
Cursor → Python Script → n8n Webhook → Zoho CRM → データ処理 → 結果返却
```

### 2. 認証フロー
```
Python Script → ZohoCRM Auth Manager → OAuth2 Token → n8n → Zoho CRM
```

### 3. エラーハンドリング
```
入力検証 → API呼び出し → レスポンス検証 → エラー処理 → ログ出力
```

## 🛠️ 使用方法

### 1. 商談データ取得

```python
from n8n_zoho_integration import N8nZohoIntegration
from zoho_crm_auth_manager import ZohoCRMAuthManager

# 認証マネージャーを初期化
auth_manager = ZohoCRMAuthManager()

# n8n統合インスタンスを作成
n8n = N8nZohoIntegration(
    base_url="http://localhost:5678",
    api_key="your_api_key",
    auth_manager=auth_manager
)

# 今期の商談データを取得
deals = n8n.get_current_period_deals_via_n8n(
    from_date="2025-04-01"
)
```

### 2. 商品内訳取得

```python
# 特定の商談の商品内訳を取得
products = n8n.get_products_for_deal("deal_id")
```

### 3. 新規商談作成

```python
# 新規商談を作成
deal_data = {
    "deal_name": "テスト商談",
    "close_date": "2025-12-31",
    "amount": 100000,
    "stage": "提案前A"
}

result = n8n.create_new_deal(deal_data)
```

## 🔐 セキュリティ

### 1. 認証情報の管理
- トークンは暗号化して保存
- 定期的なトークン更新
- アクセス権限の最小化

### 2. ネットワークセキュリティ
- HTTPS通信の使用
- ファイアウォール設定
- APIキーの適切な管理

### 3. データ保護
- 個人情報の暗号化
- アクセスログの記録
- データのバックアップ

## 🚨 トラブルシューティング

### 1. 接続エラー

**症状:** `Connection refused`
**解決策:**
- n8nインスタンスが起動しているか確認
- ポート番号が正しいか確認
- ファイアウォール設定を確認

### 2. 認証エラー

**症状:** `Invalid credentials`
**解決策:**
- Client ID/Secretが正しいか確認
- スコープが適切に設定されているか確認
- トークンの有効期限を確認

### 3. ワークフローエラー

**症状:** `Workflow not found`
**解決策:**
- ワークフローがアクティブか確認
- Webhookエンドポイントが有効か確認
- ノードの設定を確認

### 4. データ取得エラー

**症状:** `No data returned`
**解決策:**
- フィルター条件を確認
- ZohoCRMのデータ存在確認
- API制限の確認

## 📈 パフォーマンス最適化

### 1. バッチ処理
- 大量データの分割処理
- 並列実行の活用
- キャッシュ機能の実装

### 2. エラーリトライ
- 自動リトライ機能
- 指数バックオフ
- エラーログの分析

### 3. 監視・アラート
- 実行状況の監視
- エラー通知の設定
- パフォーマンスメトリクス

## 🔄 自動化

### 1. スケジュール実行
```python
import schedule
import time

def daily_deals_update():
    n8n = N8nZohoIntegration(base_url, api_key)
    deals = n8n.get_current_period_deals_via_n8n()
    # データ処理

# 毎日午前9時に実行
schedule.every().day.at("09:00").do(daily_deals_update)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 2. リアルタイム処理
```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook/zoho-update', methods=['POST'])
def handle_zoho_update():
    data = request.json
    # データ処理
    return {"status": "success"}
```

## 📚 参考資料

- [n8n公式ドキュメント](https://docs.n8n.io/)
- [ZohoCRM APIドキュメント](https://www.zoho.com/crm/developer/docs/api/)
- [n8n ZohoCRMノード](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.zohoCrm/)
- [OAuth2認証ガイド](https://www.zoho.com/crm/developer/docs/api/oauth-overview.html)

## 📞 サポート

問題が発生した場合は、以下の手順で対処してください：

1. ログファイルの確認
2. 設定ファイルの検証
3. 接続テストの実行
4. ドキュメントの参照
5. コミュニティフォーラムでの質問 