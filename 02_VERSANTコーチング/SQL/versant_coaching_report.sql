-- VERSANTコーチング 日別学習進捗レポート
-- 受講生ごとの直近3週間の日別回答件数を表示
-- 動的日付範囲（現在日から3週間前まで）

WITH 
-- 動的日付範囲の生成（直近3週間）
date_range AS (
    SELECT 
        DATE_SUB(CURDATE(), INTERVAL 20 DAY) as start_date,
        CURDATE() as end_date
),
-- 日付シリーズの生成（3週間分の日付を生成）
date_series AS (
    SELECT 
        DATE_ADD(
            (SELECT start_date FROM date_range), 
            INTERVAL (a.N + b.N * 10 + c.N * 100) DAY
        ) as report_date
    FROM 
        (SELECT 0 as N UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) a,
        (SELECT 0 as N UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) b,
        (SELECT 0 as N UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) c
    WHERE 
        DATE_ADD(
            (SELECT start_date FROM date_range), 
            INTERVAL (a.N + b.N * 10 + c.N * 100) DAY
        ) <= (SELECT end_date FROM date_range)
),
-- 対象受講生の抽出（指定商品の手配レコードに紐づく連絡先）
target_students AS (
    SELECT DISTINCT
        c.`Id` as contact_id,
        c.`姓` as last_name,
        c.`名` as first_name,
        c.`メール` as email,
        c.`電話` as phone,
        c.`会社名` as company_name,
        -- 学習開始日の取得（手配レコードから）
        MIN(ar.`学習開始日`) as study_start_date
    FROM `連絡先` c
    INNER JOIN `手配` ar ON c.`Id` = ar.`連絡先ID`
    WHERE ar.`商品ID` IN (
        '5187347000184182087',
        '5187347000184182088', 
        '5187347000159927506'
    )
    GROUP BY c.`Id`, c.`姓`, c.`名`, c.`メール`, c.`電話`, c.`会社名`
),
-- VERSANTの日別回答件数
versant_daily_counts AS (
    SELECT 
        v.`連絡先ID`,
        DATE(v.`回答日時`) as answer_date,
        COUNT(*) as daily_answer_count
    FROM `Versant` v
    WHERE v.`連絡先ID` IS NOT NULL
    GROUP BY v.`連絡先ID`, DATE(v.`回答日時`)
),
-- 最終的なレポート（受講生 × 日付のクロス集計）
final_report AS (
    SELECT 
        ts.contact_id,
        ts.last_name,
        ts.first_name,
        ts.email,
        ts.phone,
        ts.company_name,
        ts.study_start_date,
        ds.report_date,
        COALESCE(vdc.daily_answer_count, 0) as daily_answer_count
    FROM target_students ts
    CROSS JOIN date_series ds
    LEFT JOIN versant_daily_counts vdc 
        ON ts.contact_id = vdc.`連絡先ID` 
        AND ds.report_date = vdc.answer_date
)

-- メインクエリ：ピボット形式で日付を横に並べる
SELECT 
    contact_id as `受講生ID`,
    CONCAT(last_name, ' ', first_name) as `受講生名`,
    email as `メールアドレス`,
    phone as `電話番号`,
    company_name as `会社名`,
    study_start_date as `学習開始日`,
    -- 動的に日付カラムを生成（3週間分）
    MAX(CASE WHEN report_date = DATE_SUB(CURDATE(), INTERVAL 20 DAY) THEN daily_answer_count END) as `20日前`,
    MAX(CASE WHEN report_date = DATE_SUB(CURDATE(), INTERVAL 19 DAY) THEN daily_answer_count END) as `19日前`,
    MAX(CASE WHEN report_date = DATE_SUB(CURDATE(), INTERVAL 18 DAY) THEN daily_answer_count END) as `18日前`,
    MAX(CASE WHEN report_date = DATE_SUB(CURDATE(), INTERVAL 17 DAY) THEN daily_answer_count END) as `17日前`,
    MAX(CASE WHEN report_date = DATE_SUB(CURDATE(), INTERVAL 16 DAY) THEN daily_answer_count END) as `16日前`,
    MAX(CASE WHEN report_date = DATE_SUB(CURDATE(), INTERVAL 15 DAY) THEN daily_answer_count END) as `15日前`,
    MAX(CASE WHEN report_date = DATE_SUB(CURDATE(), INTERVAL 14 DAY) THEN daily_answer_count END) as `14日前`,
    MAX(CASE WHEN report_date = DATE_SUB(CURDATE(), INTERVAL 13 DAY) THEN daily_answer_count END) as `13日前`,
    MAX(CASE WHEN report_date = DATE_SUB(CURDATE(), INTERVAL 12 DAY) THEN daily_answer_count END) as `12日前`,
    MAX(CASE WHEN report_date = DATE_SUB(CURDATE(), INTERVAL 11 DAY) THEN daily_answer_count END) as `11日前`,
    MAX(CASE WHEN report_date = DATE_SUB(CURDATE(), INTERVAL 10 DAY) THEN daily_answer_count END) as `10日前`,
    MAX(CASE WHEN report_date = DATE_SUB(CURDATE(), INTERVAL 9 DAY) THEN daily_answer_count END) as `9日前`,
    MAX(CASE WHEN report_date = DATE_SUB(CURDATE(), INTERVAL 8 DAY) THEN daily_answer_count END) as `8日前`,
    MAX(CASE WHEN report_date = DATE_SUB(CURDATE(), INTERVAL 7 DAY) THEN daily_answer_count END) as `7日前`,
    MAX(CASE WHEN report_date = DATE_SUB(CURDATE(), INTERVAL 6 DAY) THEN daily_answer_count END) as `6日前`,
    MAX(CASE WHEN report_date = DATE_SUB(CURDATE(), INTERVAL 5 DAY) THEN daily_answer_count END) as `5日前`,
    MAX(CASE WHEN report_date = DATE_SUB(CURDATE(), INTERVAL 4 DAY) THEN daily_answer_count END) as `4日前`,
    MAX(CASE WHEN report_date = DATE_SUB(CURDATE(), INTERVAL 3 DAY) THEN daily_answer_count END) as `3日前`,
    MAX(CASE WHEN report_date = DATE_SUB(CURDATE(), INTERVAL 2 DAY) THEN daily_answer_count END) as `2日前`,
    MAX(CASE WHEN report_date = DATE_SUB(CURDATE(), INTERVAL 1 DAY) THEN daily_answer_count END) as `1日前`,
    MAX(CASE WHEN report_date = CURDATE() THEN daily_answer_count END) as `今日`,
    -- 合計列
    SUM(daily_answer_count) as `3週間合計`
FROM final_report
GROUP BY 
    contact_id, last_name, first_name, email, phone, company_name, study_start_date
ORDER BY 
    last_name, first_name 