import requests
import json
import os
from urllib.parse import urlencode

class ZohoAuth:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None
        self.refresh_token = None
    
    def get_authorization_url(self, scope="ZohoAnalytics.metadata.read,ZohoAnalytics.data.read"):
        """認証URLを生成"""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'scope': scope,
            'redirect_uri': self.redirect_uri,
            'access_type': 'offline'
        }
        auth_url = f"https://accounts.zoho.com/oauth/v2/auth?{urlencode(params)}"
        return auth_url
    
    def get_access_token(self, authorization_code):
        """認証コードからアクセストークンを取得"""
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
            raise Exception(f"Token取得エラー: {response.status_code} - {response.text}")
    
    def refresh_access_token(self):
        """リフレッシュトークンから新しいアクセストークンを取得"""
        if not self.refresh_token:
            raise Exception("リフレッシュトークンがありません")
        
        token_url = "https://accounts.zoho.com/oauth/v2/token"
        
        data = {
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            return token_data
        else:
            raise Exception(f"トークン更新エラー: {response.status_code} - {response.text}")
    
    def save_tokens(self, filename='zoho_tokens.json'):
        """トークンをファイルに保存"""
        token_data = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token
        }
        with open(filename, 'w') as f:
            json.dump(token_data, f)
    
    def load_tokens(self, filename='zoho_tokens.json'):
        """ファイルからトークンを読み込み"""
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                token_data = json.load(f)
                self.access_token = token_data.get('access_token')
                self.refresh_token = token_data.get('refresh_token')
                return True
        return False

if __name__ == "__main__":
    CLIENT_ID = "1000.YN0LA88XQRCDTARO3FO5PWCOEY2IFZ"
    CLIENT_SECRET = "25549573ace167da7319c6b561a8ea477ca235e0ef"
    REDIRECT_URI = "http://localhost:8080/callback"
    
    auth = ZohoAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    
    if not auth.load_tokens():
        print("認証が必要です。以下のURLにアクセスしてください:")
        print(auth.get_authorization_url())
        print("\n認証後のリダイレクトURLからcodeパラメータを取得してください")
        
        code = input("認証コードを入力してください: ")
        
        try:
            token_data = auth.get_access_token(code)
            print("認証成功!")
            print(f"アクセストークン: {token_data['access_token'][:20]}...")
            auth.save_tokens()
        except Exception as e:
            print(f"認証エラー: {e}")
    else:
        print("保存済みのトークンを読み込みました")
        print(f"アクセストークン: {auth.access_token[:20]}..." if auth.access_token else "なし")