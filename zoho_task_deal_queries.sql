-- =====================================
-- okubo.t@cts-n.net タスク・商談関連SQLクエリ
-- 生成日時: 2025-06-29
-- =====================================

-- =====================================
-- 1. 基本未完了タスク一覧
-- =====================================

-- okubo.t@cts-n.net の未完了タスク一覧
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
ORDER BY "Due_Date" ASC, "Priority" DESC;

-- =====================================
-- 2. 商談関連情報付きタスク一覧
-- =====================================

-- okubo.t@cts-n.net の未完了タスク（商談関連情報付き）
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
ORDER BY t."Due_Date" ASC, t."Priority" DESC;

-- =====================================
-- 3. 期限別タスク分析
-- =====================================

-- okubo.t@cts-n.net のタスク期限別分析
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
    END;

-- =====================================
-- 4. 商談ステージ別タスク分析
-- =====================================

-- okubo.t@cts-n.net のタスク（商談ステージ別）
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
ORDER BY 未完了タスク数 DESC, 商談総額 DESC;

-- =====================================
-- 5. 詳細タスク・商談リスト
-- =====================================

-- okubo.t@cts-n.net の詳細タスク・商談リスト
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
    t."Due_Date" ASC;

-- =====================================
-- 6. タスク進捗サマリー
-- =====================================

-- okubo.t@cts-n.net のタスク進捗サマリー
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
  AND t."Status" NOT IN ('Completed', '完了', 'Closed', '終了');

