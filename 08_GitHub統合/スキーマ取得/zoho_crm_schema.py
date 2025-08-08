import requests
import json
import pandas as pd
from datetime import datetime

class ZohoCRMSchema:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://www.zohoapis.com/crm/v2"
        
    def get_headers(self):
        return {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_all_modules(self):
        """全モジュール（タブ）の一覧を取得"""
        url = f"{self.base_url}/settings/modules"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                data = response.json()
                return data.get('modules', [])
            else:
                print(f"モジュール取得エラー: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"例外発生: {e}")
            return []
    
    def get_module_fields(self, module_api_name):
        """指定モジュールのフィールド情報を取得"""
        url = f"{self.base_url}/settings/fields"
        params = {'module': module_api_name}
        
        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('fields', [])
            else:
                print(f"フィールド取得エラー ({module_api_name}): {response.status_code}")
                return []
                
        except Exception as e:
            print(f"フィールド取得例外 ({module_api_name}): {e}")
            return []
    
    def extract_complete_crm_schema(self):
        """CRM全体のスキーマを抽出"""
        print("Zoho CRMスキーマ抽出開始...")
        
        schema_data = {
            'extraction_date': datetime.now().isoformat(),
            'extraction_source': 'zoho_crm_api_v2',
            'modules': []
        }
        
        # 全モジュール取得
        modules = self.get_all_modules()
        print(f"✓ {len(modules)} 個のモジュールを発見")
        
        success_count = 0
        
        for i, module in enumerate(modules, 1):
            module_api_name = module.get('api_name')
            module_display_name = module.get('display_label', module.get('module_name', ''))
            
            print(f"{i:2d}/{len(modules)}: {module_display_name} ({module_api_name})")
            
            # フィールド情報取得
            fields = self.get_module_fields(module_api_name)
            
            if fields:
                # フィールド情報を整理
                processed_fields = []
                for field in fields:
                    field_info = {
                        'api_name': field.get('api_name'),
                        'display_label': field.get('field_label', field.get('display_label', '')),
                        'data_type': field.get('data_type'),
                        'length': field.get('length'),
                        'required': field.get('required', False),
                        'read_only': field.get('read_only', False),
                        'custom_field': field.get('custom_field', False),
                        'default_value': field.get('default_value'),
                        'picklist_values': field.get('pick_list_values', []) if field.get('data_type') == 'picklist' else [],
                        'lookup_module': field.get('lookup', {}).get('module') if field.get('lookup') else None,
                        'formula': field.get('formula', {}).get('expression') if field.get('formula') else None
                    }
                    processed_fields.append(field_info)
                
                module_schema = {
                    'api_name': module_api_name,
                    'display_name': module_display_name,
                    'module_type': module.get('module_type'),
                    'sequence_number': module.get('sequence_number'),
                    'singular_label': module.get('singular_label'),
                    'plural_label': module.get('plural_label'),
                    'field_count': len(processed_fields),
                    'fields': processed_fields,
                    'is_deletable': module.get('deletable', False),
                    'is_creatable': module.get('creatable', False),
                    'is_editable': module.get('editable', False)
                }
                
                schema_data['modules'].append(module_schema)
                success_count += 1
                print(f"    ✓ {len(processed_fields)} 個のフィールドを取得")
            else:
                print(f"    ✗ フィールド取得失敗")
        
        print(f"\n取得完了: {success_count}/{len(modules)} モジュール")
        return schema_data
    
    def save_crm_schema(self, schema_data, filename='zoho_crm_schema.xlsx'):
        """CRMスキーマをExcelに保存"""
        # モジュールサマリー
        module_summary = []
        all_fields = []
        
        for module in schema_data['modules']:
            module_summary.append({
                'api_name': module['api_name'],
                'display_name': module['display_name'],
                'module_type': module['module_type'],
                'field_count': module['field_count'],
                'is_creatable': module['is_creatable'],
                'is_editable': module['is_editable'],
                'is_deletable': module['is_deletable']
            })
            
            for field in module['fields']:
                field_detail = {
                    'module_name': module['display_name'],
                    'module_api_name': module['api_name'],
                    'field_api_name': field['api_name'],
                    'field_display_name': field['display_label'],
                    'data_type': field['data_type'],
                    'length': field['length'],
                    'required': field['required'],
                    'read_only': field['read_only'],
                    'custom_field': field['custom_field'],
                    'default_value': field['default_value'],
                    'lookup_module': field['lookup_module'],
                    'picklist_count': len(field['picklist_values']) if field['picklist_values'] else 0
                }
                all_fields.append(field_detail)
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # モジュールサマリー
            if module_summary:
                module_df = pd.DataFrame(module_summary)
                module_df.to_excel(writer, sheet_name='Modules', index=False)
            
            # 全フィールド情報
            if all_fields:
                fields_df = pd.DataFrame(all_fields)
                fields_df.to_excel(writer, sheet_name='All_Fields', index=False)
                
                # データタイプ分析
                dtype_summary = fields_df['data_type'].value_counts().reset_index()
                dtype_summary.columns = ['data_type', 'count']
                dtype_summary.to_excel(writer, sheet_name='DataType_Summary', index=False)
                
                # カスタムフィールド
                custom_fields = fields_df[fields_df['custom_field'] == True]
                if not custom_fields.empty:
                    custom_fields.to_excel(writer, sheet_name='Custom_Fields', index=False)
                
                # 必須フィールド
                required_fields = fields_df[fields_df['required'] == True]
                if not required_fields.empty:
                    required_fields.to_excel(writer, sheet_name='Required_Fields', index=False)
        
        # JSONでも保存
        json_filename = filename.replace('.xlsx', '.json')
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(schema_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ CRMスキーマを {filename} と {json_filename} に保存")
    
    def filter_main_modules(self, schema_data):
        """主要モジュールのみを抽出"""
        # 主要なビジネスモジュール
        main_module_keywords = [
            'deals', 'contacts', 'accounts', 'leads', 'tasks', 'events',
            '商談', '連絡先', '取引先', '見込み客', 'タスク',
            'products', 'quotes', 'invoices', 'campaigns'
        ]
        
        main_modules = []
        for module in schema_data['modules']:
            module_name_lower = module['display_name'].lower()
            api_name_lower = module['api_name'].lower()
            
            if any(keyword in module_name_lower or keyword in api_name_lower 
                   for keyword in main_module_keywords):
                main_modules.append(module)
        
        return main_modules

def main():
    # CRM用トークンを使用
    try:
        with open('zoho_crm_tokens.json', 'r') as f:
            tokens = json.load(f)
        access_token = tokens['access_token']
        print("✓ CRM用トークンを使用")
        print(f"  スコープ: {tokens.get('scope', 'N/A')}")
    except:
        print("エラー: zoho_crm_tokens.jsonが見つかりません")
        return
    
    crm_extractor = ZohoCRMSchema(access_token)
    
    try:
        # CRMスキーマ抽出
        schema_data = crm_extractor.extract_complete_crm_schema()
        
        # 結果保存
        crm_extractor.save_crm_schema(schema_data)
        
        # 主要モジュール抽出
        main_modules = crm_extractor.filter_main_modules(schema_data)
        
        # 統計表示
        total_modules = len(schema_data['modules'])
        total_fields = sum(m['field_count'] for m in schema_data['modules'])
        main_module_count = len(main_modules)
        
        print(f"\n=== CRMスキーマ抽出完了 ===")
        print(f"総モジュール数: {total_modules}")
        print(f"主要モジュール数: {main_module_count}")
        print(f"総フィールド数: {total_fields}")
        
        if main_modules:
            print(f"\n=== 主要モジュール ===")
            for module in main_modules:
                print(f"  - {module['display_name']} ({module['api_name']}) - {module['field_count']} フィールド")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()