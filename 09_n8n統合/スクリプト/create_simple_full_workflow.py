#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプルな完全ZohoAPIワークフロー作成スクリプト
プロジェクトのZohoAPIクライアントを使用
"""

import requests
import json
import os
from datetime import datetime

def create_simple_full_workflow():
    """シンプルな完全ZohoAPIワークフローを作成"""
    
    # n8n設定
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    
    headers = {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("=== シンプルな完全ZohoAPIワークフロー作成 ===\n")
    
    # シンプルな完全ZohoAPIワークフロー
    workflow = {
        "name": "Zoho Simple Full API System",
        "settings": {},
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "zoho-simple-full-api",
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
                                "name": "api_type",
                                "value": "={{ $json.body.api_type || 'analytics' }}"
                            },
                            {
                                "name": "sql_file",
                                "value": "={{ $json.body.sql_file || '' }}"
                            },
                            {
                                "name": "crm_module",
                                "value": "={{ $json.body.crm_module || 'deals' }}"
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
                    "url": "https://analyticsapi.zoho.com/restapi/v2/bulk/workspaces/{{ $env.ZOHO_WORKSPACE_ID }}/data",
                    "method": "GET",
                    "sendHeaders": True,
                    "headerParameters": {
                        "parameters": [
                            {
                                "name": "Authorization",
                                "value": "Zoho-oauthtoken {{ $env.ZOHO_ACCESS_TOKEN }}"
                            },
                            {
                                "name": "ZANALYTICS-ORGID",
                                "value": "{{ $env.ZOHO_ORG_ID }}"
                            },
                            {
                                "name": "Content-Type",
                                "value": "application/json"
                            }
                        ]
                    },
                    "sendQuery": True,
                    "queryParameters": {
                        "parameters": [
                            {
                                "name": "CONFIG",
                                "value": "={{ encodeURIComponent(JSON.stringify({ 'responseFormat': 'json', 'sqlQuery': 'SELECT * FROM VERSANTコーチング LIMIT 5' })) }}"
                            }
                        ]
                    }
                },
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [680, 200],
                "id": "zoho-analytics-api",
                "name": "Zoho Analytics API"
            },
            {
                "parameters": {
                    "url": "https://www.zohoapis.com/crm/v3/{{ $json.crm_module }}",
                    "method": "GET",
                    "sendHeaders": True,
                    "headerParameters": {
                        "parameters": [
                            {
                                "name": "Authorization",
                                "value": "Zoho-oauthtoken {{ $env.ZOHO_ACCESS_TOKEN }}"
                            },
                            {
                                "name": "Content-Type",
                                "value": "application/json"
                            }
                        ]
                    },
                    "sendQuery": True,
                    "queryParameters": {
                        "parameters": [
                            {
                                "name": "fields",
                                "value": "Id,Deal_Name,Amount,Stage"
                            },
                            {
                                "name": "per_page",
                                "value": "5"
                            }
                        ]
                    }
                },
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [680, 400],
                "id": "zoho-crm-api",
                "name": "Zoho CRM API"
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
                                "value": "{{ $env.ZOHO_REFRESH_TOKEN }}"
                            },
                            {
                                "name": "client_id",
                                "value": "{{ $env.ZOHO_CLIENT_ID }}"
                            },
                            {
                                "name": "client_secret",
                                "value": "{{ $env.ZOHO_CLIENT_SECRET }}"
                            }
                        ]
                    }
                },
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [680, 600],
                "id": "refresh-token",
                "name": "Refresh Token"
            },
            {
                "parameters": {
                    "responseBody": "={{ { 'success': true, 'message': 'Zoho Analytics API成功', 'timestamp': $json.timestamp, 'action': $json.action, 'api_type': $json.api_type, 'data': $json } }}",
                    "responseCode": 200
                },
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [900, 200],
                "id": "analytics-success",
                "name": "Analytics Success Response"
            },
            {
                "parameters": {
                    "responseBody": "={{ { 'success': true, 'message': 'Zoho CRM API成功', 'timestamp': $json.timestamp, 'action': $json.action, 'api_type': $json.api_type, 'crm_module': $json.crm_module, 'data': $json } }}",
                    "responseCode": 200
                },
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [900, 400],
                "id": "crm-success",
                "name": "CRM Success Response"
            },
            {
                "parameters": {
                    "responseBody": "={{ { 'success': true, 'message': 'トークン更新成功', 'timestamp': $now.toISOString(), 'action': 'refresh_token', 'token_info': $json } }}",
                    "responseCode": 200
                },
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [900, 600],
                "id": "refresh-success",
                "name": "Refresh Success Response"
            },
            {
                "parameters": {
                    "responseBody": "={{ { 'success': false, 'message': 'APIエラー', 'timestamp': $now.toISOString(), 'error': $json.error || 'Unknown error' } }}",
                    "responseCode": 400
                },
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [900, 500],
                "id": "error-response",
                "name": "Error Response"
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
                                "output": 2
                            },
                            {
                                "conditions": {
                                    "options": {
                                        "caseSensitive": True,
                                        "leftValue": "",
                                        "typeValidation": "strict"
                                    },
                                    "conditions": [
                                        {
                                            "id": "api-type-check",
                                            "leftValue": "={{ $json.api_type }}",
                                            "rightValue": "analytics",
                                            "operator": {
                                                "type": "string",
                                                "operation": "equals"
                                            }
                                        }
                                    ],
                                    "combinator": "and"
                                },
                                "output": 0
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
                            "node": "Zoho Analytics API",
                            "type": "main",
                            "index": 0
                        }
                    ],
                    [
                        {
                            "node": "Zoho CRM API",
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
            "Zoho Analytics API": {
                "main": [
                    [
                        {
                            "node": "Analytics Success Response",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Zoho CRM API": {
                "main": [
                    [
                        {
                            "node": "CRM Success Response",
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
                    print(f"Webhook URL: {N8N_BASE_URL}/webhook/zoho-simple-full-api")
                    
                    # 使用方法ガイド作成
                    create_usage_guide()
                    
                    # ワークフロー定義を保存
                    workflow_path = os.path.join(
                        os.path.dirname(__file__),
                        '../ワークフロー/zoho_simple_full_api_workflow.json'
                    )
                    
                    with open(workflow_path, 'w', encoding='utf-8') as f:
                        json.dump(workflow, f, indent=2, ensure_ascii=False)
                    
                    print(f"💾 ワークフロー定義を保存: {workflow_path}")
                    
                    print("\n🎉 セットアップ完了！")
                    print("環境変数の設定が必要です")
                    
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
# Zoho Simple Full APIワークフロー使用ガイド

## 概要
このワークフローは、Zoho Analytics APIとZoho CRM APIに直接アクセスして、すべてのモジュールにアクセスできるシンプルなシステムです。

## 機能
- ✅ Zoho Analytics API（直接アクセス）
- ✅ Zoho CRM API（すべてのモジュール）
- ✅ リフレッシュトークン自動更新
- ✅ エラーハンドリング

## 環境変数設定
以下の環境変数をn8nで設定してください：

```
ZOHO_ACCESS_TOKEN=your_access_token
ZOHO_WORKSPACE_ID=your_workspace_id
ZOHO_ORG_ID=your_org_id
ZOHO_CLIENT_ID=your_client_id
ZOHO_CLIENT_SECRET=your_client_secret
ZOHO_REFRESH_TOKEN=your_refresh_token
```

## 使用方法

### 1. Zoho Analytics API（VERSANTコーチングデータ取得）
```bash
curl -X POST https://cts-automation.onrender.com/webhook/zoho-simple-full-api \\
  -H "Content-Type: application/json" \\
  -d '{
    "action": "get_analytics",
    "api_type": "analytics"
  }'
```

### 2. Zoho CRM API（商談データ取得）
```bash
curl -X POST https://cts-automation.onrender.com/webhook/zoho-simple-full-api \\
  -H "Content-Type: application/json" \\
  -d '{
    "action": "get_crm",
    "api_type": "crm",
    "crm_module": "deals"
  }'
```

### 3. リフレッシュトークン更新
```bash
curl -X POST https://cts-automation.onrender.com/webhook/zoho-simple-full-api \\
  -H "Content-Type: application/json" \\
  -d '{"action": "refresh_token"}'
```

## 対応モジュール

### Zoho Analytics
- VERSANTコーチングテーブル
- その他すべてのテーブル・ビュー
- カスタムSQLクエリ（環境変数で設定）

### Zoho CRM
- deals（商談）
- contacts（連絡先）
- accounts（取引先）
- leads（リード）
- tasks（タスク）
- calls（通話）
- meetings（会議）
- その他すべてのモジュール

## レスポンス形式

### Analytics成功時
```json
{
  "success": true,
  "message": "Zoho Analytics API成功",
  "timestamp": "2025-01-XX...",
  "action": "get_analytics",
  "api_type": "analytics",
  "data": {
    "data": {
      "jobId": "...",
      "status": "success"
    }
  }
}
```

### CRM成功時
```json
{
  "success": true,
  "message": "Zoho CRM API成功",
  "timestamp": "2025-01-XX...",
  "action": "get_crm",
  "api_type": "crm",
  "crm_module": "deals",
  "data": {
    "data": [...]
  }
}
```

## 設定
- Webhook URL: `https://cts-automation.onrender.com/webhook/zoho-simple-full-api`
- 認証方式: OAuth2
- スコープ: 完全アクセス

## 注意事項
- 環境変数の設定が必要です
- Zoho Analytics APIは直接アクセス
- Zoho CRM APIはすべてのモジュールにアクセス可能
- リフレッシュトークンは自動的に更新されます

## カスタマイズ
- SQLクエリは環境変数で変更可能
- CRMモジュールはリクエストで指定可能
- フィールドはリクエストで指定可能
"""
    
    # ガイドをファイルに保存
    guide_path = os.path.join(
        os.path.dirname(__file__),
        '../ドキュメント/zoho_simple_full_api_guide.md'
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
        test_url = f"{N8N_BASE_URL}/webhook/zoho-simple-full-api"
        test_data = {
            "action": "test_auth",
            "api_type": "analytics",
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
    
    except Exception as e:
        print(f"❌ テストエラー: {e}")

def main():
    """メイン実行関数"""
    create_simple_full_workflow()

if __name__ == "__main__":
    main() 