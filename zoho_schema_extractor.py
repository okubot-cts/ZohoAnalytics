import requests
import json
import pandas as pd
from datetime import datetime
import os

class ZohoSchemaExtractor:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://analyticsapi.zoho.com/restapi/v2"
        
    def get_headers(self, org_id=None):
        headers = {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'Content-Type': 'application/json'
        }
        if org_id:
            headers['ZANALYTICS-ORGID'] = str(org_id)
        return headers
    
    def get_all_workspaces(self):
        """全ワークスペースを取得"""
        url = f"{self.base_url}/workspaces"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            data = response.json()
            workspaces = []
            if 'data' in data:
                # 所有ワークスペースと共有ワークスペースを結合
                workspaces.extend(data['data'].get('ownedWorkspaces', []))
                workspaces.extend(data['data'].get('sharedWorkspaces', []))
            return workspaces
        else:
            raise Exception(f"ワークスペース取得エラー: {response.status_code} - {response.text}")
    
    def get_workspace_views(self, workspace_id, org_id):
        """指定ワークスペースの全ビューを取得"""
        url = f"{self.base_url}/workspaces/{workspace_id}/views"
        response = requests.get(url, headers=self.get_headers(org_id))
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                return data['data'].get('views', [])
            return data.get('views', [])
        else:
            print(f"Warning: ワークスペース {workspace_id} のビュー取得に失敗: {response.status_code}")
            print(f"  エラー詳細: {response.text[:200]}")
            return []
    
    def get_view_columns(self, workspace_id, view_id, org_id):
        """指定ビューの列情報を取得"""
        url = f"{self.base_url}/workspaces/{workspace_id}/views/{view_id}"
        response = requests.get(url, headers=self.get_headers(org_id))
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'columns' in data['data']:
                return data['data']['columns']
            return data.get('columns', [])
        else:
            print(f"Warning: ビュー {view_id} の列情報取得に失敗: {response.status_code}")
            return []
    
    def extract_complete_schema(self):
        """完全なスキーマ情報を抽出"""
        schema_data = {
            'extraction_date': datetime.now().isoformat(),
            'workspaces': []
        }
        
        print("スキーマ抽出を開始します...")
        
        # 全ワークスペースを取得
        workspaces = self.get_all_workspaces()
        print(f"✓ {len(workspaces)} 個のワークスペースを発見")
        
        for workspace in workspaces:
            workspace_id = workspace['workspaceId']
            workspace_name = workspace['workspaceName']
            org_id = workspace.get('orgId')
            
            print(f"\n処理中: {workspace_name} (ID: {workspace_id}, OrgID: {org_id})")
            
            workspace_schema = {
                'workspace_id': workspace_id,
                'workspace_name': workspace_name,
                'org_id': org_id,
                'description': workspace.get('workspaceDesc', ''),
                'views': []
            }
            
            # ワークスペース内の全ビューを取得
            views = self.get_workspace_views(workspace_id, org_id)
            print(f"  - {len(views)} 個のビューを発見")
            
            for view in views:
                view_id = view.get('viewId', view.get('id'))
                view_name = view.get('viewName', view.get('name'))
                
                print(f"    処理中: {view_name}")
                
                view_schema = {
                    'view_id': view_id,
                    'view_name': view_name,
                    'view_type': view.get('viewType', view.get('type', '')),
                    'description': view.get('description', ''),
                    'columns': []
                }
                
                # ビューの列情報を取得
                columns = self.get_view_columns(workspace_id, view_id, org_id)
                
                for column in columns:
                    column_info = {
                        'column_name': column.get('columnName', column.get('name', '')),
                        'data_type': column.get('dataType', column.get('type', '')),
                        'category_type': column.get('categoryType', ''),
                        'is_nullable': column.get('isNullable', True),
                        'is_primary_key': column.get('isPrimaryKey', False),
                        'description': column.get('description', '')
                    }
                    view_schema['columns'].append(column_info)
                
                print(f"      - {len(columns)} 個の列を取得")
                workspace_schema['views'].append(view_schema)
            
            schema_data['workspaces'].append(workspace_schema)
        
        return schema_data
    
    def save_schema_to_json(self, schema_data, filename='zoho_schema.json'):
        """スキーマデータをJSONファイルに保存"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(schema_data, f, indent=2, ensure_ascii=False)
        print(f"✓ スキーマデータを {filename} に保存しました")
    
    def create_schema_summary(self, schema_data):
        """スキーマサマリーを作成"""
        summary_data = []
        
        for workspace in schema_data['workspaces']:
            for view in workspace['views']:
                for column in view['columns']:
                    summary_data.append({
                        'workspace_name': workspace['workspace_name'],
                        'view_name': view['view_name'],
                        'view_type': view['view_type'],
                        'column_name': column['column_name'],
                        'data_type': column['data_type'],
                        'category_type': column['category_type'],
                        'is_nullable': column['is_nullable'],
                        'is_primary_key': column['is_primary_key']
                    })
        
        df = pd.DataFrame(summary_data)
        return df
    
    def save_schema_to_excel(self, schema_data, filename='zoho_schema.xlsx'):
        """スキーマデータをExcelファイルに保存"""
        df = self.create_schema_summary(schema_data)
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # サマリーシート
            df.to_excel(writer, sheet_name='Schema_Summary', index=False)
            
            # ワークスペース別シート
            for workspace in schema_data['workspaces']:
                workspace_name = workspace['workspace_name'][:30]  # シート名は30文字まで
                
                workspace_data = []
                for view in workspace['views']:
                    for column in view['columns']:
                        workspace_data.append({
                            'view_name': view['view_name'],
                            'view_type': view['view_type'],
                            'column_name': column['column_name'],
                            'data_type': column['data_type'],
                            'category_type': column['category_type'],
                            'is_nullable': column['is_nullable'],
                            'is_primary_key': column['is_primary_key']
                        })
                
                if workspace_data:
                    ws_df = pd.DataFrame(workspace_data)
                    ws_df.to_excel(writer, sheet_name=workspace_name, index=False)
        
        print(f"✓ スキーマデータを {filename} に保存しました")

def main():
    # トークンファイルから読み込み
    if os.path.exists('zoho_tokens.json'):
        with open('zoho_tokens.json', 'r') as f:
            tokens = json.load(f)
        access_token = tokens['access_token']
        print("✓ 保存されたトークンを使用します")
    else:
        access_token = input("アクセストークンを入力してください: ")
    
    # スキーマ抽出実行
    extractor = ZohoSchemaExtractor(access_token)
    
    try:
        schema_data = extractor.extract_complete_schema()
        
        # ファイル保存
        extractor.save_schema_to_json(schema_data)
        extractor.save_schema_to_excel(schema_data)
        
        # 統計情報表示
        total_workspaces = len(schema_data['workspaces'])
        total_views = sum(len(ws['views']) for ws in schema_data['workspaces'])
        total_columns = sum(len(view['columns']) for ws in schema_data['workspaces'] for view in ws['views'])
        
        print(f"\n=== 抽出完了 ===")
        print(f"ワークスペース数: {total_workspaces}")
        print(f"ビュー数: {total_views}")
        print(f"列数: {total_columns}")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()