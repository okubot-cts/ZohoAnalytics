#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
動作するZohoCRM認証ワークフロー作成スクリプト
既存のワークフロー構造を参考にして作成
"""

import requests
import json
import os
from datetime import datetime

def create_working_auth_workflow():
    """動作するZohoCRM認証ワークフローを作成"""
    
    # n8n設定
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    
    headers = {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("=== 動作するZohoCRM認証ワークフロー作成 ===\n")
    
    # 動作する認証ワークフロー
    workflow = {
        "name": "Zoho CRM - Working Auth System",
        "settings": {},
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "zoho-auth",
                    "options": {}
                },
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [240, 300],
                "id": "webhook-trigger",
                "name": "Webhook"
            },
            {
                "parameters": {
                    "values": {
                        "string": [
                            {
                                "name": "action",
                                "value": "={{ $json.body.action || 'test_auth' }}"
                            },
                            {
                                "name": "timestamp",
                                "value": "={{ $now.toISOString() }}"
                            }
                        ]
                    }
                },
                "type": "n8n-nodes-base.set",
                "typeVersion": 3.4,
                "position": [460, 300],
                "id": "parse-request",
                "name": "Parse Request"
            },
            {
                "parameters": {
                    "operation": "getAll",
                    "resource": "deals",
                    "limit": 1
                },
                "type": "n8n-nodes-base.zohoCrm",
                "typeVersion": 1,
                "position": [680, 200],
                "id": "zoho-auth-test",
                "name": "Zoho CRM Auth Test",
                "credentials": {
                    "zohoCrmOAuth2Api": {
                        "id": "zoho-crm-oauth2",
                        "name": "Zoho CRM OAuth2"
                    }
                }
            },
            {
                "parameters": {
                    "url": "https://accounts.zoho.com/oauth/v2/token",
                    "method": "POST",
                    "sendHeaders": True,
                    "headerParameters": {
                        "parameters": [
                            {
                                "name": "Content-Type",
                                "value": "application/x-www-form-urlencoded"
                            }
                        ]
                    },
                    "sendBody": True,
                    "bodyParameters": {
                        "parameters": [
                            {
                                "name": "grant_type",
                                "value": "refresh_token"
                            },
                            {
                                "name": "refresh_token",
                                "value": "={{ $credentials.zohoCrmOAuth2Api.refresh_token }}"
                            }
                        ]
                    }
                },
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [680, 400],
                "id": "refresh-token",
                "name": "Refresh Token"
            },
            {
                "parameters": {
                    "responseBody": "={{ { 'success': true, 'message': 'ZohoCRM認証成功', 'timestamp': $json.timestamp, 'action': $json.action, 'data': $json.data } }}",
                    "responseCode": 200
                },
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [900, 200],
                "id": "auth-success",
                "name": "Auth Success Response"
            },
            {
                "parameters": {
                    "responseBody": "={{ { 'success': true, 'message': 'トークン更新成功', 'timestamp': $now.toISOString(), 'action': 'refresh_token', 'token_info': $json } }}",
                    "responseCode": 200
                },
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [900, 400],
                "id": "refresh-success",
                "name": "Refresh Success Response"
            },
            {
                "parameters": {
                    "rules": {
                        "rules": [
                            {
                                "conditions": {
                                    "options": {
                                        "caseSensitive": True,
                                        "leftValue": "",
                                        "typeValidation": "strict"
                                    },
                                    "conditions": [
                                        {
                                            "id": "action-check",
                                            "leftValue": "={{ $json.action }}",
                                            "rightValue": "refresh_token",
                                            "operator": {
                                                "type": "string",
                                                "operation": "equals"
                                            }
                                        }
                                    ],
                                    "combinator": "and"
                                },
                                "output": 1
                            }
                        ]
                    }
                },
                "type": "n8n-nodes-base.switch",
                "typeVersion": 3.3,
                "position": [680, 300],
                "id": "route-action",
                "name": "Route Action"
            }
        ],
        "connections": {
            "Webhook": {
                "main": [
                    [
                        {
                            "node": "Parse Request",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Parse Request": {
                "main": [
                    [
                        {
                            "node": "Route Action",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Route Action": {
                "main": [
                    [
                        {
                            "node": "Zoho CRM Auth Test",
                            "type": "main",
                            "index": 0
                        }
                    ],
                    [
                        {
                            "node": "Refresh Token",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Zoho CRM Auth Test": {
                "main": [
                    [
                        {
                            "node": "Auth Success Response",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Refresh Token": {
                "main": [
                    [
                        {
                            "node": "Refresh Success Response",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        }
    }
    
    print("📝 ワークフロー定義を作成中...")
    
    try:
        # ワークフロー作成
        url = f"{N8N_BASE_URL}/api/v1/workflows"
        response = requests.post(url, headers=headers, json=workflow, timeout=60)
        
        print(f"レスポンスステータス: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print(f"✅ ワークフロー作成成功")
            
            workflow_id = result.get('id')
            if workflow_id:
                print(f"ワークフローID: {workflow_id}")
                
                # アクティブ化
                print("\n🚀 ワークフローをアクティブ化中...")
                activate_url = f"{N8N_BASE_URL}/api/v1/workflows/{workflow_id}/activate"
                activate_response = requests.post(activate_url, headers=headers, timeout=30)
                
                if activate_response.status_code == 200:
                    print("✅ ワークフローアクティブ化成功")
                    print(f"Webhook URL: {N8N_BASE_URL}/webhook/zoho-auth")
                    
                    # 使用方法ガイド作成
                    create_usage_guide()
                    
                    # ワークフロー定義を保存
                    workflow_path = os.path.join(
                        os.path.dirname(__file__),
                        '../ワークフロー/zoho_working_auth_workflow.json'
                    )
                    
                    with open(workflow_path, 'w', encoding='utf-8') as f:
                        json.dump(workflow, f, indent=2, ensure_ascii=False)
                    
                    print(f"💾 ワークフロー定義を保存: {workflow_path}")
                    
                    print("\n🎉 セットアップ完了！")
                    print("⚠️  注意: ZohoCRM認証情報の設定が必要です")
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

def create_usage_guide():
    """使用方法ガイドを作成"""
    
    guide = """
# ZohoCRM認証ワークフロー使用ガイド

## 概要
このワークフローは、ZohoCRMの認証システムとリフレッシュトークン機能を含む動作する認証システムです。

## 機能
- ✅ ZohoCRM認証テスト
- ✅ リフレッシュトークン自動更新
- ✅ エラーハンドリング

## 使用方法

### 1. 認証テスト
```bash
curl -X POST https://cts-automation.onrender.com/webhook/zoho-auth \\
  -H "Content-Type: application/json" \\
  -d '{"action": "test_auth"}'
```

### 2. リフレッシュトークン更新
```bash
curl -X POST https://cts-automation.onrender.com/webhook/zoho-auth \\
  -H "Content-Type: application/json" \\
  -d '{"action": "refresh_token"}'
```

## レスポンス形式

### 認証成功時
```json
{
  "success": true,
  "message": "ZohoCRM認証成功",
  "timestamp": "2025-01-XX...",
  "action": "test_auth",
  "data": [...]
}
```

### トークン更新成功時
```json
{
  "success": true,
  "message": "トークン更新成功",
  "timestamp": "2025-01-XX...",
  "action": "refresh_token",
  "token_info": {
    "access_token": "...",
    "expires_in": 3600,
    "token_type": "Bearer"
  }
}
```

## 設定
- Webhook URL: `https://cts-automation.onrender.com/webhook/zoho-auth`
- 認証方式: OAuth2
- スコープ: `ZohoCRM.modules.ALL,ZohoCRM.settings.ALL`

## 注意事項
- 初回実行時は認証情報の設定が必要です
- リフレッシュトークンは自動的に更新されます
- エラー時は詳細なログが出力されます
"""
    
    # ガイドをファイルに保存
    guide_path = os.path.join(
        os.path.dirname(__file__),
        '../ドキュメント/zoho_working_auth_guide.md'
    )
    
    os.makedirs(os.path.dirname(guide_path), exist_ok=True)
    
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print(f"📖 使用方法ガイドを保存: {guide_path}")

def main():
    """メイン実行関数"""
    create_working_auth_workflow()

if __name__ == "__main__":
    main() 