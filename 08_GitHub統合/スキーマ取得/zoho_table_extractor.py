import requests
import json
import pandas as pd
from datetime import datetime

class ZohoTableExtractor:
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
                workspaces.extend(data['data'].get('ownedWorkspaces', []))
                workspaces.extend(data['data'].get('sharedWorkspaces', []))
            return workspaces
        else:
            raise Exception(f"ワークスペース取得エラー: {response.status_code} - {response.text}")
    
    def get_workspace_views(self, workspace_id, org_id):
        """指定ワークスペースの全ビューを取得（基本情報のみ）"""
        url = f"{self.base_url}/workspaces/{workspace_id}/views"
        response = requests.get(url, headers=self.get_headers(org_id))
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                return data['data'].get('views', [])
            return data.get('views', [])
        else:
            print(f"Warning: ワークスペース {workspace_id} のビュー取得に失敗: {response.status_code}")
            return []
    
    def get_table_list(self, target_workspace_id=None):
        """テーブル一覧を取得（ビュータイプでフィルタ）"""
        workspaces = self.get_all_workspaces()
        print(f"✓ {len(workspaces)} 個のワークスペースを発見")
        
        all_tables = []
        
        for workspace in workspaces:
            workspace_id = workspace['workspaceId']
            workspace_name = workspace['workspaceName']
            org_id = workspace.get('orgId')
            
            # 特定のワークスペースのみ処理する場合
            if target_workspace_id and workspace_id != target_workspace_id:
                continue
            
            print(f"\n処理中: {workspace_name} (ID: {workspace_id})")
            
            views = self.get_workspace_views(workspace_id, org_id)
            print(f"  - {len(views)} 個のビューを発見")
            
            for view in views:
                table_info = {
                    'workspace_id': workspace_id,
                    'workspace_name': workspace_name,
                    'org_id': org_id,
                    'view_id': view.get('viewId', view.get('id')),
                    'view_name': view.get('viewName', view.get('name')),
                    'view_type': view.get('viewType', view.get('type', '')),
                    'description': view.get('description', ''),
                    'created_time': view.get('createdTime', ''),
                    'created_by': view.get('createdBy', ''),
                    'is_table': view.get('viewType', '').lower() == 'table'
                }
                all_tables.append(table_info)
        
        return all_tables
    
    def filter_main_tables(self, tables):
        """主要なテーブルを抽出"""
        # テーブルタイプのみをフィルタ
        main_tables = [t for t in tables if t['is_table']]
        
        # システム系やレポート系のテーブルを除外
        excluded_keywords = [
            'log', 'audit', 'activity', 'trend', 'summary', 'dashboard',
            'report', 'analysis', 'insight', 'statistics', 'count',
            'distribution', 'ratio', 'margin'
        ]
        
        filtered_tables = []
        for table in main_tables:
            table_name_lower = table['view_name'].lower()
            if not any(keyword in table_name_lower for keyword in excluded_keywords):
                filtered_tables.append(table)
        
        return filtered_tables
    
    def save_table_list_to_excel(self, tables, filename='zoho_table_list.xlsx'):
        """テーブル一覧をExcelに保存"""
        df = pd.DataFrame(tables)
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 全テーブル一覧
            df.to_excel(writer, sheet_name='All_Views', index=False)
            
            # テーブルタイプのみ
            table_only = df[df['is_table'] == True]
            if not table_only.empty:
                table_only.to_excel(writer, sheet_name='Tables_Only', index=False)
            
            # 主要テーブル
            main_tables = self.filter_main_tables(tables)
            if main_tables:
                main_df = pd.DataFrame(main_tables)
                main_df.to_excel(writer, sheet_name='Main_Tables', index=False)
            
            # ワークスペース別サマリー
            workspace_summary = df.groupby(['workspace_name', 'view_type']).size().reset_index(name='count')
            workspace_summary.to_excel(writer, sheet_name='Workspace_Summary', index=False)
        
        print(f"✓ テーブル一覧を {filename} に保存しました")
        return main_tables

def main():
    # トークンファイルから読み込み
    with open('zoho_tokens.json', 'r') as f:
        tokens = json.load(f)
    access_token = tokens['access_token']
    
    print("=== Zoho Analytics テーブル一覧取得 ===")
    
    # 指定されたワークスペースのみ処理
    target_workspace = "2527115000001040002"  # Zoho CRMの分析
    
    extractor = ZohoTableExtractor(access_token)
    
    try:
        # テーブル一覧取得
        tables = extractor.get_table_list(target_workspace)
        
        # Excel保存と主要テーブル抽出
        main_tables = extractor.save_table_list_to_excel(tables)
        
        # 統計情報表示
        total_views = len(tables)
        table_views = len([t for t in tables if t['is_table']])
        main_table_count = len(main_tables)
        
        print(f"\n=== 取得完了 ===")
        print(f"総ビュー数: {total_views}")
        print(f"テーブル数: {table_views}")
        print(f"主要テーブル数: {main_table_count}")
        
        if main_tables:
            print(f"\n=== 主要テーブル一覧 ===")
            for i, table in enumerate(main_tables[:10], 1):  # 最初の10個を表示
                print(f"{i:2d}. {table['view_name']} ({table['workspace_name']})")
            
            if len(main_tables) > 10:
                print(f"    ... 他 {len(main_tables) - 10} 個")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()