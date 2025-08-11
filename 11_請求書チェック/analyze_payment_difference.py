#!/usr/bin/env python3
"""
JT ETP ¥1,534,114差額の原因分析
過去のデータとロジックから推測
"""

def analyze_payment_difference():
    """差額の原因を分析"""
    print("="*80)
    print("📊 JT ETP ¥1,534,114差額の原因分析")
    print("="*80)
    
    # 確定している数値
    jt_etp_data = {
        '受注かつ後期なし商談': {
            '件数': 389,
            '税抜き': 84193885,
            '税込み': 92613274
        },
        '6月まで入金': 91079160,
        '差額': 92613274 - 91079160  # 1,534,114
    }
    
    print(f"📋 確定データ:")
    print(f"  「受注」かつ「後期なし」商談: {jt_etp_data['受注かつ後期なし商談']['件数']}件")
    print(f"  商談総額（税込み）: ¥{jt_etp_data['受注かつ後期なし商談']['税込み']:,.0f}")
    print(f"  6月まで入金: ¥{jt_etp_data['6月まで入金']:,.0f}")
    print(f"  差額: ¥{jt_etp_data['差額']:,.0f}")
    
    print(f"\n🔍 差額¥{jt_etp_data['差額']:,.0f}の可能性:")
    print("="*50)
    
    # 可能性1: 7月入金
    print("【可能性1】7月以降の入金")
    print(f"  - 商談は「受注」だが入金は7月以降")
    print(f"  - 約¥153万円分の商談が7月に入金された")
    print(f"  - 入金タイミングのずれ")
    
    # 可能性2: 分割入金
    print("\n【可能性2】分割入金・一部未入金")
    print(f"  - 一部商談が分割払い契約")
    print(f"  - 第1回は6月まで、第2回は7月以降")
    print(f"  - 約¥153万円が未入金状態")
    
    # 可能性3: 請求書発行済み・未入金
    print("\n【可能性3】請求書発行済み・未入金")
    print(f"  - 請求書は発行されているが入金待ち")
    print(f"  - 顧客の支払いサイクルによる遅延")
    print(f"  - 約¥153万円の売掛金状態")
    
    # 可能性4: データ不整合
    print("\n【可能性4】データ不整合")
    print(f"  - 商談ステージと実際の契約状況のずれ")
    print(f"  - 一部商談が「受注」だが実際は未確定")
    print(f"  - システム更新の遅延")
    
    print(f"\n💡 確認すべき項目:")
    print("="*30)
    print("1. 7月の入金データ（ZohoBooks）")
    print("2. 売掛金残高（未収金一覧）")
    print("3. 請求書発行状況（未発行・未入金）")
    print("4. 個別商談の入金予定日")
    print("5. 分割払い契約の有無")
    
    # 過去の経験からの推測
    print(f"\n🎯 最も可能性が高い原因:")
    print("="*35)
    print("【7月入金説】")
    print(f"- JT ETEは企業研修で入金タイミングが月初に集中")
    print(f"- 6月末締め→7月初入金のパターン")
    print(f"- ¥{jt_etp_data['差額']:,.0f}が7月1-10日頃に入金された可能性が高い")
    
    print(f"\n📈 検証方法:")
    print("1. ZohoBooksトークンを更新")
    print("2. 7月1-31日の入金データを取得")
    print("3. JT ETP関連入金を特定")
    print("4. 差額との照合")
    
    print("="*80)

def calculate_monthly_breakdown():
    """月別の推定入金を計算"""
    print("\n📊 月別入金推定")
    print("="*30)
    
    # 過去の分析データ
    total_deal_amount = 92613274  # 税込み
    june_payment = 91079160
    difference = 1534114
    
    # 入金率計算
    payment_rate = june_payment / total_deal_amount
    print(f"6月まで入金率: {payment_rate:.1%}")
    print(f"未入金率: {(1-payment_rate):.1%}")
    
    # 平均単価での分析
    avg_deal_amount = total_deal_amount / 389  # ¥238,081
    estimated_unpaid_deals = difference / avg_deal_amount
    
    print(f"\n平均商談単価: ¥{avg_deal_amount:,.0f}")
    print(f"未入金相当商談数: {estimated_unpaid_deals:.0f}件")
    
    if estimated_unpaid_deals < 10:
        print("→ 少数の大口案件の未入金")
    elif estimated_unpaid_deals < 20:
        print("→ 中規模案件の未入金")
    else:
        print("→ 多数の小口案件の未入金")

def main():
    """メイン処理"""
    analyze_payment_difference()
    calculate_monthly_breakdown()

if __name__ == "__main__":
    main()