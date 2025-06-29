import requests
import json

def test_zoho_api():
    # トークンを読み込み
    with open('zoho_tokens.json', 'r') as f:
        tokens = json.load(f)
    
    access_token = tokens['access_token']
    
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json'
    }
    
    # 複数のエンドポイントをテスト
    endpoints = [
        "https://analyticsapi.zoho.com/restapi/v2/workspaces",
        "https://analyticsapi.zoho.com/api/v1/workspaces",
        "https://www.zohoapis.com/analytics/v1/workspaces"
    ]
    
    for url in endpoints:
        print(f"\nテスト中: {url}")
        try:
            response = requests.get(url, headers=headers)
            print(f"ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"レスポンス: {json.dumps(data, indent=2)}")
                if 'workspaces' in data:
                    print(f"ワークスペース数: {len(data['workspaces'])}")
            else:
                print(f"エラー: {response.text[:500]}")
                
        except Exception as e:
            print(f"例外発生: {e}")

if __name__ == "__main__":
    test_zoho_api()