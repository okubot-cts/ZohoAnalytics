#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZohoCRM完全認証ワークフロー作成スクリプト
認証・リフレッシュトークン・エラーハンドリングを含む包括的なワークフロー
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, Optional

class ZohoCRMCompleteAuthWorkflow:
    def __init__(self):
        """初期化"""
        self.n8n_base_url = "https://cts-automation.onrender.com"
        self.n8n_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
        
        self.headers = {
            'X-N8N-API-KEY': self.n8n_api_key,
            'Content-Type': 'application/json'
        }
    
    def create_complete_auth_workflow(self) -> Dict:
        """完全なZohoCRM認証ワークフローを作成"""
        
        workflow = {
            "name": "Zoho CRM - Complete Authentication System",
            "description": "ZohoCRM認証・リフレッシュトークン・エラーハンドリングを含む完全な認証システム",
            "active": True,
            "settings": {
                "executionOrder": "v1"
            },
            "nodes": [
                # Webhookトリガー
                {
                    "id": "webhook-trigger",
                    "name": "Auth Webhook Trigger",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [240, 300],
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "zoho-auth",
                        "responseMode": "responseNode"
                    }
                },
                
                # リクエスト解析ノード
                {
                    "id": "parse-request",
                    "name": "Parse Request",
                    "type": "n8n-nodes-base.set",
                    "typeVersion": 3.4,
                    "position": [460, 300],
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
                    }
                },
                
                # 認証テストノード
                {
                    "id": "zoho-auth-test",
                    "name": "Zoho CRM Auth Test",
                    "type": "n8n-nodes-base.zohoCrm",
                    "typeVersion": 1,
                    "position": [680, 200],
                    "parameters": {
                        "operation": "getAll",
                        "resource": "deals",
                        "limit": 1
                    },
                    "credentials": {
                        "zohoCrmOAuth2Api": {
                            "id": "zoho-crm-oauth2",
                            "name": "Zoho CRM OAuth2"
                        }
                    }
                },
                
                # リフレッシュトークンノード
                {
                    "id": "refresh-token",
                    "name": "Refresh Token",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 4.2,
                    "position": [680, 400],
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
                    }
                },
                
                # 認証成功レスポンス
                {
                    "id": "auth-success",
                    "name": "Auth Success Response",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "typeVersion": 1,
                    "position": [900, 200],
                    "parameters": {
                        "responseBody": "={{ { 'success': true, 'message': 'ZohoCRM認証成功', 'timestamp': $json.timestamp, 'action': $json.action, 'data': $json.data } }}",
                        "responseCode": 200
                    }
                },
                
                # トークン更新成功レスポンス
                {
                    "id": "refresh-success",
                    "name": "Refresh Success Response",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "typeVersion": 1,
                    "position": [900, 400],
                    "parameters": {
                        "responseBody": "={{ { 'success': true, 'message': 'トークン更新成功', 'timestamp': $now.toISOString(), 'action': 'refresh_token', 'token_info': $json } }}",
                        "responseCode": 200
                    }
                },
                
                # エラーレスポンス
                {
                    "id": "error-response",
                    "name": "Error Response",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "typeVersion": 1,
                    "position": [900, 300],
                    "parameters": {
                        "responseBody": "={{ { 'success': false, 'message': '認証エラー', 'timestamp': $now.toISOString(), 'error': $json.error || 'Unknown error' } }}",
                        "responseCode": 400
                    }
                },
                
                # ルーティングノード
                {
                    "id": "route-action",
                    "name": "Route Action",
                    "type": "n8n-nodes-base.switch",
                    "typeVersion": 3.3,
                    "position": [680, 300],
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
                    }
                }
            ],
            "connections": {
                "Auth Webhook Trigger": {
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
        
        return workflow
    
    def create_credentials(self) -> Dict:
        """ZohoCRM OAuth2認証情報を作成"""
        
        credentials = {
            "name": "Zoho CRM OAuth2",
            "type": "zohoCrmOAuth2Api",
            "data": {
                "clientId": "1000.XXXXXXXXXX.XXXXXXXXXX",
                "clientSecret": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                "scope": "ZohoCRM.modules.ALL,ZohoCRM.settings.ALL",
                "authUrl": "https://accounts.zoho.com/oauth/v2/auth",
                "tokenUrl": "https://accounts.zoho.com/oauth/v2/token",
                "redirectUri": "https://www.zohoapis.com/oauth/v2/auth"
            }
        }
        
        return credentials
    
    def deploy_workflow(self, workflow: Dict) -> bool:
        """ワークフローをn8nにデプロイ"""
        
        try:
            url = f"{self.n8n_base_url}/api/v1/workflows"
            
            response = requests.post(
                url,
                headers=self.headers,
                json=workflow
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ ワークフロー作成成功: {result.get('name')}")
                print(f"   ID: {result.get('id')}")
                print(f"   Webhook URL: {self.n8n_base_url}/webhook/zoho-auth")
                return True
            else:
                print(f"❌ ワークフロー作成失敗: {response.status_code}")
                print(f"   エラー: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ デプロイエラー: {e}")
            return False
    
    def test_workflow(self) -> bool:
        """ワークフローをテスト"""
        
        try:
            # 認証テスト
            test_url = f"{self.n8n_base_url}/webhook/zoho-auth"
            test_data = {
                "action": "test_auth",
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                test_url,
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 認証テスト成功: {result.get('message')}")
                return True
            else:
                print(f"❌ 認証テスト失敗: {response.status_code}")
                print(f"   レスポンス: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ テストエラー: {e}")
            return False
    
    def create_usage_guide(self) -> str:
        """使用方法ガイドを作成"""
        
        guide = """
# ZohoCRM認証ワークフロー使用ガイド

## 概要
このワークフローは、ZohoCRMの認証システムとリフレッシュトークン機能を含む完全な認証システムです。

## 機能
- ✅ ZohoCRM認証テスト
- ✅ リフレッシュトークン自動更新
- ✅ エラーハンドリング
- ✅ 詳細なレスポンス

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

### 成功時
```json
{
  "success": true,
  "message": "ZohoCRM認証成功",
  "timestamp": "2025-01-XX...",
  "action": "test_auth",
  "data": {
    "deals_count": 1,
    "first_deal": {...}
  }
}
```

### エラー時
```json
{
  "success": false,
  "message": "認証エラー",
  "timestamp": "2025-01-XX...",
  "error": "エラー詳細"
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
        
        return guide

def main():
    """メイン実行関数"""
    
    print("=== ZohoCRM完全認証ワークフロー作成 ===\n")
    
    # ワークフロー作成
    creator = ZohoCRMCompleteAuthWorkflow()
    
    # ワークフロー定義作成
    print("📝 ワークフロー定義を作成中...")
    workflow = creator.create_complete_auth_workflow()
    
    # ワークフローデプロイ
    print("🚀 ワークフローをデプロイ中...")
    if creator.deploy_workflow(workflow):
        print("✅ デプロイ完了")
        
        # 使用方法ガイド作成
        guide = creator.create_usage_guide()
        
        # ガイドをファイルに保存
        guide_path = os.path.join(
            os.path.dirname(__file__),
            '../ドキュメント/zoho_auth_workflow_guide.md'
        )
        
        os.makedirs(os.path.dirname(guide_path), exist_ok=True)
        
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide)
        
        print(f"📖 使用方法ガイドを保存: {guide_path}")
        
        # ワークフロー定義を保存
        workflow_path = os.path.join(
            os.path.dirname(__file__),
            '../ワークフロー/zoho_complete_auth_workflow.json'
        )
        
        with open(workflow_path, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        
        print(f"💾 ワークフロー定義を保存: {workflow_path}")
        
        print("\n🎉 セットアップ完了！")
        print("Webhook URL: https://cts-automation.onrender.com/webhook/zoho-auth")
        
    else:
        print("❌ デプロイに失敗しました")

if __name__ == "__main__":
    main() 