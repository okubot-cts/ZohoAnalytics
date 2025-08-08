#!/usr/bin/env python3
"""
ZohoAnalyticsワークスペースのテーブルスキーマ情報を取得してファイルに保存
"""

from zoho_analytics_helper import ZohoAnalyticsHelper
from token_manager import ZohoTokenManager
import json
import os
from datetime import datetime

def get_schema_info():
    """ワークスペースのスキーマ情報を取得"""
    
    # CRMワークスペースのID
    crm_workspace_id = '2527115000001040002'
    
    # トークンマネージャー初期化
    token_manager = ZohoTokenManager()
    helper = ZohoAnalyticsHelper(token_manager)
    
    try:
        print('=== ZohoAnalytics スキーマ情報取得 ===\n')
        
        # ワークスペース情報を取得
        print('1. ワークスペース情報を取得中...')
        workspaces = helper.get_workspaces()
        
        # 対象ワークスペースを探す
        target_workspace = None
        all_workspaces = []
        if 'data' in workspaces:
            if 'ownedWorkspaces' in workspaces['data']:
                all_workspaces.extend(workspaces['data']['ownedWorkspaces'])
            if 'sharedWorkspaces' in workspaces['data']:
                all_workspaces.extend(workspaces['data']['sharedWorkspaces'])
        
        for ws in all_workspaces:
            if ws['workspaceId'] == crm_workspace_id:
                target_workspace = ws
                break
        
        if not target_workspace:
            print(f'❌ ワークスペースID {crm_workspace_id} が見つかりません')
            return
        
        print(f'✅ ワークスペース: {target_workspace["workspaceName"]}')
        
        # テーブル一覧を取得
        print('\n2. テーブル一覧を取得中...')
        tables_info = helper.get_tables(crm_workspace_id)
        
        if 'data' not in tables_info or 'views' not in tables_info['data']:
            print('❌ テーブル情報の取得に失敗しました')
            return
        
        views = tables_info['data']['views']
        tables = [v for v in views if v.get('viewType') == 'Table']
        
        print(f'✅ テーブル数: {len(tables)}件')
        
        # スキーマ情報を収集
        schema_data = {
            'workspace_info': target_workspace,
            'generated_at': datetime.now().isoformat(),
            'tables': []
        }
        
        print('\n3. 各テーブルのスキーマ情報を取得中...')
        
        for i, table in enumerate(tables, 1):
            table_name = table.get('viewName', 'Unknown')
            table_id = table.get('viewId')
            
            print(f'  {i}/{len(tables)}: {table_name} (ID: {table_id})')
            
            try:
                # テーブルのメタデータを取得
                metadata = helper.get_table_metadata(crm_workspace_id, table_id)
                
                table_schema = {
                    'table_name': table_name,
                    'table_id': table_id,
                    'table_type': table.get('viewType'),
                    'description': table.get('description', ''),
                    'created_time': table.get('createdTime'),
                    'modified_time': table.get('modifiedTime'),
                    'columns': []
                }
                
                # カラム情報を抽出
                if 'data' in metadata and 'columns' in metadata['data']:
                    for col in metadata['data']['columns']:
                        column_info = {
                            'column_name': col.get('columnName'),
                            'display_name': col.get('displayName'),
                            'data_type': col.get('dataType'),
                            'column_type': col.get('columnType'),
                            'aggregation_type': col.get('aggregationType'),
                            'is_hidden': col.get('isHidden', False),
                            'is_formula': col.get('isFormula', False),
                            'description': col.get('description', '')
                        }
                        table_schema['columns'].append(column_info)
                
                # 追加のメタデータ情報
                if 'data' in metadata:
                    table_schema['row_count'] = metadata['data'].get('noOfRows', 0)
                    table_schema['column_count'] = metadata['data'].get('noOfColumns', 0)
                
                schema_data['tables'].append(table_schema)
                
            except Exception as e:
                print(f'    ⚠️ テーブル {table_name} のメタデータ取得エラー: {e}')
                # エラーでも基本情報は保存
                table_schema = {
                    'table_name': table_name,
                    'table_id': table_id,
                    'table_type': table.get('viewType'),
                    'error': str(e)
                }
                schema_data['tables'].append(table_schema)
        
        # JSONファイルに保存
        output_filename = f'zoho_analytics_schema_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(schema_data, f, indent=2, ensure_ascii=False)
        
        print(f'\n✅ スキーマ情報をファイルに保存しました: {output_filename}')
        
        # 人間が読みやすい形式でも出力
        readable_filename = f'zoho_analytics_schema_readable_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        with open(readable_filename, 'w', encoding='utf-8') as f:
            f.write(f'ZohoAnalytics ワークスペース スキーマ情報\n')
            f.write(f'=' * 50 + '\n\n')
            f.write(f'ワークスペース名: {target_workspace["workspaceName"]}\n')
            f.write(f'ワークスペースID: {target_workspace["workspaceId"]}\n')
            f.write(f'取得日時: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'テーブル数: {len(schema_data["tables"])}\n\n')
            
            for table in schema_data['tables']:
                f.write(f'【テーブル】{table["table_name"]}\n')
                f.write(f'  ID: {table["table_id"]}\n')
                f.write(f'  タイプ: {table.get("table_type", "Unknown")}\n')
                
                if 'row_count' in table:
                    f.write(f'  行数: {table["row_count"]:,}\n')
                if 'column_count' in table:
                    f.write(f'  列数: {table["column_count"]}\n')
                
                if table.get('description'):
                    f.write(f'  説明: {table["description"]}\n')
                
                if 'error' in table:
                    f.write(f'  ❌ エラー: {table["error"]}\n')
                else:
                    f.write(f'  カラム一覧:\n')
                    for col in table.get('columns', []):
                        col_name = col.get('column_name', 'Unknown')
                        display_name = col.get('display_name', '')
                        data_type = col.get('data_type', '')
                        
                        f.write(f'    - {col_name}')
                        if display_name and display_name != col_name:
                            f.write(f' ({display_name})')
                        if data_type:
                            f.write(f' [{data_type}]')
                        f.write('\n')
                
                f.write('\n')
        
        print(f'✅ 読みやすい形式でも保存しました: {readable_filename}')
        
        # サマリー表示
        print(f'\n📊 取得結果サマリー:')
        print(f'  ワークスペース: {target_workspace["workspaceName"]}')
        print(f'  テーブル数: {len(schema_data["tables"])}')
        
        successful_tables = [t for t in schema_data['tables'] if 'error' not in t]
        error_tables = [t for t in schema_data['tables'] if 'error' in t]
        
        print(f'  成功: {len(successful_tables)}テーブル')
        if error_tables:
            print(f'  エラー: {len(error_tables)}テーブル')
            for table in error_tables:
                print(f'    - {table["table_name"]}: {table["error"]}')
        
        total_columns = sum(len(t.get('columns', [])) for t in successful_tables)
        print(f'  総カラム数: {total_columns}')
        
    except Exception as e:
        print(f'❌ エラーが発生しました: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_schema_info()