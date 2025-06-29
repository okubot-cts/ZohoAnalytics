# Zoho Analytics スキーマ取得・SQL生成プロジェクト

このプロジェクトは、Zoho CRM/AnalyticsからスキーマをAPIで取得し、実用的なSQLクエリを自動生成するツールセットです。

## 📋 プロジェクト概要

### 目的
- Zoho AnalyticsのスキーマをAPI経由で自動取得
- 業務に必要なSQLクエリの自動生成
- 手動作業を削減し、効率的なデータ分析を実現

### 主な成果物
- **スキーマ情報**: 4,583個のフィールド定義を含む完全なCRMスキーマ
- **SQLクエリ集**: 即座に実行可能な業務用SQLクエリ
- **認証システム**: OAuth 2.0対応の自動認証ツール

## 🎯 主要機能

### 1. API認証システム
- **OAuth 2.0認証**: Zoho CRM/Analytics API対応
- **トークン管理**: アクセストークン・リフレッシュトークンの自動管理
- **権限設定**: 適切なスコープでのAPI認証

### 2. スキーマ取得
- **全モジュール取得**: 118個のCRMモジュール
- **フィールド詳細**: データ型、必須項目、カスタムフィールド等
- **関連情報**: ルックアップ関係、ピックリスト値、数式フィールド

### 3. SQL自動生成
- **基本クエリ**: 主要テーブルの基本SELECT文
- **分析クエリ**: 商談分析、タスク管理、学習実績等
- **JOIN処理**: テーブル間関連を考慮した統合クエリ

## 📁 ファイル構成

### 認証関連
```
zoho_auth.py                    # Analytics API認証
zoho_crm_auth.py               # CRM API認証
get_token.py                   # トークン取得
get_crm_token.py              # CRMトークン取得
zoho_tokens.json              # Analytics用トークン
zoho_crm_tokens.json          # CRM用トークン
```

### スキーマ取得
```
zoho_analytics_auth.py         # Analytics認証・スキーマ取得
zoho_crm_schema.py            # CRM完全スキーマ取得
zoho_table_extractor.py       # テーブル一覧抽出
zoho_crm_schema.json          # CRMスキーマ（4,583フィールド）
zoho_crm_schema.xlsx          # CRMスキーマ（Excel版）
```

### SQL生成
```
zoho_sql_generator.py         # SQL自動生成エンジン
zoho_analytics_queries.sql    # 基本SQLクエリ集
zoho_simple_task_queries.sql  # Analytics制限対応版
zoho_task_deal_queries.sql    # タスク・商談分析用
```

### 学習関連
```
zoho_learning_comprehensive_sql.sql  # 学習関連テーブル用SQL
zoho_learning_analysis_report.xlsx   # 学習テーブル分析
zoho_field_reference.xlsx           # フィールドリファレンス
```

### テスト・検証
```
test_zoho_sql.py              # SQL実行テスト
test_api.py                   # API動作確認
zoho_sql_validation_report.txt # 検証レポート
```

## 🚀 使用方法

### 1. 環境設定
```bash
pip install requests pandas openpyxl
```

### 2. API認証
1. **Zoho Developer Console**でアプリ登録
   - https://api-console.zoho.com/
   - Server-based Applicationで作成
   - Client ID・Client Secret・Redirect URIを取得

2. **認証実行**
   ```bash
   python3 zoho_crm_auth.py
   ```

### 3. スキーマ取得
```bash
python3 zoho_crm_schema.py
```

### 4. SQL生成
```bash
python3 zoho_sql_generator.py
```

### 5. Zoho Analyticsでの実行
1. Analytics画面で「Query Table」作成
2. 生成したSQLをコピー&ペースト
3. 「Execute Query」で実行

## 📊 取得可能なデータ

### CRMスキーマ情報
- **総モジュール数**: 118個
- **総フィールド数**: 4,583個
- **主要モジュール**: 商談、連絡先、取引先、見込み客、タスク、商品

### 主要テーブル
| テーブル名 | API名 | フィールド数 | 用途 |
|-----------|-------|-------------|------|
| 商談 | Deals | 234 | 営業管理 |
| 連絡先 | Contacts | 99 | 顧客管理 |
| 取引先 | Accounts | 73 | 企業管理 |
| 見込み客 | Leads | 68 | 見込み客管理 |
| タスク | Tasks | 28 | タスク管理 |
| 商品 | Products | 56 | 商品管理 |

### 学習関連テーブル
| テーブル名 | API名 | フィールド数 | 用途 |
|-----------|-------|-------------|------|
| 受講生 | Students | 35 | 受講生管理 |
| クラス | Classes | 134 | クラス管理 |
| 出席詳細 | Attendance_Detail | 91 | 出席管理 |
| 学習実績 | CustomModule75 | 86 | 学習実績管理 |

## 💡 実用的なSQLクエリ例

### タスク管理
```sql
-- 未完了タスク一覧（商談関連情報付き）
SELECT 
    t."Subject" as タスク件名,
    t."Status" as タスクステータス,
    t."Priority" as 優先度,
    t."Due_Date" as 期限,
    d."Deal_Name" as 商談名,
    d."Stage" as 商談ステージ,
    d."Amount" as 商談金額
FROM "Tasks" t
LEFT JOIN "Deals" d ON t."What_Id" = d."id"
WHERE t."Owner" = 'okubo.t@cts-n.net'
  AND t."Status" <> 'Completed'
ORDER BY t."Due_Date" ASC;
```

### 商談分析
```sql
-- 商談ステージ別集計
SELECT 
    "Stage" as ステージ,
    COUNT(*) as 商談数,
    SUM("Amount") as 総額,
    AVG("Amount") as 平均金額
FROM "Deals"
WHERE "Amount" IS NOT NULL
GROUP BY "Stage"
ORDER BY 総額 DESC;
```

## ⚠️ 注意事項・制限事項

### API制限
- **レート制限**: API呼び出し頻度に制限あり
- **権限制限**: 個別テーブルデータアクセスに制限
- **スコープ**: 適切なOAuth権限が必要

### Zoho Analytics制限
- **SQL制限**: SELECT文のみ実行可能
- **関数制限**: 一部のSQL関数が利用不可
- **UI実行推奨**: API経由よりUI経由の実行が安定

### フィールド名調整
- **表示名 vs API名**: CRM APIとAnalytics表示名が異なる場合あり
- **日本語フィールド**: 適切なエスケープが必要
- **データ型**: Analytics固有の型変換が必要な場合あり

## 🔧 トラブルシューティング

### 認証エラー
```
INVALID_TOKEN エラー
→ トークンの有効期限切れ。再認証が必要
```

### API権限エラー
```
ORGID_NOT_PRESENT_IN_THE_HEADER
→ ヘッダーに組織IDを追加
```

### SQL実行エラー
```
"SQLのSELECT文のみ使用できます"
→ シンプル版SQLクエリを使用
```

## 📈 今後の拡張予定

- [ ] 自動データ同期機能
- [ ] リアルタイムダッシュボード生成
- [ ] カスタムレポート自動作成
- [ ] 学習進捗自動分析
- [ ] 予測分析機能

## 🤝 コントリビューション

プロジェクトへの貢献歓迎です：
1. Issueの報告
2. 新機能の提案
3. SQLクエリの改善
4. ドキュメントの更新

## 📞 サポート

技術的な質問・問題：
- GitHub Issues
- プロジェクト担当者: okubo.t@cts-n.net

## 📄 ライセンス

このプロジェクトは社内利用目的で開発されています。

---

**最終更新**: 2025-06-29  
**バージョン**: 1.0.0  
**開発者**: Claude Code Assistant & CTS Team 