#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接クエリ実行テスト
"""

import requests
import json
import os
from datetime import datetime

def test_direct_query():
    """
    直接クエリ実行をテスト
    """
    print("=== 直接クエリ実行テスト ===")
    
    # 環境変数の確認
    access_token = os.getenv('ZOHO_ANALYTICS_ACCESS_TOKEN')
    workspace_id = os.getenv('ZOHO_ANALYTICS_WORKSPACE_ID')
    
    if not access_token:
        print("❌ ZOHO_ANALYTICS_ACCESS_TOKEN が設定されていません")
        return
    
    if not workspace_id:
        print("❌ ZOHO_ANALYTICS_WORKSPACE_ID が設定されていません")
        return
    
    print("✅ 環境変数が設定されています")
    print(f"   アクセストークン: {access_token[:10]}...")
    print(f"   ワークスペースID: {workspace_id}")
    
    # ヘッダー設定
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json'
    }
    
    # テスト用のシンプルなクエリ
    test_query = '''
    SELECT 
        c."Id" as "受講生ID",
        CONCAT(c."姓", ' ', c."名") as "受講生名"
    FROM "連絡先" c
    LIMIT 5
    '''
    
    # 複数のエンドポイントを試す
    endpoints = [
        f"https://analyticsapi.zoho.com/api/v2/{workspace_id}/query",
        f"https://www.zohoapis.com/analytics/v2/{workspace_id}/query",
        f"https://analytics.zoho.com/api/v2/{workspace_id}/query"
    ]
    
    for i, endpoint in enumerate(endpoints, 1):
        print(f"\n🔍 エンドポイント {i} をテスト中: {endpoint}")
        
        payload = {
            "query": test_query,
            "output_format": "json"
        }
        
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            print(f"   ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ 成功! レスポンス: {result}")
                return True
            else:
                print(f"   ❌ 失敗: {response.status_code}")
                print(f"   レスポンス: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ エラー: {e}")
    
    return False

def test_workspace_endpoints():
    """
    ワークスペースエンドポイントをテスト
    """
    print("\n=== ワークスペースエンドポイントテスト ===")
    
    access_token = os.getenv('ZOHO_ANALYTICS_ACCESS_TOKEN')
    
    if not access_token:
        print("❌ アクセストークンが設定されていません")
        return
    
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json'
    }
    
    # 複数のワークスペースエンドポイントを試す
    workspace_endpoints = [
        "https://analyticsapi.zoho.com/api/v2/workspaces",
        "https://www.zohoapis.com/analytics/v2/workspaces",
        "https://analytics.zoho.com/api/v2/workspaces"
    ]
    
    for i, endpoint in enumerate(workspace_endpoints, 1):
        print(f"\n🔍 ワークスペースエンドポイント {i} をテスト中: {endpoint}")
        
        try:
            response = requests.get(endpoint, headers=headers, timeout=30)
            print(f"   ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ 成功! ワークスペース数: {len(result.get('workspaces', []))}")
                return True
            else:
                print(f"   ❌ 失敗: {response.status_code}")
                print(f"   レスポンス: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ エラー: {e}")
    
    return False

def main():
    """
    メイン実行関数
    """
    print("=== Zoho Analytics API エンドポイントテスト ===")
    
    # ワークスペースエンドポイントテスト
    workspace_success = test_workspace_endpoints()
    
    # 直接クエリテスト
    query_success = test_direct_query()
    
    print("\n=== テスト結果 ===")
    if workspace_success:
        print("✅ ワークスペースエンドポイント: 成功")
    else:
        print("❌ ワークスペースエンドポイント: 失敗")
    
    if query_success:
        print("✅ クエリエンドポイント: 成功")
    else:
        print("❌ クエリエンドポイント: 失敗")
    
    if workspace_success or query_success:
        print("\n🎯 一部のエンドポイントで成功しました！")
    else:
        print("\n❌ すべてのエンドポイントで失敗しました")

if __name__ == "__main__":
    main() 