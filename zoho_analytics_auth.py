import requests
import json
import urllib.parse

class ZohoAnalyticsAuth:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.base_url = "https://accounts.zoho.com/oauth/v2"
        
    def get_authorization_url(self, scope="ZohoAnalytics.fullaccess.all"):
        """認証URLを生成"""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'scope': scope,
            'redirect_uri': self.redirect_uri,
            'access_type': 'offline'
        }
        
        auth_url = f"{self.base_url}/auth?" + urllib.parse.urlencode(params)
        return auth_url
    
    def get_access_token(self, authorization_code):
        """認証コードからアクセストークンを取得"""
        token_url = f"{self.base_url}/token"
        
        data = {
            'code': authorization_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Token取得エラー: {response.status_code} - {response.text}")
    
    def refresh_access_token(self, refresh_token):
        """リフレッシュトークンから新しいアクセストークンを取得"""
        token_url = f"{self.base_url}/token"
        
        data = {
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Token更新エラー: {response.status_code} - {response.text}")

class ZohoAnalyticsAPI:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://analyticsapi.zoho.com/api"
        
    def get_headers(self):
        """APIリクエスト用のヘッダーを取得"""
        return {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_workspaces(self):
        """ワークスペース一覧を取得"""
        url = f"{self.base_url}/v1/workspaces"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"ワークスペース取得エラー: {response.status_code} - {response.text}")
    
    def get_views(self, workspace_id):
        """指定ワークスペースのビュー（テーブル）一覧を取得"""
        url = f"{self.base_url}/v1/workspaces/{workspace_id}/views"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"ビュー取得エラー: {response.status_code} - {response.text}")
    
    def get_view_metadata(self, workspace_id, view_id):
        """指定ビューのメタデータ（スキーマ情報）を取得"""
        url = f"{self.base_url}/v1/workspaces/{workspace_id}/views/{view_id}/columns"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"メタデータ取得エラー: {response.status_code} - {response.text}")

def main():
    print("ZohoAnalytics API 認証・スキーマ取得ツール")
    print("=" * 50)
    
    # 設定値（ユーザーが入力する必要があります）
    CLIENT_ID = input("Client ID を入力してください: ")
    CLIENT_SECRET = input("Client Secret を入力してください: ")
    REDIRECT_URI = input("Redirect URI を入力してください（例: http://localhost:8080/callback）: ")
    
    # 認証処理
    auth = ZohoAnalyticsAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    
    print("\n1. 以下のURLにアクセスして認証を行ってください:")
    print(auth.get_authorization_url())
    
    print("\n2. 認証後、リダイレクトされたURLから認証コードを取得してください")
    authorization_code = input("認証コードを入力してください: ")
    
    try:
        # アクセストークン取得
        token_response = auth.get_access_token(authorization_code)
        access_token = token_response['access_token']
        refresh_token = token_response.get('refresh_token')
        
        print(f"\n✓ アクセストークン取得成功")
        print(f"Access Token: {access_token[:20]}...")
        if refresh_token:
            print(f"Refresh Token: {refresh_token[:20]}...")
        
        # トークンをファイルに保存
        with open('zoho_tokens.json', 'w') as f:
            json.dump(token_response, f, indent=2)
        print("✓ トークンを zoho_tokens.json に保存しました")
        
        # API呼び出しテスト
        api = ZohoAnalyticsAPI(access_token)
        
        print("\n3. ワークスペース一覧を取得中...")
        workspaces = api.get_workspaces()
        print(f"✓ {len(workspaces.get('workspaces', []))} 個のワークスペースを発見")
        
        for workspace in workspaces.get('workspaces', []):
            print(f"  - {workspace['workspaceName']} (ID: {workspace['workspaceId']})")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()