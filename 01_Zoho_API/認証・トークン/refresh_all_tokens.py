#!/usr/bin/env python3
"""
Zoho CRMとBooksのトークン取得・管理スクリプト
"""
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode
import webbrowser

class ZohoTokenManager:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.crm_tokens_file = self.base_path / "zoho_crm_tokens.json"
        self.books_tokens_file = self.base_path / "zoho_books_tokens.json"
        
        # 設定（既存の認証情報を使用）
        self.client_id = "1000.YN0LA88XQRCDTARO3FO5PWCOEY2IFZ"
        self.client_secret = "25549573ace167da7319c6b561a8ea477ca235e0ef"
        self.redirect_uri = "http://localhost:8080/callback"
    
    def get_auth_url(self, service="crm"):
        """認証URLを生成"""
        if service == "crm":
            scope = "ZohoCRM.modules.ALL,ZohoCRM.settings.modules.READ,ZohoCRM.settings.fields.READ"
        elif service == "books":
            scope = "ZohoBooks.fullaccess.all"
        else:
            raise ValueError(f"不明なサービス: {service}")
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'scope': scope,
            'redirect_uri': self.redirect_uri,
            'access_type': 'offline'
        }
        
        auth_url = f"https://accounts.zoho.com/oauth/v2/auth?{urlencode(params)}"
        return auth_url
    
    def get_tokens_from_code(self, auth_code, service="crm"):
        """認証コードからトークンを取得"""
        token_url = "https://accounts.zoho.com/oauth/v2/token"
        
        data = {
            'code': auth_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            
            # 有効期限とスコープを追加
            token_data['expires_at'] = (datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))).isoformat()
            token_data['updated_at'] = datetime.now().isoformat()
            
            if service == "crm":
                token_data['scope'] = 'ZohoCRM.modules.ALL ZohoCRM.settings.modules.READ ZohoCRM.settings.fields.READ'
                # CRM用のAPI domainを保存
                token_data['api_domain'] = 'https://www.zohoapis.com'
            
            # トークンをファイルに保存
            tokens_file = self.crm_tokens_file if service == "crm" else self.books_tokens_file
            with open(tokens_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            print(f"✅ {service.upper()}トークンを保存しました: {tokens_file}")
            return token_data
        else:
            print(f"❌ トークン取得エラー: {response.status_code}")
            print(f"   詳細: {response.text}")
            return None
    
    def setup_crm(self):
        """ZohoCRM認証セットアップ"""
        print("\n=== Zoho CRM 認証セットアップ ===")
        auth_url = self.get_auth_url("crm")
        
        print("\n1. 以下のURLをブラウザで開いてください:")
        print(auth_url)
        print("\n2. Zohoにログインして認証を許可してください")
        print("3. リダイレクトURLから認証コードを取得してください")
        print("   例: http://localhost:8080/callback?code=1000.xxx...")
        
        # ブラウザで開く
        try:
            webbrowser.open(auth_url)
            print("\n✅ ブラウザでURLを開きました")
        except:
            print("\n⚠️  ブラウザを自動で開けませんでした。上記URLを手動で開いてください")
        
        print("\n認証コードを入力してください (codeパラメータの値): ", end="")
        auth_code = input().strip()
        
        if auth_code:
            token_data = self.get_tokens_from_code(auth_code, "crm")
            if token_data:
                print("\n✅ CRM認証が完了しました!")
                return True
        
        return False
    
    def setup_books(self):
        """ZohoBooks認証セットアップ"""
        print("\n=== Zoho Books 認証セットアップ ===")
        auth_url = self.get_auth_url("books")
        
        print("\n1. 以下のURLをブラウザで開いてください:")
        print(auth_url)
        print("\n2. Zohoにログインして認証を許可してください")
        print("3. リダイレクトURLから認証コードを取得してください")
        print("   例: http://localhost:8080/callback?code=1000.xxx...")
        
        # ブラウザで開く
        try:
            webbrowser.open(auth_url)
            print("\n✅ ブラウザでURLを開きました")
        except:
            print("\n⚠️  ブラウザを自動で開けませんでした。上記URLを手動で開いてください")
        
        print("\n認証コードを入力してください (codeパラメータの値): ", end="")
        auth_code = input().strip()
        
        if auth_code:
            token_data = self.get_tokens_from_code(auth_code, "books")
            if token_data:
                print("\n✅ Books認証が完了しました!")
                return True
        
        return False
    
    def check_tokens(self):
        """既存トークンの状態を確認"""
        print("\n=== トークン状態確認 ===")
        
        # CRMトークン確認
        if self.crm_tokens_file.exists():
            with open(self.crm_tokens_file, 'r') as f:
                crm_tokens = json.load(f)
            
            if 'expires_at' in crm_tokens:
                expires_at = datetime.fromisoformat(crm_tokens['expires_at'])
                if datetime.now() < expires_at:
                    print(f"✅ CRMトークン: 有効 (有効期限: {expires_at.strftime('%Y-%m-%d %H:%M:%S')})")
                else:
                    print(f"⚠️  CRMトークン: 期限切れ (期限: {expires_at.strftime('%Y-%m-%d %H:%M:%S')})")
            else:
                print("⚠️  CRMトークン: 有効期限情報なし")
        else:
            print("❌ CRMトークン: ファイルなし")
        
        # Booksトークン確認
        if self.books_tokens_file.exists():
            with open(self.books_tokens_file, 'r') as f:
                books_tokens = json.load(f)
            
            if 'expires_at' in books_tokens:
                expires_at = datetime.fromisoformat(books_tokens['expires_at'])
                if datetime.now() < expires_at:
                    print(f"✅ Booksトークン: 有効 (有効期限: {expires_at.strftime('%Y-%m-%d %H:%M:%S')})")
                else:
                    print(f"⚠️  Booksトークン: 期限切れ (期限: {expires_at.strftime('%Y-%m-%d %H:%M:%S')})")
            else:
                print("⚠️  Booksトークン: 有効期限情報なし")
        else:
            print("❌ Booksトークン: ファイルなし")

def main():
    """メイン処理"""
    manager = ZohoTokenManager()
    
    while True:
        print("\n" + "="*50)
        print("Zoho トークン管理ツール")
        print("="*50)
        print("\n1. トークン状態を確認")
        print("2. CRMトークンを再取得")
        print("3. Booksトークンを取得/再取得")
        print("4. 両方のトークンを再取得")
        print("0. 終了")
        
        print("\n選択してください (0-4): ", end="")
        choice = input().strip()
        
        if choice == "1":
            manager.check_tokens()
        elif choice == "2":
            if manager.setup_crm():
                print("CRM認証が完了しました")
        elif choice == "3":
            if manager.setup_books():
                print("Books認証が完了しました")
        elif choice == "4":
            crm_ok = manager.setup_crm()
            books_ok = manager.setup_books()
            if crm_ok and books_ok:
                print("\n両方の認証が完了しました!")
        elif choice == "0":
            print("\n終了します")
            break
        else:
            print("\n⚠️  無効な選択です")

if __name__ == "__main__":
    main()