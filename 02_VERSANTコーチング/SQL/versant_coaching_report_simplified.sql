-- VERSANTコーチング 簡略版レポート
-- 直近3週間の提出回数を受講生別にカウント

SELECT 
    c."Id" as "受講生ID",
    CONCAT(c."Last Name", ' ', c."First Name") as "受講生名",
    c."メール" as "メールアドレス",
    c."所属会社" as "会社名",
    
    -- 直近3週間の日別件数（短縮版）
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 20 DAY) THEN 1 ELSE 0 END) as "D20",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 19 DAY) THEN 1 ELSE 0 END) as "D19",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 18 DAY) THEN 1 ELSE 0 END) as "D18",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 17 DAY) THEN 1 ELSE 0 END) as "D17",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 16 DAY) THEN 1 ELSE 0 END) as "D16",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 15 DAY) THEN 1 ELSE 0 END) as "D15",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 14 DAY) THEN 1 ELSE 0 END) as "D14",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 13 DAY) THEN 1 ELSE 0 END) as "D13",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 12 DAY) THEN 1 ELSE 0 END) as "D12",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 11 DAY) THEN 1 ELSE 0 END) as "D11",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 10 DAY) THEN 1 ELSE 0 END) as "D10",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 9 DAY) THEN 1 ELSE 0 END) as "D9",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 8 DAY) THEN 1 ELSE 0 END) as "D8",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 7 DAY) THEN 1 ELSE 0 END) as "D7",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 6 DAY) THEN 1 ELSE 0 END) as "D6",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 5 DAY) THEN 1 ELSE 0 END) as "D5",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 4 DAY) THEN 1 ELSE 0 END) as "D4",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 3 DAY) THEN 1 ELSE 0 END) as "D3",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 2 DAY) THEN 1 ELSE 0 END) as "D2",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 1 DAY) THEN 1 ELSE 0 END) as "D1",
    SUM(CASE WHEN DATE(v."Completion Date") = CURDATE() THEN 1 ELSE 0 END) as "今日",
    
    -- 合計と平均
    SUM(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) as "3週間合計",
    ROUND(SUM(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) / 21.0, 1) as "1日平均",
    
    -- 学習状況の判定
    CASE 
        WHEN SUM(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) = 0 THEN '未学習'
        WHEN SUM(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) < 10 THEN '学習不足'
        WHEN SUM(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) < 30 THEN '学習中'
        ELSE '積極的'
    END as "学習状況"
    
FROM "連絡先" c
INNER JOIN "手配" ar ON c."Id" = ar."連絡先"
LEFT JOIN "Versant" v ON c."Id" = v."連絡先名" 
    AND DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY)
WHERE ar."商品" IN (
    '5187347000184182087',
    '5187347000184182088', 
    '5187347000159927506'
)
GROUP BY 
    c."Id", c."Last Name", c."First Name", c."メール", c."所属会社"
ORDER BY 
    "学習状況" DESC, "3週間合計" DESC, c."Last Name", c."First Name" 