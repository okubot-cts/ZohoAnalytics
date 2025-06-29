import requests
import json
import pandas as pd
from datetime import datetime
import time

class ZohoFilteredSchema:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://analyticsapi.zoho.com/restapi/v2"
        
    def get_headers(self, org_id):
        return {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'Content-Type': 'application/json',
            'ZANALYTICS-ORGID': str(org_id)
        }
    
    def get_table_data_sample(self, workspace_id, view_id, org_id, limit=3):
        """テーブルのサンプルデータを取得（高速化のため3行のみ）"""
        url = f"{self.base_url}/workspaces/{workspace_id}/views/{view_id}/data"
        params = {'limit': limit}
        
        try:
            response = requests.get(url, headers=self.get_headers(org_id), params=params, timeout=10)
            
            if response.status_code == 200:
                content = response.content
                if content.startswith(b'\xef\xbb\xbf'):
                    content = content[3:]
                data = json.loads(content.decode('utf-8'))
                return data
            else:
                return None
                
        except Exception as e:
            return None
    
    def extract_schema_from_data(self, data_response):
        """データレスポンスからスキーマ情報を抽出"""
        columns = []
        
        if not data_response or 'data' not in data_response:
            return columns
        
        data_content = data_response['data']
        
        # 列情報を直接取得できる場合
        if 'columns' in data_content:
            for col in data_content['columns']:
                column_info = {
                    'column_name': col.get('columnName', col.get('name', '')),
                    'data_type': col.get('dataType', col.get('type', '')),
                    'display_name': col.get('displayName', ''),
                    'category_type': col.get('categoryType', ''),
                    'source': 'metadata'
                }
                columns.append(column_info)
        
        # データ行から推測
        elif 'rows' in data_content and len(data_content['rows']) > 0:
            first_row = data_content['rows'][0]
            if isinstance(first_row, dict):
                for col_name, value in first_row.items():
                    column_info = {
                        'column_name': col_name,
                        'data_type': self.infer_data_type(value),
                        'display_name': col_name,
                        'source': 'inferred'
                    }
                    columns.append(column_info)
        
        return columns
    
    def infer_data_type(self, value):
        """値からデータタイプを推測"""
        if value is None or value == '':
            return 'text'
        elif isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'integer'
        elif isinstance(value, float):
            return 'decimal'
        elif isinstance(value, str):
            if any(char in value for char in ['-', '/', '年', '月', 'T', ':']):
                return 'date'
            return 'text'
        else:
            return 'text'
    
    def extract_schemas_batch(self, table_file='filtered_target_tables.xlsx'):
        """フィルタされたテーブルのスキーマを一括取得"""
        # テーブル一覧読み込み
        df = pd.read_excel(table_file)
        table_list = df.to_dict('records')
        
        print(f"対象テーブル数: {len(table_list)} 個")
        print("スキーマ抽出開始...")
        
        schema_data = {
            'extraction_date': datetime.now().isoformat(),
            'total_tables': len(table_list),
            'workspace_id': table_list[0]['workspace_id'] if table_list else '',
            'workspace_name': table_list[0]['workspace_name'] if table_list else '',
            'tables': []
        }
        
        success_count = 0
        failed_tables = []
        
        # 進捗表示用
        batch_size = 10
        
        for i, table in enumerate(table_list, 1):
            workspace_id = table['workspace_id']
            view_id = table['view_id']
            view_name = table['view_name']
            org_id = table['org_id']
            
            if i % batch_size == 1 or batch_size == 1:
                print(f"\n--- バッチ {((i-1)//batch_size)+1} ({i}-{min(i+batch_size-1, len(table_list))}) ---")
            
            print(f"{i:3d}: {view_name[:40]:<40}", end=" ")
            
            # データ取得
            data_response = self.get_table_data_sample(workspace_id, view_id, org_id)
            
            if data_response:
                columns = self.extract_schema_from_data(data_response)
                
                table_schema = {
                    'view_id': view_id,
                    'view_name': view_name,
                    'view_type': table.get('view_type', ''),
                    'description': table.get('description', ''),
                    'column_count': len(columns),
                    'columns': columns
                }
                
                schema_data['tables'].append(table_schema)
                success_count += 1
                print(f"✓ {len(columns)} 列")
            else:
                failed_tables.append(view_name)
                print("✗ 失敗")
            
            # プログレスレポート
            if i % (batch_size * 2) == 0:
                success_rate = (success_count / i) * 100
                print(f"\n  進捗: {i}/{len(table_list)} ({success_rate:.1f}% 成功)")
            
            # レート制限対策（簡易版）
            if i % 5 == 0:
                time.sleep(0.5)
        
        # 最終結果
        print(f"\n{'='*60}")
        print(f"抽出完了: {success_count}/{len(table_list)} テーブル ({(success_count/len(table_list)*100):.1f}%)")
        
        if failed_tables:
            print(f"失敗したテーブル数: {len(failed_tables)}")
        
        return schema_data, failed_tables
    
    def save_results(self, schema_data, failed_tables, filename='zoho_filtered_schema.xlsx'):
        """結果を保存"""
        # テーブルサマリー
        table_summary = []
        all_columns = []
        
        for table in schema_data['tables']:
            table_summary.append({
                'view_name': table['view_name'],
                'view_type': table['view_type'],
                'column_count': table['column_count'],
                'description': table['description']
            })
            
            for column in table['columns']:
                all_columns.append({
                    'table_name': table['view_name'],
                    'column_name': column['column_name'],
                    'data_type': column['data_type'],
                    'display_name': column.get('display_name', ''),
                    'source': column.get('source', '')
                })
        
        # Excel保存
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            if table_summary:
                pd.DataFrame(table_summary).to_excel(writer, sheet_name='Table_Summary', index=False)
            
            if all_columns:
                pd.DataFrame(all_columns).to_excel(writer, sheet_name='All_Columns', index=False)
                
                # データタイプ統計
                dtype_counts = pd.DataFrame(all_columns)['data_type'].value_counts().reset_index()
                dtype_counts.columns = ['data_type', 'count']
                dtype_counts.to_excel(writer, sheet_name='DataType_Stats', index=False)
            
            # 失敗テーブル一覧
            if failed_tables:
                pd.DataFrame({'failed_table': failed_tables}).to_excel(
                    writer, sheet_name='Failed_Tables', index=False)
        
        # JSON保存
        json_filename = filename.replace('.xlsx', '.json')
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(schema_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 結果を {filename} と {json_filename} に保存")

def main():
    # トークン読み込み
    with open('zoho_tokens.json', 'r') as f:
        tokens = json.load(f)
    access_token = tokens['access_token']
    
    extractor = ZohoFilteredSchema(access_token)
    
    try:
        start_time = time.time()
        schema_data, failed_tables = extractor.extract_schemas_batch()
        
        extractor.save_results(schema_data, failed_tables)
        
        elapsed_time = time.time() - start_time
        total_columns = sum(t['column_count'] for t in schema_data['tables'])
        
        print(f"\n=== 最終結果 ===")
        print(f"処理時間: {elapsed_time:.1f}秒")
        print(f"成功テーブル数: {len(schema_data['tables'])}")
        print(f"総列数: {total_columns}")
        print(f"平均列数: {total_columns/len(schema_data['tables']):.1f}" if schema_data['tables'] else "N/A")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()