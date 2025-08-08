import json
import pandas as pd

def search_specific_learning_tables():
    """具体的に学習実績、修了要件、受講生テーブルを検索"""
    
    with open('zoho_crm_schema.json', 'r', encoding='utf-8') as f:
        schema_data = json.load(f)
    
    target_tables = {
        '学習実績': [],
        '修了要件': [],
        '受講生': [],
        'その他学習関連': []
    }
    
    print("=== 特定テーブル詳細検索 ===\n")
    
    for module in schema_data['modules']:
        display_name = module['display_name']
        api_name = module['api_name']
        
        # 完全一致または部分一致で分類
        if '学習実績' in display_name:
            target_tables['学習実績'].append(module)
        elif '修了要件' in display_name:
            target_tables['修了要件'].append(module)
        elif '受講生' in display_name or 'Students' in api_name:
            target_tables['受講生'].append(module)
        elif any(keyword in display_name.lower() or keyword in api_name.lower() 
                for keyword in ['学習', '実績', '修了', '要件', 'learning', 'achievement', 'completion']):
            target_tables['その他学習関連'].append(module)
    
    # 検索結果表示
    all_found_modules = []
    
    for category, modules in target_tables.items():
        if modules:
            print(f"【{category}】")
            for i, module in enumerate(modules, 1):
                print(f"  {i}. {module['display_name']} ({module['api_name']}) - {module['field_count']} フィールド")
                
                # 重要そうなフィールドを表示
                important_fields = []
                for field in module['fields']:
                    field_label = field['display_label'] or field['api_name']
                    if any(kw in field_label for kw in ['名', 'ID', '時間', '日', '実績', '要件', '状況', 'ステータス']):
                        important_fields.append(f"{field_label} ({field['data_type']})")
                
                if important_fields:
                    print(f"     重要フィールド: {', '.join(important_fields[:5])}")
                
                all_found_modules.append(module)
            print()
    
    # 全モジュール名を表示（確認用）
    print("=== 全モジュール一覧（参考）===")
    all_modules = [(m['display_name'], m['api_name']) for m in schema_data['modules']]
    for i, (display, api) in enumerate(sorted(all_modules), 1):
        print(f"{i:3d}. {display} ({api})")
    
    return all_found_modules

def generate_enhanced_learning_sql():
    """見つかったテーブル用の詳細SQLを生成"""
    
    modules = search_specific_learning_tables()
    
    sql_content = f"""-- =====================================
-- 学習関連テーブル拡張SQLクエリ
-- 生成日時: {pd.Timestamp.now()}
-- 対象テーブル数: {len(modules)}
-- =====================================

"""
    
    for module in modules:
        api_name = module['api_name']
        display_name = module['display_name']
        
        # 基本クエリ
        basic_fields = []
        for field in module['fields'][:15]:  # 最初の15フィールド
            basic_fields.append(f'    "{field["api_name"]}"  -- {field["display_label"]} ({field["data_type"]})')
        
        sql_content += f"""-- {display_name} 基本クエリ
SELECT 
{',\\n'.join(basic_fields)}
FROM "{api_name}"
LIMIT 100;

"""
        
        # カスタム分析クエリ
        if '受講生' in display_name or 'Students' in api_name:
            sql_content += f"""-- {display_name} 分析クエリ
-- 受講生ステータス別集計
SELECT 
    "ステータス",
    COUNT(*) as 受講生数
FROM "{api_name}"
GROUP BY "ステータス"
ORDER BY 受講生数 DESC;

-- 受講生登録月別推移
SELECT 
    DATE_FORMAT("作成日時", '%Y-%m') as 登録月,
    COUNT(*) as 新規受講生数
FROM "{api_name}"
GROUP BY DATE_FORMAT("作成日時", '%Y-%m')
ORDER BY 登録月 DESC;

"""
        
        elif '学習実績' in display_name:
            sql_content += f"""-- {display_name} 分析クエリ
-- 受講生別学習時間集計
SELECT 
    "受講生",
    COUNT(*) as 学習記録数,
    SUM("学習時間") as 総学習時間,
    AVG("学習時間") as 平均学習時間
FROM "{api_name}"
WHERE "学習時間" IS NOT NULL
GROUP BY "受講生"
ORDER BY 総学習時間 DESC;

-- 月別学習実績
SELECT 
    DATE_FORMAT("学習日", '%Y-%m') as 学習月,
    COUNT(*) as 学習記録数,
    SUM("学習時間") as 月間学習時間
FROM "{api_name}"
GROUP BY DATE_FORMAT("学習日", '%Y-%m')
ORDER BY 学習月 DESC;

"""
        
        elif '修了要件' in display_name:
            sql_content += f"""-- {display_name} 分析クエリ
-- 修了要件一覧
SELECT 
    "要件名",
    "必要時間",
    "必要回数",
    "説明"
FROM "{api_name}"
ORDER BY "必要時間" DESC;

"""
    
    # 統合分析クエリを追加
    sql_content += """-- =====================================
-- 統合分析クエリ（例）
-- =====================================

-- 受講生学習進捗サマリー（テーブル名は実際の名前に調整が必要）
/*
SELECT 
    s."受講生名",
    s."コース",
    COUNT(l."ID") as 学習記録数,
    SUM(l."学習時間") as 総学習時間,
    r."必要時間",
    ROUND((SUM(l."学習時間") / r."必要時間") * 100, 2) as 進捗率,
    CASE 
        WHEN SUM(l."学習時間") >= r."必要時間" THEN '修了'
        ELSE '進行中'
    END as ステータス
FROM "受講生" s
LEFT JOIN "学習実績" l ON s."ID" = l."受講生ID"
LEFT JOIN "修了要件" r ON s."コース" = r."コース名"
GROUP BY s."受講生名", s."コース", r."必要時間"
ORDER BY 進捗率 DESC;
*/

-- 月次学習傾向分析
/*
SELECT 
    DATE_FORMAT(l."学習日", '%Y-%m') as 月,
    COUNT(DISTINCT s."ID") as アクティブ受講生数,
    COUNT(l."ID") as 総学習記録数,
    SUM(l."学習時間") as 総学習時間,
    AVG(l."学習時間") as 平均学習時間
FROM "学習実績" l
JOIN "受講生" s ON l."受講生ID" = s."ID"
GROUP BY DATE_FORMAT(l."学習日", '%Y-%m')
ORDER BY 月 DESC;
*/
"""
    
    # ファイル保存
    with open('zoho_learning_tables_sql.sql', 'w', encoding='utf-8') as f:
        f.write(sql_content)
    
    print(f"✓ 学習関連テーブルSQLを zoho_learning_tables_sql.sql に保存")
    
    # フィールド詳細をExcelに出力
    create_detailed_field_reference(modules)

def create_detailed_field_reference(modules):
    """詳細なフィールドリファレンスを作成"""
    
    field_data = []
    
    for module in modules:
        for field in module['fields']:
            field_data.append({
                'テーブル名': module['display_name'],
                'テーブルAPI名': module['api_name'],
                'フィールドAPI名': field['api_name'],
                'フィールド表示名': field['display_label'],
                'データ型': field['data_type'],
                '長さ': field.get('length', ''),
                '必須': field['required'],
                'カスタムフィールド': field['custom_field'],
                '読み取り専用': field['read_only'],
                'デフォルト値': field.get('default_value', ''),
                'ピックリスト値数': len(field.get('picklist_values', [])),
                'ルックアップ先': field.get('lookup_module', ''),
                '数式': field.get('formula', '')
            })
    
    if field_data:
        # Excelファイル作成
        with pd.ExcelWriter('zoho_learning_tables_fields.xlsx', engine='openpyxl') as writer:
            # 全フィールド
            df_all = pd.DataFrame(field_data)
            df_all.to_excel(writer, sheet_name='全フィールド', index=False)
            
            # テーブル別シート
            for module in modules:
                table_fields = [f for f in field_data if f['テーブルAPI名'] == module['api_name']]
                if table_fields:
                    df_table = pd.DataFrame(table_fields)
                    sheet_name = module['display_name'][:30]  # Excel制限
                    df_table.to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"✓ 学習関連フィールド詳細を zoho_learning_tables_fields.xlsx に保存")

if __name__ == "__main__":
    generate_enhanced_learning_sql()