#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ワークフローアクティブ化スクリプト
"""

import requests
import json

def activate_workflow():
    """ワークフローをアクティブ化"""
    
    # n8n設定
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    
    headers = {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("=== ワークフローアクティブ化 ===\n")
    
    # ZohoCRM認証ワークフローのID
    workflow_id = "fIXwjbTDkZVdMOel"
    
    try:
        # ワークフローをアクティブ化
        url = f"{N8N_BASE_URL}/api/v1/workflows/{workflow_id}/activate"
        response = requests.post(url, headers=headers, timeout=30)
        
        print(f"レスポンスステータス: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ ワークフローアクティブ化成功")
            print(f"Webhook URL: {N8N_BASE_URL}/webhook/zoho-auth")
            
            # テスト実行
            test_workflow()
        else:
            print(f"❌ アクティブ化エラー: {response.status_code}")
            print(f"レスポンス: {response.text}")
    
    except Exception as e:
        print(f"❌ エラー: {e}")

def test_workflow():
    """ワークフローをテスト"""
    
    # n8n設定
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
        
        print(f"レスポンスステータス: {response.status_code}")
        
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
            
            print(f"リフレッシュレスポンスステータス: {refresh_response.status_code}")
            
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
    activate_workflow()

if __name__ == "__main__":
    main() 