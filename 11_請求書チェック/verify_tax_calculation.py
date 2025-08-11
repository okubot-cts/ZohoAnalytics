#!/usr/bin/env python3
"""
消費税端数差額の逆引き検証
商談金額と請求書金額の整合性を確認
"""

def verify_tax_calculation():
    """消費税計算の逆引き検証"""
    print("="*80)
    print("📊 消費税端数差額の逆引き検証")
    print("="*80)
    
    # 正確な数値
    deal_amount_excluding_tax = 84193885  # 商談389件（税抜き）
    deal_amount_including_tax = 92613274  # 商談389件（税込み）
    invoice_amount_with_july = 92613274   # 請求書（7月入金含む）
    june_payment = 91079160              # 6月まで入金
    july_jt_etp_payment = 584400         # 7月JT ETP入金（実際は違った）
    
    print("📋 確定数値:")
    print(f"  商談389件（税抜き）: ¥{deal_amount_excluding_tax:,.0f}")
    print(f"  商談389件（税込み）: ¥{deal_amount_including_tax:,.0f}")
    print(f"  請求書（7月入金含む）: ¥{invoice_amount_with_july:,.0f}")
    print(f"  6月まで入金: ¥{june_payment:,.0f}")
    
    # 消費税計算の検証
    print(f"\n🧮 消費税計算検証:")
    calculated_tax_inclusive = deal_amount_excluding_tax * 1.10
    print(f"  計算値（税抜き × 1.10）: ¥{calculated_tax_inclusive:,.2f}")
    print(f"  実際の税込み額: ¥{deal_amount_including_tax:,.0f}")
    
    tax_diff = calculated_tax_inclusive - deal_amount_including_tax
    print(f"  差額: ¥{tax_diff:,.2f}")
    
    if abs(tax_diff) < 1:
        print("  ✅ 消費税計算は正確")
    else:
        print(f"  ⚠️ 消費税計算に{tax_diff:,.2f}円の差異")
    
    # 請求書との照合
    print(f"\n📊 請求書との照合:")
    invoice_diff = deal_amount_including_tax - invoice_amount_with_july
    print(f"  商談税込み: ¥{deal_amount_including_tax:,.0f}")
    print(f"  請求書額: ¥{invoice_amount_with_july:,.0f}")
    print(f"  差額: ¥{invoice_diff:,.0f}")
    
    if invoice_diff == 0:
        print("  ✅ 完全一致！商談と請求書は整合")
    else:
        print(f"  ⚠️ {abs(invoice_diff):,.0f}円の差異あり")
    
    # 入金との照合
    print(f"\n💰 入金との照合:")
    july_missing = deal_amount_including_tax - june_payment
    print(f"  商談税込み: ¥{deal_amount_including_tax:,.0f}")
    print(f"  6月まで入金: ¥{june_payment:,.0f}")
    print(f"  7月入金必要額: ¥{july_missing:,.0f}")
    
    # 7月の実際のJT ETP入金
    print(f"\n🔍 7月入金の検証:")
    print(f"  必要な7月入金: ¥{july_missing:,.0f}")
    print(f"  実際の7月JT ETP入金: ¥{july_jt_etp_payment:,.0f}（誤認）")
    
    # 逆引き：必要な7月入金を特定
    print(f"\n🎯 逆引き結論:")
    print("="*50)
    print("1. 商談389件と請求書は完全一致（¥92,613,274）")
    print("2. 6月まで入金: ¥91,079,160")
    print(f"3. 7月に入金されるべき額: ¥{july_missing:,.0f}")
    print("4. この¥1,534,114が7月のJT ETP関連入金として")
    print("   ZohoBooksに記録されているはず")
    
    print(f"\n💡 検証すべき点:")
    print("- 7月の入金¥1,534,114に相当するJT ETP入金を特定")
    print("- 顧客名が「JT」以外でもJT ETP関連の可能性")
    print("- 複数の小口入金の合計がこの金額になる可能性")
    
    # 平均単価から推定
    avg_deal_amount = deal_amount_excluding_tax / 389
    estimated_deals = july_missing / (avg_deal_amount * 1.10)
    
    print(f"\n📈 推定:")
    print(f"  平均商談単価（税抜き）: ¥{avg_deal_amount:,.0f}")
    print(f"  7月入金相当商談数: {estimated_deals:.1f}件")
    print(f"  → 約{estimated_deals:.0f}件分の商談が7月に入金")

if __name__ == "__main__":
    verify_tax_calculation()