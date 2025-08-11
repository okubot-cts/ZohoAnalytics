#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプルなn8nワークフロー作成スクリプト
基本的なWebhookワークフローを作成
"""

import requests
import json
from datetime import datetime

def create_simple_workflow():
    """シンプルなワークフローを作成"""
    
    # n8n設定
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    
    headers = {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("=== シンプルなn8nワークフロー作成 ===\n")
    
    # シンプルなワークフローデータ
    simple_workflow = {
        "name": "Zoho CRM - Simple Test",
        "description": "ZohoCRM接続テスト用のシンプルなワークフロー",
        "active": True,
        "settings": {
            "executionOrder": "v1"
        },
        "nodes": [
            {
                "id": "webhook-trigger",
                "name": "Webhook Trigger",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [240, 300],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "zoho-simple-test",
                    "responseMode": "responseNode"
                }
            },
            {
                "id": "respond-success",
                "name": "Success Response",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [460, 300],
                "parameters": {
                    "responseBody": "={{ { 'success': true, 'message': 'ZohoCRM simple test workflow', 'timestamp': $now.toISOString() } }}",
                    "responseCode": 200
                }
            }
        ],
        "connections": {
            "Webhook Trigger": {
                "main": [
                    [
                        {
                            "node": "Success Response",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        }
    }
    
    print("1. シンプルなワークフローを作成中...")
    
    try:
        # ワークフロー作成
        url = f"{N8N_BASE_URL}/api/v1/workflows"
        response = requests.post(url, headers=headers, json=simple_workflow, timeout=60)
        
        print(f"レスポンスステータス: {response.status_code}")
        print(f"レスポンスヘッダー: {dict(response.headers)}")
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print(f"✅ ワークフロー作成成功: {result}")
            
            workflow_id = result.get('id')
            if workflow_id:
                print(f"ワークフローID: {workflow_id}")
                
                # アクティブ化
                print("\n2. ワークフローをアクティブ化中...")
                activate_url = f"{N8N_BASE_URL}/api/v1/workflows/{workflow_id}/activate"
                activate_response = requests.post(activate_url, headers=headers, timeout=30)
                
                if activate_response.status_code == 200:
                    print("✅ ワークフローアクティブ化成功")
                    print(f"Webhook URL: {N8N_BASE_URL}/webhook/zoho-simple-test")
                else:
                    print(f"❌ アクティブ化エラー: {activate_response.status_code}")
                    print(f"レスポンス: {activate_response.text}")
        else:
            print(f"❌ ワークフロー作成エラー: {response.status_code}")
            print(f"エラーレスポンス: {response.text}")
            
            # エラーの詳細を確認
            try:
                error_data = response.json()
                print(f"エラーデータ: {json.dumps(error_data, indent=2)}")
            except:
                print("エラーレスポンスの解析に失敗")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ リクエストエラー: {e}")
    
    # 2. 既存のワークフロー一覧を確認
    print("\n3. 既存のワークフロー一覧を確認中...")
    
    try:
        list_url = f"{N8N_BASE_URL}/api/v1/workflows"
        list_response = requests.get(list_url, headers=headers, timeout=30)
        
        if list_response.status_code == 200:
            workflows_data = list_response.json()
            workflows = workflows_data.get('data', workflows_data)
            
            if isinstance(workflows, list):
                print(f"✅ ワークフロー一覧取得成功: {len(workflows)}件")
                
                # ZohoCRM関連のワークフローを検索
                zoho_workflows = [w for w in workflows if 'zoho' in w.get('name', '').lower()]
                
                if zoho_workflows:
                    print("ZohoCRM関連のワークフロー:")
                    for workflow in zoho_workflows:
                        print(f"  - {workflow.get('name')} (ID: {workflow.get('id')}, アクティブ: {workflow.get('active', False)})")
                else:
                    print("ZohoCRM関連のワークフローは見つかりませんでした")
            else:
                print(f"ワークフローデータ: {workflows}")
        else:
            print(f"❌ ワークフロー一覧取得エラー: {list_response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ ワークフロー一覧取得エラー: {e}")

def test_webhook():
    """Webhookをテスト"""
    print("\n4. Webhookテスト...")
    
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    
    try:
        # 作成したWebhookをテスト
        webhook_url = f"{N8N_BASE_URL}/webhook/zoho-simple-test"
        test_data = {"test": True, "timestamp": datetime.now().isoformat()}
        
        response = requests.post(webhook_url, json=test_data, timeout=10)
        
        print(f"Webhookテスト結果: HTTP {response.status_code}")
        if response.status_code == 200:
            print(f"レスポンス: {response.text}")
        else:
            print(f"エラーレスポンス: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Webhookテストエラー: {e}")

def main():
    """メイン実行関数"""
    print("n8nシンプルワークフロー作成ツール\n")
    
    # ワークフロー作成
    create_simple_workflow()
    
    # Webhookテスト
    test_webhook()
    
    print("\n=== 完了 ===")
    print("次のステップ:")
    print("1. n8nダッシュボードでワークフローを確認")
    print("2. 必要に応じて手動でワークフローを調整")
    print("3. ZohoCRMノードを追加")

if __name__ == "__main__":
    main() 