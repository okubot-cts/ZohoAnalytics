#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
n8n認証情報タイプ確認スクリプト
"""

import requests
import json

def check_credentials():
    """認証情報を確認"""
    
    # n8n設定
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    
    headers = {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("=== n8n認証情報確認 ===\n")
    
    try:
        # 認証情報一覧を取得
        url = f"{N8N_BASE_URL}/api/v1/credentials"
        response = requests.get(url, headers=headers)
        
        print(f"レスポンスステータス: {response.status_code}")
        
        if response.status_code == 200:
            credentials = response.json()
            print(f"✅ 認証情報取得成功")
            print(f"認証情報数: {len(credentials)}")
            
            for i, cred in enumerate(credentials):
                print(f"\n--- 認証情報 {i+1} ---")
                print(f"ID: {cred.get('id')}")
                print(f"名前: {cred.get('name')}")
                print(f"タイプ: {cred.get('type')}")
                print(f"作成日: {cred.get('createdAt')}")
                
                # データ構造を確認
                if 'data' in cred:
                    print(f"データキー: {list(cred['data'].keys())}")
                else:
                    print("データ: なし")
        else:
            print(f"❌ 認証情報取得失敗: {response.status_code}")
            print(f"エラーレスポンス: {response.text}")
    
    except Exception as e:
        print(f"❌ エラー: {e}")

def check_workflows():
    """ワークフローを確認"""
    
    # n8n設定
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    
    headers = {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("\n=== n8nワークフロー確認 ===\n")
    
    try:
        # ワークフロー一覧を取得
        url = f"{N8N_BASE_URL}/api/v1/workflows"
        response = requests.get(url, headers=headers)
        
        print(f"レスポンスステータス: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ ワークフロー取得成功")
            
            if isinstance(result, dict) and 'data' in result:
                workflows = result['data']
                print(f"ワークフロー数: {len(workflows)}")
                
                for i, workflow in enumerate(workflows):
                    if isinstance(workflow, dict):
                        print(f"\n--- ワークフロー {i+1} ---")
                        print(f"ID: {workflow.get('id')}")
                        print(f"名前: {workflow.get('name')}")
                        print(f"アクティブ: {workflow.get('active')}")
                        print(f"作成日: {workflow.get('createdAt')}")
                        
                        # ノード情報を確認
                        nodes = workflow.get('nodes', [])
                        print(f"ノード数: {len(nodes)}")
                        
                        for j, node in enumerate(nodes):
                            if node.get('type') == 'n8n-nodes-base.zohoCrm':
                                print(f"  ZohoCRMノード {j+1}: {node.get('name')}")
                                if 'credentials' in node:
                                    print(f"    認証情報: {node['credentials']}")
                    else:
                        print(f"ワークフロー {i+1}: {workflow}")
            else:
                print(f"レスポンス形式: {result}")
        else:
            print(f"❌ ワークフロー取得失敗: {response.status_code}")
            print(f"エラーレスポンス: {response.text}")
    
    except Exception as e:
        print(f"❌ エラー: {e}")

def main():
    """メイン実行関数"""
    check_credentials()
    check_workflows()

if __name__ == "__main__":
    main() 