import requests
import json
import pandas as pd
from datetime import datetime
import time

class ZohoSchemaDetailed:
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
    
    def get_view_metadata(self, workspace_id, view_id, org_id):
        """ビューの詳細メタデータを取得"""
        # 複数のエンドポイントを試行
        endpoints = [
            f"{self.base_url}/workspaces/{workspace_id}/views/{view_id}",
            f"{self.base_url}/workspaces/{workspace_id}/views/{view_id}/metadata"
        ]
        
        for url in endpoints:
            try:
                response = requests.get(url, headers=self.get_headers(org_id))
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # レスポンス構造を確認
                    if 'data' in data:
                        view_data = data['data']
                        if isinstance(view_data, dict):
                            return view_data
                        elif isinstance(view_data, list) and len(view_data) > 0:
                            return view_data[0]
                    
                    return data
                    
            except Exception as e:
                print(f"    エラー（{url}）: {e}")
                continue
        
        return None
    
    def extract_columns_from_metadata(self, metadata):
        """メタデータから列情報を抽出"""
        columns = []
        
        if not metadata:
            return columns
        
        # 様々な可能性のある列情報の場所をチェック
        column_sources = [
            metadata.get('columns', []),
            metadata.get('fields', []),
            metadata.get('schema', {}).get('columns', []),
            metadata.get('viewSchema', {}).get('columns', [])
        ]
        
        for source in column_sources:
            if source and isinstance(source, list):
                for col in source:
                    if isinstance(col, dict):
                        column_info = {
                            'column_name': col.get('columnName', col.get('name', col.get('fieldName', ''))),
                            'data_type': col.get('dataType', col.get('type', col.get('fieldType', ''))),
                            'category_type': col.get('categoryType', ''),
                            'display_name': col.get('displayName', col.get('label', '')),
                            'is_nullable': col.get('isNullable', True),
                            'is_primary_key': col.get('isPrimaryKey', False),
                            'description': col.get('description', ''),
                            'format': col.get('format', ''),
                            'aggregation': col.get('aggregationType', '')
                        }
                        columns.append(column_info)
                break  # 最初に見つかった有効なソースを使用
        
        return columns
    
    def get_schema_for_tables(self, table_list, max_tables=None):
        """主要テーブルのスキーマ情報を取得"""
        schema_data = {
            'extraction_date': datetime.now().isoformat(),
            'workspace_id': table_list[0]['workspace_id'] if table_list else '',
            'workspace_name': table_list[0]['workspace_name'] if table_list else '',
            'tables': []
        }
        
        # 処理するテーブル数を制限
        if max_tables:
            table_list = table_list[:max_tables]
        
        print(f"スキーマ抽出開始: {len(table_list)} 個のテーブルを処理")
        
        success_count = 0
        for i, table in enumerate(table_list, 1):
            workspace_id = table['workspace_id']
            view_id = table['view_id']
            view_name = table['view_name']
            org_id = table['org_id']
            
            print(f"{i:3d}/{len(table_list)}: {view_name}")
            
            # メタデータ取得
            metadata = self.get_view_metadata(workspace_id, view_id, org_id)
            
            if metadata:
                columns = self.extract_columns_from_metadata(metadata)
                
                table_schema = {
                    'view_id': view_id,
                    'view_name': view_name,
                    'view_type': table['view_type'],
                    'description': table['description'],
                    'created_time': table['created_time'],
                    'created_by': table['created_by'],
                    'column_count': len(columns),
                    'columns': columns
                }
                
                schema_data['tables'].append(table_schema)
                success_count += 1
                print(f"    ✓ {len(columns)} 個の列を取得")
            else:
                print(f"    ✗ メタデータ取得失敗")
            
            # レート制限を避けるため少し待機
            if i % 10 == 0:
                time.sleep(1)
        
        print(f"\n取得完了: {success_count}/{len(table_list)} テーブル")
        return schema_data
    
    def save_detailed_schema(self, schema_data, filename='zoho_detailed_schema.xlsx'):
        """詳細スキーマをExcelに保存"""
        # テーブルサマリー
        table_summary = []
        all_columns = []
        
        for table in schema_data['tables']:
            table_summary.append({
                'view_name': table['view_name'],
                'view_type': table['view_type'],
                'column_count': table['column_count'],
                'created_time': table['created_time'],
                'created_by': table['created_by'],
                'description': table['description']
            })
            
            for column in table['columns']:
                column_detail = {
                    'table_name': table['view_name'],
                    'column_name': column['column_name'],
                    'data_type': column['data_type'],
                    'category_type': column['category_type'],
                    'display_name': column['display_name'],
                    'is_nullable': column['is_nullable'],
                    'is_primary_key': column['is_primary_key'],
                    'description': column['description'],
                    'format': column['format'],
                    'aggregation': column['aggregation']
                }
                all_columns.append(column_detail)
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # テーブルサマリー
            if table_summary:
                summary_df = pd.DataFrame(table_summary)
                summary_df.to_excel(writer, sheet_name='Table_Summary', index=False)
            
            # 全列情報
            if all_columns:
                columns_df = pd.DataFrame(all_columns)
                columns_df.to_excel(writer, sheet_name='All_Columns', index=False)
            
            # データタイプ分析
            if all_columns:
                dtype_summary = columns_df['data_type'].value_counts().reset_index()
                dtype_summary.columns = ['data_type', 'count']
                dtype_summary.to_excel(writer, sheet_name='DataType_Summary', index=False)
        
        # JSONでも保存
        json_filename = filename.replace('.xlsx', '.json')
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(schema_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 詳細スキーマを {filename} と {json_filename} に保存")

def main():
    # トークン読み込み
    with open('zoho_tokens.json', 'r') as f:
        tokens = json.load(f)
    access_token = tokens['access_token']
    
    # テーブル一覧を読み込み
    try:
        df = pd.read_excel('zoho_table_list.xlsx', sheet_name='Main_Tables')
        table_list = df.to_dict('records')
        print(f"✓ {len(table_list)} 個の主要テーブルを読み込み")
    except Exception as e:
        print(f"テーブル一覧の読み込みエラー: {e}")
        return
    
    extractor = ZohoSchemaDetailed(access_token)
    
    # 最初の20テーブルのみテスト（全て処理する場合はmax_tables=Noneに設定）
    max_tables = 20
    
    try:
        schema_data = extractor.get_schema_for_tables(table_list, max_tables=max_tables)
        extractor.save_detailed_schema(schema_data)
        
        # 統計表示
        total_tables = len(schema_data['tables'])
        total_columns = sum(t['column_count'] for t in schema_data['tables'])
        
        print(f"\n=== 詳細スキーマ取得完了 ===")
        print(f"取得テーブル数: {total_tables}")
        print(f"総列数: {total_columns}")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()