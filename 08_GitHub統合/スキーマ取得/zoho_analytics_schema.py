import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# 環境変数を読み込み
load_dotenv()

class ZohoAnalyticsAPI:
    def __init__(self):
        self.client_id = os.getenv('ZOHO_CLIENT_ID')
        self.client_secret = os.getenv('ZOHO_CLIENT_SECRET')
        self.refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')
        self.base_url = "https://analyticsapi.zoho.com/api"
        self.access_token = None
        
    def get_access_token(self):
        """アクセストークンを取得"""
        url = "https://accounts.zoho.com/oauth/v2/token"
        data = {
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(url, data=data)
        if response.status_code == 200:
            self.access_token = response.json()['access_token']
            return self.access_token
        else:
            raise Exception(f"アクセストークンの取得に失敗: {response.text}")
    
    def get_workspaces(self):
        """ワークスペース一覧を取得"""
        if not self.access_token:
            self.get_access_token()
            
        url = f"{self.base_url}/workspaces"
        headers = {'Authorization': f'Zoho-oauthtoken {self.access_token}'}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"ワークスペース取得に失敗: {response.text}")
    
    def get_tables(self, workspace_id):
        """テーブル一覧を取得"""
        if not self.access_token:
            self.get_access_token()
            
        url = f"{self.base_url}/{workspace_id}/tables"
        headers = {'Authorization': f'Zoho-oauthtoken {self.access_token}'}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"テーブル取得に失敗: {response.text}")
    
    def get_table_schema(self, workspace_id, table_name):
        """テーブルのスキーマ情報を取得"""
        if not self.access_token:
            self.get_access_token()
            
        url = f"{self.base_url}/{workspace_id}/tables/{table_name}/columns"
        headers = {'Authorization': f'Zoho-oauthtoken {self.access_token}'}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"スキーマ取得に失敗: {response.text}")

def main():
    """メイン処理"""
    try:
        api = ZohoAnalyticsAPI()
        
        # ワークスペース一覧を取得
        print("ワークスペース一覧を取得中...")
        workspaces = api.get_workspaces()
        
        # スキーマ情報を格納する辞書
        schema_info = {
            'workspaces': workspaces,
            'tables': {},
            'schemas': {},
            'generated_at': datetime.now().isoformat()
        }
        
        # 各ワークスペースのテーブル情報を取得
        for workspace in workspaces.get('workspaces', []):
            workspace_id = workspace['workspace_id']
            workspace_name = workspace['workspace_name']
            
            print(f"ワークスペース '{workspace_name}' のテーブル情報を取得中...")
            
            tables = api.get_tables(workspace_id)
            schema_info['tables'][workspace_id] = {
                'workspace_name': workspace_name,
                'tables': tables
            }
            
            # 各テーブルのスキーマ情報を取得
            for table in tables.get('tables', []):
                table_name = table['table_name']
                print(f"  テーブル '{table_name}' のスキーマを取得中...")
                
                schema = api.get_table_schema(workspace_id, table_name)
                schema_info['schemas'][f"{workspace_id}.{table_name}"] = {
                    'workspace_name': workspace_name,
                    'table_name': table_name,
                    'schema': schema
                }
        
        # スキーマ情報をJSONファイルに保存
        with open('zoho_analytics_schema.json', 'w', encoding='utf-8') as f:
            json.dump(schema_info, f, ensure_ascii=False, indent=2)
        
        print("スキーマ情報を 'zoho_analytics_schema.json' に保存しました。")
        
        # SQLファイルのテンプレートを生成
        generate_sql_template(schema_info)
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

def generate_sql_template(schema_info):
    """SQLテンプレートファイルを生成"""
    sql_content = """-- ZohoAnalytics SQL テンプレート
-- 生成日時: {generated_at}

-- 利用可能なテーブル一覧:
""".format(generated_at=schema_info['generated_at'])
    
    for key, schema in schema_info['schemas'].items():
        workspace_name = schema['workspace_name']
        table_name = schema['table_name']
        
        sql_content += f"\n-- ワークスペース: {workspace_name}\n"
        sql_content += f"-- テーブル: {table_name}\n"
        sql_content += f"-- カラム:\n"
        
        for column in schema['schema'].get('columns', []):
            col_name = column.get('column_name', '')
            col_type = column.get('data_type', '')
            sql_content += f"--   {col_name} ({col_type})\n"
        
        sql_content += f"\n-- SELECT * FROM {table_name};\n\n"
    
    # サンプルクエリを追加
    sql_content += """
-- サンプルクエリ例:

-- 1. 基本的なSELECT文
-- SELECT column1, column2 FROM table_name WHERE condition;

-- 2. 集計クエリ
-- SELECT 
--     column1,
--     COUNT(*) as count,
--     SUM(column2) as total
-- FROM table_name 
-- GROUP BY column1;

-- 3. JOINクエリ
-- SELECT 
--     t1.column1,
--     t2.column2
-- FROM table1 t1
-- JOIN table2 t2 ON t1.id = t2.id;

-- 4. サブクエリ
-- SELECT * FROM table1 
-- WHERE column1 IN (SELECT column1 FROM table2 WHERE condition);
"""
    
    with open('zoho_analytics_queries.sql', 'w', encoding='utf-8') as f:
        f.write(sql_content)
    
    print("SQLテンプレートを 'zoho_analytics_queries.sql' に生成しました。")

if __name__ == "__main__":
    main() 