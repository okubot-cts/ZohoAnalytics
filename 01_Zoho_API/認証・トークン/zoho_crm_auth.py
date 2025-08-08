import requests
import json
from urllib.parse import urlencode

class ZohoCRMAuth:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None
        self.refresh_token = None
    
    def get_crm_authorization_url(self):
        """CRM API用の認証URLを生成（必要なスコープ付き）"""
        scope = "ZohoCRM.modules.ALL,ZohoCRM.settings.modules.READ,ZohoCRM.settings.fields.READ"
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'scope': scope,
            'redirect_uri': self.redirect_uri,
            'access_type': 'offline'
        }
        
        auth_url = f"https://accounts.zoho.com/oauth/v2/auth?{urlencode(params)}"
        return auth_url
    
    def get_crm_access_token(self, authorization_code):
        """CRM用認証コードからアクセストークンを取得"""
        token_url = "https://accounts.zoho.com/oauth/v2/token"
        
        data = {
            'code': authorization_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            return token_data
        else:
            raise Exception(f"CRMトークン取得エラー: {response.status_code} - {response.text}")
    
    def save_crm_tokens(self, filename='zoho_crm_tokens.json'):
        """CRMトークンをファイルに保存"""
        if self.access_token:
            token_data = {
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'scope': 'ZohoCRM.modules.ALL,ZohoCRM.settings.modules.READ,ZohoCRM.settings.fields.READ'
            }
            with open(filename, 'w') as f:
                json.dump(token_data, f, indent=2)
            print(f"✓ CRMトークンを {filename} に保存")

def main():
    print("=== Zoho CRM API認証 ===")
    print("CRMスキーマ取得用の認証を行います\n")
    
    # 既存の認証情報を使用
    CLIENT_ID = "1000.YN0LA88XQRCDTARO3FO5PWCOEY2IFZ"
    CLIENT_SECRET = "25549573ace167da7319c6b561a8ea477ca235e0ef"
    REDIRECT_URI = "http://localhost:8080/callback"
    
    auth = ZohoCRMAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    
    print("1. 以下のURLにアクセスしてCRM API認証を行ってください:")
    print(auth.get_crm_authorization_url())
    print("\n2. 認証後のリダイレクトURLから認証コードを取得してください")
    print("   例: http://localhost:8080/callback?code=1000.abc123...")
    print("\n認証コードを入力してください: ", end="")
    
    # 実際の使用時はここでinputを使用
    print("\n[注意] 実際の認証コードを入力してスクリプトを実行してください")

if __name__ == "__main__":
    main()