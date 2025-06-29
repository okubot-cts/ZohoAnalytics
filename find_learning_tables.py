import json
import pandas as pd

def find_learning_related_tables():
    """学習関連テーブル（学習実績、修了要件、受講生）を検索"""
    
    # CRMスキーマから検索
    with open('zoho_crm_schema.json', 'r', encoding='utf-8') as f:
        schema_data = json.load(f)
    
    # 検索キーワード
    learning_keywords = [
        '学習実績', '修了要件', '受講生',
        'learning', 'student', 'completion', 'requirement',
        'achievement', 'progress', 'study'
    ]
    
    found_modules = []
    
    print("=== 学習関連テーブル検索 ===\n")
    
    for module in schema_data['modules']:
        module_name = module['display_name'].lower()
        api_name = module['api_name'].lower()
        
        # キーワードマッチング
        for keyword in learning_keywords:
            if keyword in module_name or keyword in api_name:
                found_modules.append(module)
                break
    
    print(f"発見されたテーブル数: {len(found_modules)}")
    
    for i, module in enumerate(found_modules, 1):
        print(f"{i:2d}. {module['display_name']} ({module['api_name']}) - {module['field_count']} フィールド")
        
        # 主要フィールドを表示
        important_fields = []
        for field in module['fields'][:10]:  # 最初の10個
            field_name = field['display_label'] or field['api_name']
            important_fields.append(f"{field_name} ({field['data_type']})")
        
        print(f"    主要フィールド: {', '.join(important_fields[:5])}...")
        print()
    
    return found_modules

def generate_learning_sql(modules):
    """学習関連テーブル用のSQLを生成"""
    
    sql_queries = []
    
    for module in modules:
        api_name = module['api_name']
        display_name = module['display_name']
        
        # 基本SELECT文
        fields = []
        for field in module['fields'][:10]:  # 最初の10フィールド
            fields.append(f'"{field["api_name"]}"')
        
        basic_query = f"""-- {display_name} の基本クエリ
SELECT 
    {',\\n    '.join(fields)}
FROM "{api_name}"
LIMIT 100;"""
        
        sql_queries.append(basic_query)
        
        # 学習実績の場合は集計クエリも追加
        if '学習実績' in display_name or 'learning' in api_name.lower():
            # 日付別集計の例
            learning_analysis = f"""-- {display_name} 分析クエリ
-- 受講生別学習時間集計（例）
SELECT 
    "受講生" as student_name,
    COUNT(*) as record_count,
    SUM(CAST("学習時間" as DECIMAL)) as total_hours
FROM "{api_name}"
WHERE "学習時間" IS NOT NULL
GROUP BY "受講生"
ORDER BY total_hours DESC
LIMIT 20;"""
            sql_queries.append(learning_analysis)
        
        # 修了要件の場合
        elif '修了要件' in display_name or 'completion' in api_name.lower():
            completion_query = f"""-- {display_name} 分析クエリ
-- 修了要件別集計（例）
SELECT 
    "要件名" as requirement_name,
    "必要時間" as required_hours,
    COUNT(*) as student_count
FROM "{api_name}"
GROUP BY "要件名", "必要時間"
ORDER BY required_hours DESC;"""
            sql_queries.append(completion_query)
        
        # 受講生の場合
        elif '受講生' in display_name or 'student' in api_name.lower():
            student_query = f"""-- {display_name} 分析クエリ
-- 受講生ステータス別集計（例）
SELECT 
    "ステータス" as status,
    COUNT(*) as student_count,
    "コース名" as course_name
FROM "{api_name}"
GROUP BY "ステータス", "コース名"
ORDER BY student_count DESC;"""
            sql_queries.append(student_query)
    
    return sql_queries

def create_enhanced_sql_file():
    """拡張されたSQLファイルを作成"""
    
    # 学習関連テーブルを検索
    learning_modules = find_learning_related_tables()
    
    if not learning_modules:
        print("学習関連テーブルが見つかりませんでした。")
        return
    
    # 学習関連SQLを生成
    learning_sql = generate_learning_sql(learning_modules)
    
    # 既存のSQLファイルを読み込み
    try:
        with open('zoho_analytics_queries.sql', 'r', encoding='utf-8') as f:
            existing_sql = f.read()
    except:
        existing_sql = ""
    
    # 拡張SQLファイルを作成
    with open('zoho_analytics_queries_extended.sql', 'w', encoding='utf-8') as f:
        f.write(existing_sql)
        f.write("\n\n-- =====================================\n")
        f.write("-- 学習関連テーブル (追加)\n")
        f.write("-- =====================================\n\n")
        
        for sql in learning_sql:
            f.write(sql)
            f.write("\n\n")
        
        # 学習関連の統合分析クエリ
        f.write("-- =====================================\n")
        f.write("-- 学習関連統合分析\n")
        f.write("-- =====================================\n\n")
        
        # 受講生の学習進捗統合クエリ（例）
        integrated_query = """-- 受講生学習進捗統合分析（例）
-- 注意: 実際のテーブル名とフィールド名に合わせて調整が必要
SELECT 
    s."受講生名" as student_name,
    s."コース名" as course_name,
    s."登録日" as enrollment_date,
    COUNT(lr.id) as learning_records,
    SUM(CAST(lr."学習時間" as DECIMAL)) as total_hours,
    r."必要時間" as required_hours,
    CASE 
        WHEN SUM(CAST(lr."学習時間" as DECIMAL)) >= r."必要時間" 
        THEN '修了' 
        ELSE '未修了' 
    END as completion_status
FROM "受講生" s
LEFT JOIN "学習実績" lr ON s.id = lr."受講生ID"
LEFT JOIN "修了要件" r ON s."コース名" = r."コース名"
GROUP BY s."受講生名", s."コース名", s."登録日", r."必要時間"
ORDER BY total_hours DESC;"""
        
        f.write(integrated_query)
        f.write("\n\n")
    
    print(f"✓ 拡張SQLクエリを zoho_analytics_queries_extended.sql に保存")
    
    # 学習関連テーブルのフィールドリファレンスも作成
    create_learning_field_reference(learning_modules)

def create_learning_field_reference(modules):
    """学習関連テーブルのフィールドリファレンスを作成"""
    
    reference_data = []
    
    for module in modules:
        for field in module['fields']:
            reference_data.append({
                'table_name': module['display_name'],
                'table_api_name': module['api_name'],
                'field_api_name': field['api_name'],
                'field_display_name': field['display_label'],
                'data_type': field['data_type'],
                'length': field.get('length', ''),
                'required': field['required'],
                'custom_field': field['custom_field'],
                'default_value': field.get('default_value', ''),
                'picklist_values': len(field.get('picklist_values', [])) if field.get('picklist_values') else 0
            })
    
    if reference_data:
        df = pd.DataFrame(reference_data)
        df.to_excel('zoho_learning_field_reference.xlsx', index=False)
        print(f"✓ 学習関連フィールドリファレンスを zoho_learning_field_reference.xlsx に保存")

if __name__ == "__main__":
    create_enhanced_sql_file()