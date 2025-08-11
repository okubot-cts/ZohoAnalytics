#!/usr/bin/env python3
"""
既存の88件データで「後期」分析
現在取得できているJT ETP商談データを分析
"""
print("="*80)
print("📊 JT ETP 既存88件「後期」分析")
print("="*80)

# これまでの分析で判明した情報
jt_etp_existing_data = {
    'parent_id': '5187347000129692086',
    'parent_name': '【2025】JT ETP _事務局',
    'children_count': 88,
    'children_amount_excluding_tax': 14908559,
    'children_amount_including_tax': 16399414.9,
    'invoice_count': 28,
    'total_invoice_amount': 15501617
}

print("📋 既存の88件データ:")
print(f"  親商談: {jt_etp_existing_data['parent_name']}")
print(f"  親商談ID: {jt_etp_existing_data['parent_id']}")
print(f"  子商談数: {jt_etp_existing_data['children_count']}件")
print(f"  子商談総額（税抜き）: ¥{jt_etp_existing_data['children_amount_excluding_tax']:,.0f}")
print(f"  子商談総額（税込み）: ¥{jt_etp_existing_data['children_amount_including_tax']:,.0f}")

print(f"\n🤔 重要な仮説:")
print("既存の88件は「後期」商談である可能性が高い")
print("理由:")
print("  1. 531件中88件のみ取得 = フィルタ条件で絞り込まれた")
print("  2. 分析スクリプトは「受注ステージ」でフィルタしていた") 
print("  3. 「後期」商談が先に受注ステージになった可能性")

print(f"\n🔍 531件の構成推測:")

# 88件が後期なら、残り443件が「後期なし」
if_88_is_kouki = {
    'kouki_count': 88,
    'kouki_amount': 14908559,  # 税抜き
    'no_kouki_count': 531 - 88,
    'no_kouki_estimated_amount': 0  # 不明
}

print(f"  「後期」商談: {if_88_is_kouki['kouki_count']}件")
print(f"  「後期」金額（税抜き）: ¥{if_88_is_kouki['kouki_amount']:,.0f}")
print(f"  「後期なし」商談: {if_88_is_kouki['no_kouki_count']}件")
print(f"  「後期なし」金額: 不明（要調査）")

# 入金データとの照合
payment_until_june = 91079160  # 6月まで入金（110円除く）

print(f"\n💰 入金データとの照合:")
print(f"  6月まで入金額: ¥{payment_until_june:,.0f}")
print(f"  88件商談額（税込み）: ¥{jt_etp_existing_data['children_amount_including_tax']:,.0f}")
print(f"  差額: ¥{payment_until_june - jt_etp_existing_data['children_amount_including_tax']:,.0f}")

remaining_payment = payment_until_june - jt_etp_existing_data['children_amount_including_tax']
print(f"\n📊 残り443件の推定:")
print(f"  入金から逆算した金額: ¥{remaining_payment:,.0f}（税込み）")
print(f"  税抜き推定: ¥{remaining_payment / 1.1:,.0f}")

# 平均単価での分析
if remaining_payment > 0:
    avg_per_deal_remaining = (remaining_payment / 1.1) / 443
    avg_per_deal_88 = if_88_is_kouki['kouki_amount'] / 88
    
    print(f"\n💡 商談単価比較:")
    print(f"  88件平均単価: ¥{avg_per_deal_88:,.0f}（税抜き）")
    print(f"  残り443件平均単価: ¥{avg_per_deal_remaining:,.0f}（税抜き）")
    
    ratio = avg_per_deal_remaining / avg_per_deal_88
    print(f"  単価比率: {ratio:.2f}倍")
    
    if ratio > 1.5:
        print("  → 残り443件の方が高額案件の傾向")
    elif ratio < 0.7:
        print("  → 88件の方が高額案件の傾向")
    else:
        print("  → ほぼ同等の単価")

print(f"\n🎯 回答への道筋:")
print("="*50)
print("531件のうち「後期」なし商談の総額を知るには：")
print("")
print("【仮説1】88件が「後期」商談の場合")
print(f"  「後期なし」総額（税抜き）: ¥{remaining_payment / 1.1:,.0f}")
print(f"  「後期なし」総額（税込み）: ¥{remaining_payment:,.0f}")
print("")
print("【仮説2】88件が「後期なし」商談の場合")
print(f"  「後期なし」総額（税抜き）: ¥{if_88_is_kouki['kouki_amount']:,.0f}")
print(f"  「後期なし」総額（税込み）: ¥{jt_etp_existing_data['children_amount_including_tax']:,.0f}")

print(f"\n🔬 仮説検証の方法:")
print("1. 認証URLでZohoCRM APIトークンを更新")
print("2. 531件すべてを取得")
print("3. 商談名で「後期」フィルタを適用")
print("4. 正確な金額を集計")

print(f"\n⚡ 暫定回答:")
print("="*30)
print("現在の情報では2つの可能性があります：")
print("")
print("【可能性A】「後期なし」商談総額")
print(f"  税抜き: ¥{remaining_payment / 1.1:,.0f}")
print(f"  税込み: ¥{remaining_payment:,.0f}")
print("")
print("【可能性B】「後期なし」商談総額")  
print(f"  税抜き: ¥{if_88_is_kouki['kouki_amount']:,.0f}")
print(f"  税込み: ¥{jt_etp_existing_data['children_amount_including_tax']:,.0f}")
print("")
print("正確な回答には、APIトークン更新→531件完全取得が必要です。")

print("="*80)