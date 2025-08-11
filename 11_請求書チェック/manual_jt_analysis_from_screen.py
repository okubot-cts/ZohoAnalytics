#!/usr/bin/env python3
"""
JT ETP 手動分析（画面情報ベース）
ZohoCRM画面から確認できる請求書情報の分析
"""
print("="*90)
print("📊 JT ETP 手動分析（画面情報ベース）")
print("="*90)

# 画面から確認できる請求書データ
visible_invoices = [
    {'invoice_number': 'INV-008953', 'amount': 110, 'date': '2025/09/30', 'reference': '5187347000012', 'status': '下書き'},
    {'invoice_number': 'INV-008952', 'amount': 110, 'date': '2025/10/31', 'reference': '5187347000012', 'status': '下書き'},
    {'invoice_number': 'INV-008733', 'amount': 965194, 'date': '2025/06/30', 'reference': '5187347000012', 'status': '支払い済み'},
    {'invoice_number': 'INV-008359', 'amount': 568920, 'date': '2025/07/31', 'reference': '5187347000012', 'status': '支払い済み'},
    {'invoice_number': 'INV-008270', 'amount': 9903319, 'date': '2025/05/31', 'reference': '5187347000012', 'status': '支払い済み'},
    {'invoice_number': 'INV-007676', 'amount': 47090472, 'date': '2025/04/30', 'reference': '5187347000012', 'status': '支払い済み'},
    {'invoice_number': 'INV-007046', 'amount': 34085369, 'date': '2025/03/31', 'reference': '5187347000012', 'status': '支払い済み'},
]

print("🔍 画面から確認できる請求書:")
print("="*90)

total_amount = 0
paid_amount = 0
draft_amount = 0
upper_period_amount = 0  # 上期（〜5月）
lower_period_amount = 0  # 下期（6月〜）

upper_period_count = 0
lower_period_count = 0

for i, invoice in enumerate(visible_invoices, 1):
    amount = invoice['amount']
    date = invoice['date']
    status = invoice['status']
    
    # 期間判定
    try:
        month = int(date.split('/')[1]) if '/' in date else 12
        if month <= 5:
            period = '上期'
            upper_period_amount += amount
            upper_period_count += 1
        else:
            period = '下期'
            lower_period_amount += amount
            lower_period_count += 1
    except:
        period = '不明'
        lower_period_amount += amount
        lower_period_count += 1
    
    total_amount += amount
    
    if status == '支払い済み':
        paid_amount += amount
    elif status == '下書き':
        draft_amount += amount
    
    print(f"{i:2}. {invoice['invoice_number']}")
    print(f"    金額: ¥{amount:,.0f}")
    print(f"    日付: {date} ({period})")
    print(f"    ステータス: {status}")
    print(f"    参照: {invoice['reference']}")
    print()

print("="*90)
print("📊 集計結果")
print("="*90)

print(f"📄 請求書統計:")
print(f"  確認できた請求書数: {len(visible_invoices)}件")
print(f"  請求書総額: ¥{total_amount:,.0f}")
print(f"  支払い済み: ¥{paid_amount:,.0f}")
print(f"  下書き: ¥{draft_amount:,.0f} ({visible_invoices[0]['amount'] + visible_invoices[1]['amount']}円)")

print(f"\n📅 期間別統計:")
print(f"  上期（〜5月）: {upper_period_count}件, ¥{upper_period_amount:,.0f}")
print(f"  下期（6月〜）: {lower_period_count}件, ¥{lower_period_amount:,.0f}")

# 前回分析との比較
previous_analysis = {
    'found_amount': 15501617,
    'excluded_110': 220,
    'effective_amount': 15501617 - 220
}

print(f"\n🔍 前回分析との比較:")
print(f"  前回分析で発見: ¥{previous_analysis['effective_amount']:,.0f}")
print(f"  今回画面確認: ¥{total_amount:,.0f}")
print(f"  差異: ¥{total_amount - previous_analysis['effective_amount']:,.0f}")

if total_amount > previous_analysis['effective_amount']:
    print(f"  → 追加で ¥{total_amount - previous_analysis['effective_amount']:,.0f} 発見！")

# 110円請求書の確認
draft_110_count = sum(1 for inv in visible_invoices if inv['amount'] == 110 and inv['status'] == '下書き')
print(f"\n💰 110円請求書:")
print(f"  下書き状態: {draft_110_count}件 (¥{draft_110_count * 110})")
print(f"  → これらは実質的に請求されていない")

# 実質的な請求額（110円除外）
effective_total = total_amount - (draft_110_count * 110)
print(f"\n📊 実質請求額（110円下書き除外）:")
print(f"  実質請求額: ¥{effective_total:,.0f}")

# 理論値との比較
print(f"\n🎯 理論分析との比較:")
print(f"  531件理論推定（税込）: ¥98,955,560")
print(f"  実際の請求額: ¥{effective_total:,.0f}")
print(f"  推定未請求額: ¥{98955560 - effective_total:,.0f}")

# 重要な発見
print(f"\n" + "="*90)
print("🚨 重要な発見")
print("="*90)
print("1. 【実際の請求状況】")
print(f"   • 確認できた請求書: ¥{effective_total:,.0f}（110円除外後）")
print(f"   • 前回分析の約{effective_total / previous_analysis['effective_amount']:.1f}倍の請求書を発見")

print(f"\n2. 【期間別実態】")
print(f"   • 上期請求: ¥{upper_period_amount:,.0f} ({upper_period_count}件)")
print(f"   • 下期請求: ¥{lower_period_amount:,.0f} ({lower_period_count}件)")
print(f"   • 下期が上期の{lower_period_amount / upper_period_amount:.1f}倍")

print(f"\n3. 【推定未請求規模】")
print(f"   • 531件ベース推定: ¥{98955560 - effective_total:,.0f}")
print(f"   • ただし、画面で確認できたのは一部の可能性")

print(f"\n4. 【分析精度の問題】")
print(f"   • reference_number による自動マッチングが不完全")
print(f"   • 手動確認により大幅に請求書を発見")
print(f"   • システム上の紐づけ分析に改善が必要")

print(f"\n5. 【次のアクション】")
print(f"   • ZohoBooks で JT関連の全請求書を手動検索")
print(f"   • 顧客名・プロジェクト別での請求書確認")
print(f"   • 実際の契約金額との照合")

print("="*90)

# 簡易CSV出力
import pandas as pd
from datetime import datetime

df = pd.DataFrame(visible_invoices)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"JT_ETP画面確認請求書_{timestamp}.csv"
df.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"📁 画面確認データを保存: {output_file}")