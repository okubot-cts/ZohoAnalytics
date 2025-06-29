-- Zoho Analytics SQL クエリ集
-- 生成日時: 2025-06-29T12:45:36.362192
-- 基づくスキーマ: Zoho CRM
-- 総モジュール数: 118

-- =====================================
-- 基本クエリ (主要モジュール)
-- =====================================

-- Deals の基本クエリ
SELECT 
    "Owner",\n    "Amount",\n    "Deal_Name",\n    "Closing_Date",\n    "Account_Name",\n    "Stage",\n    "Type",\n    "Probability",\n    "Next_Step",\n    "Lead_Source"
FROM "Deals"
LIMIT 100;

-- Contacts の基本クエリ
SELECT 
    "Owner",\n    "Lead_Source",\n    "First_Name",\n    "Last_Name",\n    "Account_Name",\n    "Vendor_Name",\n    "Email",\n    "Title",\n    "Department",\n    "Phone"
FROM "Contacts"
LIMIT 100;

-- Accounts の基本クエリ
SELECT 
    "Owner",\n    "Rating",\n    "Account_Name",\n    "Phone",\n    "Account_Site",\n    "Fax",\n    "Parent_Account",\n    "Website",\n    "Account_Number",\n    "Ticker_Symbol"
FROM "Accounts"
LIMIT 100;

-- Leads の基本クエリ
SELECT 
    "Owner",\n    "Company",\n    "First_Name",\n    "Last_Name",\n    "Designation",\n    "Email",\n    "Phone",\n    "Fax",\n    "Mobile",\n    "Website"
FROM "Leads"
LIMIT 100;

-- Tasks の基本クエリ
SELECT 
    "Owner",\n    "Subject",\n    "Due_Date",\n    "Who_Id",\n    "What_Id",\n    "Status",\n    "Priority",\n    "Created_By",\n    "Modified_By",\n    "Created_Time"
FROM "Tasks"
LIMIT 100;

-- Products の基本クエリ
SELECT 
    "Owner",\n    "Product_Name",\n    "Product_Code",\n    "Vendor_Name",\n    "Product_Active",\n    "Manufacturer",\n    "Product_Category",\n    "Sales_Start_Date",\n    "Sales_End_Date",\n    "Support_Start_Date"
FROM "Products"
LIMIT 100;

-- =====================================
-- 分析クエリ
-- =====================================

-- 商談ステージ別集計
SELECT 
    "Stage",
    COUNT(*) as deal_count,
    SUM(CAST("Amount" as DECIMAL)) as total_amount,
    AVG(CAST("Amount" as DECIMAL)) as avg_amount
FROM "Deals"
WHERE "Amount" IS NOT NULL
GROUP BY "Stage"
ORDER BY total_amount DESC;

-- 商談月次トレンド
SELECT 
    DATE_FORMAT("Created_Time", '%Y-%m') as month,
    COUNT(*) as new_deals,
    SUM(CASE WHEN "Stage" = 'Closed Won' THEN CAST("Amount" as DECIMAL) ELSE 0 END) as won_amount
FROM "Deals"
GROUP BY DATE_FORMAT("Created_Time", '%Y-%m')
ORDER BY month DESC;

-- 取引先別連絡先数
SELECT 
    "Account_Name",
    COUNT(*) as contact_count
FROM "Contacts"
WHERE "Account_Name" IS NOT NULL
GROUP BY "Account_Name"
ORDER BY contact_count DESC
LIMIT 20;

-- タスク完了率
SELECT 
    "Status",
    COUNT(*) as task_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM "Tasks"), 2) as percentage
FROM "Tasks"
GROUP BY "Status"
ORDER BY task_count DESC;

-- =====================================
-- JOIN例
-- =====================================

-- Deals と関連テーブルの結合クエリ
SELECT 
    main."Owner" as main_Owner,\n    main."Amount" as main_Amount,\n    main."Deal_Name" as main_Deal_Name,\n    main."Closing_Date" as main_Closing_Date,\n    main."Account_Name" as main_Account_Name
    contacts."Owner" as contacts_Owner
    contacts."Lead_Source" as contacts_Lead_Source
    contacts."First_Name" as contacts_First_Name
    accounts."Owner" as accounts_Owner
    accounts."Rating" as accounts_Rating
    accounts."Account_Name" as accounts_Account_Name
FROM "Deals" main
LEFT JOIN "Contacts" contacts 
    ON main.id = contacts.deals_id
LEFT JOIN "Accounts" accounts 
    ON main.id = accounts.deals_id
LIMIT 100;



-- =====================================
-- 学習関連テーブル (追加)
-- =====================================

-- CustomModule15 の基本クエリ
SELECT 
    "Name",\n    "Owner",\n    "Email",\n    "Created_By",\n    "Modified_By",\n    "Created_Time",\n    "Modified_Time",\n    "Last_Activity_Time",\n    "Currency",\n    "Exchange_Rate"
FROM "Students"
LIMIT 100;

-- CustomModule15 分析クエリ
-- 受講生ステータス別集計（例）
SELECT 
    "ステータス" as status,
    COUNT(*) as student_count,
    "コース名" as course_name
FROM "Students"
GROUP BY "ステータス", "コース名"
ORDER BY student_count DESC;

-- LinkingModule12 の基本クエリ
SELECT 
    "Created_Time",\n    "Parent_Id",\n    "Contact",\n    "Note",\n    "Status",\n    "Student",\n    "Gemini_Prof_ID"
FROM "Students_List"
LIMIT 100;

-- LinkingModule12 分析クエリ
-- 受講生ステータス別集計（例）
SELECT 
    "ステータス" as status,
    COUNT(*) as student_count,
    "コース名" as course_name
FROM "Students_List"
GROUP BY "ステータス", "コース名"
ORDER BY student_count DESC;

-- =====================================
-- 学習関連統合分析
-- =====================================

-- 受講生学習進捗統合分析（例）
-- 注意: 実際のテーブル名とフィールド名に合わせて調整が必要
SELECT 
    s."受講生名" as student_name,
    s."コース名" as course_name,
    s."登録日" as enrollment_date,
    COUNT(lr.id) as learning_records,
    SUM(CAST(lr."学習時間" as DECIMAL)) as total_hours,
    r."必要時間" as required_hours,
    CASE 
        WHEN SUM(CAST(lr."学習時間" as DECIMAL)) >= r."必要時間" 
        THEN '修了' 
        ELSE '未修了' 
    END as completion_status
FROM "受講生" s
LEFT JOIN "学習実績" lr ON s.id = lr."受講生ID"
LEFT JOIN "修了要件" r ON s."コース名" = r."コース名"
GROUP BY s."受講生名", s."コース名", s."登録日", r."必要時間"
ORDER BY total_hours DESC;

