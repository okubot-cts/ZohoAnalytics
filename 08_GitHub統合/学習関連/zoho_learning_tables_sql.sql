-- =====================================
-- 学習関連テーブル拡張SQLクエリ
-- 生成日時: 2025-06-29 12:52:30.860540
-- 対象テーブル数: 2
-- =====================================

-- CustomModule15 基本クエリ
SELECT 
    "Name"  -- 受講生コード (autonumber),\n    "Owner"  -- 受講生の担当者 (ownerlookup),\n    "Email"  -- メール (email),\n    "Created_By"  -- 作成者 (ownerlookup),\n    "Modified_By"  -- 更新者 (ownerlookup),\n    "Created_Time"  -- 作成日時 (datetime),\n    "Modified_Time"  -- 更新日時 (datetime),\n    "Last_Activity_Time"  -- 最新の操作日時 (datetime),\n    "Currency"  -- 通貨 (picklist),\n    "Exchange_Rate"  -- 為替レート (double),\n    "Tag"  -- タグ (text),\n    "Unsubscribed_Mode"  -- 配信停止の方法 (picklist),\n    "Unsubscribed_Time"  -- 配信停止の日時 (datetime),\n    "Record_Image"  -- 受講生の画像 (profileimage),\n    "Locked__s"  -- Locked (boolean)
FROM "Students"
LIMIT 100;

-- CustomModule15 分析クエリ
-- 受講生ステータス別集計
SELECT 
    "ステータス",
    COUNT(*) as 受講生数
FROM "Students"
GROUP BY "ステータス"
ORDER BY 受講生数 DESC;

-- 受講生登録月別推移
SELECT 
    DATE_FORMAT("作成日時", '%Y-%m') as 登録月,
    COUNT(*) as 新規受講生数
FROM "Students"
GROUP BY DATE_FORMAT("作成日時", '%Y-%m')
ORDER BY 登録月 DESC;

-- LinkingModule12 基本クエリ
SELECT 
    "Created_Time"  -- 作成日時 (datetime),\n    "Parent_Id"  -- 親データID (lookup),\n    "Contact"  -- 連絡先 (lookup),\n    "Note"  -- 備考 (text),\n    "Status"  -- ステータス (picklist),\n    "Student"  -- 受講生 (lookup),\n    "Gemini_Prof_ID"  -- Gemini Prof ID (integer)
FROM "Students_List"
LIMIT 100;

-- LinkingModule12 分析クエリ
-- 受講生ステータス別集計
SELECT 
    "ステータス",
    COUNT(*) as 受講生数
FROM "Students_List"
GROUP BY "ステータス"
ORDER BY 受講生数 DESC;

-- 受講生登録月別推移
SELECT 
    DATE_FORMAT("作成日時", '%Y-%m') as 登録月,
    COUNT(*) as 新規受講生数
FROM "Students_List"
GROUP BY DATE_FORMAT("作成日時", '%Y-%m')
ORDER BY 登録月 DESC;

-- =====================================
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
