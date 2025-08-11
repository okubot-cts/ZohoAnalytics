#!/usr/bin/env python3
import json
import requests
from datetime import datetime, timedelta

def refresh_crm_token():
    """ZohoCRMのアクセストークンをリフレッシュ"""
    
    token_file = "/Users/ks1-utakashio/Desktop/CursorProjects/20250726_ZohoAnalytics/01_Zoho_API/認証・トークン/zoho_crm_tokens.json"
    
    try:
        with open(token_file, "r") as f:
            tokens = json.load(f)
    except FileNotFoundError:
        print("トークンファイルが見つかりません")
        return None
    
    if "refresh_token" not in tokens:
        print("リフレッシュトークンが見つかりません")
        return None
    
    CLIENT_ID = "1000.YN0LA88XQRCDTARO3FO5PWCOEY2IFZ"
    CLIENT_SECRET = "25549573ace167da7319c6b561a8ea477ca235e0ef"
    
    token_url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        'refresh_token': tokens['refresh_token'],
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token'
    }
    
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        new_token_data = response.json()
        
        # 有効期限を追加
        expires_at = datetime.now() + timedelta(seconds=new_token_data.get('expires_in', 3600))
        new_token_data['expires_at'] = expires_at.isoformat()
        new_token_data['updated_at'] = datetime.now().isoformat()
        
        # リフレッシュトークンと既存情報を保持
        if 'refresh_token' not in new_token_data:
            new_token_data['refresh_token'] = tokens['refresh_token']
        
        new_token_data['scope'] = tokens.get('scope', 'ZohoCRM.modules.ALL ZohoCRM.settings.modules.READ ZohoCRM.settings.fields.READ')
        new_token_data['api_domain'] = tokens.get('api_domain', 'https://www.zohoapis.com')
        new_token_data['token_type'] = 'Bearer'
        
        # 新しいトークンを保存
        with open(token_file, "w") as f:
            json.dump(new_token_data, f, indent=2)
        
        print("✓ CRMアクセストークンが更新されました")
        print(f"新しいアクセストークン: {new_token_data['access_token'][:50]}...")
        print(f"有効期限: {new_token_data['expires_at']}")
        
        return new_token_data
    else:
        print(f"トークン更新エラー: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    refresh_crm_token()