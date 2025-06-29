import requests
import json
import pandas as pd
from datetime import datetime
import time

class ZohoSchemaFromData:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://analyticsapi.zoho.com/restapi/v2"
        
    def get_headers(self, org_id):
        return {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'Content-Type': 'application/json',
            'ZANALYTICS-ORGID': str(org_id)
        }
    
    def get_table_data_sample(self, workspace_id, view_id, org_id, limit=5):
        """テーブルのサンプルデータを取得してスキーマを推測"""
        url = f"{self.base_url}/workspaces/{workspace_id}/views/{view_id}/data"
        params = {'limit': limit}
        
        try:
            response = requests.get(url, headers=self.get_headers(org_id), params=params)
            
            if response.status_code == 200:
                # UTF-8 BOMを処理
                content = response.content
                if content.startswith(b'\xef\xbb\xbf'):
                    content = content[3:]
                
                data = json.loads(content.decode('utf-8'))
                return data
            else:
                print(f"    データ取得エラー: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"    例外発生: {e}")
            return None
    
    def extract_schema_from_data(self, data_response):
        """データレスポンスからスキーマ情報を抽出"""
        columns = []
        
        if not data_response or 'data' not in data_response:
            return columns
        
        data_content = data_response['data']
        
        # 列情報を探す
        if 'columns' in data_content:
            # 列定義が直接ある場合
            for col in data_content['columns']:
                column_info = {
                    'column_name': col.get('columnName', col.get('name', '')),
                    'data_type': col.get('dataType', col.get('type', '')),
                    'display_name': col.get('displayName', ''),
                    'category_type': col.get('categoryType', ''),
                    'format': col.get('format', ''),
                    'source': 'metadata'
                }
                columns.append(column_info)
        
        elif 'rows' in data_content and len(data_content['rows']) > 0:
            # データ行から列を推測
            if 'columns' in data_content:
                # 列名がある場合
                for col in data_content['columns']:
                    column_info = {
                        'column_name': col.get('columnName', col.get('name', '')),
                        'data_type': self.infer_data_type_from_sample(data_content['rows'], col.get('columnName', '')),
                        'display_name': col.get('displayName', ''),
                        'source': 'inferred_from_data'
                    }
                    columns.append(column_info)
            else:
                # 最初の行のキーから列名を取得
                first_row = data_content['rows'][0]
                if isinstance(first_row, dict):
                    for col_name, value in first_row.items():
                        column_info = {
                            'column_name': col_name,
                            'data_type': self.infer_data_type_from_value(value),
                            'display_name': col_name,
                            'source': 'inferred_from_keys'
                        }
                        columns.append(column_info)
        
        return columns
    
    def infer_data_type_from_value(self, value):
        """値からデータタイプを推測"""
        if value is None:
            return 'null'
        elif isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'integer'
        elif isinstance(value, float):
            return 'decimal'
        elif isinstance(value, str):
            # 日付っぽい文字列かチェック
            if self.looks_like_date(value):
                return 'date'
            return 'text'
        else:
            return 'unknown'
    
    def looks_like_date(self, value):
        """文字列が日付っぽいかチェック"""
        date_patterns = ['-', '/', '年', '月', '日', 'T', ':']
        return any(pattern in str(value) for pattern in date_patterns) and len(str(value)) > 8
    
    def infer_data_type_from_sample(self, rows, column_name):
        """サンプルデータから列のデータタイプを推測"""
        values = []
        for row in rows:
            if isinstance(row, dict) and column_name in row:
                values.append(row[column_name])
        
        if not values:
            return 'unknown'
        
        # 非null値を分析
        non_null_values = [v for v in values if v is not None]
        if not non_null_values:
            return 'null'
        
        # 最初の非null値でタイプを判定
        return self.infer_data_type_from_value(non_null_values[0])
    
    def extract_schema_for_tables(self, table_list, max_tables=None):
        """テーブルリストからスキーマを抽出"""
        if max_tables:
            table_list = table_list[:max_tables]
        
        schema_data = {
            'extraction_date': datetime.now().isoformat(),
            'extraction_method': 'data_sampling',
            'workspace_id': table_list[0]['workspace_id'] if table_list else '',
            'workspace_name': table_list[0]['workspace_name'] if table_list else '',
            'tables': []
        }
        
        print(f"データサンプリングによるスキーマ抽出: {len(table_list)} テーブル")
        
        success_count = 0
        for i, table in enumerate(table_list, 1):
            workspace_id = table['workspace_id']
            view_id = table['view_id']
            view_name = table['view_name']
            org_id = table['org_id']
            
            print(f"{i:3d}/{len(table_list)}: {view_name}")
            
            # サンプルデータ取得
            data_response = self.get_table_data_sample(workspace_id, view_id, org_id)
            
            if data_response:
                columns = self.extract_schema_from_data(data_response)
                
                table_schema = {
                    'view_id': view_id,
                    'view_name': view_name,
                    'view_type': table['view_type'],
                    'description': table['description'],
                    'created_time': table['created_time'],
                    'created_by': table['created_by'],
                    'column_count': len(columns),
                    'columns': columns,
                    'data_sample_available': True
                }
                
                schema_data['tables'].append(table_schema)
                success_count += 1
                print(f"    ✓ {len(columns)} 個の列を推測")
            else:
                print(f"    ✗ データ取得失敗")
            
            # レート制限対策
            if i % 10 == 0:
                time.sleep(1)
        
        print(f"\n抽出完了: {success_count}/{len(table_list)} テーブル")
        return schema_data
    
    def save_schema_results(self, schema_data, filename='zoho_schema_from_data.xlsx'):
        """結果をExcelに保存"""
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
                    'display_name': column.get('display_name', ''),
                    'category_type': column.get('category_type', ''),
                    'format': column.get('format', ''),
                    'source': column.get('source', '')
                }
                all_columns.append(column_detail)
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            if table_summary:
                summary_df = pd.DataFrame(table_summary)
                summary_df.to_excel(writer, sheet_name='Table_Summary', index=False)
            
            if all_columns:
                columns_df = pd.DataFrame(all_columns)
                columns_df.to_excel(writer, sheet_name='All_Columns', index=False)
                
                # データタイプ分析
                dtype_summary = columns_df['data_type'].value_counts().reset_index()
                dtype_summary.columns = ['data_type', 'count']
                dtype_summary.to_excel(writer, sheet_name='DataType_Summary', index=False)
        
        # JSONでも保存
        json_filename = filename.replace('.xlsx', '.json')
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(schema_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ スキーマ情報を {filename} と {json_filename} に保存")

def main():
    # トークン読み込み
    with open('zoho_tokens.json', 'r') as f:
        tokens = json.load(f)
    access_token = tokens['access_token']
    
    # テーブル一覧読み込み
    try:
        df = pd.read_excel('zoho_table_list.xlsx', sheet_name='Main_Tables')
        table_list = df.to_dict('records')
        print(f"✓ {len(table_list)} 個の主要テーブルを読み込み")
    except Exception as e:
        print(f"テーブル一覧読み込みエラー: {e}")
        return
    
    extractor = ZohoSchemaFromData(access_token)
    
    # 最初の30テーブルでテスト
    max_tables = 30
    
    try:
        schema_data = extractor.extract_schema_for_tables(table_list, max_tables=max_tables)
        extractor.save_schema_results(schema_data)
        
        # 統計表示
        total_tables = len(schema_data['tables'])
        total_columns = sum(t['column_count'] for t in schema_data['tables'])
        
        print(f"\n=== スキーマ抽出完了 ===")
        print(f"成功テーブル数: {total_tables}")
        print(f"総列数: {total_columns}")
        
        if total_tables > 0:
            avg_columns = total_columns / total_tables
            print(f"平均列数: {avg_columns:.1f}")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()