#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZohoCRM認証ノードを含むワークフローを作成するスクリプト
認証システムを組み込んだ基本的なワークフロー
"""

import requests
import json
import os
from datetime import datetime

def create_zoho_auth_workflow():
    """ZohoCRM認証ノードを含むワークフローを作成"""
    
    # n8n設定
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    
    headers = {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("=== ZohoCRM認証ワークフロー作成 ===\n")
    
    # ZohoCRM認証ノードを含むワークフロー
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
                "id": "zoho-crm-auth",
                "name": "Zoho CRM - Test Auth",
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
                "id": "auth-success",
                "name": "Auth Success Response",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [680, 200],
                "parameters": {
                    "responseBody": "={{ { 'success': true, 'message': 'ZohoCRM認証成功', 'timestamp': $now.toISOString(), 'data': $json } }}",
                    "responseCode": 200
                }
            },
            {
                "id": "auth-error",
                "name": "Auth Error Response",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [680, 400],
                "parameters": {
                    "responseBody": "={{ { 'success': false, 'message': 'ZohoCRM認証エラー', 'timestamp': $now.toISOString(), 'error': $json } }}",
                    "responseCode": 400
                }
            }
        ],
        "connections": {
            "Webhook Trigger": {
                "main": [
                    [
                        {
                            "node": "Zoho CRM - Test Auth",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Zoho CRM - Test Auth": {
                "main": [
                    [
                        {
                            "node": "Auth Success Response",
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

def create_simple_auth_workflow():
    """シンプルな認証テストワークフローを作成"""
    
    # n8n設定
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    
    headers = {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("\n3. シンプルな認証テストワークフローを作成中...")
    
    # シンプルな認証テストワークフロー
    simple_auth_workflow = {
        "name": "Zoho CRM - Simple Auth Test",
        "description": "ZohoCRM認証の基本的なテスト",
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
                    "path": "zoho-simple-auth",
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
                "id": "respond-success",
                "name": "Success Response",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [680, 300],
                "parameters": {
                    "responseBody": "={{ { 'success': true, 'message': 'ZohoCRM認証テスト成功', 'modules_count': $json.length, 'timestamp': $now.toISOString() } }}",
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
                            "node": "Success Response",
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
        response = requests.post(url, headers=headers, json=simple_auth_workflow, timeout=60)
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            workflow_id = result.get('id')
            
            if workflow_id:
                print(f"✅ シンプル認証ワークフロー作成成功: {workflow_id}")
                
                # アクティブ化
                activate_url = f"{N8N_BASE_URL}/api/v1/workflows/{workflow_id}/activate"
                activate_response = requests.post(activate_url, headers=headers, timeout=30)
                
                if activate_response.status_code == 200:
                    print("✅ シンプル認証ワークフローアクティブ化成功")
                    print(f"Webhook URL: {N8N_BASE_URL}/webhook/zoho-simple-auth")
                else:
                    print(f"❌ アクティブ化エラー: {activate_response.status_code}")
        else:
            print(f"❌ シンプル認証ワークフロー作成エラー: {response.status_code}")
            print(f"エラーレスポンス: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ リクエストエラー: {e}")

def get_existing_workflows():
    """既存のワークフロー一覧を取得"""
    
    # n8n設定
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    
    headers = {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("\n4. 既存のワークフロー一覧を確認中...")
    
    try:
        url = f"{N8N_BASE_URL}/api/v1/workflows"
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            workflows_data = response.json()
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
            print(f"❌ ワークフロー一覧取得エラー: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ ワークフロー一覧取得エラー: {e}")

def main():
    """メイン実行関数"""
    print("ZohoCRM認証ワークフロー作成ツール\n")
    
    # ZohoCRM認証ワークフローを作成
    create_zoho_auth_workflow()
    
    # シンプルな認証ワークフローを作成
    create_simple_auth_workflow()
    
    # 既存のワークフロー一覧を確認
    get_existing_workflows()
    
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

if __name__ == "__main__":
    main() 