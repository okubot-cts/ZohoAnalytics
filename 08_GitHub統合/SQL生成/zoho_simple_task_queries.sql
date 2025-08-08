-- =====================================
-- okubo.t@cts-n.net タスク・商談関連 シンプルSQLクエリ
-- Zoho Analytics SELECT文のみ対応版
-- =====================================

-- =====================================
-- 1. 基本未完了タスク一覧（シンプル版）
-- =====================================

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
  AND "Status" <> 'Completed'
ORDER BY "Due_Date" ASC;

-- =====================================
-- 2. 商談関連情報付きタスク一覧（シンプル版）
-- =====================================

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
    d."Closing_Date" as 商談完了予定日
FROM "Tasks" t
LEFT JOIN "Deals" d ON t."What_Id" = d."id"
WHERE t."Owner" = 'okubo.t@cts-n.net'
  AND t."Status" <> 'Completed'
ORDER BY t."Due_Date" ASC;

-- =====================================
-- 3. 期限超過タスク一覧
-- =====================================

SELECT 
    "Subject" as タスク件名,
    "Status" as ステータス,
    "Priority" as 優先度,
    "Due_Date" as 期限,
    "Description" as 説明
FROM "Tasks"
WHERE "Owner" = 'okubo.t@cts-n.net'
  AND "Status" <> 'Completed'
  AND "Due_Date" < NOW()
ORDER BY "Due_Date" ASC;

-- =====================================
-- 4. 本日期限のタスク
-- =====================================

SELECT 
    "Subject" as タスク件名,
    "Status" as ステータス,
    "Priority" as 優先度,
    "Due_Date" as 期限,
    "Description" as 説明
FROM "Tasks"
WHERE "Owner" = 'okubo.t@cts-n.net'
  AND "Status" <> 'Completed'
  AND DATE("Due_Date") = DATE(NOW())
ORDER BY "Priority" DESC;

-- =====================================
-- 5. 高優先度の未完了タスク
-- =====================================

SELECT 
    "Subject" as タスク件名,
    "Status" as ステータス,
    "Priority" as 優先度,
    "Due_Date" as 期限,
    "Description" as 説明,
    "Created_Time" as 作成日時
FROM "Tasks"
WHERE "Owner" = 'okubo.t@cts-n.net'
  AND "Status" <> 'Completed'
  AND "Priority" = 'High'
ORDER BY "Due_Date" ASC;

-- =====================================
-- 6. 商談関連タスクのみ
-- =====================================

SELECT 
    t."Subject" as タスク件名,
    t."Status" as タスクステータス,
    t."Priority" as 優先度,
    t."Due_Date" as 期限,
    d."Deal_Name" as 商談名,
    d."Stage" as 商談ステージ,
    d."Amount" as 商談金額,
    d."Account_Name" as 取引先名
FROM "Tasks" t
INNER JOIN "Deals" d ON t."What_Id" = d."id"
WHERE t."Owner" = 'okubo.t@cts-n.net'
  AND t."Status" <> 'Completed'
ORDER BY t."Due_Date" ASC;

-- =====================================
-- 7. 連絡先関連タスク（商談情報付き）
-- =====================================

SELECT 
    t."Subject" as タスク件名,
    t."Status" as タスクステータス,
    t."Priority" as 優先度,
    t."Due_Date" as 期限,
    c."First_Name" as 連絡先名,
    c."Last_Name" as 連絡先姓,
    c."Email" as 連絡先メール,
    d."Deal_Name" as 商談名,
    d."Stage" as 商談ステージ
FROM "Tasks" t
LEFT JOIN "Contacts" c ON t."Who_Id" = c."id"
LEFT JOIN "Deals" d ON t."What_Id" = d."id"
WHERE t."Owner" = 'okubo.t@cts-n.net'
  AND t."Status" <> 'Completed'
ORDER BY t."Due_Date" ASC;

-- =====================================
-- 8. 最近作成されたタスク（過去7日）
-- =====================================

SELECT 
    "Subject" as タスク件名,
    "Status" as ステータス,
    "Priority" as 優先度,
    "Due_Date" as 期限,
    "Created_Time" as 作成日時,
    "Description" as 説明
FROM "Tasks"
WHERE "Owner" = 'okubo.t@cts-n.net'
  AND "Status" <> 'Completed'
  AND "Created_Time" >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY "Created_Time" DESC;

-- =====================================
-- 9. 期限が設定されていない未完了タスク
-- =====================================

SELECT 
    "Subject" as タスク件名,
    "Status" as ステータス,
    "Priority" as 優先度,
    "Due_Date" as 期限,
    "Created_Time" as 作成日時,
    "Description" as 説明
FROM "Tasks"
WHERE "Owner" = 'okubo.t@cts-n.net'
  AND "Status" <> 'Completed'
  AND ("Due_Date" IS NULL OR "Due_Date" = '')
ORDER BY "Created_Time" DESC;

-- =====================================
-- 10. 特定商談ステージのタスク
-- =====================================

SELECT 
    t."Subject" as タスク件名,
    t."Status" as タスクステータス,
    t."Priority" as 優先度,
    t."Due_Date" as 期限,
    d."Deal_Name" as 商談名,
    d."Stage" as 商談ステージ,
    d."Amount" as 商談金額
FROM "Tasks" t
INNER JOIN "Deals" d ON t."What_Id" = d."id"
WHERE t."Owner" = 'okubo.t@cts-n.net'
  AND t."Status" <> 'Completed'
  AND d."Stage" IN ('Proposal', '提案', 'Negotiation', '交渉')
ORDER BY d."Amount" DESC;