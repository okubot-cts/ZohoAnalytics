import requests
import json

CLIENT_ID = "1000.YN0LA88XQRCDTARO3FO5PWCOEY2IFZ"
CLIENT_SECRET = "25549573ace167da7319c6b561a8ea477ca235e0ef"
REDIRECT_URI = "http://localhost:8080/callback"
CODE = "1000.5b5e6f223db233a67c49eec91cf6e9ce.70a7cd9c8cac867d51c517e439328f11"

token_url = "https://accounts.zoho.com/oauth/v2/token"

data = {
    'code': CODE,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'redirect_uri': REDIRECT_URI,
    'grant_type': 'authorization_code'
}

response = requests.post(token_url, data=data)

if response.status_code == 200:
    token_data = response.json()
    print("CRM認証成功!")
    print(f"Access Token: {token_data['access_token'][:20]}...")
    print(f"Scope: {token_data.get('scope', 'N/A')}")
    
    # CRM用トークンを保存
    with open('zoho_crm_tokens.json', 'w') as f:
        json.dump(token_data, f, indent=2)
    
    print("✓ CRMトークンを zoho_crm_tokens.json に保存しました")
    print("次は CRMスキーマ抽出を実行します...")
    
else:
    print(f"エラー: {response.status_code}")
    print(response.text)