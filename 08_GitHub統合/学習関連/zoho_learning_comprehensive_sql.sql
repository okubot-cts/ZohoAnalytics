-- =====================================
-- 学習実績・修了要件・受講生 包括的SQLクエリ
-- 生成日時: 2025-06-29 12:53:25.560669
-- 対象テーブル数: 19
-- =====================================

-- =====================================
-- CustomModule53 (Attendance_Detail)
-- フィールド数: 91
-- =====================================

-- 全フィールド基本クエリ
SELECT 
    "Name"  -- 詳細名 (text),
    "Owner"  -- 詳細の担当者 (ownerlookup),
    "Created_By"  -- 作成者 (ownerlookup),
    "Modified_By"  -- 更新者 (ownerlookup),
    "Created_Time"  -- 作成日時 (datetime),
    "Modified_Time"  -- 更新日時 (datetime),
    "Last_Activity_Time"  -- 最新の操作日時 (datetime),
    "Currency"  -- 通貨 (picklist),
    "Exchange_Rate"  -- 為替レート (double),
    "Layout"  -- レイアウト (bigint),
    "Tag"  -- タグ (text),
    "Unsubscribed_Mode"  -- 配信停止の方法 (picklist),
    "Unsubscribed_Time"  -- 配信停止の日時 (datetime),
    "Record_Image"  -- 詳細の画像 (profileimage),
    "Locked__s"  -- Locked (boolean),
    "Attendance_List"  -- 出欠情報 (subform),
    "Class"  -- クラス (lookup),
    "field2"  -- レッスン開始時刻 (datetime),
    "field3"  -- レッスン終了時刻 (datetime),
    "Instructor_Information"  -- 講師情報 (lookup),
    "URL"  -- レッスンURL (website),
    "Class_Place"  -- 開講場所 (text),
    "Cancell_Policy"  -- キャンセル規定 (text),
    "field"  -- オファー (multiselectlookup),
    "field1"  -- 講師時給（単価） (currency),
    "H1"  -- レッスン時間（H） (formula),
    "field4"  -- 休憩時間（分） (integer),
    "field5"  -- アプリ売上（単価） (currency),
    "field6"  -- レッスン時の注意事項 (textarea),
    "field7"  -- レッスン講師給与 (formula),
    "field8"  -- レッスン売上金額 (formula),
    "field9"  -- 評価表 (picklist),
    "field10"  -- 評価表作成締切日 (date),
    "field11"  -- 最終レッスン (boolean),
    "field12"  -- アンケート (picklist),
    "field13"  -- アンケート種類 (picklist),
    "field14"  -- クライテリア (picklist),
    "field16"  -- 商品 (lookup),
    "field17"  -- アプリ数量 (integer),
    "field18"  -- アプリ原価（単価） (currency),
    "field19"  -- アプリ売上金額 (formula),
    "field20"  -- アプリ原価金額 (formula),
    "field21"  -- 原価金額 (formula),
    "field22"  -- アプリ終了日 (date),
    "field23"  -- 宿題メモ (textarea),
    "ID1"  -- アプリID (text),
    "field24"  -- キャンアド (lookup),
    "field25"  -- 宿題 (textarea),
    "field26"  -- 教材① (lookup),
    "field27"  -- アプリ開始日 (date),
    "CS"  -- 講師メモ (textarea),
    "field28"  -- 売上金額 (formula),
    "field29"  -- 備考 (textarea),
    "field30"  -- 教材② (lookup),
    "TOEIC_IP"  -- TOEIC IP (lookup),
    "VERSANT"  -- VERSANT (lookup),
    "GTEC"  -- GTEC (lookup),
    "field15"  -- ステータス (picklist),
    "Gemini1"  -- Gemini講師単価 (currency),
    "Gemini2"  -- Gemini売上金額 (currency),
    "Gemini4"  -- Gemini数量 (integer),
    "Gemini3"  -- Gemini原価金額 (formula),
    "field31"  -- 講師区分 (picklist),
    "field32"  -- レッスン講師日給 (currency),
    "PDF"  -- 教材①受講生用PDF (website),
    "PPT"  -- 教材①講師用PPT (website),
    "field33"  -- 教材①講師用マニュアル (website),
    "PPT1"  -- 教材②講師用PPT (website),
    "PDF1"  -- 教材②受講生用PDF (website),
    "field34"  -- 教材②講師用マニュアル (website),
    "TORA"  -- TORA固有キー (text),
    "field35"  -- コメント回収予定日 (date),
    "field36"  -- コメント対象レッスン最終回 (boolean),
    "field37"  -- コメント確認済 (boolean),
    "field38"  -- コメント回収済 (boolean),
    "field39"  -- 種類 (picklist),
    "field40"  -- 開講チェック (boolean),
    "field41"  -- 開始時刻曜日 (formula),
    "field42"  -- ホスト情報 (text),
    "field43"  -- コメント送信済 (boolean),
    "Gemini_task_id"  -- Gemini task id (integer),
    "field44"  -- 開講担当者 (userlookup),
    "field45"  -- その他給与 (currency),
    "field46"  -- その他給与メモ (textarea),
    "record_year"  -- 集計年 (integer),
    "record_month"  -- 集計月 (integer),
    "field47"  -- 詳細コード (autonumber),
    "TimerexID"  -- TimerexID (text),
    "URL1"  -- レッスンURL変更日 (date),
    "ID2"  -- MeetingID／カレンダーID (text),
    "field48"  -- 作業担当者 (userlookup)
FROM "Attendance_Detail"
LIMIT 100;

-- CustomModule53 レコード数確認
SELECT COUNT(*) as total_records
FROM "Attendance_Detail";

-- CustomModule53 出席率分析
SELECT 
    "出席ステータス",
    COUNT(*) as 記録数,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM "Attendance_Detail"), 2) as 割合
FROM "Attendance_Detail"
GROUP BY "出席ステータス"
ORDER BY 記録数 DESC;

-- =====================================
-- CustomModule56 (Seoul)
-- フィールド数: 48
-- =====================================

-- 全フィールド基本クエリ
SELECT 
    "Name"  -- Seoul作業依頼番号 (autonumber),
    "Owner"  -- Seoul作業依頼の担当者 (ownerlookup),
    "Created_By"  -- 作成者 (ownerlookup),
    "Modified_By"  -- 更新者 (ownerlookup),
    "Created_Time"  -- 作成日時 (datetime),
    "Modified_Time"  -- 更新日時 (datetime),
    "Last_Activity_Time"  -- 最新の操作日時 (datetime),
    "Layout"  -- レイアウト (bigint),
    "Tag"  -- タグ (text),
    "Unsubscribed_Mode"  -- 配信停止の方法 (picklist),
    "Unsubscribed_Time"  -- 配信停止の日時 (datetime),
    "Record_Image"  -- Seoul作業依頼の画像 (profileimage),
    "field"  -- 作業期限 (datetime),
    "field1"  -- 作業内容詳細 (textarea),
    "field2"  -- 依頼者（入力者） (userlookup),
    "field3"  -- 作業担当者 (userlookup),
    "field4"  -- 作業完了通知先 (textarea),
    "field5"  -- 商談名 (lookup),
    "field6"  -- 添付ファイル① (fileupload),
    "field7"  -- 依頼種類 (picklist),
    "Locked__s"  -- Locked (boolean),
    "field8"  -- 連絡先 (lookup),
    "field9"  -- アプリ (multiselectpicklist),
    "field10"  -- メール送信方法 (picklist),
    "field11"  -- 登録対象タブ (picklist),
    "field12"  -- ステータス (picklist),
    "field13"  -- 件名 (text),
    "zoho_URL"  -- zohoレポートURL① (website),
    "field14"  -- 優先度 (picklist),
    "field15"  -- レポートに必要な項目 (textarea),
    "zoho_URL1"  -- zohoレポートURL② (website),
    "zoho_URL2"  -- zohoレポートURL③ (website),
    "field16"  -- レポートの用途 (textarea),
    "URL"  -- URL ③ (website),
    "field17"  -- 添付ファイル② (fileupload),
    "field18"  -- 添付ファイル③ (fileupload),
    "URL1"  -- URL ① (website),
    "URL2"  -- URL ② (website),
    "field19"  -- 商談4詳細 (text),
    "field20"  -- 商談1詳細 (text),
    "field21"  -- 商談5詳細 (text),
    "field22"  -- 商談2詳細 (text),
    "field23"  -- 商談3詳細 (text),
    "field24"  -- 商談 4 (lookup),
    "field25"  -- 商談 5 (lookup),
    "field26"  -- 商談 2 (lookup),
    "field27"  -- 商談 3 (lookup),
    "field28"  -- 商談 1 (lookup)
FROM "Seoul"
LIMIT 100;

-- CustomModule56 レコード数確認
SELECT COUNT(*) as total_records
FROM "Seoul";

-- =====================================
-- CustomModule15 (Students)
-- フィールド数: 35
-- =====================================

-- 全フィールド基本クエリ
SELECT 
    "Name"  -- 受講生コード (autonumber),
    "Owner"  -- 受講生の担当者 (ownerlookup),
    "Email"  -- メール (email),
    "Created_By"  -- 作成者 (ownerlookup),
    "Modified_By"  -- 更新者 (ownerlookup),
    "Created_Time"  -- 作成日時 (datetime),
    "Modified_Time"  -- 更新日時 (datetime),
    "Last_Activity_Time"  -- 最新の操作日時 (datetime),
    "Currency"  -- 通貨 (picklist),
    "Exchange_Rate"  -- 為替レート (double),
    "Tag"  -- タグ (text),
    "Unsubscribed_Mode"  -- 配信停止の方法 (picklist),
    "Unsubscribed_Time"  -- 配信停止の日時 (datetime),
    "Record_Image"  -- 受講生の画像 (profileimage),
    "Locked__s"  -- Locked (boolean),
    "Class"  -- クラス (lookup),
    "Contact"  -- 連絡先 (lookup),
    "field2"  -- 取引先名 (lookup),
    "field3"  -- 受講生のメール (email),
    "Last_Name"  -- 姓 (text),
    "First_Name"  -- 名 (text),
    "Account_Name"  -- 取引先 (text),
    "Gemini_Prof_ID"  -- Gemini Prof ID (integer),
    "Survey_URL"  -- Survey回答URL (website),
    "Last_Name_kana"  -- フリガナ(姓) (text),
    "First_Name_kana"  -- フリガナ(名) (text),
    "field"  -- 初回アンケート回答日時 (datetime),
    "field1"  -- 初回アンケート送信済 (boolean),
    "field4"  -- 終了アンケート送信済 (boolean),
    "field5"  -- 終了アンケート回答日時 (datetime),
    "field6"  -- クラス名 (text),
    "field7"  -- 初回アンケートリマインド日時 (datetime),
    "field8"  -- 終了アンケートリマインド日時 (datetime),
    "field9"  -- 終了アンケート種類 (picklist),
    "field10"  -- 初回アンケート種類 (picklist)
FROM "Students"
LIMIT 100;

-- CustomModule15 レコード数確認
SELECT COUNT(*) as total_records
FROM "Students";

-- CustomModule15 ステータス分析
SELECT 
    "ステータス",
    COUNT(*) as 件数
FROM "Students"
GROUP BY "ステータス"
ORDER BY 件数 DESC;

-- CustomModule15 月別登録数
SELECT 
    DATE_FORMAT("作成日時", '%Y-%m') as 登録月,
    COUNT(*) as 新規登録数
FROM "Students"
GROUP BY DATE_FORMAT("作成日時", '%Y-%m')
ORDER BY 登録月 DESC;

-- =====================================
-- CustomModule38 (Classes)
-- フィールド数: 134
-- =====================================

-- 全フィールド基本クエリ
SELECT 
    "Name"  -- クラスコード (autonumber),
    "Owner"  -- クラスの担当者 (ownerlookup),
    "Created_By"  -- 作成者 (ownerlookup),
    "Modified_By"  -- 更新者 (ownerlookup),
    "Created_Time"  -- 作成日時 (datetime),
    "Modified_Time"  -- 更新日時 (datetime),
    "Last_Activity_Time"  -- 最新の操作日時 (datetime),
    "Currency"  -- 通貨 (picklist),
    "Exchange_Rate"  -- 為替レート (double),
    "Tag"  -- タグ (text),
    "Unsubscribed_Mode"  -- 配信停止の方法 (picklist),
    "Unsubscribed_Time"  -- 配信停止の日時 (datetime),
    "Record_Image"  -- クラスの画像 (profileimage),
    "Locked__s"  -- Locked (boolean),
    "field"  -- 総時間／クラス (text),
    "Special_Note"  -- キャンアド履歴 (textarea),
    "field3"  -- 特記事項（社外秘） (textarea),
    "field5"  -- レッスン時間 (text),
    "field8"  -- 人数 (integer),
    "Frequency"  -- レッスン回数 (integer),
    "field10"  -- 出欠レポート選択 (picklist),
    "field12"  -- 出欠報告提出方法 (picklist),
    "field13"  -- 契約キャンセル回数 (picklist),
    "Language"  -- 言語 (picklist),
    "field18"  -- 曜日 (multiselectpicklist),
    "field20"  -- 営業拠点 (picklist),
    "field22"  -- 備考 (textarea),
    "Students_List"  -- 受講生名 (subform),
    "Type"  -- 種類 (picklist),
    "Instructor_Information"  -- 講師情報１ (lookup),
    "Other_Language"  -- その他言語 (text),
    "Class_Name"  -- クラス名 (text),
    "field28"  -- 内容 (picklist),
    "field29"  -- レベル (picklist),
    "field30"  -- 拘束時間 (text),
    "field31"  -- 関連データ (website),
    "URL"  -- レッスンURL (website),
    "Is_Created_Student"  -- 受講生作成済み (boolean),
    "Is_Created_Attendance_Detail"  -- 詳細作成済み (boolean),
    "Arrangement_Name"  -- 手配 (lookup),
    "field2"  -- 商談 (lookup),
    "field4"  -- キャンセル規定 (picklist),
    "field6"  -- レッスン備考 (textarea),
    "field11"  -- CS添付 (fileupload),
    "field14"  -- 提案背景 (textarea),
    "field15"  -- 提案プログラム (textarea),
    "field16"  -- 提案骨子 (textarea),
    "field19"  -- 講師1へ送付済 (boolean),
    "field21"  -- 講師2へ送付済 (boolean),
    "field24"  -- 講師情報２ (lookup),
    "field25"  -- 開講案内済 (boolean),
    "field33"  -- 受講生へ送付済 (boolean),
    "field34"  -- 自由記載欄 (textarea),
    "field35"  -- 開講場所 (picklist),
    "Timerex"  -- Timerex案内済 (boolean),
    "Timerex1"  -- Timerexリンク (website),
    "field36"  -- 面談実施済み (boolean),
    "field37"  -- 面談回数 (integer),
    "field38"  -- 講師用教材手配済 (boolean),
    "field39"  -- 実施タイミング (textarea),
    "field40"  -- メモ (textarea),
    "field41"  -- 初回アンケート送付日 (date),
    "field42"  -- 終了アンケート送付日 (date),
    "field43"  -- 中間アンケート送付日 (date),
    "field44"  -- 評価表１の回収日 (date),
    "field7"  -- 出欠報告 (picklist),
    "field45"  -- 教材手配作業依頼 (multiselectlookup),
    "field46"  -- レッスン設計メモ (textarea),
    "Gemini"  -- Gemini設計メモ (textarea),
    "field47"  -- アセスメント設計メモ (textarea),
    "field48"  -- 面談設計メモ (textarea),
    "field49"  -- アプリ設計メモ (textarea),
    "LinkingModule18"  -- 使用教材 (subform),
    "field1"  -- 講師 (multiselectlookup),
    "field50"  -- 手配作業 (multiselectpicklist),
    "field55"  -- 講師1へ送付 (picklist),
    "field56"  -- 講師2へ送付 (picklist),
    "field23"  -- 受講生へ送付 (picklist),
    "CS"  -- レッスンCS (subform),
    "field26"  -- 評価コメント回収 (picklist),
    "Gemini1"  -- Gemini終了日 (date),
    "Gemini2"  -- Gemini頻度 (textarea),
    "Gemini3"  -- Gemini開始日 (date),
    "Gemini_1"  -- Gemini講師1 (lookup),
    "Gemini_2"  -- Gemini講師2 (lookup),
    "Gemini2_BF"  -- Gemini2 BF (picklist),
    "Gemini1_BF"  -- Gemini1 BF (picklist),
    "Gemini21"  -- Gemini2 ブリーフィングメモ (textarea),
    "Gemini11"  -- Gemini1 ブリーフィングメモ (textarea),
    "field27"  -- ステータス (picklist),
    "field32"  -- キャンアド (lookup),
    "ZohoSign"  -- ZohoSign (lookup),
    "field51"  -- クラス_終了日 (date),
    "w"  -- 学習フォロー1w送信日時 (datetime),
    "JT1"  -- 開講案内送信日時（JT人事用） (datetime),
    "M"  -- 学習フォロー2M送信日時 (datetime),
    "w1"  -- 学習フォロー4w送信日時 (datetime),
    "School_Open_Date"  -- クラス_開講日 (date),
    "field57"  -- レッスン開始日 (date),
    "field58"  -- レッスン終了日 (date),
    "field59"  -- 開講案内送付済み (boolean),
    "field60"  -- アセスメント回数 (integer),
    "field61"  -- 担当教務 (userlookup),
    "field62"  -- クラスタイプ (picklist),
    "field63"  -- 評価表１回収済 (boolean),
    "field65"  -- 評価表１クライテリア (picklist),
    "field66"  -- 評価表２回収済 (boolean),
    "field67"  -- 評価表２の回収日 (date),
    "field69"  -- 評価表３の回収日 (date),
    "field71"  -- 評価表３回収済 (boolean),
    "field73"  -- 評価表２クライテリア (picklist),
    "field74"  -- 評価表３クライテリア (picklist),
    "field75"  -- 評価表３確認済 (boolean),
    "field76"  -- 評価表１確認済 (boolean),
    "field77"  -- 評価表２確認済 (boolean),
    "TORA"  -- TORA固有キー (text),
    "field78"  -- 連絡先 (lookup),
    "Gemini_Prof_ID"  -- Gemini Prof ID (integer),
    "Access"  -- Access入力日 (date),
    "Products_List"  -- 商品リスト (subform),
    "Excel"  -- 開講案内添付用日程表 (website),
    "field79"  -- アンケート特記事項 (text),
    "field80"  -- オンライン入室可能時間 (text),
    "URL1"  -- 教材保存先URL (website),
    "URL2"  -- クラスカリキュラムURL (website),
    "field81"  -- 研修実施住所アクセス方法 (textarea),
    "field82"  -- 研修実施住所待ち合わせ場所・時間 (textarea),
    "field83"  -- 研修実施住所 (text),
    "field84"  -- アテンド有無 (picklist),
    "field85"  -- 終了アンケート送信担当 (userlookup),
    "field86"  -- 初回アンケート送信担当 (userlookup),
    "field87"  -- 中間アンケート送信担当 (userlookup),
    "field88"  -- 教材発送先 (textarea),
    "field89"  -- アテンド担当 (userlookup)
FROM "Classes"
LIMIT 100;

-- CustomModule38 レコード数確認
SELECT COUNT(*) as total_records
FROM "Classes";

-- CustomModule38 クラス分析
SELECT 
    "クラス名",
    "開始日",
    "終了日",
    COUNT(*) as 参加者数
FROM "Classes"
GROUP BY "クラス名", "開始日", "終了日"
ORDER BY 参加者数 DESC;

-- =====================================
-- CustomModule5010 (Subscriptions_Line_Item__s)
-- フィールド数: 25
-- =====================================

-- 全フィールド基本クエリ
SELECT 
    "Name"  -- Subscription Line Item Name (text),
    "Owner"  -- Plan/Addonの担当者 (ownerlookup),
    "Created_By"  -- 作成者 (ownerlookup),
    "Modified_By"  -- 更新者 (ownerlookup),
    "Created_Time"  -- 作成日時 (datetime),
    "Modified_Time"  -- 更新日時 (datetime),
    "Last_Activity_Time"  -- 最新の操作日時 (datetime),
    "Currency"  -- 通貨 (picklist),
    "Exchange_Rate"  -- 為替レート (double),
    "Subscription_Item_ID"  -- サブスクリプションの商品ID (text),
    "Product_Name"  -- 商品名 (text),
    "Description"  -- 詳細情報 (textarea),
    "Code"  -- コード (text),
    "Quantity"  -- 数量 (double),
    "Rate"  -- 割合 (currency),
    "Tax"  -- 税 (currency),
    "Tax_Percentage"  -- 税率（%） (double),
    "Amount"  -- 総額 (currency),
    "Type"  -- 種類 (text),
    "Coupon_Name"  -- クーポン名 (text),
    "Coupon_Code"  -- クーポンコード (text),
    "Coupon_Discount_Amount"  -- クーポンの割引額 (currency),
    "Coupon_Discount_Percentage"  -- クーポンの割引率 (double),
    "Coupon_Redemption_Type"  -- クーポンの利用方法 (text),
    "CustomModule5010_External_Id__s"  -- CustomModule5010 External Id (text)
FROM "Subscriptions_Line_Item__s"
LIMIT 100;

-- CustomModule5010 レコード数確認
SELECT COUNT(*) as total_records
FROM "Subscriptions_Line_Item__s";

-- =====================================
-- CustomModule55 (CustomModule55)
-- フィールド数: 23
-- =====================================

-- 全フィールド基本クエリ
SELECT 
    "Name"  -- Temp Item名 (text),
    "Owner"  -- Temp Itemの担当者 (ownerlookup),
    "Created_Time"  -- 作成日時 (datetime),
    "Modified_Time"  -- 更新日時 (datetime),
    "Last_Activity_Time"  -- 最新の操作日時 (datetime),
    "Currency"  -- Currency (picklist),
    "Exchange_Rate"  -- Exchange Rate (double),
    "Tag"  -- タグ (text),
    "Unsubscribed_Mode"  -- 配信停止の方法 (picklist),
    "Unsubscribed_Time"  -- 配信停止の日時 (datetime),
    "Record_Image"  -- Temp Itemの画像 (profileimage),
    "Quantity"  -- 数量 (integer),
    "Sales_Deals"  -- 商談名 (lookup),
    "Locked__s"  -- Locked (boolean),
    "Price"  -- 単価 (currency),
    "Parent_ID"  -- 商談ID (text),
    "Product_Name"  -- 商品名 (text),
    "Product_ID"  -- 商品ID (text),
    "field"  -- メールアドレス (email),
    "text"  -- 商談名_text (text),
    "field1"  -- 連絡先 (lookup),
    "field2"  -- 単価（税込） (formula),
    "Self_Payment"  -- 自己負担金 (currency)
FROM "CustomModule55"
LIMIT 100;

-- CustomModule55 レコード数確認
SELECT COUNT(*) as total_records
FROM "CustomModule55";

-- =====================================
-- CustomModule58 (abceed1)
-- フィールド数: 29
-- =====================================

-- 全フィールド基本クエリ
SELECT 
    "Name"  -- アプリ名 (text),
    "Owner"  -- abceed（スコア）の担当者 (ownerlookup),
    "Created_By"  -- 作成者 (ownerlookup),
    "Modified_By"  -- 更新者 (ownerlookup),
    "Created_Time"  -- 作成日時 (datetime),
    "Modified_Time"  -- 更新日時 (datetime),
    "Last_Activity_Time"  -- 最新の操作日時 (datetime),
    "Tag"  -- タグ (text),
    "Unsubscribed_Mode"  -- 配信停止の方法 (picklist),
    "Unsubscribed_Time"  -- 配信停止の日時 (datetime),
    "Record_Image"  -- abceed（スコア）の画像 (profileimage),
    "field"  -- 所属 (text),
    "field1"  -- 属性１ (text),
    "field2"  -- 商談 (lookup),
    "field3"  -- 属性２ (text),
    "field5"  -- 属性３ (text),
    "field7"  -- 日付 (date),
    "field8"  -- データ取得日 (date),
    "Total_Score"  -- Total Score (integer),
    "field9"  -- 受講者番号 (email),
    "Listening_Score"  -- Listening Score (integer),
    "field10"  -- ユーザー名 (text),
    "Reading_Score"  -- Reading Score (integer),
    "Locked__s"  -- Locked (boolean),
    "field4"  -- クラス (lookup),
    "field6"  -- 連絡先 (lookup),
    "field11"  -- 通し番号 (text),
    "field12"  -- 合格率 (text),
    "field13"  -- 試験種別 (text)
FROM "abceed1"
LIMIT 100;

-- CustomModule58 レコード数確認
SELECT COUNT(*) as total_records
FROM "abceed1";

-- =====================================
-- CustomModule59 (CustomModule59)
-- フィールド数: 25
-- =====================================

-- 全フィールド基本クエリ
SELECT 
    "Name"  -- 教材名 (text),
    "Owner"  -- 教材の担当者 (ownerlookup),
    "Last_Activity_Time"  -- 最新の操作日時 (datetime),
    "Tag"  -- タグ (text),
    "Unsubscribed_Mode"  -- 配信停止の方法 (picklist),
    "Unsubscribed_Time"  -- 配信停止の日時 (datetime),
    "Record_Image"  -- 教材の画像 (profileimage),
    "field"  -- 使用上の注意 (textarea),
    "field1"  -- 仕入先 (lookup),
    "field3"  -- 関連ツール (picklist),
    "Locked__s"  -- Locked (boolean),
    "field4"  -- 内容 (textarea),
    "field6"  -- 講師用マニュアル / Instructor's Manual (website),
    "field5"  -- コマあたりの時間（分） (text),
    "Contents"  -- Contents (textarea),
    "Comments_for_instructors"  -- Comments for instructors (textarea),
    "field8"  -- 関連ツール（その他の場合） (text),
    "field7"  -- 強化できるスキル (multiselectpicklist),
    "PPT"  -- 講師用PPT (website),
    "JT_NT"  -- JT/NT (picklist),
    "field2"  -- 対象レベル (multiselectpicklist),
    "field9"  -- チャプターコード (text),
    "field10"  -- 教材コード (text),
    "PDF"  -- 受講生用PDF (website),
    "Gemini_ID"  -- Gemini教材ID (text)
FROM "CustomModule59"
LIMIT 100;

-- CustomModule59 レコード数確認
SELECT COUNT(*) as total_records
FROM "CustomModule59";

-- =====================================
-- CustomModule5 (CustomModule5)
-- フィールド数: 137
-- =====================================

-- 全フィールド基本クエリ
SELECT 
    "Name"  -- データ（アプリ）名 (text),
    "Owner"  -- データ（アプリ）の担当者 (ownerlookup),
    "Email"  -- メール (email),
    "Secondary_Email"  -- サブのメールアドレス (email),
    "Created_By"  -- 作成者 (ownerlookup),
    "Modified_By"  -- 更新者 (ownerlookup),
    "Created_Time"  -- 作成日時 (datetime),
    "Modified_Time"  -- 更新日時 (datetime),
    "Last_Activity_Time"  -- 最新の操作日時 (datetime),
    "Currency"  -- 通貨 (picklist),
    "Email_Opt_Out"  -- メール対象外（オプトアウト） (boolean),
    "Layout"  -- レイアウト (bigint),
    "Tag"  -- タグ (text),
    "Unsubscribed_Mode"  -- 配信停止の方法 (picklist),
    "Unsubscribed_Time"  -- 配信停止の日時 (datetime),
    "Record_Image"  -- データ（アプリ）の画像 (profileimage),
    "field"  -- 総学習時間 (サプリ内) (integer),
    "field1"  -- 正解率 (double),
    "field6"  -- オートリスニング総学習時間 (integer),
    "field7"  -- 部署名 (text),
    "field9"  -- 従業員番号_to (text),
    "field10"  -- コース (text),
    "field13"  -- 企業名 (text),
    "field14"  -- 商談 (lookup),
    "field16"  -- 姓 (text),
    "field17"  -- 姓（カナ） (text),
    "field18"  -- 名 (text),
    "field19"  -- 名（カナ） (text),
    "field31"  -- 開始日 (date),
    "field8"  -- 終了日 (date),
    "field11"  -- 従業員番号 (integer),
    "field33"  -- オートリスニング期間指定学習時間) (integer),
    "field35"  -- デイリーレッスン学習時間 (分) (integer),
    "field39"  -- 連絡先 (lookup),
    "field43"  -- 出席 (integer),
    "field46"  -- 法人管理情報-1 (text),
    "field47"  -- 法人管理情報-2 (text),
    "field48"  -- ニックネーム (text),
    "User_ID"  -- User ID (text),
    "field49"  -- プラン (text),
    "field50"  -- 残チケット枚数 (integer),
    "field51"  -- 講師都合キャンセル (integer),
    "field52"  -- 欠席 (integer),
    "iKnow"  -- iKnow学習時間 (text),
    "field53"  -- 生徒氏名 (text),
    "field54"  -- 発話セリフ数（繰返し無） (integer),
    "field55"  -- 総録音回数 (integer),
    "field56"  -- 会員プラン (text),
    "GoLive"  -- GoLiveレッスン受講数 (integer),
    "GoLive1"  -- GoLive受講回数目標 (integer),
    "field57"  -- 視聴動画 (integer),
    "field58"  -- 学習単語（学ぶ/単語クイズ） (integer),
    "field60"  -- 単語学習回数 (同じ単語を含む) (integer),
    "field61"  -- 視聴動画数の目標 (integer),
    "field62"  -- 学習単語数の目標 (integer),
    "field63"  -- 教材総学習時間（任意入力） (integer),
    "field64"  -- 教材期間指定学習時間 (任意入力) (integer),
    "field65"  -- マスターしたレッスン数 (integer),
    "field66"  -- コース内学習時間 (サプリ内) (integer),
    "sb"  -- 氏名_sb (text),
    "sb1"  -- 更新者_sb (text),
    "sb2"  -- 社員番号_sb (integer),
    "field37"  -- オートリスニング学習時間 (分) (integer),
    "sb3"  -- 完了レッスン数_sb (integer),
    "sb4"  -- 受講中のコース_sb (text),
    "PLUS"  -- リスニングPLUS学習時間 (分) (integer),
    "sb5"  -- 組織名_sb (text),
    "sb7"  -- 総学習時間 (分)_sb (integer),
    "sb8"  -- 連絡先_sb (lookup),
    "sb9"  -- 部署名_sb (text),
    "field40"  -- 学習問題数 (integer),
    "field42"  -- 属性1 (text),
    "field44"  -- 受講者番号 (text),
    "field67"  -- 学習時間(秒) (integer),
    "field68"  -- 発話セリフ数の目標 (integer),
    "field69"  -- 平均発話グレード (text),
    "E"  -- E会員コード (text),
    "field71"  -- ディスカッション問題への回答（繰り返し無し） (integer),
    "field32"  -- ディスカッション問題の総回答数 (integer),
    "ID2"  -- アカウントID (text),
    "field59"  -- これまでの学習進捗 (text),
    "field72"  -- 属性2 (text),
    "field73"  -- 日付 (date),
    "field74"  -- 属性3 (text),
    "field75"  -- 教材名 (text),
    "ID3"  -- 生徒ID (text),
    "ID4"  -- タスクID (text),
    "field76"  -- 音読吹き込み日付 (date),
    "field77"  -- タスク日付 (date),
    "ID5"  -- 音読ファイルID (text),
    "field4"  -- 計画時間 (integer),
    "field12"  -- 実績時間 (integer),
    "field78"  -- 姓（日本語） (text),
    "field79"  -- 名（ローマ字） (text),
    "RE"  -- 部署名_RE (text),
    "field80"  -- 名（日本語） (text),
    "field81"  -- プログラム名 (text),
    "field82"  -- 備考 (textarea),
    "field83"  -- コース名 (text),
    "field84"  -- コース開始日 (date),
    "field85"  -- 必須レッスン数 (text),
    "field86"  -- 受講アイテム数 (text),
    "Lesson_Studied"  -- Lessons Studied (text),
    "field87"  -- 合格レッスン数 (text),
    "field88"  -- 推奨レベル (text),
    "field89"  -- 現在のレベル (text),
    "field90"  -- 投稿コメント数 (text),
    "field91"  -- 推奨バンド (text),
    "field92"  -- 平均レッスンスコア (text),
    "field93"  -- 必須コメント数 (text),
    "field94"  -- プログラム登録日時 (datetime),
    "field95"  -- 進捗率 (text),
    "field96"  -- コース終了日 (date),
    "field97"  -- 最終アクセス日時 (datetime),
    "field98"  -- ステータス (text),
    "field99"  -- 学習時間（秒） (datetime),
    "field100"  -- 初回アクセス日時 (datetime),
    "field101"  -- 合格アイテム数 (text),
    "field102"  -- サインイン回数 (integer),
    "field103"  -- コース修了日 (date),
    "field104"  -- レポート種別 (text),
    "Average_Test_Score"  -- Average Test Score (text),
    "field105"  -- 姓（ローマ字） (text),
    "ID1"  -- ユーザID (text),
    "field2"  -- コメント (textarea),
    "field3"  -- レッスンスコア (text),
    "field5"  -- テストスコア (text),
    "field15"  -- テスト名 (text),
    "Test_Level"  -- Test Level (text),
    "field41"  -- 平均テスト時間（秒） (integer),
    "Test_Band"  -- Test Band (text),
    "field106"  -- スキル名 (text),
    "field107"  -- 学習日 (datetime),
    "field108"  -- レッスンレベル (text),
    "field109"  -- レッスン名 (text),
    "field110"  -- 合格状況 (text),
    "Locked__s"  -- Locked (boolean)
FROM "CustomModule5"
LIMIT 100;

-- CustomModule5 レコード数確認
SELECT COUNT(*) as total_records
FROM "CustomModule5";

-- =====================================
-- CustomModule75 (CustomModule75)
-- フィールド数: 86
-- =====================================

-- 全フィールド基本クエリ
SELECT 
    "Name"  -- 学習実績名 (text),
    "Owner"  -- 学習実績の担当者 (ownerlookup),
    "Email"  -- メール (email),
    "Created_By"  -- 作成者 (ownerlookup),
    "Modified_By"  -- 更新者 (ownerlookup),
    "Created_Time"  -- 作成日時 (datetime),
    "Modified_Time"  -- 更新日時 (datetime),
    "Last_Activity_Time"  -- 最新の操作日時 (datetime),
    "Currency"  -- 通貨 (picklist),
    "Exchange_Rate"  -- 為替レート (double),
    "Layout"  -- レイアウト (bigint),
    "Tag"  -- タグ (text),
    "Unsubscribed_Mode"  -- 配信停止の方法 (picklist),
    "Unsubscribed_Time"  -- 配信停止の日時 (datetime),
    "Record_Image"  -- 学習実績の画像 (profileimage),
    "Contact"  -- 連絡先 (lookup),
    "Locked__s"  -- Locked (boolean),
    "End_Date"  -- 集計終了日 (date),
    "Condition"  -- 修了要件1 (lookup),
    "Start_Date"  -- 集計開始日 (date),
    "Result"  -- 判定 (picklist),
    "field9"  -- 要件タイプ1-① (text),
    "Class"  -- クラス (lookup),
    "field2"  -- 備考 (textarea),
    "field3"  -- 取引先 (lookup),
    "field4"  -- 商品名 (lookup),
    "field5"  -- 商談名 (lookup),
    "field1"  -- 実績値 (double),
    "field6"  -- 要件1-① (double),
    "field7"  -- メール (連絡先) (email),
    "Overall"  -- Overall (integer),
    "Speaking"  -- Speakingスコア (integer),
    "field8"  -- 受験状況 (multiselectpicklist),
    "field10"  -- 総合得点 (integer),
    "Reading"  -- Readingスコア (integer),
    "Total"  -- Totalスコア (integer),
    "Listening"  -- Listeningスコア (integer),
    "field11"  -- 修了要件2 (lookup),
    "field12"  -- 要件タイプ2-① (text),
    "field13"  -- 要件種類2 (text),
    "field14"  -- 要件種類1 (text),
    "field15"  -- 社内区分 (text),
    "field16"  -- 要件2-① (double),
    "field17"  -- 要件達成条件2 (picklist),
    "field18"  -- 要件達成条件1 (picklist),
    "field19"  -- 判定条件 (picklist),
    "field20"  -- 要件1-② (double),
    "field21"  -- 要件タイプ1-② (text),
    "field22"  -- 要件2-② (double),
    "field23"  -- 要件タイプ2-② (text),
    "field24"  -- 目標 (double),
    "field25"  -- 学習実績種類 (picklist),
    "field26"  -- レポート対象月 (picklist),
    "field27"  -- 修了率 (text),
    "field"  -- 備考2 (textarea),
    "field28"  -- 学習開始日 (date),
    "field29"  -- 学習終了日 (date),
    "field30"  -- 実績値2 (double),
    "CEFR_Level"  -- CEFR Level (text),
    "Overall_Score"  -- Overall Score (integer),
    "field31"  -- 受講生確認ステータス (picklist),
    "field32"  -- 備考（集計用） (text),
    "field33"  -- ステータス（集計用） (multiselectpicklist),
    "field34"  -- 詳細 (修了要件2) (textarea),
    "field35"  -- 詳細 (修了要件1) (textarea),
    "Year"  -- 対象年 (integer),
    "Month"  -- 対象月 (integer),
    "field36"  -- 目標2 (double),
    "field37"  -- 修了率2 (text),
    "field38"  -- 修了要件母数① (double),
    "field39"  -- 修了要件母数② (double),
    "field40"  -- 関連キャンペーン (lookup),
    "Status"  -- Status (text),
    "Speaking1"  -- Speaking (integer),
    "Overall_CEFR"  -- Overall CEFR (text),
    "Listening1"  -- Listening (integer),
    "Manner_of_Speaking"  -- Manner of Speaking (integer),
    "fieldRPA"  -- RPA実績値 (double),
    "RPA_2"  -- RPA実績値2 (double),
    "field41"  -- 送信日時 (datetime),
    "field42"  -- 通知メールテンプレート (picklist),
    "RPA_3"  -- RPA実績値3 (double),
    "RPA_4"  -- RPA実績値4 (double),
    "RPA"  -- RPA実績値(備考) (text),
    "field43"  -- 受験日 (date),
    "field44"  -- 手配 (lookup)
FROM "CustomModule75"
LIMIT 100;

-- CustomModule75 レコード数確認
SELECT COUNT(*) as total_records
FROM "CustomModule75";

-- =====================================
-- CustomModule5005 (CustomModule5005)
-- フィールド数: 26
-- =====================================

-- 全フィールド基本クエリ
SELECT 
    "Name"  -- 商品番号 (text),
    "Owner"  -- 商品の担当者 (ownerlookup),
    "Created_By"  -- 作成者 (ownerlookup),
    "Modified_By"  -- 更新者 (ownerlookup),
    "Created_Time"  -- 作成日時 (datetime),
    "Modified_Time"  -- 更新日時 (datetime),
    "Last_Activity_Time"  -- 最新の操作日時 (datetime),
    "Currency"  -- 通貨 (picklist),
    "Exchange_Rate"  -- 為替レート (double),
    "Item_Line_ID"  -- Item Line ID (bigint),
    "Item_Description"  -- Item Description (textarea),
    "Product_ID"  -- Product ID (lookup),
    "Quantity"  -- 数量 (double),
    "Rate"  -- 割合 (currency),
    "Unit"  -- Unit (text),
    "Discount_Amount"  -- 割引額 (currency),
    "Discount_Percentage"  -- 割引率 (double),
    "Tax_Amount"  -- 税額 (currency),
    "Tax_Percentage"  -- 税率（%） (double),
    "Tax_Name"  -- Tax Name (text),
    "Total"  -- 合計 (currency),
    "Invoice_ID"  -- Invoice ID (lookup),
    "Estimate_ID"  -- Estimate ID (lookup),
    "Sales_Order_ID"  -- Sales Order ID (lookup),
    "Purchase_Order_ID"  -- Purchase Order ID (lookup),
    "CustomModule5005_External_Id__s"  -- CustomModule5005 External Id (text)
FROM "CustomModule5005"
LIMIT 100;

-- CustomModule5005 レコード数確認
SELECT COUNT(*) as total_records
FROM "CustomModule5005";

-- =====================================
-- CustomModule5001 (CustomModule5001)
-- フィールド数: 39
-- =====================================

-- 全フィールド基本クエリ
SELECT 
    "Name"  -- 請求書番号 (text),
    "Owner"  -- 請求書の担当者 (ownerlookup),
    "Created_By"  -- 作成者 (ownerlookup),
    "Modified_By"  -- 更新者 (ownerlookup),
    "Created_Time"  -- 作成日時 (datetime),
    "Modified_Time"  -- 更新日時 (datetime),
    "Last_Activity_Time"  -- 最新の操作日時 (datetime),
    "Currency"  -- 通貨 (picklist),
    "Exchange_Rate"  -- 為替レート (double),
    "Account_Name"  -- 取引先名 (lookup),
    "Contact_Name"  -- 連絡先名 (lookup),
    "Potential_Name"  -- 商談名 (lookup),
    "Invoice_ID"  -- Invoice ID (text),
    "Order_Number"  -- 注文番号 (text),
    "Invoice_Date"  -- 請求書発行日 (date),
    "Due_Date"  -- 期限 (date),
    "Adjustments"  -- 調整 (currency),
    "Discount_Amount"  -- 割引額 (currency),
    "Discount_Percentage"  -- 割引率 (double),
    "Balance"  -- 残額 (currency),
    "Grand_Total"  -- 総計 (currency),
    "Terms_and_Conditions"  -- 取引条件 (textarea),
    "Shipping_Charges"  -- 配送料 (currency),
    "Sales_Person"  -- 営業担当者 (text),
    "Status"  -- ステータス (picklist),
    "ExchangeRate"  -- 為替レート（請求書） (double),
    "Sub_Total"  -- 小計 (currency),
    "Client_Viewed"  -- クライアントが表示済み (boolean),
    "field"  -- 件名 (text),
    "field1"  -- 支払いリンク (website),
    "field2"  -- 部署名 (text),
    "field3"  -- 請求先種別 (picklist),
    "field4"  -- 所属会社 (text),
    "field7"  -- (領)受講期間 (text),
    "field6"  -- (領)支払日 (date),
    "field5"  -- (領)支払方法 (picklist),
    "field8"  -- (領)領収書発行日 (date),
    "CustomModule5001_External_Id__s"  -- CustomModule5001 External Id (text),
    "field9"  -- 支払い種別 (picklist)
FROM "CustomModule5001"
LIMIT 100;

-- CustomModule5001 レコード数確認
SELECT COUNT(*) as total_records
FROM "CustomModule5001";

-- =====================================
-- CustomModule5002 (CustomModule5002)
-- フィールド数: 29
-- =====================================

-- 全フィールド基本クエリ
SELECT 
    "Name"  -- 見積書番号 (text),
    "Owner"  -- 見積書の担当者 (ownerlookup),
    "Created_By"  -- 作成者 (ownerlookup),
    "Modified_By"  -- 更新者 (ownerlookup),
    "Created_Time"  -- 作成日時 (datetime),
    "Modified_Time"  -- 更新日時 (datetime),
    "Last_Activity_Time"  -- 最新の操作日時 (datetime),
    "Currency"  -- 通貨 (picklist),
    "Exchange_Rate"  -- 為替レート (double),
    "Account_Name"  -- 取引先名 (lookup),
    "Contact_Name"  -- 連絡先名 (lookup),
    "Potential_Name"  -- 商談名 (lookup),
    "Estimate_ID"  -- Estimate ID (text),
    "Reference_Number"  -- 参照番号 (text),
    "Estimate_Date"  -- 見積日 (date),
    "Expiry_Date"  -- 有効期限 (date),
    "Adjustments"  -- 調整 (currency),
    "Discount_Amount"  -- 割引額 (currency),
    "Discount_Percentage"  -- 割引率 (double),
    "Grand_Total"  -- 総計 (currency),
    "Terms_and_Conditions"  -- 取引条件 (textarea),
    "Shipping_Charges"  -- 配送料 (currency),
    "Sales_Person"  -- 営業担当者 (text),
    "Status"  -- ステータス (picklist),
    "ExchangeRate"  -- 為替レート（見積書） (double),
    "Sub_Total"  -- 小計 (currency),
    "Client_Viewed"  -- クライアントが表示済み (boolean),
    "field"  -- 件名 (text),
    "CustomModule5002_External_Id__s"  -- CustomModule5002 External Id (text)
FROM "CustomModule5002"
LIMIT 100;

-- CustomModule5002 レコード数確認
SELECT COUNT(*) as total_records
FROM "CustomModule5002";

-- =====================================
-- CustomModule5004 (CustomModule5004)
-- フィールド数: 28
-- =====================================

-- 全フィールド基本クエリ
SELECT 
    "Name"  -- 受注書番号 (text),
    "Owner"  -- 受注書の担当者 (ownerlookup),
    "Created_By"  -- 作成者 (ownerlookup),
    "Modified_By"  -- 更新者 (ownerlookup),
    "Created_Time"  -- 作成日時 (datetime),
    "Modified_Time"  -- 更新日時 (datetime),
    "Last_Activity_Time"  -- 最新の操作日時 (datetime),
    "Currency"  -- 通貨 (picklist),
    "Exchange_Rate"  -- 為替レート (double),
    "Account_Name"  -- 取引先名 (lookup),
    "Contact_Name"  -- 連絡先名 (lookup),
    "Potential_Name"  -- 商談名 (lookup),
    "Sales_Order_ID"  -- Sales Order ID (text),
    "Reference_Number"  -- 参照番号 (text),
    "Sales_Order_Date"  -- 受注日 (date),
    "Shipping_Date"  -- 出荷日 (date),
    "Adjustments"  -- 調整 (currency),
    "Discount_Amount"  -- 割引額 (currency),
    "Discount_Percentage"  -- 割引率 (double),
    "Grand_Total"  -- 総計 (currency),
    "Terms_And_Conditions"  -- 取引条件 (textarea),
    "Shipping_Charges"  -- 配送料 (currency),
    "Sales_Person"  -- 営業担当者 (text),
    "Status"  -- ステータス (picklist),
    "ExchangeRate"  -- 為替レート（発注書） (double),
    "Sub_Total"  -- 小計 (currency),
    "field"  -- 件名 (text),
    "CustomModule5004_External_Id__s"  -- CustomModule5004 External Id (text)
FROM "CustomModule5004"
LIMIT 100;

-- CustomModule5004 レコード数確認
SELECT COUNT(*) as total_records
FROM "CustomModule5004";

-- =====================================
-- CustomModule5003 (CustomModule5003)
-- フィールド数: 24
-- =====================================

-- 全フィールド基本クエリ
SELECT 
    "Name"  -- 発注書番号 (text),
    "Owner"  -- 発注書の担当者 (ownerlookup),
    "Created_By"  -- 作成者 (ownerlookup),
    "Modified_By"  -- 更新者 (ownerlookup),
    "Created_Time"  -- 作成日時 (datetime),
    "Modified_Time"  -- 更新日時 (datetime),
    "Last_Activity_Time"  -- 最新の操作日時 (datetime),
    "Currency"  -- 通貨 (picklist),
    "Exchange_Rate"  -- 為替レート (double),
    "Vendor_Name"  -- 仕入先名 (lookup),
    "Purchase_Order_ID"  -- Purchase Order ID (text),
    "Reference_Number"  -- 参照番号 (text),
    "Purchase_Order_Date"  -- 発注日 (date),
    "Delivery_Date"  -- 納品日 (date),
    "Grand_Total"  -- 総計 (currency),
    "Terms_and_Conditions"  -- 取引条件 (textarea),
    "Sales_Person"  -- 営業担当者 (text),
    "Status"  -- ステータス (picklist),
    "ExchangeRate"  -- 為替レート（受注書） (double),
    "Sub_Total"  -- 小計 (currency),
    "field"  -- 件名 (text),
    "field2"  -- 請求書番号 (text),
    "field1"  -- 入金予定日 (date),
    "CustomModule5003_External_Id__s"  -- CustomModule5003 External Id (text)
FROM "CustomModule5003"
LIMIT 100;

-- CustomModule5003 レコード数確認
SELECT COUNT(*) as total_records
FROM "CustomModule5003";

-- =====================================
-- CustomModule5006 (CustomModule5006)
-- フィールド数: 57
-- =====================================

-- 全フィールド基本クエリ
SELECT 
    "Name"  -- Expense Name (text),
    "Owner"  -- Expense Owner (ownerlookup),
    "Created_By"  -- 作成者 (ownerlookup),
    "Modified_By"  -- 更新者 (ownerlookup),
    "Created_Time"  -- 作成日時 (datetime),
    "Modified_Time"  -- 更新日時 (datetime),
    "Last_Activity_Time"  -- 最新の操作日時 (datetime),
    "Currency"  -- 通貨 (picklist),
    "Exchange_Rate"  -- 為替レート (double),
    "Account_Name"  -- 取引先名 (lookup),
    "Contact_Name"  -- 連絡先名 (lookup),
    "Potential_Name"  -- 商談名 (lookup),
    "Expense_ID"  -- Expense ID (text),
    "Expense_Date"  -- 経費の発生日 (date),
    "GL_Account_Name"  -- GL Account Name (text),
    "Description"  -- 詳細情報 (textarea),
    "Reference_Number"  -- 参照番号 (text),
    "Location"  -- 場所 (text),
    "Expense_Status"  -- 経費のステータス (picklist),
    "Currency5006"  -- 通貨 (text),
    "Expense_Grand_Total"  -- Expense Grand Total (currency),
    "Sub_Total"  -- 小計 (currency),
    "Exchange_Rate5006"  -- 為替レート (currency),
    "Distance"  -- Expense_Distance (currency),
    "Number_of_Days"  -- Number of Days (currency),
    "Is_Inclusive_Tax"  -- Is Inclusive Tax (boolean),
    "Is_Billable"  -- Is Billable (boolean),
    "Is_Reimbursable"  -- Is Reimbursable (boolean),
    "Merchant_Name"  -- Merchant Name (text),
    "Payment_Mode_Name"  -- Payment Mode Name (text),
    "Expense_Report_ID"  -- Expense Report ID (text),
    "Attendees"  -- Attendees (text),
    "Expense_Type"  -- Expense Type (picklist),
    "Department_Name"  -- Department Name (text),
    "Department_Code"  -- Department Code (text),
    "Surcharge_Amount"  -- Surcharge Amount (currency),
    "Surcharge_Percentage"  -- Surcharge Percentage (currency),
    "Trip_Number"  -- Trip Number (text),
    "Trip_Status"  -- Trip Status (picklist),
    "Mileage_Units"  -- Mileage Units (text),
    "Mileage_Rate"  -- Mileage Rate (currency),
    "Vehical_Type"  -- Vehical Type (picklist),
    "Fuel_Type"  -- Fuel Type (picklist),
    "Engine_Capacity_Range"  -- Engine Capacity Range (picklist),
    "Fuel_Rate"  -- Fuel Rate (currency),
    "Fuel_Element"  -- Fuel Element (currency),
    "Is_Personal"  -- Is Personal (boolean),
    "Policy_Name"  -- Policy Name (text),
    "Paid_Through_Account_Name"  -- Paid Through Account Name (text),
    "Custom_Policy_Violation_Count"  -- Custom Policy Violation Count (text),
    "Receipt_Required_Flag"  -- Receipt Required Flag (text),
    "Expense_Max_Amount_Flag"  -- Expense Max Amount Flag (text),
    "Expense_Description_Flag"  -- Expense Description Flag (text),
    "User_Name"  -- ユーザー名 (text),
    "From"  -- 詳細 (text),
    "To"  -- To (text),
    "CustomModule5006_External_Id__s"  -- CustomModule5006 External Id (text)
FROM "CustomModule5006"
LIMIT 100;

-- CustomModule5006 レコード数確認
SELECT COUNT(*) as total_records
FROM "CustomModule5006";

-- =====================================
-- CustomModule5007 (CustomModule5007)
-- フィールド数: 42
-- =====================================

-- 全フィールド基本クエリ
SELECT 
    "Name"  -- Expense Report Name (text),
    "Owner"  -- Expense Report Owner (ownerlookup),
    "Created_By"  -- 作成者 (ownerlookup),
    "Modified_By"  -- 更新者 (ownerlookup),
    "Created_Time"  -- 作成日時 (datetime),
    "Modified_Time"  -- 更新日時 (datetime),
    "Last_Activity_Time"  -- 最新の操作日時 (datetime),
    "Currency"  -- 通貨 (picklist),
    "Exchange_Rate"  -- 為替レート (double),
    "Account_Name"  -- 取引先名 (lookup),
    "Contact_Name"  -- 連絡先名 (lookup),
    "Potential_Name"  -- 商談名 (lookup),
    "Expense_Report_ID"  -- Expense Report ID (text),
    "Expense_Report_Title"  -- Expense Report Title (text),
    "Business_Purpose"  -- Business Purpose (text),
    "Start_Date"  -- 開始日 (date),
    "End_Date"  -- 終了日 (date),
    "Project_Name"  -- Project Name (text),
    "Submitted_to"  -- Submitted to (text),
    "Total_Expense_Amount"  -- Total Expense Amount (currency),
    "Submitted_By"  -- Submitted By (text),
    "Submited_Date"  -- Submited Date (date),
    "End_Date5007"  -- 終了日 (date),
    "Approver_Name"  -- Approver Name (text),
    "Reimbursable_Total"  -- Reimbursable Total (currency),
    "Is_Pushed_to_QB"  -- Is Pushed to QB (boolean),
    "Non-reimbursable_Amount"  -- Non-reimbursable Amount (currency),
    "Advance_Amount"  -- Advance Amount (currency),
    "Expense_Report_Number"  -- Expense Report Number (text),
    "Currency5007"  -- 通貨 (text),
    "Expense_Report_Status"  -- Expense Report Status (picklist),
    "Approved_Date"  -- Approved Date (date),
    "Trip_Number"  -- Trip Number (text),
    "Trip_Status"  -- Trip Status (text),
    "Policy_Name"  -- Policy Name (text),
    "Custom_Policy_Violation_Count"  -- Custom Policy Violation Count (text),
    "User_Name"  -- ユーザー名 (text),
    "Receipt_Required_Flag_Count"  -- Receipt Required Flag Count (text),
    "Expense_Max_Amount_Flag_Count"  -- Expense Max Amount Flag Count (text),
    "Expense_Description_Flag_Count"  -- Expense Description Flag Count (text),
    "Uncategorized_Expense_Flag_Count"  -- Uncategorized Expense Flag Count (text),
    "CustomModule5007_External_Id__s"  -- CustomModule5007 External Id (text)
FROM "CustomModule5007"
LIMIT 100;

-- CustomModule5007 レコード数確認
SELECT COUNT(*) as total_records
FROM "CustomModule5007";

-- =====================================
-- CustomModule5008 (CustomModule5008)
-- フィールド数: 20
-- =====================================

-- 全フィールド基本クエリ
SELECT 
    "Name"  -- CustomModule5008 Name (text),
    "Owner"  -- Expense Itemの担当者 (ownerlookup),
    "Created_By"  -- 作成者 (ownerlookup),
    "Modified_By"  -- 更新者 (ownerlookup),
    "Created_Time"  -- 作成日時 (datetime),
    "Modified_Time"  -- 更新日時 (datetime),
    "Last_Activity_Time"  -- 最新の操作日時 (datetime),
    "Currency"  -- 通貨 (picklist),
    "Exchange_Rate"  -- 為替レート (double),
    "Category_Name"  -- Category Name (text),
    "Offset_Account_GLID"  -- Offset Account GLID (text),
    "Expense_ID"  -- Expense ID (lookup),
    "Expense_Item_ID"  -- Expense Item ID (text),
    "Description"  -- 詳細情報 (textarea),
    "Expense_Amount"  -- 経費の金額 (currency),
    "Project_Name"  -- Project Name (text),
    "Tax_Name"  -- Tax Name (text),
    "Tax_Percentage"  -- 税率（%） (currency),
    "Tax_Amount"  -- 税額 (currency),
    "CustomModule5008_External_Id__s"  -- CustomModule5008 External Id (text)
FROM "CustomModule5008"
LIMIT 100;

-- CustomModule5008 レコード数確認
SELECT COUNT(*) as total_records
FROM "CustomModule5008";

-- =====================================
-- CustomModule110 (CustomModule110)
-- フィールド数: 88
-- =====================================

-- 全フィールド基本クエリ
SELECT 
    "Name"  -- 超速中国語名 (text),
    "Owner"  -- 超速中国語の担当者 (ownerlookup),
    "Email"  -- メール (email),
    "Created_By"  -- 作成者 (ownerlookup),
    "Modified_By"  -- 更新者 (ownerlookup),
    "Created_Time"  -- 作成日時 (datetime),
    "Modified_Time"  -- 更新日時 (datetime),
    "Last_Activity_Time"  -- 最新の操作日時 (datetime),
    "Currency"  -- 通貨 (picklist),
    "Tag"  -- タグ (text),
    "Unsubscribed_Mode"  -- 配信停止の方法 (picklist),
    "Unsubscribed_Time"  -- 配信停止の日時 (datetime),
    "Record_Image"  -- 超速中国語の画像 (profileimage),
    "Part2"  -- 30課 Part2 (text),
    "Part21"  -- 35課 Part2 (text),
    "Part1"  -- 31課 Part1 (text),
    "Part11"  -- 36課 Part1 (text),
    "field"  -- 1課 (text),
    "Part22"  -- 31課 Part2 (text),
    "field1"  -- 受講コース (text),
    "Part23"  -- 36課 Part2 (text),
    "field2"  -- 2課 (text),
    "Part12"  -- 32課 Part1 (text),
    "field3"  -- 11課 (text),
    "Part13"  -- 37課 Part1 (text),
    "field4"  -- 3課 (text),
    "Part24"  -- 32課 Part2 (text),
    "field5"  -- 12課 (text),
    "Part25"  -- 37課 Part2 (text),
    "field6"  -- 4課 (text),
    "field7"  -- 13課 (text),
    "field8"  -- 5課 (text),
    "field9"  -- 14課 (text),
    "Part14"  -- 38課 Part1 (text),
    "Part26"  -- 38課 Part2 (text),
    "Part15"  -- 33課 Part1 (text),
    "field10"  -- 15課 (text),
    "Part16"  -- 39課 Part1 (text),
    "Part27"  -- 33課 Part2 (text),
    "field11"  -- 16課 (text),
    "Part28"  -- 39課 Part2 (text),
    "field12"  -- 6課 (text),
    "Part17"  -- 34課 Part1 (text),
    "field13"  -- 17課 (text),
    "Part18"  -- 40課 Part1 (text),
    "field14"  -- 7課 (text),
    "Part29"  -- 34課 Part2 (text),
    "field15"  -- 18課 (text),
    "field16"  -- 8課 (text),
    "Part19"  -- 35課 Part1 (text),
    "field17"  -- 19課 (text),
    "field18"  -- 9課 (text),
    "field19"  -- オンラインレッスン(通常レッスン) 受講済回数 (integer),
    "field20"  -- 10課 (text),
    "field21"  -- オンラインレッスン(通常レッスン) 残チケット数 (integer),
    "id1"  -- 超速中国語id (text),
    "field22"  -- オンラインレッスン(通常レッスン) 無効チケット数 (integer),
    "field23"  -- 氏名 (text),
    "field24"  -- オンラインレッスン(習得度チェック) 受講済回数 (integer),
    "Part210"  -- 40課 Part2 (text),
    "Part110"  -- 21課 Part1 (text),
    "field25"  -- 20課 (text),
    "Part211"  -- 21課 Part2 (text),
    "Part212"  -- 25課 Part2 (text),
    "Part111"  -- 22課 Part1 (text),
    "Part112"  -- 26課 Part1 (text),
    "Part213"  -- 22課 Part2 (text),
    "Part214"  -- 26課 Part2 (text),
    "Part113"  -- 23課 Part1 (text),
    "Part114"  -- 27課 Part1 (text),
    "Part215"  -- 27課 Part2 (text),
    "Part115"  -- 28課 Part1 (text),
    "Part216"  -- 23課 Part2 (text),
    "field26"  -- 有効期限 (date),
    "Part217"  -- 28課 Part2 (text),
    "Part116"  -- 24課 Part1 (text),
    "field27"  -- 受講開始日 (date),
    "Part117"  -- 29課 Part1 (text),
    "field28"  -- オンラインレッスン(習得度チェック) 残チケット数 (integer),
    "Part218"  -- 24課 Part2 (text),
    "field29"  -- 初期登録 (text),
    "Part219"  -- 29課 Part2 (text),
    "field30"  -- オンラインレッスン(習得度チェック) 無効チケット数 (integer),
    "Part118"  -- 25課 Part1 (text),
    "field31"  -- ガイダンス受講 (text),
    "Part119"  -- 30課 Part1 (text),
    "OL"  -- OL有無 (text),
    "Locked__s"  -- Locked (boolean)
FROM "CustomModule110"
LIMIT 100;

-- CustomModule110 レコード数確認
SELECT COUNT(*) as total_records
FROM "CustomModule110";


-- =====================================
-- 統合分析クエリ例
-- =====================================

-- 注意: 以下のクエリは実際のテーブル名・フィールド名に合わせて調整が必要です

-- 受講生別総合レポート例
/*
SELECT 
    s."受講生名",
    s."コース",
    s."登録日",
    COUNT(DISTINCT c."クラスID") as 参加クラス数,
    COUNT(a."出席ID") as 出席記録数,
    SUM(CASE WHEN a."出席ステータス" = '出席' THEN 1 ELSE 0 END) as 出席回数,
    ROUND(SUM(CASE WHEN a."出席ステータス" = '出席' THEN 1 ELSE 0 END) * 100.0 / COUNT(a."出席ID"), 2) as 出席率
FROM "Students" s
LEFT JOIN "Classes" c ON s."ID" = c."受講生ID"
LEFT JOIN "Attendance_Detail" a ON s."ID" = a."受講生ID"
GROUP BY s."受講生名", s."コース", s."登録日"
ORDER BY 出席率 DESC;
*/

-- コース別実績サマリー例
/*
SELECT 
    "コース名",
    COUNT(DISTINCT "受講生ID") as 受講生数,
    COUNT("クラスID") as 開催クラス数,
    AVG("出席率") as 平均出席率,
    SUM("修了者数") as 修了者数
FROM (
    SELECT 
        s."コース",
        s."ID" as "受講生ID",
        c."ID" as "クラスID",
        AVG(CASE WHEN a."出席ステータス" = '出席' THEN 1.0 ELSE 0.0 END) as "出席率",
        MAX(CASE WHEN s."ステータス" = '修了' THEN 1 ELSE 0 END) as "修了者数"
    FROM "Students" s
    LEFT JOIN "Classes" c ON s."コース" = c."コース名"
    LEFT JOIN "Attendance_Detail" a ON s."ID" = a."受講生ID"
    GROUP BY s."コース", s."ID", c."ID"
) subquery
GROUP BY "コース名"
ORDER BY 受講生数 DESC;
*/
