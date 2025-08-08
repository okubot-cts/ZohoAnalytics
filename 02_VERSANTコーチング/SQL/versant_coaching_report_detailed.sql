-- VERSANTコーチング 詳細レポート
-- 受講生ごとの学習進捗分析

SELECT 
    v."連絡先名" as "受講生ID",
    CONCAT(v."Last Name", ' ', v."First Name") as "受講生名",
    v."メール" as "メールアドレス",
    
    -- 最新のテスト結果
    MAX(v."Overall") as "最新スコア",
    MAX(v."Overall CEFR") as "最新CEFR",
    MAX(v."Completion Date") as "最新テスト日",
    
    -- テスト回数
    COUNT(*) as "テスト回数",
    
    -- スコアの推移
    MIN(v."Overall") as "最低スコア",
    MAX(v."Overall") as "最高スコア",
    ROUND(AVG(CAST(v."Overall" AS DECIMAL(5,2))), 1) as "平均スコア",
    
    -- 学習状況の判定
    CASE 
        WHEN COUNT(*) = 1 THEN '初回受験'
        WHEN COUNT(*) < 3 THEN '学習開始'
        WHEN COUNT(*) < 10 THEN '学習中'
        ELSE '継続学習'
    END as "学習段階",
    
    -- スコア改善状況
    CASE 
        WHEN MAX(CAST(v."Overall" AS DECIMAL(5,2))) - MIN(CAST(v."Overall" AS DECIMAL(5,2))) > 10 THEN '大幅改善'
        WHEN MAX(CAST(v."Overall" AS DECIMAL(5,2))) - MIN(CAST(v."Overall" AS DECIMAL(5,2))) > 5 THEN '改善'
        WHEN MAX(CAST(v."Overall" AS DECIMAL(5,2))) - MIN(CAST(v."Overall" AS DECIMAL(5,2))) > 0 THEN '微改善'
        ELSE '変化なし'
    END as "スコア推移",
    
    -- 最新のテスト詳細
    MAX(v."TestName") as "最新テスト名",
    MAX(v."Status") as "最新ステータス"
    
FROM "Versant" v
WHERE v."Completion Date" IS NOT NULL
AND DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
AND v."Overall" IS NOT NULL
AND v."Overall" != ''
GROUP BY 
    v."連絡先名", v."Last Name", v."First Name", v."メール"
HAVING COUNT(*) >= 1
ORDER BY 
    "最新テスト日" DESC, "テスト回数" DESC, "最新スコア" DESC 