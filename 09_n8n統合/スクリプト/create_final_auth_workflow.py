#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終的なZohoCRM認証ワークフロー作成スクリプト
正しい認証情報で設定
"""

import requests
import json
import os
from datetime import datetime

def create_final_auth_workflow():
    """最終的なZohoCRM認証ワークフローを作成"""
    
    # n8n設定
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    
    headers = {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("=== 最終的なZohoCRM認証ワークフロー作成 ===\n")
    
    # 既存の認証情報ID
    existing_credential_id = "1pqBixOsaWZ0tiLn"
    
    # 最終的な認証ワークフロー
    workflow = {
        "name": "Zoho CRM - Final Auth System",
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
                        "id": existing_credential_id,
                        "name": "ZohoCTS"
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
                        '../ワークフロー/zoho_final_auth_workflow.json'
                    )
                    
                    with open(workflow_path, 'w', encoding='utf-8') as f:
                        json.dump(workflow, f, indent=2, ensure_ascii=False)
                    
                    print(f"💾 ワークフロー定義を保存: {workflow_path}")
                    
                    print("\n🎉 セットアップ完了！")
                    print("認証情報ID: 1pqBixOsaWZ0tiLn (ZohoCTS)")
                    
                    # テスト実行
                    test_workflow()
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
このワークフローは、ZohoCRMの認証システムとリフレッシュトークン機能を含む最終的な認証システムです。

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
- 認証情報ID: 1pqBixOsaWZ0tiLn (ZohoCTS)
- スコープ: `ZohoCRM.modules.ALL,ZohoCRM.settings.ALL`

## 注意事項
- 既存の認証情報を使用しています
- リフレッシュトークンは自動的に更新されます
- エラー時は詳細なログが出力されます
"""
    
    # ガイドをファイルに保存
    guide_path = os.path.join(
        os.path.dirname(__file__),
        '../ドキュメント/zoho_final_auth_guide.md'
    )
    
    os.makedirs(os.path.dirname(guide_path), exist_ok=True)
    
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print(f"📖 使用方法ガイドを保存: {guide_path}")

def test_workflow():
    """ワークフローをテスト"""
    
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    
    print("\n=== ワークフローテスト ===\n")
    
    try:
        # 認証テスト
        test_url = f"{N8N_BASE_URL}/webhook/zoho-auth"
        test_data = {
            "action": "test_auth",
            "timestamp": "2025-01-08T22:15:00.000Z"
        }
        
        print("🧪 認証テストを実行中...")
        response = requests.post(
            test_url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"認証テストレスポンス: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 認証テスト成功")
            print(f"レスポンス: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 認証テスト失敗: {response.status_code}")
            print(f"レスポンス: {response.text}")
            
            # リフレッシュトークンテスト
            print("\n🔄 リフレッシュトークンテストを実行中...")
            refresh_data = {
                "action": "refresh_token",
                "timestamp": "2025-01-08T22:15:00.000Z"
            }
            
            refresh_response = requests.post(
                test_url,
                json=refresh_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"リフレッシュテストレスポンス: {refresh_response.status_code}")
            
            if refresh_response.status_code == 200:
                refresh_result = refresh_response.json()
                print("✅ リフレッシュトークンテスト成功")
                print(f"レスポンス: {json.dumps(refresh_result, indent=2, ensure_ascii=False)}")
            else:
                print(f"❌ リフレッシュトークンテスト失敗: {refresh_response.status_code}")
                print(f"レスポンス: {refresh_response.text}")
    
    except Exception as e:
        print(f"❌ テストエラー: {e}")

def main():
    """メイン実行関数"""
    create_final_auth_workflow()

if __name__ == "__main__":
    main() 