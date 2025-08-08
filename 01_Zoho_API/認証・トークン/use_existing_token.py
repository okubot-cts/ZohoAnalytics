#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
既存のトークンファイルからリフレッシュトークンを使って新しいアクセストークンを取得
"""

import json
import requests
import os
from datetime import datetime

def load_existing_tokens():
    """
    既存のトークンファイルを読み込み
    """
    try:
        with open('zoho_tokens.json', 'r', encoding='utf-8') as f:
            tokens = json.load(f)
        return tokens
    except FileNotFoundError:
        print("❌ zoho_tokens.json ファイルが見つかりません")
        return None
    except json.JSONDecodeError:
        print("❌ zoho_tokens.json ファイルの形式が正しくありません")
        return None

def refresh_access_token(refresh_token, client_id, client_secret):
    """
    リフレッシュトークンから新しいアクセストークンを取得
    """
    url = "https://accounts.zoho.com/oauth/v2/token"
    
    payload = {
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'refresh_token'
    }
    
    try:
        print("🔄 アクセストークンを更新中...")
        response = requests.post(url, data=payload)
        response.raise_for_status()
        
        token_data = response.json()
        
        # 現在時刻を追加
        token_data['refreshed_at'] = datetime.now().isoformat()
        
        # トークン情報をファイルに保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"zoho_tokens_updated_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(token_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 新しいトークン情報を保存しました: {filename}")
        
        return token_data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ トークン更新エラー: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   レスポンス: {e.response.text}")
        return None

def setup_environment_variables(token_data):
    """
    環境変数を設定
    """
    if 'access_token' in token_data:
        access_token = token_data['access_token']
        
        # .envファイルに保存
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(f"ZOHO_ANALYTICS_ACCESS_TOKEN={access_token}\n")
            if 'refresh_token' in token_data:
                f.write(f"ZOHO_ANALYTICS_REFRESH_TOKEN={token_data['refresh_token']}\n")
        
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
    print("=== 既存トークンからアクセストークン更新 ===")
    
    # 既存のトークンを読み込み
    existing_tokens = load_existing_tokens()
    if not existing_tokens:
        return
    
    print("✅ 既存のトークンファイルを読み込みました")
    print(f"   リフレッシュトークン: {existing_tokens.get('refresh_token', 'N/A')[:10]}...")
    print(f"   スコープ: {existing_tokens.get('scope', 'N/A')}")
    
    # クライアント情報の入力
    print("\n📋 クライアント情報を入力してください:")
    client_id = input("クライアントID: ").strip()
    client_secret = input("クライアントシークレット: ").strip()
    
    if not client_id or not client_secret:
        print("❌ クライアントIDとクライアントシークレットが必要です")
        return
    
    # リフレッシュトークンを取得
    refresh_token = existing_tokens.get('refresh_token')
    if not refresh_token:
        print("❌ リフレッシュトークンが見つかりません")
        return
    
    # 新しいアクセストークンを取得
    new_token_data = refresh_access_token(refresh_token, client_id, client_secret)
    if new_token_data:
        # 環境変数を設定
        if setup_environment_variables(new_token_data):
            print("\n🎯 完了!")
            print("✅ 新しいアクセストークンを取得しました")
            print("✅ 環境変数が設定されました")
            print("\n📋 次のステップ:")
            print("1. python3 test_actual_api.py でAPIテストを実行")
            print("2. python3 zoho_analytics_api_client.py でVERSANTレポートを実行")
        else:
            print("❌ 環境変数の設定に失敗しました")
    else:
        print("❌ アクセストークンの更新に失敗しました")

if __name__ == "__main__":
    main() 