-- VERSANTコーチングテーブルの構造確認
-- テーブルが存在する場合の構造を確認

-- 1. VERSANTコーチングテーブルの構造確認
SELECT 
    'VERSANTコーチング構造' as "確認項目",
    '全カラム' as "詳細",
    '1レコード取得' as "ステータス"
FROM "VERSANTコーチング" 
LIMIT 1

UNION ALL

-- 2. VERSANTコーチングテーブルの基本情報
SELECT 
    'VERSANTコーチング基本' as "確認項目",
    '件数確認' as "詳細",
    CONCAT('総件数: ', COUNT(*)) as "ステータス"
FROM "VERSANTコーチング"

UNION ALL

-- 3. VERSANTコーチングテーブルの日付範囲確認
SELECT 
    'VERSANTコーチング日付' as "確認項目",
    '日付範囲' as "詳細",
    CONCAT('最新: ', MAX("回答日"), ' / 最古: ', MIN("回答日")) as "ステータス"
FROM "VERSANTコーチング"
WHERE "回答日" IS NOT NULL

UNION ALL

-- 4. 特定メールアドレスのVERSANTコーチングデータ確認
SELECT 
    'VERSANTコーチング特定' as "確認項目",
    'naokazu.onishi@lixil.com' as "詳細",
    CONCAT('件数: ', COUNT(*)) as "ステータス"
FROM "VERSANTコーチング"
WHERE "メールアドレス" = 'naokazu.onishi@lixil.com' 