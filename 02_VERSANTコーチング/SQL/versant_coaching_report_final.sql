-- VERSANTコーチング 日別学習進捗レポート（最終版）
-- 実際のテーブル構造に基づいて作成

SELECT 
    c."Id" as "受講生ID",
    CONCAT(c."姓", ' ', c."名") as "受講生名",
    c."メール" as "メールアドレス",
    c."所属会社" as "会社名",
    MIN(ar."学習開始日") as "学習開始日",
    
    -- 直近3週間の日別件数
    SUM(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) as "3週間合計",
    ROUND(SUM(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) / 21.0, 1) as "1日平均",
    
    -- 最新のテスト結果
    MAX(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN v."Overall" ELSE NULL END) as "最新スコア",
    MAX(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN v."Overall CEFR" ELSE NULL END) as "最新CEFR",
    
    -- 学習状況の判定
    CASE 
        WHEN SUM(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) = 0 THEN '未学習'
        WHEN SUM(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) < 3 THEN '学習不足'
        WHEN SUM(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) < 10 THEN '学習中'
        ELSE '積極的'
    END as "学習状況",
    
    -- 担当者情報
    ar."手配の担当者 Name" as "担当者"
    
FROM "連絡先" c
INNER JOIN "手配" ar ON c."Id" = ar."連絡先"
LEFT JOIN "Versant" v ON c."Id" = v."連絡先名" 
    AND DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY)
WHERE ar."商品" IN (
    '5187347000184182087',
    '5187347000184182088', 
    '5187347000159927506'
)
AND ar."ステータス" = '手配完了'
GROUP BY 
    c."Id", c."姓", c."名", c."メール", c."所属会社", ar."手配の担当者 Name"
ORDER BY 
    "学習状況" DESC, "3週間合計" DESC, c."姓", c."名" 