#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最小限のZohoCRMワークフロー作成スクリプト
確実に動作する基本構成のみ
"""

import requests
import json
import os

def create_minimal_zoho_workflow():
    """最小限のZohoCRMワークフローを作成"""
    
    # n8n設定
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    
    headers = {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("=== 最小限ZohoCRMワークフロー作成 ===\n")
    
    # 最小限のワークフロー（Webhook + HTTP Request + Respond）
    workflow = {
        "name": "Zoho CRM - Minimal Working",
        "settings": {},
        "nodes": [
            # 1. Webhook
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "zoho-minimal"
                },
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1.0,
                "position": [300, 300],
                "id": "webhook-node",
                "name": "Webhook"
            },
            
            # 2. HTTP Request - ZohoCRM API
            {
                "parameters": {
                    "url": "https://www.zohoapis.com/crm/v2/Deals",
                    "method": "GET",
                    "headerParametersUi": {
                        "parameter": [
                            {
                                "name": "Authorization",
                                "value": "Zoho-oauthtoken 1000.f7cebcf43331706bec1653ec150e4956.86a18caddb092ba38c443fef26f4ca25"
                            }
                        ]
                    },
                    "queryParametersUi": {
                        "parameter": [
                            {
                                "name": "per_page",
                                "value": "10"
                            }
                        ]
                    }
                },
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 2,
                "position": [600, 300],
                "id": "http-request-node",
                "name": "Get Deals"
            },
            
            # 3. Respond to Webhook
            {
                "parameters": {
                    "responseBody": "={{ JSON.stringify({ success: true, data: $json, timestamp: new Date().toISOString() }) }}",
                    "responseCode": 200
                },
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [900, 300],
                "id": "respond-node",
                "name": "Respond"
            }
        ],
        "connections": {
            "Webhook": {
                "main": [
                    [
                        {
                            "node": "Get Deals",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Get Deals": {
                "main": [
                    [
                        {
                            "node": "Respond",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        }
    }
    
    print("📝 最小限ワークフロー定義を作成中...")
    
    try:
        # ワークフロー作成
        url = f"{N8N_BASE_URL}/api/v1/workflows"
        response = requests.post(url, headers=headers, json=workflow, timeout=60)
        
        print(f"レスポンスステータス: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ 最小限ワークフロー作成成功")
            
            workflow_id = result.get('id')
            if workflow_id:
                print(f"ワークフローID: {workflow_id}")
                webhook_url = f"{N8N_BASE_URL}/webhook/zoho-minimal"
                print(f"Webhook URL: {webhook_url}")
                
                # アクティブ化を試行
                print("\n🚀 ワークフローをアクティブ化中...")
                activate_url = f"{N8N_BASE_URL}/api/v1/workflows/{workflow_id}/activate"
                activate_response = requests.post(activate_url, headers=headers, timeout=30)
                
                if activate_response.status_code == 200:
                    print("✅ ワークフローアクティブ化成功")
                    print("\n🎉 最小限ZohoCRMワークフロー完成！")
                    
                    print(f"\n📋 テスト用コマンド:")
                    print(f'curl -X POST {webhook_url} \\')
                    print('  -H "Content-Type: application/json" \\')
                    print('  -d \'{"test": "data"}\'')
                    
                else:
                    print(f"⚠️  アクティブ化エラー: {activate_response.status_code}")
                    print(f"レスポンス: {activate_response.text}")
                    print("手動でアクティブ化してください")
                    
                print(f"\n📄 ワークフロー基本情報:")
                print(f"- ID: {workflow_id}")
                print(f"- URL: {webhook_url}")
                print(f"- 機能: ZohoCRM商談データ取得")
                print(f"- 認証: プロジェクト内アクセストークン使用")
                
        else:
            print(f"❌ ワークフロー作成エラー: {response.status_code}")
            print(f"エラーレスポンス: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ リクエストエラー: {e}")

def main():
    """メイン実行関数"""
    create_minimal_zoho_workflow()

if __name__ == "__main__":
    main()