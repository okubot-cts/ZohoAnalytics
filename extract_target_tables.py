import json
import pandas as pd

def extract_target_learning_tables():
    """具体的なテーブル名から学習関連テーブルを特定"""
    
    with open('zoho_crm_schema.json', 'r', encoding='utf-8') as f:
        schema_data = json.load(f)
    
    # 検索対象
    target_names = [
        '学習実績', '修了要件', '受講生',
        'Classes', 'Students', 'CustomModule5'  # CustomModule5が怪しい
    ]
    
    # より広範囲で検索
    additional_candidates = [
        'CustomModule5',    # 137フィールドと多い
        'CustomModule38',   # Classes - 134フィールド
        'CustomModule53',   # Attendance_Detail - 出席関連
        'CustomModule75',   # 86フィールド
        'CustomModule110',  # 88フィールド
    ]
    
    found_tables = []
    
    print("=== 対象テーブル詳細分析 ===\n")
    
    # 全モジュールから関連するものを検索
    for module in schema_data['modules']:
        api_name = module['api_name']
        display_name = module['display_name']
        
        # 直接マッチング
        if (any(target in display_name for target in target_names) or 
            api_name in target_names or
            api_name in additional_candidates):
            
            found_tables.append(module)
            
            print(f"【{display_name} ({api_name})】 - {module['field_count']} フィールド")
            
            # 重要フィールドを分析
            important_fields = []
            learning_fields = []
            
            for field in module['fields']:
                field_name = field['display_label'] or field['api_name']
                api_field = field['api_name']
                
                # 学習関連キーワードを含むフィールド
                learning_keywords = ['学習', '実績', '時間', '修了', '要件', '受講', '出席', 
                                   'learning', 'study', 'completion', 'requirement', 
                                   'attendance', 'progress', 'achievement']
                
                if any(kw in field_name.lower() for kw in learning_keywords):
                    learning_fields.append(f"{field_name} ({field['data_type']})")
                
                # 重要そうなフィールド（ID、名前、日付、ステータス等）
                key_patterns = ['名', 'ID', '日', '時', 'ステータス', 'name', 'date', 'time', 'status']
                if any(pattern in field_name for pattern in key_patterns):
                    important_fields.append(f"{field_name} ({field['data_type']})")
            
            print(f"  重要フィールド: {', '.join(important_fields[:8])}")
            if learning_fields:
                print(f"  学習関連: {', '.join(learning_fields[:5])}")
            print()
    
    return found_tables

def generate_comprehensive_sql():
    """包括的なSQL生成"""
    
    target_tables = extract_target_learning_tables()
    
    # 各テーブルの詳細なSQLを生成
    sql_content = f"""-- =====================================
-- 学習実績・修了要件・受講生 包括的SQLクエリ
-- 生成日時: {pd.Timestamp.now()}
-- 対象テーブル数: {len(target_tables)}
-- =====================================

"""
    
    for module in target_tables:
        api_name = module['api_name']
        display_name = module['display_name']
        
        sql_content += f"""-- =====================================
-- {display_name} ({api_name})
-- フィールド数: {module['field_count']}
-- =====================================

-- 全フィールド基本クエリ
SELECT 
"""
        
        # 全フィールドを列挙（コメント付き）
        field_lines = []
        for i, field in enumerate(module['fields']):
            field_comment = f"{field['display_label']} ({field['data_type']})"
            field_lines.append(f'    "{field["api_name"]}"  -- {field_comment}')
        
        sql_content += ',\n'.join(field_lines)
        sql_content += f'\nFROM "{api_name}"\nLIMIT 100;\n\n'
        
        # カウントクエリ
        sql_content += f"""-- {display_name} レコード数確認
SELECT COUNT(*) as total_records
FROM "{api_name}";

"""
        
        # 特定の分析クエリ
        if 'Students' in api_name or '受講生' in display_name:
            sql_content += f"""-- {display_name} ステータス分析
SELECT 
    "ステータス",
    COUNT(*) as 件数
FROM "{api_name}"
GROUP BY "ステータス"
ORDER BY 件数 DESC;

-- {display_name} 月別登録数
SELECT 
    DATE_FORMAT("作成日時", '%Y-%m') as 登録月,
    COUNT(*) as 新規登録数
FROM "{api_name}"
GROUP BY DATE_FORMAT("作成日時", '%Y-%m')
ORDER BY 登録月 DESC;

"""
        
        elif 'Classes' in api_name or 'クラス' in display_name:
            sql_content += f"""-- {display_name} クラス分析
SELECT 
    "クラス名",
    "開始日",
    "終了日",
    COUNT(*) as 参加者数
FROM "{api_name}"
GROUP BY "クラス名", "開始日", "終了日"
ORDER BY 参加者数 DESC;

"""
        
        elif 'Attendance' in api_name or '出席' in display_name:
            sql_content += f"""-- {display_name} 出席率分析
SELECT 
    "出席ステータス",
    COUNT(*) as 記録数,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM "{api_name}"), 2) as 割合
FROM "{api_name}"
GROUP BY "出席ステータス"
ORDER BY 記録数 DESC;

"""
    
    # 統合分析の例
    sql_content += """
-- =====================================
-- 統合分析クエリ例
-- =====================================

-- 注意: 以下のクエリは実際のテーブル名・フィールド名に合わせて調整が必要です

-- 受講生別総合レポート例
/*
SELECT 
    s."受講生名",
    s."コース",
    s."登録日",
    COUNT(DISTINCT c."クラスID") as 参加クラス数,
    COUNT(a."出席ID") as 出席記録数,
    SUM(CASE WHEN a."出席ステータス" = '出席' THEN 1 ELSE 0 END) as 出席回数,
    ROUND(SUM(CASE WHEN a."出席ステータス" = '出席' THEN 1 ELSE 0 END) * 100.0 / COUNT(a."出席ID"), 2) as 出席率
FROM "Students" s
LEFT JOIN "Classes" c ON s."ID" = c."受講生ID"
LEFT JOIN "Attendance_Detail" a ON s."ID" = a."受講生ID"
GROUP BY s."受講生名", s."コース", s."登録日"
ORDER BY 出席率 DESC;
*/

-- コース別実績サマリー例
/*
SELECT 
    "コース名",
    COUNT(DISTINCT "受講生ID") as 受講生数,
    COUNT("クラスID") as 開催クラス数,
    AVG("出席率") as 平均出席率,
    SUM("修了者数") as 修了者数
FROM (
    SELECT 
        s."コース",
        s."ID" as "受講生ID",
        c."ID" as "クラスID",
        AVG(CASE WHEN a."出席ステータス" = '出席' THEN 1.0 ELSE 0.0 END) as "出席率",
        MAX(CASE WHEN s."ステータス" = '修了' THEN 1 ELSE 0 END) as "修了者数"
    FROM "Students" s
    LEFT JOIN "Classes" c ON s."コース" = c."コース名"
    LEFT JOIN "Attendance_Detail" a ON s."ID" = a."受講生ID"
    GROUP BY s."コース", s."ID", c."ID"
) subquery
GROUP BY "コース名"
ORDER BY 受講生数 DESC;
*/
"""
    
    # ファイル保存
    with open('zoho_learning_comprehensive_sql.sql', 'w', encoding='utf-8') as f:
        f.write(sql_content)
    
    print(f"✓ 包括的学習SQLを zoho_learning_comprehensive_sql.sql に保存")
    
    # Excel詳細レポート作成
    create_table_analysis_report(target_tables)

def create_table_analysis_report(tables):
    """テーブル分析レポートを作成"""
    
    # テーブルサマリー
    table_summary = []
    all_fields = []
    
    for table in tables:
        table_summary.append({
            'テーブル名': table['display_name'],
            'API名': table['api_name'],
            'フィールド数': table['field_count'],
            'カテゴリ': 'Students' if 'Students' in table['api_name'] else 
                      'Classes' if 'Classes' in table['api_name'] else
                      'Attendance' if 'Attendance' in table['api_name'] else
                      'CustomModule',
            '作成可能': table['is_creatable'],
            '編集可能': table['is_editable'],
            '削除可能': table['is_deletable']
        })
        
        # 全フィールド情報
        for field in table['fields']:
            all_fields.append({
                'テーブル名': table['display_name'],
                'テーブルAPI名': table['api_name'],
                'フィールドAPI名': field['api_name'],
                'フィールド表示名': field['display_label'],
                'データ型': field['data_type'],
                '長さ': field.get('length', ''),
                '必須': field['required'],
                'カスタム': field['custom_field'],
                '読み取り専用': field['read_only'],
                'デフォルト値': str(field.get('default_value', ''))[:50],
                'ピックリスト値数': len(field.get('picklist_values', [])),
                'ルックアップ先': field.get('lookup_module', '')
            })
    
    # Excel出力
    with pd.ExcelWriter('zoho_learning_analysis_report.xlsx', engine='openpyxl') as writer:
        # テーブルサマリー
        df_summary = pd.DataFrame(table_summary)
        df_summary.to_excel(writer, sheet_name='テーブルサマリー', index=False)
        
        # 全フィールド
        df_fields = pd.DataFrame(all_fields)
        df_fields.to_excel(writer, sheet_name='全フィールド', index=False)
        
        # データ型分析
        dtype_analysis = df_fields['データ型'].value_counts().reset_index()
        dtype_analysis.columns = ['データ型', '件数']
        dtype_analysis.to_excel(writer, sheet_name='データ型分析', index=False)
        
        # テーブル別詳細
        for table in tables:
            table_fields = df_fields[df_fields['テーブルAPI名'] == table['api_name']]
            if not table_fields.empty:
                sheet_name = table['display_name'][:30]
                table_fields.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"✓ 学習テーブル分析レポートを zoho_learning_analysis_report.xlsx に保存")

if __name__ == "__main__":
    generate_comprehensive_sql()