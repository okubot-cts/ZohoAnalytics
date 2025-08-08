-- 特定の受講生の手配データ確認
-- naokazu.onishi@lixil.com の手配情報を確認

SELECT 
    ar."連絡先" as "連絡先ID",
    ar."商品" as "商品ID",
    ar."商品名" as "商品名",
    ar."ステータス" as "ステータス",
    ar."作成日時" as "作成日時",
    c."姓" as "姓",
    c."名" as "名",
    c."メール" as "メールアドレス",
    c."所属会社" as "会社名"
FROM "手配" ar
INNER JOIN "連絡先" c ON ar."連絡先" = c."Id"
WHERE c."メール" = 'naokazu.onishi@lixil.com'
ORDER BY ar."作成日時" DESC 