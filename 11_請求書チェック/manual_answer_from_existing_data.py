#!/usr/bin/env python3
"""
既存データからの回答
JT ETP 531件のうち「後期」なし商談の実際の総額
"""
print("="*90)
print("📊 JT ETP 「後期」なし商談の実際の総額回答")
print("="*90)

print("🔍 現在の状況:")
print("  • APIトークン期限切れにより531件の完全データ取得不可")
print("  • 既存の88件取得済みデータから分析")
print("  • 手動での画面確認が必要")

print(f"\n📋 既存の取得済みデータ:")
existing_88_deals = {
    'count': 88,
    'total_amount_excluding_tax': 14908559
}

print(f"  取得済み件数: {existing_88_deals['count']}件")
print(f"  取得済み総額（税抜き）: ¥{existing_88_deals['total_amount_excluding_tax']:,.0f}")
print(f"  取得済み総額（税込み）: ¥{existing_88_deals['total_amount_excluding_tax'] * 1.1:,.0f}")

print(f"\n🎯 回答:")
print("="*30)
print("❌ 申し訳ありませんが、現在は以下の理由により")
print("   531件すべての実際の商談総額をお答えできません:")
print("")
print("1. ❌ ZohoCRM APIトークンが期限切れ")
print("2. ❌ 531件中88件のみ取得済み（83%が未取得）") 
print("3. ❌ 商談名に「後期」が含まれるかどうかの判定不可")

print(f"\n🔧 実際の総額を確認する方法:")
print("="*40)
print("【方法1】ZohoCRM画面での手動確認")
print("  1. ZohoCRMにログイン")
print("  2. 商談ID「5187347000129692086」を開く")
print("  3. 関連する子商談一覧を表示")
print("  4. 商談名に「後期」が含まれない商談をフィルタ")
print("  5. 金額列の合計を計算")

print(f"\n【方法2】CSVエクスポート")
print("  1. 子商談一覧をCSVエクスポート")
print("  2. Excelで「後期」を含む行を除外")
print("  3. 残りの金額を合計")

print(f"\n【方法3】APIトークンの更新")
print("  1. ZohoCRM設定でAPIトークンを再生成")
print("  2. 上記スクリプトを再実行")

print(f"\n📝 参考情報:")
print(f"  • 88件のサンプルから推測される531件の規模:")
print(f"    - 推定総額: ¥{(existing_88_deals['total_amount_excluding_tax'] * 531 / 88):,.0f}（税抜き）")
print(f"    - ただし、これは「後期」フィルタなしの全体推定")
print(f"  • 実際には「後期」商談を除外する必要あり")

print("="*90)
print("💡 正確な回答には実際のデータアクセスが必要です")
print("="*90)