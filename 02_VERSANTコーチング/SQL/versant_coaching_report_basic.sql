-- VERSANTコーチング 基本版レポート
-- 直近3週間の提出回数を受講生別にカウント

SELECT 
    v."連絡先名" as "受講生ID",
    COUNT(*) as "3週間合計",
    ROUND(COUNT(*) / 21.0, 1) as "1日平均",
    
    -- 学習状況の判定
    CASE 
        WHEN COUNT(*) = 0 THEN '未学習'
        WHEN COUNT(*) < 10 THEN '学習不足'
        WHEN COUNT(*) < 30 THEN '学習中'
        ELSE '積極的'
    END as "学習状況"
    
FROM "Versant" v
WHERE v."Completion Date" IS NOT NULL
    AND DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY)
GROUP BY 
    v."連絡先名"
ORDER BY 
    "学習状況" DESC, "3週間合計" DESC 