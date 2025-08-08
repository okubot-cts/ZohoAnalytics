-- VERSANTコーチング 日別学習進捗レポート（ZohoAnalytics専用）
-- SELECT文のみ使用、ZohoAnalytics構文に最適化

SELECT 
    c."Id" as "受講生ID",
    CONCAT(c."姓", ' ', c."名") as "受講生名",
    c."メール" as "メールアドレス",
    c."会社名" as "会社名",
    MIN(ar."学習開始日") as "学習開始日",
    
    -- 直近3週間の日別件数
    SUM(CASE WHEN DATE(v."回答日時") = DATE_SUB(CURDATE(), INTERVAL 20 DAY) THEN 1 ELSE 0 END) as "20日前",
    SUM(CASE WHEN DATE(v."回答日時") = DATE_SUB(CURDATE(), INTERVAL 19 DAY) THEN 1 ELSE 0 END) as "19日前",
    SUM(CASE WHEN DATE(v."回答日時") = DATE_SUB(CURDATE(), INTERVAL 18 DAY) THEN 1 ELSE 0 END) as "18日前",
    SUM(CASE WHEN DATE(v."回答日時") = DATE_SUB(CURDATE(), INTERVAL 17 DAY) THEN 1 ELSE 0 END) as "17日前",
    SUM(CASE WHEN DATE(v."回答日時") = DATE_SUB(CURDATE(), INTERVAL 16 DAY) THEN 1 ELSE 0 END) as "16日前",
    SUM(CASE WHEN DATE(v."回答日時") = DATE_SUB(CURDATE(), INTERVAL 15 DAY) THEN 1 ELSE 0 END) as "15日前",
    SUM(CASE WHEN DATE(v."回答日時") = DATE_SUB(CURDATE(), INTERVAL 14 DAY) THEN 1 ELSE 0 END) as "14日前",
    SUM(CASE WHEN DATE(v."回答日時") = DATE_SUB(CURDATE(), INTERVAL 13 DAY) THEN 1 ELSE 0 END) as "13日前",
    SUM(CASE WHEN DATE(v."回答日時") = DATE_SUB(CURDATE(), INTERVAL 12 DAY) THEN 1 ELSE 0 END) as "12日前",
    SUM(CASE WHEN DATE(v."回答日時") = DATE_SUB(CURDATE(), INTERVAL 11 DAY) THEN 1 ELSE 0 END) as "11日前",
    SUM(CASE WHEN DATE(v."回答日時") = DATE_SUB(CURDATE(), INTERVAL 10 DAY) THEN 1 ELSE 0 END) as "10日前",
    SUM(CASE WHEN DATE(v."回答日時") = DATE_SUB(CURDATE(), INTERVAL 9 DAY) THEN 1 ELSE 0 END) as "9日前",
    SUM(CASE WHEN DATE(v."回答日時") = DATE_SUB(CURDATE(), INTERVAL 8 DAY) THEN 1 ELSE 0 END) as "8日前",
    SUM(CASE WHEN DATE(v."回答日時") = DATE_SUB(CURDATE(), INTERVAL 7 DAY) THEN 1 ELSE 0 END) as "7日前",
    SUM(CASE WHEN DATE(v."回答日時") = DATE_SUB(CURDATE(), INTERVAL 6 DAY) THEN 1 ELSE 0 END) as "6日前",
    SUM(CASE WHEN DATE(v."回答日時") = DATE_SUB(CURDATE(), INTERVAL 5 DAY) THEN 1 ELSE 0 END) as "5日前",
    SUM(CASE WHEN DATE(v."回答日時") = DATE_SUB(CURDATE(), INTERVAL 4 DAY) THEN 1 ELSE 0 END) as "4日前",
    SUM(CASE WHEN DATE(v."回答日時") = DATE_SUB(CURDATE(), INTERVAL 3 DAY) THEN 1 ELSE 0 END) as "3日前",
    SUM(CASE WHEN DATE(v."回答日時") = DATE_SUB(CURDATE(), INTERVAL 2 DAY) THEN 1 ELSE 0 END) as "2日前",
    SUM(CASE WHEN DATE(v."回答日時") = DATE_SUB(CURDATE(), INTERVAL 1 DAY) THEN 1 ELSE 0 END) as "1日前",
    SUM(CASE WHEN DATE(v."回答日時") = CURDATE() THEN 1 ELSE 0 END) as "今日",
    
    -- 合計と平均
    SUM(CASE WHEN DATE(v."回答日時") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) as "3週間合計",
    ROUND(SUM(CASE WHEN DATE(v."回答日時") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) / 21.0, 1) as "1日平均",
    
    -- 学習状況の判定
    CASE 
        WHEN SUM(CASE WHEN DATE(v."回答日時") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) = 0 THEN '未学習'
        WHEN SUM(CASE WHEN DATE(v."回答日時") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) < 10 THEN '学習不足'
        WHEN SUM(CASE WHEN DATE(v."回答日時") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) < 30 THEN '学習中'
        ELSE '積極的'
    END as "学習状況"
    
FROM "連絡先" c
INNER JOIN "手配" ar ON c."Id" = ar."連絡先ID"
LEFT JOIN "Versant" v ON c."Id" = v."連絡先ID" 
    AND DATE(v."回答日時") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY)
WHERE ar."商品ID" IN (
    '5187347000184182087',
    '5187347000184182088', 
    '5187347000159927506'
)
GROUP BY 
    c."Id", c."姓", c."名", c."メール", c."会社名"
ORDER BY 
    "学習状況" DESC, "3週間合計" DESC, c."姓", c."名" 