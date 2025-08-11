#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ワークフロー認証情報更新スクリプト
既存の認証情報を使用するようにワークフローを更新
"""

import requests
import json

def update_workflow_credentials():
    """ワークフローの認証情報を更新"""
    
    # n8n設定
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    
    headers = {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("=== ワークフロー認証情報更新 ===\n")
    
    # ZohoCRM認証ワークフローのID
    workflow_id = "fIXwjbTDkZVdMOel"
    
    try:
        # 現在のワークフローを取得
        url = f"{N8N_BASE_URL}/api/v1/workflows/{workflow_id}"
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"ワークフロー取得レスポンス: {response.status_code}")
        
        if response.status_code == 200:
            workflow = response.json()
            print("✅ ワークフロー取得成功")
            
            # 既存の認証情報IDを使用
            existing_credential_id = "1pqBixOsaWZ0tiLn"  # 既存のZohoCRM認証情報
            
            # ノードの認証情報を更新
            nodes = workflow.get('nodes', [])
            updated = False
            
            for node in nodes:
                if node.get('type') == 'n8n-nodes-base.zohoCrm':
                    if 'credentials' in node:
                        node['credentials']['zohoCrmOAuth2Api']['id'] = existing_credential_id
                        node['credentials']['zohoCrmOAuth2Api']['name'] = 'ZohoCTS'
                        updated = True
                        print(f"✅ ノード '{node.get('name')}' の認証情報を更新")
            
            if updated:
                # 不要なプロパティを削除
                if 'createdAt' in workflow:
                    del workflow['createdAt']
                if 'updatedAt' in workflow:
                    del workflow['updatedAt']
                if 'id' in workflow:
                    del workflow['id']
                
                # ワークフローを更新
                update_url = f"{N8N_BASE_URL}/api/v1/workflows/{workflow_id}"
                update_response = requests.put(update_url, headers=headers, json=workflow, timeout=30)
                
                print(f"ワークフロー更新レスポンス: {update_response.status_code}")
                
                if update_response.status_code == 200:
                    print("✅ ワークフロー更新成功")
                    
                    # アクティブ化を試行
                    activate_workflow(workflow_id, headers)
                else:
                    print(f"❌ ワークフロー更新失敗: {update_response.status_code}")
                    print(f"レスポンス: {update_response.text}")
            else:
                print("⚠️  更新対象のノードが見つかりませんでした")
        else:
            print(f"❌ ワークフロー取得失敗: {response.status_code}")
            print(f"レスポンス: {response.text}")
    
    except Exception as e:
        print(f"❌ エラー: {e}")

def activate_workflow(workflow_id, headers):
    """ワークフローをアクティブ化"""
    
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    
    try:
        # ワークフローをアクティブ化
        url = f"{N8N_BASE_URL}/api/v1/workflows/{workflow_id}/activate"
        response = requests.post(url, headers=headers, timeout=30)
        
        print(f"アクティブ化レスポンス: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ ワークフローアクティブ化成功")
            print(f"Webhook URL: {N8N_BASE_URL}/webhook/zoho-auth")
            
            # テスト実行
            test_workflow()
        else:
            print(f"❌ アクティブ化エラー: {response.status_code}")
            print(f"レスポンス: {response.text}")
    
    except Exception as e:
        print(f"❌ アクティブ化エラー: {e}")

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
    update_workflow_credentials()

if __name__ == "__main__":
    main() 