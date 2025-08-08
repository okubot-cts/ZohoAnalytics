-- VERSANTコーチング 重複カウント修正版レポート
-- 手配レコードが複数ある場合でもAnswerテーブルの数値が重複しないように修正

SELECT
    c."Id" as "受講生ID",
    CONCAT(c."姓", ' ', c."名") as "受講生名",
    c."メール" as "メールアドレス",
    acc."取引先名" as "会社名",
    GROUP_CONCAT(DISTINCT p."商品名" SEPARATOR ', ') as "手配商品名",
    MIN(ar."学習開始日") as "学習開始日",
    
    -- 直近3週間の日別VERSANTコーチング回答数（重複なし）
    COALESCE(answer_stats."20日前", 0) as "20日前",
    COALESCE(answer_stats."19日前", 0) as "19日前",
    COALESCE(answer_stats."18日前", 0) as "18日前",
    COALESCE(answer_stats."17日前", 0) as "17日前",
    COALESCE(answer_stats."16日前", 0) as "16日前",
    COALESCE(answer_stats."15日前", 0) as "15日前",
    COALESCE(answer_stats."14日前", 0) as "14日前",
    COALESCE(answer_stats."13日前", 0) as "13日前",
    COALESCE(answer_stats."12日前", 0) as "12日前",
    COALESCE(answer_stats."11日前", 0) as "11日前",
    COALESCE(answer_stats."10日前", 0) as "10日前",
    COALESCE(answer_stats."9日前", 0) as "9日前",
    COALESCE(answer_stats."8日前", 0) as "8日前",
    COALESCE(answer_stats."7日前", 0) as "7日前",
    COALESCE(answer_stats."6日前", 0) as "6日前",
    COALESCE(answer_stats."5日前", 0) as "5日前",
    COALESCE(answer_stats."4日前", 0) as "4日前",
    COALESCE(answer_stats."3日前", 0) as "3日前",
    COALESCE(answer_stats."2日前", 0) as "2日前",
    COALESCE(answer_stats."1日前", 0) as "1日前",
    COALESCE(answer_stats."今日", 0) as "今日",
    
    -- 直近3週間の合計VERSANTコーチング回答数
    COALESCE(answer_stats."3週間合計", 0) as "3週間合計",
    COALESCE(answer_stats."1日平均", 0) as "1日平均",
    
    -- 全期間のVERSANTコーチング回答数
    COALESCE(answer_stats."全期間合計", 0) as "全期間合計",
    
    -- 学習状況の判定
    CASE 
        WHEN COALESCE(answer_stats."3週間合計", 0) = 0 THEN '未学習'
        WHEN COALESCE(answer_stats."3週間合計", 0) < 10 THEN '学習不足'
        WHEN COALESCE(answer_stats."3週間合計", 0) < 30 THEN '学習中'
        ELSE '積極的'
    END as "学習状況"
    
FROM "連絡先" c
INNER JOIN "手配" ar ON c."Id" = ar."連絡先"
LEFT JOIN "取引先" acc ON c."取引先名" = acc."Id"
LEFT JOIN "商品" p ON ar."商品" = p."Id"
LEFT JOIN (
    -- Answerテーブルの集計を先に行う（重複を防ぐ）
    SELECT 
        a."eMail" as "メール",
        SUM(CASE WHEN DATE(a."Created at") = DATE_SUB(CURDATE(), INTERVAL 20 DAY) THEN 1 ELSE 0 END) as "20日前",
        SUM(CASE WHEN DATE(a."Created at") = DATE_SUB(CURDATE(), INTERVAL 19 DAY) THEN 1 ELSE 0 END) as "19日前",
        SUM(CASE WHEN DATE(a."Created at") = DATE_SUB(CURDATE(), INTERVAL 18 DAY) THEN 1 ELSE 0 END) as "18日前",
        SUM(CASE WHEN DATE(a."Created at") = DATE_SUB(CURDATE(), INTERVAL 17 DAY) THEN 1 ELSE 0 END) as "17日前",
        SUM(CASE WHEN DATE(a."Created at") = DATE_SUB(CURDATE(), INTERVAL 16 DAY) THEN 1 ELSE 0 END) as "16日前",
        SUM(CASE WHEN DATE(a."Created at") = DATE_SUB(CURDATE(), INTERVAL 15 DAY) THEN 1 ELSE 0 END) as "15日前",
        SUM(CASE WHEN DATE(a."Created at") = DATE_SUB(CURDATE(), INTERVAL 14 DAY) THEN 1 ELSE 0 END) as "14日前",
        SUM(CASE WHEN DATE(a."Created at") = DATE_SUB(CURDATE(), INTERVAL 13 DAY) THEN 1 ELSE 0 END) as "13日前",
        SUM(CASE WHEN DATE(a."Created at") = DATE_SUB(CURDATE(), INTERVAL 12 DAY) THEN 1 ELSE 0 END) as "12日前",
        SUM(CASE WHEN DATE(a."Created at") = DATE_SUB(CURDATE(), INTERVAL 11 DAY) THEN 1 ELSE 0 END) as "11日前",
        SUM(CASE WHEN DATE(a."Created at") = DATE_SUB(CURDATE(), INTERVAL 10 DAY) THEN 1 ELSE 0 END) as "10日前",
        SUM(CASE WHEN DATE(a."Created at") = DATE_SUB(CURDATE(), INTERVAL 9 DAY) THEN 1 ELSE 0 END) as "9日前",
        SUM(CASE WHEN DATE(a."Created at") = DATE_SUB(CURDATE(), INTERVAL 8 DAY) THEN 1 ELSE 0 END) as "8日前",
        SUM(CASE WHEN DATE(a."Created at") = DATE_SUB(CURDATE(), INTERVAL 7 DAY) THEN 1 ELSE 0 END) as "7日前",
        SUM(CASE WHEN DATE(a."Created at") = DATE_SUB(CURDATE(), INTERVAL 6 DAY) THEN 1 ELSE 0 END) as "6日前",
        SUM(CASE WHEN DATE(a."Created at") = DATE_SUB(CURDATE(), INTERVAL 5 DAY) THEN 1 ELSE 0 END) as "5日前",
        SUM(CASE WHEN DATE(a."Created at") = DATE_SUB(CURDATE(), INTERVAL 4 DAY) THEN 1 ELSE 0 END) as "4日前",
        SUM(CASE WHEN DATE(a."Created at") = DATE_SUB(CURDATE(), INTERVAL 3 DAY) THEN 1 ELSE 0 END) as "3日前",
        SUM(CASE WHEN DATE(a."Created at") = DATE_SUB(CURDATE(), INTERVAL 2 DAY) THEN 1 ELSE 0 END) as "2日前",
        SUM(CASE WHEN DATE(a."Created at") = DATE_SUB(CURDATE(), INTERVAL 1 DAY) THEN 1 ELSE 0 END) as "1日前",
        SUM(CASE WHEN DATE(a."Created at") = CURDATE() THEN 1 ELSE 0 END) as "今日",
        SUM(CASE WHEN DATE(a."Created at") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) as "3週間合計",
        ROUND(SUM(CASE WHEN DATE(a."Created at") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) / 21.0, 1) as "1日平均",
        COUNT(a."Created at") as "全期間合計"
    FROM "Answer" a
    WHERE a."eMail" <> 'admin@cts-n.net'
        AND a."Created at" IS NOT NULL
    GROUP BY a."eMail"
) answer_stats ON c."メール" = answer_stats."メール"
WHERE ar."商品" IN (
    '5187347000184182087',
    '5187347000184182088', 
    '5187347000159927506'
)
GROUP BY 
    c."Id", c."姓", c."名", c."メール", acc."取引先名", 
    answer_stats."20日前", answer_stats."19日前", answer_stats."18日前", answer_stats."17日前", 
    answer_stats."16日前", answer_stats."15日前", answer_stats."14日前", answer_stats."13日前", 
    answer_stats."12日前", answer_stats."11日前", answer_stats."10日前", answer_stats."9日前", 
    answer_stats."8日前", answer_stats."7日前", answer_stats."6日前", answer_stats."5日前", 
    answer_stats."4日前", answer_stats."3日前", answer_stats."2日前", answer_stats."1日前", 
    answer_stats."今日", answer_stats."3週間合計", answer_stats."1日平均", answer_stats."全期間合計"
ORDER BY 
    "学習状況" DESC, "3週間合計" DESC, c."姓", c."名" 