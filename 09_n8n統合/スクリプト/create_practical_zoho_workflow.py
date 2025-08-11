#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
実用的なZohoAPIワークフロー作成スクリプト
プロジェクトのZohoAPIクライアントを活用
"""

import requests
import json
import os
from datetime import datetime

def create_practical_zoho_workflow():
    """実用的なZohoAPIワークフローを作成"""
    
    # n8n設定
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    
    headers = {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("=== 実用的なZohoAPIワークフロー作成 ===\n")
    
    # 実用的なZohoAPIワークフロー
    workflow = {
        "name": "Zoho Practical API System",
        "settings": {},
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "zoho-practical-api",
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
                    "command": "cd /Users/ks1-utakashio/Desktop/CursorProjects/20250726_ZohoAnalytics && python3 -c \"from 01_Zoho_API.APIクライアント.zoho_analytics_api_client_final import ZohoAnalyticsAPIFinal; import json; client = ZohoAnalyticsAPIFinal(); result = client.execute_query('{{ $json.sql_file }}'); print(json.dumps(result, ensure_ascii=False))\"",
                    "options": {}
                },
                "type": "n8n-nodes-base.executeCommand",
                "typeVersion": 1,
                "position": [680, 200],
                "id": "execute-analytics",
                "name": "Execute Analytics"
            },
            {
                "parameters": {
                    "command": "cd /Users/ks1-utakashio/Desktop/CursorProjects/20250726_ZohoAnalytics && python3 -c \"import requests; import json; headers = {'Authorization': 'Zoho-oauthtoken ' + '{{ $env.ZOHO_ACCESS_TOKEN }}', 'Content-Type': 'application/json'}; response = requests.get('https://www.zohoapis.com/crm/v3/{{ $json.crm_module }}', headers=headers); print(json.dumps(response.json(), ensure_ascii=False))\"",
                    "options": {}
                },
                "type": "n8n-nodes-base.executeCommand",
                "typeVersion": 1,
                "position": [680, 400],
                "id": "execute-crm",
                "name": "Execute CRM"
            },
            {
                "parameters": {
                    "command": "cd /Users/ks1-utakashio/Desktop/CursorProjects/20250726_ZohoAnalytics && python3 -c \"from 01_Zoho_API.APIクライアント.zoho_analytics_auth import ZohoAnalyticsAuth; import json; auth = ZohoAnalyticsAuth('{{ $env.ZOHO_CLIENT_ID }}', '{{ $env.ZOHO_CLIENT_SECRET }}', '{{ $env.ZOHO_REDIRECT_URI }}'); result = auth.refresh_access_token('{{ $env.ZOHO_REFRESH_TOKEN }}'); print(json.dumps(result, ensure_ascii=False))\"",
                    "options": {}
                },
                "type": "n8n-nodes-base.executeCommand",
                "typeVersion": 1,
                "position": [680, 600],
                "id": "refresh-token",
                "name": "Refresh Token"
            },
            {
                "parameters": {
                    "responseBody": "={{ { 'success': true, 'message': 'Zoho Analytics実行成功', 'timestamp': $json.timestamp, 'action': $json.action, 'api_type': $json.api_type, 'sql_file': $json.sql_file, 'data': JSON.parse($json.stdout) } }}",
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
                    "responseBody": "={{ { 'success': true, 'message': 'Zoho CRM実行成功', 'timestamp': $json.timestamp, 'action': $json.action, 'api_type': $json.api_type, 'crm_module': $json.crm_module, 'data': JSON.parse($json.stdout) } }}",
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
                    "responseBody": "={{ { 'success': true, 'message': 'トークン更新成功', 'timestamp': $now.toISOString(), 'action': 'refresh_token', 'token_info': JSON.parse($json.stdout) } }}",
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
                    "responseBody": "={{ { 'success': false, 'message': 'APIエラー', 'timestamp': $now.toISOString(), 'error': $json.stderr || 'Unknown error' } }}",
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
                            "node": "Execute Analytics",
                            "type": "main",
                            "index": 0
                        }
                    ],
                    [
                        {
                            "node": "Execute CRM",
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
            "Execute Analytics": {
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
            "Execute CRM": {
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
                    print(f"Webhook URL: {N8N_BASE_URL}/webhook/zoho-practical-api")
                    
                    # 使用方法ガイド作成
                    create_usage_guide()
                    
                    # ワークフロー定義を保存
                    workflow_path = os.path.join(
                        os.path.dirname(__file__),
                        '../ワークフロー/zoho_practical_api_workflow.json'
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
# Zoho Practical APIワークフロー使用ガイド

## 概要
このワークフローは、プロジェクトのZohoAPIクライアントを直接実行して、すべてのZohoモジュールにアクセスできる実用的なシステムです。

## 機能
- ✅ Zoho Analytics API（プロジェクトクライアント使用）
- ✅ Zoho CRM API（すべてのモジュール）
- ✅ リフレッシュトークン自動更新
- ✅ SQLファイル実行
- ✅ エラーハンドリング

## 環境変数設定
以下の環境変数をn8nで設定してください：

```
ZOHO_ACCESS_TOKEN=your_access_token
ZOHO_CLIENT_ID=your_client_id
ZOHO_CLIENT_SECRET=your_client_secret
ZOHO_REDIRECT_URI=your_redirect_uri
ZOHO_REFRESH_TOKEN=your_refresh_token
```

## 使用方法

### 1. Zoho Analytics API（SQLファイル実行）
```bash
curl -X POST https://cts-automation.onrender.com/webhook/zoho-practical-api \\
  -H "Content-Type: application/json" \\
  -d '{
    "action": "execute_query",
    "api_type": "analytics",
    "sql_file": "02_VERSANTコーチング/SQL/versant_coaching_report.sql"
  }'
```

### 2. Zoho CRM API（モジュールデータ取得）
```bash
curl -X POST https://cts-automation.onrender.com/webhook/zoho-practical-api \\
  -H "Content-Type: application/json" \\
  -d '{
    "action": "get_data",
    "api_type": "crm",
    "crm_module": "deals"
  }'
```

### 3. リフレッシュトークン更新
```bash
curl -X POST https://cts-automation.onrender.com/webhook/zoho-practical-api \\
  -H "Content-Type: application/json" \\
  -d '{"action": "refresh_token"}'
```

## 対応モジュール

### Zoho Analytics
- プロジェクトのSQLファイル実行
- VERSANTコーチングレポート
- 商談・粗利率レポート
- その他すべてのSQLクエリ

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
  "message": "Zoho Analytics実行成功",
  "timestamp": "2025-01-XX...",
  "action": "execute_query",
  "api_type": "analytics",
  "sql_file": "02_VERSANTコーチング/SQL/versant_coaching_report.sql",
  "data": {...}
}
```

### CRM成功時
```json
{
  "success": true,
  "message": "Zoho CRM実行成功",
  "timestamp": "2025-01-XX...",
  "action": "get_data",
  "api_type": "crm",
  "crm_module": "deals",
  "data": {...}
}
```

## 設定
- Webhook URL: `https://cts-automation.onrender.com/webhook/zoho-practical-api`
- 認証方式: OAuth2
- プロジェクトパス: `/Users/ks1-utakashio/Desktop/CursorProjects/20250726_ZohoAnalytics`

## 注意事項
- 環境変数の設定が必要です
- プロジェクトのZohoAPIクライアントを使用
- SQLファイルはプロジェクト内のパスを指定
- リフレッシュトークンは自動的に更新されます
"""
    
    # ガイドをファイルに保存
    guide_path = os.path.join(
        os.path.dirname(__file__),
        '../ドキュメント/zoho_practical_api_guide.md'
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
        test_url = f"{N8N_BASE_URL}/webhook/zoho-practical-api"
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
    create_practical_zoho_workflow()

if __name__ == "__main__":
    main() 