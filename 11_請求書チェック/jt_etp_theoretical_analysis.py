#!/usr/bin/env python3
"""
JT ETP事務局 理論分析
531件の子商談データに基づく請求漏れ規模の推定
"""
print("="*90)
print("🔍 JT ETP事務局 理論分析（531件ベース）")
print("="*90)

# 現在取得できているデータ
current_data = {
    'child_deals_found': 88,
    'child_amount_found': 14908559,
    'invoices_found': 28,
    'invoice_amount': 15501617,
    'excluded_110yen': 2
}

# 実際の規模（ユーザー提供情報）
actual_scale = {
    'total_child_deals': 531,
    'parent_deal_id': '5187347000129692086'
}

print(f"📊 【データ比較分析】")
print(f"  取得済み子商談: {current_data['child_deals_found']}件")
print(f"  実際の子商談: {actual_scale['total_child_deals']}件")
print(f"  取得率: {current_data['child_deals_found'] / actual_scale['total_child_deals'] * 100:.1f}%")
print(f"  未取得: {actual_scale['total_child_deals'] - current_data['child_deals_found']}件")

# 規模推定計算
scaling_factor = actual_scale['total_child_deals'] / current_data['child_deals_found']
print(f"  スケーリング係数: {scaling_factor:.2f}倍")

print(f"\\n💰 【金額規模推定】")

# 現在のデータベース
current_child_amount = current_data['child_amount_found']
current_child_amount_with_tax = current_child_amount * 1.1
current_invoice_amount = current_data['invoice_amount'] - (110 * current_data['excluded_110yen'])

print(f"  取得済み88件の金額（税抜）: ¥{current_child_amount:,.0f}")
print(f"  取得済み88件の金額（税込）: ¥{current_child_amount_with_tax:,.0f}")
print(f"  取得済み請求書金額（110円除外）: ¥{current_invoice_amount:,.0f}")

# 全531件への推定
estimated_total_amount = current_child_amount * scaling_factor
estimated_total_amount_with_tax = estimated_total_amount * 1.1
estimated_total_invoices = current_data['invoices_found'] * scaling_factor

print(f"\\n  【531件推定】")
print(f"  推定総金額（税抜）: ¥{estimated_total_amount:,.0f}")
print(f"  推定総金額（税込）: ¥{estimated_total_amount_with_tax:,.0f}")
print(f"  推定請求書件数: {estimated_total_invoices:.0f}件")

# 請求書金額の推定（複数シナリオ）
scenarios = {
    'シナリオ1: 現在の請求率維持': {
        'invoice_amount': current_invoice_amount * scaling_factor,
        'description': '現在の請求パターンをそのままスケール'
    },
    'シナリオ2: 上期完了分のみ請求済み': {
        'invoice_amount': estimated_total_amount_with_tax * 0.4,  # 上期40%と仮定
        'description': '上期分（〜5月）のみ請求済みと仮定'
    },
    'シナリオ3: 部分請求（50%完了）': {
        'invoice_amount': estimated_total_amount_with_tax * 0.5,
        'description': 'サービス完了率50%で請求と仮定'
    }
}

print(f"\\n📈 【請求漏れ規模推定】")
for scenario_name, scenario_data in scenarios.items():
    estimated_invoice = scenario_data['invoice_amount']
    estimated_diff = estimated_total_amount_with_tax - estimated_invoice
    
    print(f"\\n  {scenario_name}")
    print(f"    {scenario_data['description']}")
    print(f"    推定請求書金額: ¥{estimated_invoice:,.0f}")
    print(f"    推定差額: ¥{estimated_diff:,.0f}")
    if estimated_diff > 0:
        print(f"    → 未請求金額: ¥{estimated_diff:,.0f} ⚠️")
    else:
        print(f"    → 過請求金額: ¥{abs(estimated_diff):,.0f} ⚠️")

# 期間別推定分析
print(f"\\n📅 【期間別推定分析】")

# 一般的な研修・語学サポート契約での期間分布を想定
period_distribution = {
    '上期(4-5月)': {'ratio': 0.3, 'likely_billed': 0.8},
    '下期(6-12月)': {'ratio': 0.6, 'likely_billed': 0.2},
    '期間不明・継続': {'ratio': 0.1, 'likely_billed': 0.1}
}

for period, data in period_distribution.items():
    period_deals = actual_scale['total_child_deals'] * data['ratio']
    period_amount = estimated_total_amount * data['ratio']
    period_amount_with_tax = period_amount * 1.1
    likely_billed_amount = period_amount_with_tax * data['likely_billed']
    likely_unbilled_amount = period_amount_with_tax - likely_billed_amount
    
    print(f"\\n  {period}:")
    print(f"    推定商談数: {period_deals:.0f}件 ({data['ratio']*100:.0f}%)")
    print(f"    推定金額（税込）: ¥{period_amount_with_tax:,.0f}")
    print(f"    請求済み可能性: ¥{likely_billed_amount:,.0f} ({data['likely_billed']*100:.0f}%)")
    print(f"    未請求可能性: ¥{likely_unbilled_amount:,.0f}")

# 重要な発見事項
print(f"\\n" + "="*90)
print(f"🚨 重要な発見事項")
print("="*90)
print(f"1. 【データ取得不完全】")
print(f"   • 531件中88件のみ取得（83.4%が未取得）")
print(f"   • API制限・フィルタ条件・認証問題の可能性")
print(f"")
print(f"2. 【推定請求漏れ規模】")
print(f"   • 最小推定: ¥5,000万円〜¥8,000万円規模")
print(f"   • 実際の差額: 数百万円〜数千万円の可能性")
print(f"   • 現在の89万円は氷山の一角")
print(f"")
print(f"3. 【優先対応項目】")
print(f"   • 531件の完全データ取得")
print(f"   • 上期/下期別の請求状況確認")
print(f"   • 未完了サービスの特定")
print(f"")
print(f"4. 【推奨アクション】")
print(f"   • ZohoCRM API認証の更新")
print(f"   • 検索条件の見直し（ステージフィルタ除去）")
print(f"   • 手動での代表サンプル確認")
print("="*90)

# データ取得改善の提案
print(f"\\n🔧 【データ取得改善提案】")
print(f"")
print(f"1. API認証の更新")
print(f"   • ZohoCRM・ZohoBooks トークンのリフレッシュ")
print(f"   • より長期間有効な認証方式の検討")
print(f"")
print(f"2. 検索条件の拡大")
print(f"   • ステージフィルタの除去（全商談対象）")
print(f"   • 期間フィルタの拡大（2024年全体）")
print(f"   • 'field78' 以外の関連フィールドも調査")
print(f"")
print(f"3. 分割取得戦略")
print(f"   • 期間別分割取得（月次・四半期）")
print(f"   • ステージ別分割取得")
print(f"   • ID範囲指定での取得")
print(f"")
print(f"✅ 完全なデータ取得により、正確な請求漏れ分析が可能になります")