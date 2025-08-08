-- VERSANTコーチング 拡張版レポート（日付範囲拡大・商品フィルターなし）
-- より長期間のデータを確認

SELECT 
    c."Id" as "受講生ID",
    CONCAT(c."姓", ' ', c."名") as "受講生名",
    c."メール" as "メールアドレス",
    c."所属会社" as "会社名",
    
    -- 直近3週間の合計件数
    SUM(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) as "3週間合計",
    ROUND(SUM(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) / 21.0, 1) as "1日平均",
    
    -- 直近90日の合計件数
    SUM(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 90 DAY) THEN 1 ELSE 0 END) as "90日合計",
    
    -- 全期間の合計件数
    COUNT(*) as "全期間合計",
    
    -- 学習状況の判定
    CASE 
        WHEN SUM(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) = 0 THEN '未学習'
        WHEN SUM(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) < 10 THEN '学習不足'
        WHEN SUM(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) < 30 THEN '学習中'
        ELSE '積極的'
    END as "学習状況"
    
FROM "連絡先" c
LEFT JOIN "Versant" v ON c."Id" = v."連絡先名" 
    AND v."Completion Date" IS NOT NULL
GROUP BY 
    c."Id", c."姓", c."名", c."メール", c."所属会社"
HAVING COUNT(*) > 0
ORDER BY 
    "全期間合計" DESC, "90日合計" DESC, "3週間合計" DESC 