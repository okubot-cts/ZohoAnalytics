-- 特定の受講生のデータ確認
-- naokazu.onishi@lixil.com の詳細データを確認

SELECT 
    v."連絡先名" as "受講生ID",
    v."Last Name" as "姓",
    v."First Name" as "名",
    v."メール" as "メールアドレス",
    v."Completion Date" as "完了日",
    v."Overall" as "スコア",
    v."TestName" as "テスト名",
    v."Status" as "ステータス"
FROM "Versant" v
WHERE v."メール" = 'naokazu.onishi@lixil.com'
ORDER BY v."Completion Date" DESC 