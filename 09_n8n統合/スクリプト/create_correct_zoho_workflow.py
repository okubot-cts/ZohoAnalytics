#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正しい形式でZohoCRM認証ワークフローを作成するスクリプト
既存のワークフロー構造を基に作成
"""

import requests
import json
from datetime import datetime

def create_zoho_auth_workflow():
    """ZohoCRM認証ワークフローを作成"""
    
    # n8n設定
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    
    headers = {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("=== ZohoCRM認証ワークフロー作成 ===\n")
    
    # 正しい形式のZohoCRM認証ワークフロー
    zoho_auth_workflow = {
        "name": "Zoho CRM - Authentication Test",
        "description": "ZohoCRM認証ノードを含むテストワークフロー",
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
                    "path": "zoho-auth-test",
                    "responseMode": "responseNode"
                }
            },
            {
                "id": "zoho-crm-test",
                "name": "Zoho CRM - Test Connection",
                "type": "n8n-nodes-base.zohoCrm",
                "typeVersion": 1,
                "position": [460, 300],
                "parameters": {
                    "operation": "getAll",
                    "resource": "deals",
                    "limit": 1
                },
                "credentials": {
                    "zohoCrmOAuth2Api": {
                        "id": "zoho-crm-credentials",
                        "name": "Zoho CRM OAuth2"
                    }
                }
            },
            {
                "id": "respond-success",
                "name": "Success Response",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [680, 300],
                "parameters": {
                    "responseBody": "={{ { 'success': true, 'message': 'ZohoCRM認証成功', 'timestamp': $now.toISOString(), 'data_count': $json.length } }}",
                    "responseCode": 200
                }
            }
        ],
        "connections": {
            "Webhook Trigger": {
                "main": [
                    [
                        {
                            "node": "Zoho CRM - Test Connection",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Zoho CRM - Test Connection": {
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
    
    print("1. ZohoCRM認証ワークフローを作成中...")
    
    try:
        # ワークフロー作成
        url = f"{N8N_BASE_URL}/api/v1/workflows"
        response = requests.post(url, headers=headers, json=zoho_auth_workflow, timeout=60)
        
        print(f"レスポンスステータス: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print(f"✅ ワークフロー作成成功")
            
            workflow_id = result.get('id')
            if workflow_id:
                print(f"ワークフローID: {workflow_id}")
                
                # アクティブ化
                print("\n2. ワークフローをアクティブ化中...")
                activate_url = f"{N8N_BASE_URL}/api/v1/workflows/{workflow_id}/activate"
                activate_response = requests.post(activate_url, headers=headers, timeout=30)
                
                if activate_response.status_code == 200:
                    print("✅ ワークフローアクティブ化成功")
                    print(f"Webhook URL: {N8N_BASE_URL}/webhook/zoho-auth-test")
                    print("\n⚠️ 注意: ZohoCRM認証情報の設定が必要です")
                    print("n8nダッシュボードで認証情報を設定してください")
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

def create_simple_modules_workflow():
    """ZohoCRMモジュール取得ワークフローを作成"""
    
    # n8n設定
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    
    headers = {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("\n3. ZohoCRMモジュール取得ワークフローを作成中...")
    
    # モジュール取得ワークフロー
    modules_workflow = {
        "name": "Zoho CRM - Get Modules",
        "description": "ZohoCRMモジュール一覧を取得するワークフロー",
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
                    "path": "zoho-modules",
                    "responseMode": "responseNode"
                }
            },
            {
                "id": "zoho-crm-modules",
                "name": "Zoho CRM - Get Modules",
                "type": "n8n-nodes-base.zohoCrm",
                "typeVersion": 1,
                "position": [460, 300],
                "parameters": {
                    "operation": "getAll",
                    "resource": "modules"
                },
                "credentials": {
                    "zohoCrmOAuth2Api": {
                        "id": "zoho-crm-credentials",
                        "name": "Zoho CRM OAuth2"
                    }
                }
            },
            {
                "id": "respond-modules",
                "name": "Modules Response",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [680, 300],
                "parameters": {
                    "responseBody": "={{ { 'success': true, 'message': 'ZohoCRMモジュール取得成功', 'modules_count': $json.length, 'modules': $json, 'timestamp': $now.toISOString() } }}",
                    "responseCode": 200
                }
            }
        ],
        "connections": {
            "Webhook Trigger": {
                "main": [
                    [
                        {
                            "node": "Zoho CRM - Get Modules",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Zoho CRM - Get Modules": {
                "main": [
                    [
                        {
                            "node": "Modules Response",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        }
    }
    
    try:
        # ワークフロー作成
        url = f"{N8N_BASE_URL}/api/v1/workflows"
        response = requests.post(url, headers=headers, json=modules_workflow, timeout=60)
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            workflow_id = result.get('id')
            
            if workflow_id:
                print(f"✅ モジュール取得ワークフロー作成成功: {workflow_id}")
                
                # アクティブ化
                activate_url = f"{N8N_BASE_URL}/api/v1/workflows/{workflow_id}/activate"
                activate_response = requests.post(activate_url, headers=headers, timeout=30)
                
                if activate_response.status_code == 200:
                    print("✅ モジュール取得ワークフローアクティブ化成功")
                    print(f"Webhook URL: {N8N_BASE_URL}/webhook/zoho-modules")
                else:
                    print(f"❌ アクティブ化エラー: {activate_response.status_code}")
        else:
            print(f"❌ モジュール取得ワークフロー作成エラー: {response.status_code}")
            print(f"エラーレスポンス: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ リクエストエラー: {e}")

def list_zoho_workflows():
    """ZohoCRM関連のワークフロー一覧を表示"""
    
    # n8n設定
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    
    headers = {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("\n4. ZohoCRM関連ワークフロー一覧:")
    
    try:
        url = f"{N8N_BASE_URL}/api/v1/workflows"
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            workflows_data = response.json()
            workflows = workflows_data.get('data', workflows_data)
            
            if isinstance(workflows, list):
                # ZohoCRM関連のワークフローを検索
                zoho_workflows = [w for w in workflows if 'zoho' in w.get('name', '').lower()]
                
                if zoho_workflows:
                    print("ZohoCRM関連のワークフロー:")
                    for i, workflow in enumerate(zoho_workflows, 1):
                        print(f"  {i}. {workflow.get('name')} (ID: {workflow.get('id')}, アクティブ: {workflow.get('active', False)})")
                        if workflow.get('active'):
                            print(f"     Webhook URL: {N8N_BASE_URL}/webhook/[path]")
                else:
                    print("ZohoCRM関連のワークフローは見つかりませんでした")
            else:
                print(f"ワークフローデータ: {workflows}")
        else:
            print(f"❌ ワークフロー一覧取得エラー: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ ワークフロー一覧取得エラー: {e}")

def main():
    """メイン実行関数"""
    print("ZohoCRM認証ワークフロー作成ツール\n")
    
    # ZohoCRM認証ワークフローを作成
    create_zoho_auth_workflow()
    
    # モジュール取得ワークフローを作成
    create_simple_modules_workflow()
    
    # ZohoCRM関連ワークフロー一覧を表示
    list_zoho_workflows()
    
    print("\n=== 作成完了 ===")
    print("次のステップ:")
    print("1. n8nダッシュボードでワークフローを確認")
    print("2. ZohoCRM認証情報を設定:")
    print("   - Client ID")
    print("   - Client Secret")
    print("   - Authorization URL: https://accounts.zoho.com/oauth/v2/auth")
    print("   - Token URL: https://accounts.zoho.com/oauth/v2/token")
    print("   - Scope: ZohoCRM.modules.ALL,ZohoCRM.settings.ALL")
    print("3. 認証テストを実行")
    print("\n利用可能なWebhook:")
    print("- https://cts-automation.onrender.com/webhook/zoho-auth-test")
    print("- https://cts-automation.onrender.com/webhook/zoho-modules")

if __name__ == "__main__":
    main() 