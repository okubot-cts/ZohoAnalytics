#!/bin/bash
# Zoho Analytics API 環境変数設定スクリプト

echo "=== Zoho Analytics API 環境変数設定 ==="

# 環境変数の設定
echo "Zoho Analytics API アクセストークンを入力してください:"
read -s ZOHO_ACCESS_TOKEN

echo "Zoho Analytics ワークスペースIDを入力してください:"
read ZOHO_WORKSPACE_ID

# .envファイルに保存
cat > .env << EOF
# Zoho Analytics API 設定
ZOHO_ANALYTICS_ACCESS_TOKEN=$ZOHO_ACCESS_TOKEN
ZOHO_ANALYTICS_WORKSPACE_ID=$ZOHO_WORKSPACE_ID
EOF

echo "✅ 環境変数を .env ファイルに保存しました"

# 環境変数を現在のセッションに読み込み
export ZOHO_ANALYTICS_ACCESS_TOKEN=$ZOHO_ACCESS_TOKEN
export ZOHO_ANALYTICS_WORKSPACE_ID=$ZOHO_WORKSPACE_ID

echo "✅ 環境変数を現在のセッションに設定しました"

# 設定の確認
echo ""
echo "=== 設定確認 ==="
echo "アクセストークン: ${ZOHO_ANALYTICS_ACCESS_TOKEN:0:10}..."
echo "ワークスペースID: $ZOHO_ANALYTICS_WORKSPACE_ID"

echo ""
echo "=== 使用方法 ==="
echo "1. 環境変数を読み込む:"
echo "   source .env"
echo ""
echo "2. Pythonクライアントを実行:"
echo "   python3 zoho_analytics_api_client.py"
echo ""
echo "3. または直接実行:"
echo "   ZOHO_ANALYTICS_ACCESS_TOKEN=your_token ZOHO_ANALYTICS_WORKSPACE_ID=your_workspace python3 zoho_analytics_api_client.py" 