import requests
import json
import pandas as pd

def test_table_schema():
    # トークン読み込み
    with open('zoho_tokens.json', 'r') as f:
        tokens = json.load(f)
    access_token = tokens['access_token']
    
    # テーブル一覧から最初のテーブルを取得
    df = pd.read_excel('zoho_table_list.xlsx', sheet_name='Main_Tables')
    first_table = df.iloc[0]
    
    workspace_id = first_table['workspace_id']
    view_id = first_table['view_id']
    view_name = first_table['view_name']
    org_id = first_table['org_id']
    
    print(f"テストテーブル: {view_name}")
    print(f"Workspace ID: {workspace_id}")
    print(f"View ID: {view_id}")
    print(f"Org ID: {org_id}")
    
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json',
        'ZANALYTICS-ORGID': str(org_id)
    }
    
    # 様々なエンドポイントをテスト
    base_url = "https://analyticsapi.zoho.com/restapi/v2"
    
    test_urls = [
        f"{base_url}/workspaces/{workspace_id}/views/{view_id}",
        f"{base_url}/workspaces/{workspace_id}/views/{view_id}/metadata",
        f"{base_url}/workspaces/{workspace_id}/views/{view_id}/columns",
        f"{base_url}/workspaces/{workspace_id}/views/{view_id}/schema",
        f"{base_url}/workspaces/{workspace_id}/views/{view_id}/data?limit=1",
        f"{base_url}/workspaces/{workspace_id}/tables/{view_id}",
        f"{base_url}/workspaces/{workspace_id}/tables/{view_id}/columns"
    ]
    
    for url in test_urls:
        print(f"\n--- テスト: {url.split('/')[-2:]} ---")
        try:
            response = requests.get(url, headers=headers)
            print(f"ステータス: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"レスポンス構造: {list(data.keys())}")
                
                # データ構造を詳しく確認
                if 'data' in data:
                    data_content = data['data']
                    if isinstance(data_content, dict):
                        print(f"data内容: {list(data_content.keys())}")
                        
                        # 列情報を探す
                        for key, value in data_content.items():
                            if key in ['columns', 'fields', 'schema', 'metadata']:
                                print(f"  {key}: {type(value)} ({len(value) if isinstance(value, list) else 'N/A'})")
                                if isinstance(value, list) and len(value) > 0:
                                    print(f"    最初の要素: {list(value[0].keys()) if isinstance(value[0], dict) else value[0]}")
                    
                    elif isinstance(data_content, list):
                        print(f"data配列長: {len(data_content)}")
                        if len(data_content) > 0:
                            print(f"最初の要素: {list(data_content[0].keys()) if isinstance(data_content[0], dict) else data_content[0]}")
                
                # JSONレスポンスを保存（最初の成功例のみ）
                if response.status_code == 200:
                    with open(f'sample_response_{url.split("/")[-1]}.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"  レスポンスを sample_response_{url.split('/')[-1]}.json に保存")
                    
            else:
                error_text = response.text[:200]
                print(f"エラー: {error_text}")
                
        except Exception as e:
            print(f"例外: {e}")

if __name__ == "__main__":
    test_table_schema()