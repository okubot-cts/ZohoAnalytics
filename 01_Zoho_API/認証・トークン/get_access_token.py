#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zoho Analytics API アクセストークン取得スクリプト
リフレッシュトークンから新しいアクセストークンを取得
"""

import requests
import json
import os
from datetime import datetime

def get_access_token_from_refresh(refresh_token, client_id, client_secret):
    """
    リフレッシュトークンからアクセストークンを取得
    
    Args:
        refresh_token (str): リフレッシュトークン
        client_id (str): クライアントID
        client_secret (str): クライアントシークレット
    
    Returns:
        dict: トークン情報
    """
    url = "https://accounts.zoho.com/oauth/v2/token"
    
    payload = {
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'refresh_token'
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        
        token_data = response.json()
        
        # トークン情報をファイルに保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"token_info_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(token_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ トークン情報を保存しました: {filename}")
        
        return token_data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ トークン取得エラー: {e}")
        return None

def get_access_token_from_auth_code(auth_code, client_id, client_secret, redirect_uri):
    """
    認証コードからアクセストークンを取得
    
    Args:
        auth_code (str): 認証コード
        client_id (str): クライアントID
        client_secret (str): クライアントシークレット
        redirect_uri (str): リダイレクトURI
    
    Returns:
        dict: トークン情報
    """
    url = "https://accounts.zoho.com/oauth/v2/token"
    
    payload = {
        'code': auth_code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        
        token_data = response.json()
        
        # トークン情報をファイルに保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"token_info_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(token_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ トークン情報を保存しました: {filename}")
        
        return token_data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ トークン取得エラー: {e}")
        return None

def setup_environment_variables(token_data):
    """
    環境変数を設定
    
    Args:
        token_data (dict): トークン情報
    """
    if 'access_token' in token_data:
        access_token = token_data['access_token']
        
        # .envファイルに保存
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(f"ZOHO_ANALYTICS_ACCESS_TOKEN={access_token}\n")
            f.write(f"ZOHO_ANALYTICS_REFRESH_TOKEN={token_data.get('refresh_token', '')}\n")
            f.write(f"ZOHO_ANALYTICS_CLIENT_ID={os.getenv('ZOHO_CLIENT_ID', '')}\n")
            f.write(f"ZOHO_ANALYTICS_CLIENT_SECRET={os.getenv('ZOHO_CLIENT_SECRET', '')}\n")
        
        # 環境変数を設定
        os.environ['ZOHO_ANALYTICS_ACCESS_TOKEN'] = access_token
        
        print("✅ 環境変数を設定しました")
        print(f"   アクセストークン: {access_token[:10]}...")
        
        return True
    else:
        print("❌ アクセストークンが取得できませんでした")
        return False

def main():
    """
    メイン実行関数
    """
    print("=== Zoho Analytics API アクセストークン取得 ===")
    
    print("\n📋 取得方法を選択してください:")
    print("1. リフレッシュトークンから取得")
    print("2. 認証コードから取得")
    print("3. 手動でトークンを入力")
    
    choice = input("\n選択してください (1-3): ").strip()
    
    if choice == "1":
        # リフレッシュトークンから取得
        print("\n=== リフレッシュトークンから取得 ===")
        
        refresh_token = input("リフレッシュトークンを入力してください: ").strip()
        client_id = input("クライアントIDを入力してください: ").strip()
        client_secret = input("クライアントシークレットを入力してください: ").strip()
        
        if refresh_token and client_id and client_secret:
            token_data = get_access_token_from_refresh(refresh_token, client_id, client_secret)
            if token_data:
                setup_environment_variables(token_data)
        else:
            print("❌ 必要な情報が不足しています")
    
    elif choice == "2":
        # 認証コードから取得
        print("\n=== 認証コードから取得 ===")
        
        auth_code = input("認証コードを入力してください: ").strip()
        client_id = input("クライアントIDを入力してください: ").strip()
        client_secret = input("クライアントシークレットを入力してください: ").strip()
        redirect_uri = input("リダイレクトURIを入力してください: ").strip()
        
        if auth_code and client_id and client_secret and redirect_uri:
            token_data = get_access_token_from_auth_code(auth_code, client_id, client_secret, redirect_uri)
            if token_data:
                setup_environment_variables(token_data)
        else:
            print("❌ 必要な情報が不足しています")
    
    elif choice == "3":
        # 手動でトークンを入力
        print("\n=== 手動でトークンを入力 ===")
        
        access_token = input("アクセストークンを入力してください: ").strip()
        workspace_id = input("ワークスペースIDを入力してください: ").strip()
        
        if access_token and workspace_id:
            # .envファイルに保存
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(f"ZOHO_ANALYTICS_ACCESS_TOKEN={access_token}\n")
                f.write(f"ZOHO_ANALYTICS_WORKSPACE_ID={workspace_id}\n")
            
            # 環境変数を設定
            os.environ['ZOHO_ANALYTICS_ACCESS_TOKEN'] = access_token
            os.environ['ZOHO_ANALYTICS_WORKSPACE_ID'] = workspace_id
            
            print("✅ 環境変数を設定しました")
            print(f"   アクセストークン: {access_token[:10]}...")
            print(f"   ワークスペースID: {workspace_id}")
        else:
            print("❌ 必要な情報が不足しています")
    
    else:
        print("❌ 無効な選択です")

if __name__ == "__main__":
    main() 