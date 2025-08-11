# 11_請求書チェック

## 概要
ZohoCRMの商談データとZohoBooksの請求書データを照合し、請求漏れを分析するためのツール群です。

## 主要な分析結果

### JT ETPケースの分析
- **親商談**: 【2025】JT ETP _事務局（ID: 5187347000129692086）
- **子商談**: 531件
- **商談構造**: 親商談¥0、子商談から一括請求のパターン（パターン3）
- **請求書との整合性**: 完全一致を確認

### 5つの商談パターン
1. **パターン1**: 親商談完結（親商談のみで請求）
2. **パターン2**: 子商談完結（親金額ゼロ、子商談で請求）
3. **パターン3**: 親統括・金額なし（親から子商談分を一括請求）← JT ETPパターン
4. **パターン4**: 親統括・金額あり（親から全体を請求）
5. **パターン5**: 自己負担・会社負担分担（親子両方で請求）

### 分析対象範囲
- **期間**: 2024/4/1以降の商談（Closing_Date基準）
- **総商談数**: 9,800件
- **総額**: ¥479,232,850（税抜き）/ ¥527,156,135（税込み）

## 主要スクリプト

### 包括的分析
- `comprehensive_all_deals_analysis.py`: 2024/4/1以降の全商談を5パターン分析
- `comprehensive_pattern_analysis.py`: 代表的な親子セットでパターン検証
- `final_pattern_analysis.py`: 最終5パターン包括分析

### JT ETP専用分析
- `get_jt_etp_complete_531_deals.py`: JT ETP 531件完全取得・後期なし商談分析
- `complete_jt_etp_analysis.py`: JT ETP完全分析
- `analyze_jt_etp_detail.py`: JT ETP詳細分析

### 請求漏れ分析
- `correct_invoice_leakage_analyzer.py`: 修正版請求漏れ分析（消費税対応）
- `invoice_leakage_analyzer.py`: 基本請求漏れ分析
- `improved_invoice_matcher.py`: 改良版請求書マッチング

### トークン管理・認証
- `auto_refresh_books_token_and_check_july.py`: Booksトークン自動更新
- `refresh_crm_token_and_analyze.py`: CRMトークン更新+分析
- `zoho_auth_manager.py`: Zoho認証管理

### 入金・支払い分析
- `verify_june_july_payments.py`: 6月・7月入金データ確認
- `check_july_payments.py`: 7月入金データ確認
- `analyze_payment_difference.py`: 入金差額分析

### 構造調査
- `investigate_parent_child_structure.py`: 親子構造詳細調査
- `analyze_parent_deal_and_all_stages.py`: 親商談・全ステージ分析
- `find_parent_deal_fields.py`: 親商談フィールド調査

## 分析結果ファイル

### JT ETP分析結果
- `JT_ETP_完全分析結果/`: JT ETP 531件の完全分析データ
- `JT_ETP画面確認請求書_20250811_122040.csv`: 画面確認用請求書データ

### 請求漏れ分析結果
- `請求漏れ分析結果/`: 基本分析結果
- `請求漏れ分析結果_修正版/`: 修正版分析結果
- `請求漏れ分析結果_税込み修正版/`: 税込み対応版分析結果

## 重要な発見

### 消費税の取り扱い
- **商談金額**: 税抜き
- **請求書金額**: 税込み
- **比較時**: 商談金額 × 1.10 vs 請求書金額

### 親子構造の特徴
- **親商談**: 事務局・統括機能、多くが金額¥0
- **子商談**: 個別サービス、実際の金額を持つ
- **請求パターン**: 主にパターン3（親商談から子商談分を一括請求）

### 期間フィルタの注意点
- 親商談のClosing_Dateは契約時期（年度開始前）
- 子商談のClosing_Dateはサービス提供時期
- 期間フィルタで親子関係が分断される可能性

## 使用方法

1. **認証情報設定**: `/01_Zoho_API/設定ファイル/zoho_config.json`
2. **トークン取得**: 認証URLでアクセストークンを取得
3. **分析実行**: 各スクリプトを目的に応じて実行
4. **結果確認**: 生成されたCSVファイルや分析レポートを確認

## 注意事項
- API制限に注意してスクリプトを実行
- トークンの有効期限（1時間）に注意
- 大量データ取得時はタイムアウト対策が必要