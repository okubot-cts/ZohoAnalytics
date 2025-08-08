import requests
import json

def test_workspace_views():
    workspace_id = "2527115000001040002"
    
    # トークンを読み込み
    with open('zoho_tokens.json', 'r') as f:
        tokens = json.load(f)
    
    access_token = tokens['access_token']
    
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json'
    }
    
    # 複数のビュー取得エンドポイントをテスト
    endpoints = [
        f"https://analyticsapi.zoho.com/restapi/v2/workspaces/{workspace_id}/views",
        f"https://analyticsapi.zoho.com/restapi/v2/workspaces/{workspace_id}/tables",
        f"https://analyticsapi.zoho.com/restapi/v2/workspaces/{workspace_id}",
        f"https://analyticsapi.zoho.com/restapi/v2/workspaces/{workspace_id}/reports"
    ]
    
    for url in endpoints:
        print(f"\nテスト中: {url}")
        try:
            response = requests.get(url, headers=headers)
            print(f"ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"レスポンス構造: {list(data.keys())}")
                
                # データ構造を確認
                if 'data' in data:
                    print(f"data構造: {list(data['data'].keys())}")
                    
                    # ビュー、テーブル、レポートなどの項目を確認
                    for key, value in data['data'].items():
                        if isinstance(value, list):
                            print(f"{key}: {len(value)} 個")
                            if len(value) > 0:
                                print(f"  最初の項目: {list(value[0].keys()) if isinstance(value[0], dict) else value[0]}")
                        else:
                            print(f"{key}: {value}")
                            
            else:
                print(f"エラーレスポンス: {response.text[:200]}...")
                
        except Exception as e:
            print(f"例外発生: {e}")

if __name__ == "__main__":
    test_workspace_views()