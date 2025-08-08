-- VERSANTコーチング シンプル版レポート
-- 基本的なクエリから始める

SELECT 
    v."Id" as "テストID",
    v."連絡先名" as "受講生ID",
    v."メール" as "メールアドレス",
    v."First Name" as "名",
    v."Last Name" as "姓",
    v."Completion Date" as "完了日",
    v."Overall" as "総合スコア",
    v."Overall CEFR" as "CEFRレベル",
    v."Status" as "ステータス",
    v."TestName" as "テスト名"
FROM "Versant" v
WHERE v."Completion Date" IS NOT NULL
AND DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
ORDER BY v."Completion Date" DESC
LIMIT 10 