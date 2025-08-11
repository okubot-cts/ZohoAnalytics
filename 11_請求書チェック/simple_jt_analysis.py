#!/usr/bin/env python3
"""
JT ETP事務局 簡易分析（CSVデータベース）
110円除外、上期/下期分離での差額分析
"""
print("="*80)
print("🔍 JT ETP事務局 簡易差額分析")
print("="*80)

# 元データから分析
print("📊 【2025】JT ETP事務局の基本情報:")
print("  親商談金額: ¥0")
print("  子商談数: 88件")
print("  子商談合計（税抜）: ¥14,908,559") 
print("  子商談合計（税込）: ¥16,399,415")
print("  実際請求書金額: ¥15,501,617")
print("  差額（修正前）: ¥897,798")

print(f"\n🔧 修正計算:")

# 110円請求書を2件除外
excluded_110yen = 110 * 2
print(f"  110円請求書除外: ¥{excluded_110yen} (2件)")

# 修正後の請求書金額
adjusted_invoice_amount = 15501617 - excluded_110yen
print(f"  修正後請求書金額: ¥{adjusted_invoice_amount:,.0f}")

# 修正後の差額
adjusted_diff = 16399415 - adjusted_invoice_amount  
print(f"  修正後差額: ¥{adjusted_diff:,.0f}")

print(f"\n📅 上期/下期想定分析:")
print("  ※ 実際の完了予定日データが必要ですが、推定分析:")

# 仮定: 88件を上期/下期で分割（一般的には上期40%、下期60%程度）
upper_ratio = 0.4  # 上期40%と仮定
lower_ratio = 0.6  # 下期60%と仮定

total_child_amount = 14908559
upper_estimated_amount = total_child_amount * upper_ratio
lower_estimated_amount = total_child_amount * lower_ratio

upper_estimated_with_tax = upper_estimated_amount * 1.1
lower_estimated_with_tax = lower_estimated_amount * 1.1

print(f"\n  【推定上期分析（〜5月）】")
print(f"    推定商談数: {int(88 * upper_ratio)}件")
print(f"    推定金額（税抜）: ¥{upper_estimated_amount:,.0f}")
print(f"    推定金額（税込）: ¥{upper_estimated_with_tax:,.0f}")

print(f"\n  【推定下期分析（6月〜）】") 
print(f"    推定商談数: {int(88 * lower_ratio)}件")
print(f"    推定金額（税抜）: ¥{lower_estimated_amount:,.0f}")
print(f"    推定金額（税込）: ¥{lower_estimated_with_tax:,.0f}")

print(f"\n💡 分析推論:")
print(f"  1. 110円請求書2件除外により差額は ¥{adjusted_diff:,.0f}")
print(f"  2. この差額は主に以下の要因と推定:")
print(f"     • 一部子商談の請求漏れ")
print(f"     • 上期/下期での請求タイミングずれ")
print(f"     • 実績ベース調整（サービス未完了等）")

print(f"\n🔍 確認が必要な項目:")
print(f"  1. 88件の子商談の完了予定日別内訳")
print(f"  2. 28件の請求書の発行月・対象期間")
print(f"  3. 未請求60件の理由（完了待ち・キャンセル等）")

print("="*80)