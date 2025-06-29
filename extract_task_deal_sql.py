import json

def analyze_task_and_deal_schema():
    """タスクと商談テーブルのスキーマを分析"""
    
    with open('zoho_crm_schema.json', 'r', encoding='utf-8') as f:
        schema_data = json.load(f)
    
    # タスクと商談テーブルを検索
    task_module = None
    deal_module = None
    
    for module in schema_data['modules']:
        if module['api_name'] == 'Tasks':
            task_module = module
        elif module['api_name'] == 'Deals':
            deal_module = module
    
    print("=== タスクテーブル分析 ===")
    if task_module:
        print(f"テーブル名: {task_module['display_name']} ({task_module['api_name']})")
        print(f"フィールド数: {task_module['field_count']}")
        print("\n重要フィールド:")
        
        for field in task_module['fields']:
            field_name = field['display_label'] or field['api_name']
            if any(keyword in field_name.lower() for keyword in ['subject', '件名', 'status', 'ステータス', 'due', '期限', 'owner', '担当', 'what', 'who', '関連']):
                print(f"  - {field['api_name']}: {field_name} ({field['data_type']})")
    
    print("\n=== 商談テーブル分析 ===")
    if deal_module:
        print(f"テーブル名: {deal_module['display_name']} ({deal_module['api_name']})")
        print(f"フィールド数: {deal_module['field_count']}")
        print("\n重要フィールド:")
        
        for field in deal_module['fields']:
            field_name = field['display_label'] or field['api_name']
            if any(keyword in field_name.lower() for keyword in ['deal', '商談', 'name', '名', 'amount', '金額', 'stage', 'ステージ', 'account', '取引先', 'owner', '担当']):
                print(f"  - {field['api_name']}: {field_name} ({field['data_type']})")
    
    return task_module, deal_module

def generate_task_deal_sql():
    """okubo.t@cts-n.netの未完了タスクと商談関連SQLを生成"""
    
    task_module, deal_module = analyze_task_and_deal_schema()
    
    sql_queries = []
    
    # 1. 基本的な未完了タスク取得
    basic_task_sql = """-- okubo.t@cts-n.net の未完了タスク一覧
SELECT 
    "Subject" as タスク件名,
    "Status" as ステータス,
    "Priority" as 優先度,
    "Due_Date" as 期限,
    "What_Id" as 関連レコードID,
    "Who_Id" as 連絡先ID,
    "Description" as 説明,
    "Created_Time" as 作成日時,
    "Modified_Time" as 更新日時
FROM "Tasks"
WHERE "Owner" = 'okubo.t@cts-n.net'
  AND "Status" NOT IN ('Completed', '完了', 'Closed', '終了')
ORDER BY "Due_Date" ASC, "Priority" DESC;"""
    
    sql_queries.append(basic_task_sql)
    
    # 2. 商談関連タスクの詳細
    task_with_deal_sql = """-- okubo.t@cts-n.net の未完了タスク（商談関連情報付き）
SELECT 
    t."Subject" as タスク件名,
    t."Status" as タスクステータス,
    t."Priority" as 優先度,
    t."Due_Date" as 期限,
    t."Description" as タスク説明,
    d."Deal_Name" as 商談名,
    d."Stage" as 商談ステージ,
    d."Amount" as 商談金額,
    d."Account_Name" as 取引先名,
    d."Closing_Date" as 商談完了予定日,
    t."Created_Time" as タスク作成日時,
    t."Modified_Time" as タスク更新日時
FROM "Tasks" t
LEFT JOIN "Deals" d ON t."What_Id" = d."id"
WHERE t."Owner" = 'okubo.t@cts-n.net'
  AND t."Status" NOT IN ('Completed', '完了', 'Closed', '終了')
ORDER BY t."Due_Date" ASC, t."Priority" DESC;"""
    
    sql_queries.append(task_with_deal_sql)
    
    # 3. 期限別タスク分析
    task_by_deadline_sql = """-- okubo.t@cts-n.net のタスク期限別分析
SELECT 
    CASE 
        WHEN "Due_Date" < CURDATE() THEN '期限超過'
        WHEN "Due_Date" = CURDATE() THEN '本日期限'
        WHEN "Due_Date" <= DATE_ADD(CURDATE(), INTERVAL 3 DAY) THEN '3日以内'
        WHEN "Due_Date" <= DATE_ADD(CURDATE(), INTERVAL 7 DAY) THEN '1週間以内'
        ELSE '1週間以降'
    END as 期限区分,
    COUNT(*) as タスク数,
    GROUP_CONCAT("Subject" SEPARATOR ', ') as タスク一覧
FROM "Tasks"
WHERE "Owner" = 'okubo.t@cts-n.net'
  AND "Status" NOT IN ('Completed', '完了', 'Closed', '終了')
GROUP BY 
    CASE 
        WHEN "Due_Date" < CURDATE() THEN '期限超過'
        WHEN "Due_Date" = CURDATE() THEN '本日期限'
        WHEN "Due_Date" <= DATE_ADD(CURDATE(), INTERVAL 3 DAY) THEN '3日以内'
        WHEN "Due_Date" <= DATE_ADD(CURDATE(), INTERVAL 7 DAY) THEN '1週間以内'
        ELSE '1週間以降'
    END
ORDER BY 
    CASE 
        WHEN 期限区分 = '期限超過' THEN 1
        WHEN 期限区分 = '本日期限' THEN 2
        WHEN 期限区分 = '3日以内' THEN 3
        WHEN 期限区分 = '1週間以内' THEN 4
        ELSE 5
    END;"""
    
    sql_queries.append(task_by_deadline_sql)
    
    # 4. 商談ステージ別タスク分析
    task_by_deal_stage_sql = """-- okubo.t@cts-n.net のタスク（商談ステージ別）
SELECT 
    d."Stage" as 商談ステージ,
    COUNT(t."id") as 関連タスク数,
    COUNT(CASE WHEN t."Status" NOT IN ('Completed', '完了') THEN 1 END) as 未完了タスク数,
    SUM(d."Amount") as 商談総額,
    GROUP_CONCAT(t."Subject" SEPARATOR '; ') as タスク件名一覧
FROM "Deals" d
LEFT JOIN "Tasks" t ON d."id" = t."What_Id" 
    AND t."Owner" = 'okubo.t@cts-n.net'
WHERE d."Owner" = 'okubo.t@cts-n.net'
  OR t."Owner" = 'okubo.t@cts-n.net'
GROUP BY d."Stage"
HAVING COUNT(t."id") > 0
ORDER BY 未完了タスク数 DESC, 商談総額 DESC;"""
    
    sql_queries.append(task_by_deal_stage_sql)
    
    # 5. 詳細な商談関連タスクリスト
    detailed_task_deal_sql = """-- okubo.t@cts-n.net の詳細タスク・商談リスト
SELECT 
    t."Subject" as タスク件名,
    t."Status" as タスクステータス,
    t."Priority" as 優先度,
    DATE_FORMAT(t."Due_Date", '%Y-%m-%d') as 期限,
    DATEDIFF(t."Due_Date", CURDATE()) as 期限まで日数,
    d."Deal_Name" as 商談名,
    d."Stage" as 商談ステージ,
    FORMAT(d."Amount", 0) as 商談金額,
    d."Account_Name" as 取引先名,
    DATE_FORMAT(d."Closing_Date", '%Y-%m-%d') as 商談完了予定日,
    c."First_Name" as 連絡先名,
    c."Last_Name" as 連絡先姓,
    c."Email" as 連絡先メール,
    t."Description" as タスク説明
FROM "Tasks" t
LEFT JOIN "Deals" d ON t."What_Id" = d."id"
LEFT JOIN "Contacts" c ON t."Who_Id" = c."id"
WHERE t."Owner" = 'okubo.t@cts-n.net'
  AND t."Status" NOT IN ('Completed', '完了', 'Closed', '終了')
ORDER BY 
    CASE t."Priority"
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'Low' THEN 3
        ELSE 4
    END,
    t."Due_Date" ASC;"""
    
    sql_queries.append(detailed_task_deal_sql)
    
    # 6. タスク進捗サマリー
    task_summary_sql = """-- okubo.t@cts-n.net のタスク進捗サマリー
SELECT 
    'タスク総数' as 項目,
    COUNT(*) as 件数,
    '' as 詳細
FROM "Tasks"
WHERE "Owner" = 'okubo.t@cts-n.net'

UNION ALL

SELECT 
    '未完了タスク数' as 項目,
    COUNT(*) as 件数,
    '' as 詳細
FROM "Tasks"
WHERE "Owner" = 'okubo.t@cts-n.net'
  AND "Status" NOT IN ('Completed', '完了', 'Closed', '終了')

UNION ALL

SELECT 
    '期限超過タスク数' as 項目,
    COUNT(*) as 件数,
    GROUP_CONCAT("Subject" SEPARATOR ', ') as 詳細
FROM "Tasks"
WHERE "Owner" = 'okubo.t@cts-n.net'
  AND "Status" NOT IN ('Completed', '完了', 'Closed', '終了')
  AND "Due_Date" < CURDATE()

UNION ALL

SELECT 
    '商談関連タスク数' as 項目,
    COUNT(*) as 件数,
    '' as 詳細
FROM "Tasks" t
JOIN "Deals" d ON t."What_Id" = d."id"
WHERE t."Owner" = 'okubo.t@cts-n.net'
  AND t."Status" NOT IN ('Completed', '完了', 'Closed', '終了');"""
    
    sql_queries.append(task_summary_sql)
    
    return sql_queries

def save_task_deal_sql():
    """タスク・商談SQLをファイルに保存"""
    
    print("=== タスク・商談関連SQL生成 ===\n")
    
    # スキーマ分析
    analyze_task_and_deal_schema()
    
    # SQL生成
    sql_queries = generate_task_deal_sql()
    
    # ファイル保存
    with open('zoho_task_deal_queries.sql', 'w', encoding='utf-8') as f:
        f.write("""-- =====================================
-- okubo.t@cts-n.net タスク・商談関連SQLクエリ
-- 生成日時: 2025-06-29
-- =====================================

""")
        
        query_titles = [
            "1. 基本未完了タスク一覧",
            "2. 商談関連情報付きタスク一覧", 
            "3. 期限別タスク分析",
            "4. 商談ステージ別タスク分析",
            "5. 詳細タスク・商談リスト",
            "6. タスク進捗サマリー"
        ]
        
        for i, (title, sql) in enumerate(zip(query_titles, sql_queries)):
            f.write(f"-- =====================================\n")
            f.write(f"-- {title}\n")
            f.write(f"-- =====================================\n\n")
            f.write(sql)
            f.write("\n\n")
    
    print(f"✓ タスク・商談SQLクエリを zoho_task_deal_queries.sql に保存")
    
    # 使用方法の説明
    print("\n=== 使用方法 ===")
    print("1. Zoho Analyticsにログイン")
    print("2. 'Zoho CRMの分析' ワークスペースを開く")
    print("3. 'Query Table' を作成")
    print("4. 上記SQLをコピー&ペーストして実行")
    print("\n=== 注意事項 ===")
    print("- フィールド名が実際のテーブルと異なる場合は調整が必要")
    print("- 日付関数はZoho Analytics固有の書式に調整が必要な場合があります")
    print("- Owner フィールドの値の形式を確認してください")

if __name__ == "__main__":
    save_task_deal_sql()