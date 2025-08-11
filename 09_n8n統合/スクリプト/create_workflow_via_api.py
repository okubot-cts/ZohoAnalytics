#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
n8n REST APIを使用してワークフローを作成するスクリプト
MCP経由でワークフロー作成を実現
"""

import requests
import json
import os
from datetime import datetime

class N8nWorkflowCreator:
    def __init__(self, base_url: str, api_key: str):
        """
        n8nワークフロー作成クラスの初期化
        
        Args:
            base_url (str): n8nインスタンスのベースURL
            api_key (str): n8nのAPIキー
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'X-N8N-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
    
    def create_workflow(self, workflow_data: dict) -> dict:
        """
        ワークフローを作成
        
        Args:
            workflow_data (dict): ワークフローデータ
        
        Returns:
            dict: 作成結果
        """
        url = f"{self.base_url}/api/v1/workflows"
        
        try:
            response = requests.post(url, headers=self.headers, json=workflow_data, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"ワークフロー作成エラー: {e}")
            return {"error": str(e)}
    
    def update_workflow(self, workflow_id: str, workflow_data: dict) -> dict:
        """
        既存のワークフローを更新
        
        Args:
            workflow_id (str): ワークフローID
            workflow_data (dict): 更新データ
        
        Returns:
            dict: 更新結果
        """
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}"
        
        try:
            response = requests.put(url, headers=self.headers, json=workflow_data, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"ワークフロー更新エラー: {e}")
            return {"error": str(e)}
    
    def activate_workflow(self, workflow_id: str) -> dict:
        """
        ワークフローをアクティブ化
        
        Args:
            workflow_id (str): ワークフローID
        
        Returns:
            dict: アクティブ化結果
        """
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}/activate"
        
        try:
            response = requests.post(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"ワークフローアクティブ化エラー: {e}")
            return {"error": str(e)}
    
    def get_workflow_by_name(self, name: str) -> dict:
        """
        名前でワークフローを検索
        
        Args:
            name (str): ワークフロー名
        
        Returns:
            dict: ワークフロー情報（見つからない場合はNone）
        """
        url = f"{self.base_url}/api/v1/workflows"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            workflows_data = response.json()
            workflows = workflows_data.get('data', workflows_data)
            
            if isinstance(workflows, list):
                for workflow in workflows:
                    if workflow.get('name') == name:
                        return workflow
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"ワークフロー検索エラー: {e}")
            return None

def load_workflow_template(template_path: str) -> dict:
    """ワークフローテンプレートを読み込み"""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"テンプレートファイルが見つかりません: {template_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"テンプレートファイルの形式が正しくありません: {e}")
        return {}

def create_zoho_crm_workflows():
    """ZohoCRMワークフローを作成"""
    
    # n8n設定
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    
    # ワークフロー作成インスタンスを初期化
    creator = N8nWorkflowCreator(N8N_BASE_URL, N8N_API_KEY)
    
    print("=== n8n ZohoCRMワークフロー作成 ===\n")
    
    # 1. 商談取得ワークフローを作成
    print("1. 商談取得ワークフローを作成中...")
    
    # テンプレートを読み込み
    template_path = os.path.join(
        os.path.dirname(__file__), 
        '../ワークフロー/zoho_crm_deals_workflow.json'
    )
    
    workflow_data = load_workflow_template(template_path)
    
    if not workflow_data:
        print("❌ テンプレートの読み込みに失敗しました")
        return
    
    # 既存のワークフローをチェック
    existing_workflow = creator.get_workflow_by_name(workflow_data['name'])
    
    if existing_workflow:
        print(f"既存のワークフローが見つかりました: {existing_workflow['id']}")
        
        # 更新するかどうか確認
        update_choice = input("既存のワークフローを更新しますか？ (y/n): ").strip().lower()
        
        if update_choice == 'y':
            print("ワークフローを更新中...")
            result = creator.update_workflow(existing_workflow['id'], workflow_data)
            
            if "error" not in result:
                print("✅ ワークフロー更新完了")
                
                # アクティブ化
                print("ワークフローをアクティブ化中...")
                activate_result = creator.activate_workflow(existing_workflow['id'])
                
                if "error" not in activate_result:
                    print("✅ ワークフローアクティブ化完了")
                else:
                    print(f"❌ アクティブ化エラー: {activate_result['error']}")
            else:
                print(f"❌ 更新エラー: {result['error']}")
        else:
            print("更新をスキップしました")
    else:
        # 新規作成
        print("新規ワークフローを作成中...")
        result = creator.create_workflow(workflow_data)
        
        if "error" not in result:
            workflow_id = result.get('id')
            print(f"✅ ワークフロー作成完了: {workflow_id}")
            
            # アクティブ化
            print("ワークフローをアクティブ化中...")
            activate_result = creator.activate_workflow(workflow_id)
            
            if "error" not in activate_result:
                print("✅ ワークフローアクティブ化完了")
                print(f"Webhook URL: {N8N_BASE_URL}/webhook/zoho-deals")
            else:
                print(f"❌ アクティブ化エラー: {activate_result['error']}")
        else:
            print(f"❌ 作成エラー: {result['error']}")
    
    # 2. 簡単なワークフローも作成（テスト用）
    print("\n2. テスト用ワークフローを作成中...")
    
    test_workflow = {
        "name": "Zoho CRM - Test Connection",
        "description": "ZohoCRM接続テスト用の簡単なワークフロー",
        "active": True,
        "nodes": [
            {
                "id": "webhook-test",
                "name": "Webhook Trigger",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [240, 300],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "zoho-test",
                    "responseMode": "responseNode"
                }
            },
            {
                "id": "respond-test",
                "name": "Test Response",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [460, 300],
                "parameters": {
                    "responseBody": "={{ { 'status': 'success', 'message': 'ZohoCRM connection test', 'timestamp': $now.toISOString() } }}",
                    "responseCode": 200
                }
            }
        ],
        "connections": {
            "Webhook Trigger": {
                "main": [
                    [
                        {
                            "node": "Test Response",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        }
    }
    
    # テストワークフローを作成
    test_result = creator.create_workflow(test_workflow)
    
    if "error" not in test_result:
        test_workflow_id = test_result.get('id')
        print(f"✅ テストワークフロー作成完了: {test_workflow_id}")
        
        # アクティブ化
        test_activate_result = creator.activate_workflow(test_workflow_id)
        
        if "error" not in test_activate_result:
            print("✅ テストワークフローアクティブ化完了")
            print(f"テストWebhook URL: {N8N_BASE_URL}/webhook/zoho-test")
        else:
            print(f"❌ テストワークフローアクティブ化エラー: {test_activate_result['error']}")
    else:
        print(f"❌ テストワークフロー作成エラー: {test_result['error']}")

def main():
    """メイン実行関数"""
    print("n8n ZohoCRMワークフロー作成ツール\n")
    
    # ワークフロー作成を実行
    create_zoho_crm_workflows()
    
    print("\n=== 作成完了 ===")
    print("次のステップ:")
    print("1. n8nダッシュボードでワークフローを確認")
    print("2. ZohoCRM認証情報を設定")
    print("3. 統合テストを実行")

if __name__ == "__main__":
    main() 