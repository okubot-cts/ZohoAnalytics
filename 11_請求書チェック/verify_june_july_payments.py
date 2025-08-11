#!/usr/bin/env python3
"""
6月・7月の入金データを元データで確認・検算
JT ETP関連入金の実際の金額を特定
"""
import requests
import json
from pathlib import Path

def load_books_token():
    """Booksトークンを読み込み"""
    token_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン" / "zoho_books_tokens.json"
    with open(token_path, 'r') as f:
        tokens = json.load(f)
    return tokens['access_token']

def get_payments_for_period(headers, org_id, start_date, end_date, period_name):
    """指定期間の入金データを取得"""
    print(f"📊 {period_name}の入金データ取得中 ({start_date}～{end_date})")
    
    url = "https://www.zohoapis.com/books/v3/customerpayments"
    all_payments = []
    page = 1
    
    while page <= 20:
        params = {
            'organization_id': org_id,
            'per_page': 200,
            'page': page,
            'sort_column': 'date',
            'sort_order': 'D',
            'date_start': start_date,
            'date_end': end_date
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                payments = data.get('customerpayments', [])
                
                if payments:
                    all_payments.extend(payments)
                    print(f"  ページ{page}: {len(payments)}件取得 (累計: {len(all_payments)}件)")
                    
                    page_context = data.get('page_context', {})
                    if not page_context.get('has_more_page', False):
                        break
                    page += 1
                else:
                    print(f"  ページ{page}: データなし")
                    break
            else:
                print(f"  ❌ ページ{page}エラー: {response.status_code}")
                if page == 1:
                    print(f"     レスポンス: {response.text}")
                break
                
        except Exception as e:
            print(f"  ❌ ページ{page}例外: {str(e)}")
            break
    
    print(f"✅ {period_name}入金データ取得完了: {len(all_payments)}件")
    return all_payments

def analyze_jt_etp_payments(payments, period_name):
    """JT ETP関連入金を詳細分析"""
    print(f"\n💰 {period_name}のJT ETP関連入金分析")
    print("="*60)
    
    total_amount = sum(p.get('amount', 0) for p in payments)
    print(f"  {period_name}総入金額: ¥{total_amount:,.0f}")
    print(f"  {period_name}総入金件数: {len(payments)}件")
    
    jt_etp_candidates = []
    
    # JT ETP関連候補を幅広く検索
    for payment in payments:
        amount = payment.get('amount', 0)
        customer_name = payment.get('customer_name', '').upper()
        description = payment.get('description', '').upper()
        reference_number = payment.get('reference_number', '').upper()
        
        search_text = f"{customer_name} {description} {reference_number}"
        
        # JT ETP関連キーワード（拡張版）
        jt_keywords = [
            'JT', 'ジェイティ', 'JAPAN TOBACCO', 'ETP', 
            'JTビジネス', 'JTBC', '日本たばこ', 'たばこ',
            '外川', '真吾'  # 個人名も含める
        ]
        
        # 顧客IDも確認
        customer_id = payment.get('customer_id', '')
        
        is_jt_etp = any(keyword in search_text for keyword in jt_keywords)
        
        if is_jt_etp:
            jt_etp_candidates.append({
                'payment': payment,
                'match_reason': [kw for kw in jt_keywords if kw in search_text]
            })
    
    if jt_etp_candidates:
        jt_etp_total = sum(c['payment'].get('amount', 0) for c in jt_etp_candidates)
        print(f"\n🎯 JT ETP関連入金:")
        print(f"  件数: {len(jt_etp_candidates)}件")
        print(f"  金額: ¥{jt_etp_total:,.0f}")
        
        print(f"\n  詳細:")
        for i, candidate in enumerate(jt_etp_candidates, 1):
            payment = candidate['payment']
            date = payment.get('date', '')
            amount = payment.get('amount', 0)
            customer = payment.get('customer_name', 'N/A')
            description = payment.get('description', '')
            reference = payment.get('reference_number', '')
            match_reason = ', '.join(candidate['match_reason'])
            
            print(f"    {i:2}. {date}: ¥{amount:,.0f}")
            print(f"        顧客: {customer}")
            print(f"        マッチ理由: {match_reason}")
            if description:
                print(f"        メモ: {description}")
            if reference:
                print(f"        参照番号: {reference}")
            print()
        
        return jt_etp_total, jt_etp_candidates
    else:
        print(f"  JT ETP関連入金: なし")
        return 0, []

def search_amount_near_target(payments, target_amount, tolerance=50000):
    """目標金額に近い入金を検索"""
    print(f"\n🔍 目標金額¥{target_amount:,.0f}に近い入金を検索（±¥{tolerance:,.0f}）")
    
    candidates = []
    for payment in payments:
        amount = payment.get('amount', 0)
        if abs(amount - target_amount) <= tolerance:
            candidates.append(payment)
    
    if candidates:
        print(f"  候補: {len(candidates)}件")
        for payment in candidates:
            date = payment.get('date', '')
            amount = payment.get('amount', 0)
            customer = payment.get('customer_name', 'N/A')
            description = payment.get('description', '')
            diff = amount - target_amount
            print(f"    {date}: ¥{amount:,.0f} (差額: ¥{diff:,.0f}) - {customer}")
            if description:
                print(f"      メモ: {description}")
    else:
        print(f"  該当なし")
    
    return candidates

def verify_calculation():
    """検算実行"""
    print("="*80)
    print("📊 6月・7月入金データの元データ確認・検算")
    print("="*80)
    
    # 目標値
    target_values = {
        'deal_amount_tax_included': 92613274,
        'june_until_payment': 91079160,
        'july_required_payment': 1534114
    }
    
    print("📋 検算対象:")
    print(f"  商談総額（税込み）: ¥{target_values['deal_amount_tax_included']:,.0f}")
    print(f"  6月まで入金: ¥{target_values['june_until_payment']:,.0f}")
    print(f"  7月必要入金: ¥{target_values['july_required_payment']:,.0f}")
    
    # Booksトークン読み込み
    try:
        access_token = load_books_token()
        headers = {'Authorization': f'Bearer {access_token}'}
        org_id = "772043849"  # 前回取得した組織ID
        print("✅ Booksトークン準備完了")
    except Exception as e:
        print(f"❌ トークン準備エラー: {e}")
        return
    
    # 6月入金データ取得
    june_payments = get_payments_for_period(
        headers, org_id, '2025-06-01', '2025-06-30', '6月'
    )
    
    # 7月入金データ取得
    july_payments = get_payments_for_period(
        headers, org_id, '2025-07-01', '2025-07-31', '7月'
    )
    
    # JT ETP関連分析
    june_jt_amount, june_jt_candidates = analyze_jt_etp_payments(june_payments, '6月')
    july_jt_amount, july_jt_candidates = analyze_jt_etp_payments(july_payments, '7月')
    
    # 合計検算
    total_jt_etp = june_jt_amount + july_jt_amount
    
    print(f"\n" + "="*80)
    print("🎯 検算結果")
    print("="*80)
    print(f"6月JT ETP入金: ¥{june_jt_amount:,.0f}")
    print(f"7月JT ETP入金: ¥{july_jt_amount:,.0f}")
    print(f"6-7月JT ETP合計: ¥{total_jt_etp:,.0f}")
    print(f"商談総額（税込み）: ¥{target_values['deal_amount_tax_included']:,.0f}")
    print(f"差額: ¥{target_values['deal_amount_tax_included'] - total_jt_etp:,.0f}")
    
    if abs(target_values['deal_amount_tax_included'] - total_jt_etp) < 100000:
        print("✅ ほぼ一致！JT ETP入金は正常")
    else:
        print("⚠️ 大きな差額があります")
        
        # 目標金額に近い入金を検索
        search_amount_near_target(july_payments, target_values['july_required_payment'])
    
    print("="*80)

if __name__ == "__main__":
    verify_calculation()