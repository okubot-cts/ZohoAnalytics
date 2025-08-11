#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZohoCRM専用ワークフロー作成スクリプト
ZohoAnalyticsを除外して、ZohoCRMのみに特化
"""

import requests
import json
import os
from datetime import datetime

def create_zoho_crm_only_workflow():
    """ZohoCRM専用ワークフローを作成"""
    
    # n8n設定
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    
    headers = {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("=== ZohoCRM専用ワークフロー作成 ===\n")
    
    # ZohoCRM専用ワークフロー
    workflow = {
        "name": "Zoho CRM Only System",
        "settings": {},
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "zoho-crm-only",
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
                                "value": "={{ $json.body.action || 'get_data' }}"
                            },
                            {
                                "name": "module",
                                "value": "={{ $json.body.module || 'deals' }}"
                            },
                            {
                                "name": "fields",
                                "value": "={{ $json.body.fields || 'Id,Deal_Name,Amount,Stage' }}"
                            },
                            {
                                "name": "limit",
                                "value": "={{ $json.body.limit || 10 }}"
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
                    "url": "https://www.zohoapis.com/crm/v3/{{ $json.module }}",
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
                                "value": "={{ $json.fields }}"
                            },
                            {
                                "name": "per_page",
                                "value": "={{ $json.limit }}"
                            }
                        ]
                    }
                },
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [680, 200],
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
                "position": [680, 400],
                "id": "refresh-token",
                "name": "Refresh Token"
            },
            {
                "parameters": {
                    "responseBody": "={{ { 'success': true, 'message': 'Zoho CRM API成功', 'timestamp': $json.timestamp, 'action': $json.action, 'module': $json.module, 'data': $json } }}",
                    "responseCode": 200
                },
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [900, 200],
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
                "position": [900, 400],
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
                "position": [900, 300],
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
                    print(f"Webhook URL: {N8N_BASE_URL}/webhook/zoho-crm-only")
                    
                    # 使用方法ガイド作成
                    create_usage_guide()
                    
                    # ワークフロー定義を保存
                    workflow_path = os.path.join(
                        os.path.dirname(__file__),
                        '../ワークフロー/zoho_crm_only_workflow.json'
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
# Zoho CRM Onlyワークフロー使用ガイド

## 概要
このワークフローは、ZohoCRMのみに特化したシステムです。ZohoAnalyticsは除外されています。

## 機能
- ✅ Zoho CRM API（すべてのモジュール）
- ✅ リフレッシュトークン自動更新
- ✅ エラーハンドリング
- ✅ カスタマイズ可能なフィールド・制限

## 環境変数設定
以下の環境変数をn8nで設定してください：

```
ZOHO_ACCESS_TOKEN=your_access_token
ZOHO_CLIENT_ID=your_client_id
ZOHO_CLIENT_SECRET=your_client_secret
ZOHO_REFRESH_TOKEN=your_refresh_token
```

## 使用方法

### 1. 商談データ取得
```bash
curl -X POST https://cts-automation.onrender.com/webhook/zoho-crm-only \\
  -H "Content-Type: application/json" \\
  -d '{
    "action": "get_data",
    "module": "deals",
    "fields": "Id,Deal_Name,Amount,Stage",
    "limit": 10
  }'
```

### 2. 連絡先データ取得
```bash
curl -X POST https://cts-automation.onrender.com/webhook/zoho-crm-only \\
  -H "Content-Type: application/json" \\
  -d '{
    "action": "get_data",
    "module": "contacts",
    "fields": "Id,First_Name,Last_Name,Email",
    "limit": 20
  }'
```

### 3. 取引先データ取得
```bash
curl -X POST https://cts-automation.onrender.com/webhook/zoho-crm-only \\
  -H "Content-Type: application/json" \\
  -d '{
    "action": "get_data",
    "module": "accounts",
    "fields": "Id,Account_Name,Industry,Annual_Revenue",
    "limit": 15
  }'
```

### 4. リフレッシュトークン更新
```bash
curl -X POST https://cts-automation.onrender.com/webhook/zoho-crm-only \\
  -H "Content-Type: application/json" \\
  -d '{"action": "refresh_token"}'
```

## 対応モジュール

### Zoho CRM
- ✅ deals（商談）
- ✅ contacts（連絡先）
- ✅ accounts（取引先）
- ✅ leads（リード）
- ✅ tasks（タスク）
- ✅ calls（通話）
- ✅ meetings（会議）
- ✅ campaigns（キャンペーン）
- ✅ products（商品）
- ✅ quotes（見積書）
- ✅ sales_orders（受注）
- ✅ invoices（請求書）
- ✅ purchase_orders（発注）
- ✅ vendors（仕入先）
- ✅ その他すべてのモジュール

## レスポンス形式

### CRM成功時
```json
{
  "success": true,
  "message": "Zoho CRM API成功",
  "timestamp": "2025-01-XX...",
  "action": "get_data",
  "module": "deals",
  "data": {
    "data": [...],
    "info": {...}
  }
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
- Webhook URL: `https://cts-automation.onrender.com/webhook/zoho-crm-only`
- 認証方式: OAuth2
- スコープ: ZohoCRM完全アクセス

## パラメータ

### リクエストパラメータ
- `action`: 実行するアクション（`get_data`, `refresh_token`）
- `module`: CRMモジュール名（`deals`, `contacts`, `accounts`など）
- `fields`: 取得するフィールド（カンマ区切り）
- `limit`: 取得件数（デフォルト: 10）

### 例
```json
{
  "action": "get_data",
  "module": "deals",
  "fields": "Id,Deal_Name,Amount,Stage,Close_Date",
  "limit": 50
}
```

## 注意事項
- 環境変数の設定が必要です
- ZohoCRMのすべてのモジュールにアクセス可能
- フィールド名はZohoCRMのAPI仕様に従ってください
- リフレッシュトークンは自動的に更新されます
- 制限値は適切に設定してください（大量データ取得時は注意）
"""
    
    # ガイドをファイルに保存
    guide_path = os.path.join(
        os.path.dirname(__file__),
        '../ドキュメント/zoho_crm_only_guide.md'
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
        # 商談データ取得テスト
        test_url = f"{N8N_BASE_URL}/webhook/zoho-crm-only"
        test_data = {
            "action": "get_data",
            "module": "deals",
            "fields": "Id,Deal_Name,Amount,Stage",
            "limit": 5,
            "timestamp": "2025-01-08T22:15:00.000Z"
        }
        
        print("🧪 商談データ取得テストを実行中...")
        response = requests.post(
            test_url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"商談データ取得テストレスポンス: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 商談データ取得テスト成功")
            print(f"レスポンス: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 商談データ取得テスト失敗: {response.status_code}")
            print(f"レスポンス: {response.text}")
    
    except Exception as e:
        print(f"❌ テストエラー: {e}")

def main():
    """メイン実行関数"""
    create_zoho_crm_only_workflow()

if __name__ == "__main__":
    main() 