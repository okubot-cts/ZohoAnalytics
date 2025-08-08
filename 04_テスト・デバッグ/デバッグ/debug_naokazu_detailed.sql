-- 大西さんの詳細データ確認
-- naokazu.onishi@lixil.com の手配・連絡先・VERSANTデータを詳細確認

-- 1. 連絡先データの確認
SELECT 
    '連絡先データ' as "データ種別",
    c."Id" as "連絡先ID",
    c."姓" as "姓",
    c."名" as "名", 
    c."メール" as "メールアドレス",
    c."所属会社" as "会社名"
FROM "連絡先" c
WHERE c."メール" = 'naokazu.onishi@lixil.com'

UNION ALL

-- 2. 手配データの確認
SELECT 
    '手配データ' as "データ種別",
    ar."連絡先ID" as "連絡先ID",
    ar."商品ID" as "商品ID",
    ar."商品名" as "商品名",
    ar."ステータス" as "ステータス",
    ar."作成日時" as "作成日時"
FROM "手配" ar
INNER JOIN "連絡先" c ON ar."連絡先ID" = c."Id"
WHERE c."メール" = 'naokazu.onishi@lixil.com'

UNION ALL

-- 3. VERSANTデータの確認（直近3週間）
SELECT 
    'VERSANTデータ（3週間）' as "データ種別",
    v."連絡先名" as "連絡先ID",
    v."Completion Date" as "回答日",
    v."Overall" as "スコア",
    v."TestName" as "テスト名",
    v."Status" as "ステータス"
FROM "Versant" v
WHERE v."メール" = 'naokazu.onishi@lixil.com'
    AND DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY)

UNION ALL

-- 4. VERSANTデータの確認（全期間）
SELECT 
    'VERSANTデータ（全期間）' as "データ種別",
    v."連絡先名" as "連絡先ID",
    v."Completion Date" as "回答日",
    v."Overall" as "スコア",
    v."TestName" as "テスト名",
    v."Status" as "ステータス"
FROM "Versant" v
WHERE v."メール" = 'naokazu.onishi@lixil.com'
ORDER BY "データ種別", "回答日" DESC 