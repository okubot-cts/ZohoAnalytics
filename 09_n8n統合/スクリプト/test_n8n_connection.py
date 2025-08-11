#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
n8nとの接続テストスクリプト
正しいn8nインスタンスURLで接続を確認
"""

import requests
import json
from datetime import datetime

def test_n8n_connection(base_url: str, api_key: str):
    """n8nとの接続をテスト"""
    
    headers = {
        'X-N8N-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    print("=== n8n接続テスト ===\n")
    print(f"接続先: {base_url}\n")
    
    # 1. ワークフロー一覧取得テスト
    print("1. ワークフロー一覧取得テスト...")
    try:
        url = f"{base_url}/api/v1/workflows"
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            workflows_data = response.json()
            print(f"✅ 成功: ワークフローデータを取得しました")
            
            # レスポンスの構造を確認
            print(f"レスポンス構造: {type(workflows_data)}")
            if isinstance(workflows_data, dict):
                print(f"キー: {list(workflows_data.keys())}")
                workflows = workflows_data.get('data', workflows_data)
            else:
                workflows = workflows_data
            
            if workflows and isinstance(workflows, list):
                print(f"ワークフロー数: {len(workflows)}")
                print("利用可能なワークフロー:")
                for i, workflow in enumerate(workflows[:5], 1):
                    print(f"  {i}. ID: {workflow.get('id')}, 名前: {workflow.get('name')}")
                    print(f"     アクティブ: {workflow.get('active', False)}")
                    if 'tags' in workflow:
                        print(f"     タグ: {[tag.get('name') for tag in workflow.get('tags', [])]}")
                    print()
            else:
                print(f"ワークフローデータ: {workflows}")
        else:
            print(f"❌ エラー: HTTP {response.status_code}")
            print(f"レスポンス: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 接続エラー: {e}")
        return False
    
    # 2. 実行履歴取得テスト
    print("2. 実行履歴取得テスト...")
    try:
        if workflows and isinstance(workflows, list) and len(workflows) > 0:
            workflow_id = workflows[0]['id']
            url = f"{base_url}/api/v1/workflows/{workflow_id}/executions"
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                executions_data = response.json()
                if isinstance(executions_data, dict):
                    executions = executions_data.get('data', executions_data)
                else:
                    executions = executions_data
                
                if isinstance(executions, list):
                    print(f"✅ 成功: {len(executions)}件の実行履歴を取得")
                else:
                    print(f"✅ 実行履歴データ: {executions}")
            else:
                print(f"❌ エラー: HTTP {response.status_code}")
        else:
            print("⚠️ ワークフローが見つからないためスキップ")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 接続エラー: {e}")
    
    # 3. Webhookテスト（利用可能な場合）
    print("\n3. Webhookテスト...")
    try:
        # 一般的なWebhookパスをテスト
        webhook_paths = ["zoho-deals", "test", "webhook"]
        
        for path in webhook_paths:
            url = f"{base_url}/webhook/{path}"
            response = requests.post(url, json={"test": True}, timeout=10)
            
            if response.status_code in [200, 404, 405]:
                print(f"✅ Webhook {path}: 応答あり (HTTP {response.status_code})")
                if response.status_code == 200:
                    print(f"   レスポンス: {response.text[:100]}...")
                break
        else:
            print("⚠️ アクティブなWebhookが見つかりません")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Webhookテストエラー: {e}")
    
    # 4. 接続情報の表示
    print("\n4. 接続情報:")
    print(f"   n8n URL: {base_url}")
    print(f"   API Key: {api_key[:20]}...{api_key[-20:]}")
    print(f"   テスト時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True

def main():
    """メイン実行関数"""
    
    # n8n設定（正しいURLに更新）
    N8N_BASE_URL = "https://cts-automation.onrender.com"  # n8nのベースURL
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    
    print("n8n接続テストを開始します...\n")
    
    # 接続テスト実行
    success = test_n8n_connection(N8N_BASE_URL, N8N_API_KEY)
    
    if success:
        print("\n✅ 接続テスト完了")
        print("\n次のステップ:")
        print("1. n8nワークフローを作成")
        print("2. ZohoCRMノードを設定")
        print("3. Webhookエンドポイントを有効化")
        print("4. 統合スクリプトを実行")
    else:
        print("\n❌ 接続テスト失敗")
        print("\n確認事項:")
        print("1. n8nインスタンスが起動しているか")
        print("2. URLが正しいか")
        print("3. APIキーが有効か")
        print("4. ネットワーク接続が正常か")

if __name__ == "__main__":
    main() 