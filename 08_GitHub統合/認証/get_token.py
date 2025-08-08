import requests
import json

CLIENT_ID = "1000.YN0LA88XQRCDTARO3FO5PWCOEY2IFZ"
CLIENT_SECRET = "25549573ace167da7319c6b561a8ea477ca235e0ef"
REDIRECT_URI = "http://localhost:8080/callback"
CODE = "1000.27796666563adb7463dc7a9dff9ad131.67b4d549d51e1796d91f9ea583534242"

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
    print("認証成功!")
    print(f"Access Token: {token_data['access_token'][:20]}...")
    
    # トークンを保存
    with open('zoho_tokens.json', 'w') as f:
        json.dump(token_data, f, indent=2)
    
    print("✓ トークンを zoho_tokens.json に保存しました")
    print("次は以下を実行してください:")
    print("python3 zoho_schema_extractor.py")
    
else:
    print(f"エラー: {response.status_code}")
    print(response.text)