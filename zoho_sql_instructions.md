# Zoho Analytics SQL実行手順

## 🎯 生成したSQLをZoho Analyticsで実行する方法

### 方法1: Zoho Analytics UI（推奨・簡単）

1. **Zoho Analyticsにログイン**
   - https://analytics.zoho.com にアクセス
   - 「Zoho CRMの分析」ワークスペースを開く

2. **Query Tableを作成**
   - 左サイドパネルの「Create」をクリック
   - 「Query Table」を選択
   - SQL Query Editorが開く

3. **SQLを貼り付けて実行**
   - 生成したSQLクエリをコピー
   - エディターに貼り付け
   - 「Execute Query」をクリック

4. **レポート作成**
   - 実行結果からレポートやチャートを作成
   - ダッシュボードに追加可能

### 方法2: CloudSQL API（プログラム実行）

APIエンドポイント:
```
https://analyticsapi.zoho.com/api/v1/workspaces/{workspace_id}/data
```

必要なパラメータ:
- SQL: SQLクエリ文
- CONFIG: 出力設定
- ZOHO_OUTPUT_FORMAT: json/csv/pdf/html

### 🔧 SQLの調整が必要な場合

#### テーブル名の確認
CRM APIのモジュール名とAnalyticsのテーブル名が異なる場合があります：

**CRM API名** → **Analytics名**
- `Deals` → `商談` または `Deals`
- `Contacts` → `連絡先` または `Contacts`
- `Accounts` → `取引先` または `Accounts`

#### フィールド名の調整
1. **日本語表示名**: `"商談名"`, `"取引先名"`
2. **API名**: `"Deal_Name"`, `"Account_Name"`
3. **Analytics内部名**: 実際のテーブル構造による

### 📊 実用的なSQLクエリ例

#### 商談分析
```sql
-- 商談ステージ別売上
SELECT 
    ステージ,
    COUNT(*) as 件数,
    SUM(金額) as 総売上
FROM 商談
WHERE 金額 IS NOT NULL
GROUP BY ステージ
ORDER BY 総売上 DESC;
```

#### 月次トレンド
```sql
-- 月次商談作成数
SELECT 
    DATE_FORMAT(作成日時, '%Y-%m') as 月,
    COUNT(*) as 新規商談数
FROM 商談
GROUP BY DATE_FORMAT(作成日時, '%Y-%m')
ORDER BY 月 DESC;
```

#### 営業担当者別実績
```sql
-- 担当者別売上実績
SELECT 
    担当者,
    COUNT(*) as 商談数,
    SUM(金額) as 総売上,
    AVG(金額) as 平均単価
FROM 商談
WHERE ステージ = '受注'
GROUP BY 担当者
ORDER BY 総売上 DESC;
```

### ⚠️ 注意点

1. **テーブル名・フィールド名の確認**
   - Analytics UIで実際の名前を確認
   - 日本語名の場合は適切にエスケープ

2. **データ型の調整**
   - 金額フィールドの型変換
   - 日付フォーマットの調整

3. **権限の確認**
   - 必要なテーブルにアクセス権限があることを確認
   - 読み取り専用権限で十分

### 🎯 次のステップ

1. **Analytics UIでテーブル名確認**
2. **簡単なクエリから実行開始**
3. **段階的に複雑なクエリに拡張**
4. **レポート・ダッシュボード作成**

### 📞 サポート

問題が発生した場合:
- Zoho Analytics Help: https://help.zoho.com/portal/en/kb/analytics
- SQL構文リファレンス: ANSI SQL準拠
- カスタムクエリサポート: 各フィールドの実際の名前確認が重要