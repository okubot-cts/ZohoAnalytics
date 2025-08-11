#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
既存のワークフローの詳細を取得して、正しい形式を確認するスクリプト
"""

import requests
import json

def get_workflow_details():
    """既存のワークフローの詳細を取得"""
    
    # n8n設定
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    
    headers = {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("=== 既存ワークフロー詳細取得 ===\n")
    
    # 1. ワークフロー一覧を取得
    print("1. ワークフロー一覧を取得中...")
    
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
                    print("\nZohoCRM関連のワークフロー:")
                    for i, workflow in enumerate(zoho_workflows, 1):
                        print(f"  {i}. {workflow.get('name')} (ID: {workflow.get('id')}, アクティブ: {workflow.get('active', False)})")
                    
                    # 最初のZohoCRMワークフローの詳細を取得
                    if zoho_workflows:
                        first_workflow = zoho_workflows[0]
                        workflow_id = first_workflow['id']
                        
                        print(f"\n2. ワークフロー詳細を取得中: {first_workflow['name']}")
                        
                        # ワークフロー詳細を取得
                        detail_url = f"{N8N_BASE_URL}/api/v1/workflows/{workflow_id}"
                        detail_response = requests.get(detail_url, headers=headers, timeout=30)
                        
                        if detail_response.status_code == 200:
                            workflow_detail = detail_response.json()
                            print("✅ ワークフロー詳細取得成功")
                            
                            # 重要なフィールドを表示
                            print(f"\nワークフロー詳細:")
                            print(f"  ID: {workflow_detail.get('id')}")
                            print(f"  名前: {workflow_detail.get('name')}")
                            print(f"  説明: {workflow_detail.get('description')}")
                            print(f"  アクティブ: {workflow_detail.get('active')}")
                            print(f"  設定: {workflow_detail.get('settings')}")
                            print(f"  ノード数: {len(workflow_detail.get('nodes', []))}")
                            
                            # ノードの詳細を表示
                            nodes = workflow_detail.get('nodes', [])
                            if nodes:
                                print(f"\nノード一覧:")
                                for i, node in enumerate(nodes[:5], 1):  # 最初の5個のみ表示
                                    print(f"  {i}. {node.get('name')} ({node.get('type')})")
                                    if node.get('credentials'):
                                        print(f"     認証情報: {list(node.get('credentials', {}).keys())}")
                            
                            # ワークフロー構造をファイルに保存
                            output_file = f"workflow_structure_{workflow_id}.json"
                            with open(output_file, 'w', encoding='utf-8') as f:
                                json.dump(workflow_detail, f, indent=2, ensure_ascii=False)
                            print(f"\n✅ ワークフロー構造を保存: {output_file}")
                            
                            # 正しいワークフロー作成形式を推測
                            print(f"\n3. 正しいワークフロー作成形式:")
                            correct_format = {
                                "name": "Test Workflow",
                                "description": "Test description",
                                "active": True,
                                "settings": workflow_detail.get('settings', {}),
                                "nodes": [
                                    {
                                        "id": "webhook-trigger",
                                        "name": "Webhook Trigger",
                                        "type": "n8n-nodes-base.webhook",
                                        "typeVersion": 1,
                                        "position": [240, 300],
                                        "parameters": {
                                            "httpMethod": "POST",
                                            "path": "test-webhook",
                                            "responseMode": "responseNode"
                                        }
                                    }
                                ],
                                "connections": {
                                    "Webhook Trigger": {
                                        "main": [
                                            [
                                                {
                                                    "node": "Webhook Trigger",
                                                    "type": "main",
                                                    "index": 0
                                                }
                                            ]
                                        ]
                                    }
                                }
                            }
                            
                            print(f"正しい形式の例:")
                            print(json.dumps(correct_format, indent=2, ensure_ascii=False))
                            
                        else:
                            print(f"❌ ワークフロー詳細取得エラー: {detail_response.status_code}")
                            print(f"エラーレスポンス: {detail_response.text}")
                    else:
                        print("ZohoCRM関連のワークフローは見つかりませんでした")
                else:
                    print("ZohoCRM関連のワークフローは見つかりませんでした")
            else:
                print(f"❌ ワークフロー詳細取得エラー: {response.status_code}")
                print(f"エラーレスポンス: {response.text}")
        else:
            print(f"❌ ワークフロー一覧取得エラー: {response.status_code}")
            print(f"エラーレスポンス: {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ リクエストエラー: {e}")

def main():
    """メイン実行関数"""
    print("既存ワークフロー詳細取得ツール\n")
    
    # ワークフロー詳細を取得
    get_workflow_details()
    
    print("\n=== 完了 ===")
    print("取得した情報を基に、正しい形式でワークフローを作成できます。")

if __name__ == "__main__":
    main() 