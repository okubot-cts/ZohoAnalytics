#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプルなZohoCRM統合ワークフロー作成スクリプト
基本的なn8nノードのみ使用
"""

import requests
import json
import os
from datetime import datetime

def create_simple_zoho_workflow():
    """基本ノードのみを使用したZohoCRMワークフローを作成"""
    
    # n8n設定
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    
    headers = {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("=== シンプルZohoCRM統合ワークフロー作成 ===\n")
    
    # シンプルワークフロー定義（基本ノードのみ）
    workflow = {
        "name": "Zoho CRM - Simple Integration",
        "settings": {},
        "nodes": [
            # 1. Webhook トリガー
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "zoho-simple",
                    "options": {}
                },
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [240, 300],
                "id": "webhook-trigger",
                "name": "Webhook"
            },
            
            # 2. Set（リクエスト解析）
            {
                "parameters": {
                    "values": {
                        "string": [
                            {
                                "name": "action",
                                "value": "={{ $json.body.action || 'get_records' }}"
                            },
                            {
                                "name": "module",
                                "value": "={{ $json.body.module || 'Deals' }}"
                            },
                            {
                                "name": "limit",
                                "value": "={{ $json.body.limit || 100 }}"
                            },
                            {
                                "name": "timestamp",
                                "value": "={{ $now.toISOString() }}"
                            }
                        ]
                    }
                },
                "type": "n8n-nodes-base.set",
                "typeVersion": 1,
                "position": [460, 300],
                "id": "parse-request",
                "name": "Parse Request"
            },
            
            # 3. IF（アクション分岐）
            {
                "parameters": {
                    "conditions": {
                        "string": [
                            {
                                "value1": "={{ $json.action }}",
                                "operation": "equal",
                                "value2": "refresh_token"
                            }
                        ]
                    }
                },
                "type": "n8n-nodes-base.if",
                "typeVersion": 1,
                "position": [680, 300],
                "id": "check-action",
                "name": "Check Action"
            },
            
            # 4. HTTP Request（トークン更新）
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
                    "bodyContentType": "form-urlencoded",
                    "bodyParameters": {
                        "parameters": [
                            {
                                "name": "refresh_token",
                                "value": "1000.486e1e72a12e31310c1428d35112914e.af4d5c117f6008106f6b118e5fb61747"
                            },
                            {
                                "name": "client_id",
                                "value": "1000.YN0LA88XQRCDTARO3FO5PWCOEY2IFZ"
                            },
                            {
                                "name": "client_secret",
                                "value": "25549573ace167da7319c6b561a8ea477ca235e0ef"
                            },
                            {
                                "name": "grant_type",
                                "value": "refresh_token"
                            }
                        ]
                    }
                },
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 1,
                "position": [900, 200],
                "id": "refresh-token",
                "name": "Refresh Token"
            },
            
            # 5. HTTP Request（ZohoCRM API）
            {
                "parameters": {
                    "url": "=https://www.zohoapis.com/crm/v2/{{ $json.module }}",
                    "method": "GET",
                    "sendHeaders": True,
                    "headerParameters": {
                        "parameters": [
                            {
                                "name": "Authorization",
                                "value": "Zoho-oauthtoken 1000.f7cebcf43331706bec1653ec150e4956.86a18caddb092ba38c443fef26f4ca25"
                            }
                        ]
                    },
                    "sendQuery": True,
                    "queryParameters": {
                        "parameters": [
                            {
                                "name": "per_page",
                                "value": "={{ $json.limit }}"
                            }
                        ]
                    }
                },
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 1,
                "position": [900, 400],
                "id": "zoho-api",
                "name": "Zoho CRM API"
            },
            
            # 6. Set（レスポンス整形）
            {
                "parameters": {
                    "values": {
                        "string": [
                            {
                                "name": "success",
                                "value": "True"
                            },
                            {
                                "name": "action",
                                "value": "={{ $json.action }}"
                            },
                            {
                                "name": "timestamp",
                                "value": "={{ $now.toISOString() }}"
                            }
                        ],
                        "object": [
                            {
                                "name": "response_data",
                                "value": "={{ $json }}"
                            }
                        ]
                    }
                },
                "type": "n8n-nodes-base.set",
                "typeVersion": 1,
                "position": [1120, 300],
                "id": "format-response",
                "name": "Format Response"
            },
            
            # 7. Respond to Webhook
            {
                "parameters": {
                    "responseBody": "={{ JSON.stringify($json) }}",
                    "responseCode": 200
                },
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [1340, 300],
                "id": "respond",
                "name": "Respond"
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
                            "node": "Check Action",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Check Action": {
                "main": [
                    [
                        {
                            "node": "Refresh Token",
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
                    ]
                ]
            },
            "Refresh Token": {
                "main": [
                    [
                        {
                            "node": "Format Response",
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
                            "node": "Format Response",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Format Response": {
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
    
    print("📝 シンプルワークフロー定義を作成中...")
    
    try:
        # ワークフロー作成
        url = f"{N8N_BASE_URL}/api/v1/workflows"
        response = requests.post(url, headers=headers, json=workflow, timeout=60)
        
        print(f"レスポンスステータス: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ シンプルワークフロー作成成功")
            
            workflow_id = result.get('id')
            if workflow_id:
                print(f"ワークフローID: {workflow_id}")
                print(f"Webhook URL: {N8N_BASE_URL}/webhook/zoho-simple")
                
                # アクティブ化
                print("\n🚀 ワークフローをアクティブ化中...")
                activate_url = f"{N8N_BASE_URL}/api/v1/workflows/{workflow_id}/activate"
                activate_response = requests.post(activate_url, headers=headers, timeout=30)
                
                if activate_response.status_code == 200:
                    print("✅ ワークフローアクティブ化成功")
                    print("\n🎉 シンプルZohoCRM統合ワークフロー完成！")
                    
                    # 使用例を表示
                    print("\n📋 使用例:")
                    print("1. レコード取得:")
                    print(f'curl -X POST {N8N_BASE_URL}/webhook/zoho-simple \\')
                    print('  -H "Content-Type: application/json" \\')
                    print('  -d \'{"action": "get_records", "module": "Deals", "limit": 10}\'')
                    
                    print("\n2. トークン更新:")
                    print(f'curl -X POST {N8N_BASE_URL}/webhook/zoho-simple \\')
                    print('  -H "Content-Type: application/json" \\')
                    print('  -d \'{"action": "refresh_token"}\'')
                    
                else:
                    print(f"❌ アクティブ化エラー: {activate_response.status_code}")
                    print(f"レスポンス: {activate_response.text}")
        else:
            print(f"❌ ワークフロー作成エラー: {response.status_code}")
            print(f"エラーレスポンス: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ リクエストエラー: {e}")

def main():
    """メイン実行関数"""
    create_simple_zoho_workflow()

if __name__ == "__main__":
    main()