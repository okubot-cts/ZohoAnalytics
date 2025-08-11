#!/usr/bin/env python3
"""
Zoho CRM 認証セットアップスクリプト
"""
import json
from pathlib import Path
from urllib.parse import urlencode
import webbrowser

def setup_zoho_crm():
    """Zoho CRM認証の手順を表示"""
    
    # 既存の認証情報を使用
    CLIENT_ID = "1000.YN0LA88XQRCDTARO3FO5PWCOEY2IFZ"
    CLIENT_SECRET = "25549573ace167da7319c6b561a8ea477ca235e0ef"
    REDIRECT_URI = "http://localhost:8080/callback"
    
    print("="*60)
    print("Zoho CRM 認証セットアップ")
    print("="*60)
    
    # CRM用のスコープ
    scope = "ZohoCRM.modules.ALL,ZohoCRM.settings.modules.READ,ZohoCRM.settings.fields.READ"
    
    # 認証URLを生成
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'access_type': 'offline'
    }
    
    auth_url = f"https://accounts.zoho.com/oauth/v2/auth?{urlencode(params)}"
    
    print("\n📝 Zoho CRM認証手順：\n")
    print("1. 以下のURLをブラウザで開いてください：")
    print("-"*60)
    print(auth_url)
    print("-"*60)
    
    print("\n2. Zohoアカウントでログインしてください")
    print("   ※ 既にログイン済みの場合はスキップされます")
    
    print("\n3. 「Accept」ボタンをクリックして、アプリケーションのアクセスを許可してください")
    print("   要求される権限：")
    print("   - CRMモジュールへのフルアクセス")
    print("   - 設定モジュールの読み取り")
    print("   - フィールド設定の読み取り")
    
    print("\n4. 認証後、以下のようなURLにリダイレクトされます：")
    print("   http://localhost:8080/callback?code=1000.xxxxx...")
    print("   ※ ページが表示されなくてもURLは有効です")
    
    print("\n5. URLから「code=」の後の値（認証コード）をコピーしてください")
    print("   例: 1000.a1b2c3d4e5f6...")
    
    # ブラウザで自動的に開く
    try:
        webbrowser.open(auth_url)
        print("\n✅ ブラウザで認証URLを開きました")
    except:
        print("\n⚠️  ブラウザを自動で開けませんでした")
        print("    上記のURLを手動でブラウザにコピー＆ペーストしてください")
    
    print("\n" + "="*60)
    print("認証コードを取得したら、以下のスクリプトを実行してください：")
    print("\npython3 get_crm_token_new.py [認証コード]")
    print("\n例:")
    print("python3 get_crm_token_new.py 1000.a1b2c3d4e5f6...")
    print("="*60)

if __name__ == "__main__":
    setup_zoho_crm()