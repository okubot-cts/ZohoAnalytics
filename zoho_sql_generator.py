import json
import pandas as pd
from datetime import datetime

class ZohoSQLGenerator:
    def __init__(self, schema_file='zoho_crm_schema.json'):
        with open(schema_file, 'r', encoding='utf-8') as f:
            self.schema_data = json.load(f)
        
        self.modules = {m['api_name']: m for m in self.schema_data['modules']}
        
    def get_module_info(self, module_name):
        """モジュール情報を取得"""
        return self.modules.get(module_name)
    
    def get_field_info(self, module_name, field_name=None):
        """フィールド情報を取得"""
        module = self.get_module_info(module_name)
        if not module:
            return None
        
        if field_name:
            for field in module['fields']:
                if field['api_name'] == field_name:
                    return field
            return None
        else:
            return module['fields']
    
    def generate_basic_select(self, module_name, limit=100):
        """基本的なSELECT文を生成"""
        module = self.get_module_info(module_name)
        if not module:
            return f"-- モジュール '{module_name}' が見つかりません"
        
        # 主要フィールドを選択（最初の10個程度）
        fields = module['fields'][:10]
        field_names = [f'"{field["api_name"]}"' for field in fields]
        
        sql = f"""-- {module['display_name']} の基本クエリ
SELECT 
    {',\\n    '.join(field_names)}
FROM "{module_name}"
LIMIT {limit};"""
        
        return sql
    
    def generate_field_list(self, module_name):
        """全フィールド一覧を生成"""
        module = self.get_module_info(module_name)
        if not module:
            return f"-- モジュール '{module_name}' が見つかりません"
        
        field_info = []
        for field in module['fields']:
            field_info.append(f"-- {field['display_label']}: {field['data_type']} {'(必須)' if field['required'] else ''}")
            field_info.append(f'    "{field["api_name"]}"')
        
        sql = f"""-- {module['display_name']} の全フィールド一覧
-- 総フィールド数: {len(module['fields'])}個

SELECT 
{',\\n'.join(field_info)}
FROM "{module_name}";"""
        
        return sql
    
    def generate_joins_sql(self, main_module, related_modules):
        """JOIN文を含むSQLを生成"""
        main_info = self.get_module_info(main_module)
        if not main_info:
            return f"-- メインモジュール '{main_module}' が見つかりません"
        
        # メインテーブルの主要フィールド
        main_fields = [f'main."{field["api_name"]}" as main_{field["api_name"]}' 
                      for field in main_info['fields'][:5]]
        
        sql_parts = [f"""-- {main_info['display_name']} と関連テーブルの結合クエリ
SELECT 
    {',\\n    '.join(main_fields)}"""]
        
        join_parts = []
        for related_module in related_modules:
            related_info = self.get_module_info(related_module)
            if related_info:
                # 関連テーブルの主要フィールド
                related_fields = [f'{related_module.lower()}."{field["api_name"]}" as {related_module.lower()}_{field["api_name"]}' 
                                for field in related_info['fields'][:3]]
                sql_parts.extend([f"    {field}" for field in related_fields])
                
                # JOIN部分（実際の関連キーは手動で調整が必要）
                join_parts.append(f"""LEFT JOIN "{related_module}" {related_module.lower()} 
    ON main.id = {related_module.lower()}.{main_module.lower()}_id""")
        
        sql_parts.append(f'FROM "{main_module}" main')
        sql_parts.extend(join_parts)
        sql_parts.append("LIMIT 100;")
        
        return '\n'.join(sql_parts)
    
    def generate_analytics_queries(self):
        """よく使われる分析クエリを生成"""
        queries = {}
        
        # 商談分析
        if 'Deals' in self.modules:
            queries['deals_by_stage'] = f"""-- 商談ステージ別集計
SELECT 
    "Stage",
    COUNT(*) as deal_count,
    SUM(CAST("Amount" as DECIMAL)) as total_amount,
    AVG(CAST("Amount" as DECIMAL)) as avg_amount
FROM "Deals"
WHERE "Amount" IS NOT NULL
GROUP BY "Stage"
ORDER BY total_amount DESC;"""
            
            queries['deals_monthly_trend'] = f"""-- 商談月次トレンド
SELECT 
    DATE_FORMAT("Created_Time", '%Y-%m') as month,
    COUNT(*) as new_deals,
    SUM(CASE WHEN "Stage" = 'Closed Won' THEN CAST("Amount" as DECIMAL) ELSE 0 END) as won_amount
FROM "Deals"
GROUP BY DATE_FORMAT("Created_Time", '%Y-%m')
ORDER BY month DESC;"""
        
        # 連絡先分析
        if 'Contacts' in self.modules:
            queries['contacts_by_account'] = f"""-- 取引先別連絡先数
SELECT 
    "Account_Name",
    COUNT(*) as contact_count
FROM "Contacts"
WHERE "Account_Name" IS NOT NULL
GROUP BY "Account_Name"
ORDER BY contact_count DESC
LIMIT 20;"""
        
        # タスク分析
        if 'Tasks' in self.modules:
            queries['task_completion_rate'] = f"""-- タスク完了率
SELECT 
    "Status",
    COUNT(*) as task_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM "Tasks"), 2) as percentage
FROM "Tasks"
GROUP BY "Status"
ORDER BY task_count DESC;"""
        
        return queries
    
    def save_sql_queries(self, filename='zoho_analytics_queries.sql'):
        """生成したSQLクエリをファイルに保存"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"""-- Zoho Analytics SQL クエリ集
-- 生成日時: {datetime.now().isoformat()}
-- 基づくスキーマ: Zoho CRM
-- 総モジュール数: {len(self.modules)}

""")
            
            # 主要モジュールの基本クエリ
            important_modules = ['Deals', 'Contacts', 'Accounts', 'Leads', 'Tasks', 'Products']
            
            f.write("-- =====================================\n")
            f.write("-- 基本クエリ (主要モジュール)\n")
            f.write("-- =====================================\n\n")
            
            for module in important_modules:
                if module in self.modules:
                    f.write(self.generate_basic_select(module))
                    f.write("\n\n")
            
            # 分析クエリ
            f.write("-- =====================================\n")
            f.write("-- 分析クエリ\n")
            f.write("-- =====================================\n\n")
            
            analytics_queries = self.generate_analytics_queries()
            for name, query in analytics_queries.items():
                f.write(query)
                f.write("\n\n")
            
            # JOIN例
            f.write("-- =====================================\n")
            f.write("-- JOIN例\n")
            f.write("-- =====================================\n\n")
            
            if 'Deals' in self.modules and 'Contacts' in self.modules:
                join_query = self.generate_joins_sql('Deals', ['Contacts', 'Accounts'])
                f.write(join_query)
                f.write("\n\n")
        
        print(f"✓ SQLクエリを {filename} に保存しました")
    
    def generate_field_reference(self):
        """フィールドリファレンスを生成"""
        important_modules = ['Deals', 'Contacts', 'Accounts', 'Leads', 'Tasks', 'Products']
        
        reference_data = []
        for module_name in important_modules:
            if module_name in self.modules:
                module = self.modules[module_name]
                for field in module['fields']:
                    reference_data.append({
                        'module_name': module['display_name'],
                        'module_api_name': module_name,
                        'field_api_name': field['api_name'],
                        'field_display_name': field['display_label'],
                        'data_type': field['data_type'],
                        'required': field['required'],
                        'custom_field': field['custom_field'],
                        'length': field.get('length', ''),
                        'default_value': field.get('default_value', '')
                    })
        
        df = pd.DataFrame(reference_data)
        df.to_excel('zoho_field_reference.xlsx', index=False)
        print("✓ フィールドリファレンスを zoho_field_reference.xlsx に保存しました")

def main():
    try:
        sql_gen = ZohoSQLGenerator()
        
        print("=== Zoho Analytics SQL Generator ===")
        print(f"読み込み完了: {len(sql_gen.modules)} モジュール")
        
        # SQLクエリ生成・保存
        sql_gen.save_sql_queries()
        
        # フィールドリファレンス生成
        sql_gen.generate_field_reference()
        
        # 主要モジュールの情報表示
        print("\n=== 主要モジュール情報 ===")
        important_modules = ['Deals', 'Contacts', 'Accounts', 'Leads', 'Tasks', 'Products']
        
        for module_name in important_modules:
            if module_name in sql_gen.modules:
                module = sql_gen.modules[module_name]
                field_count = len(module['fields'])
                print(f"{module['display_name']:12} ({module_name:12}): {field_count:3d} フィールド")
        
        print(f"\n✓ 生成ファイル:")
        print(f"  - zoho_analytics_queries.sql (SQLクエリ集)")
        print(f"  - zoho_field_reference.xlsx (フィールドリファレンス)")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()