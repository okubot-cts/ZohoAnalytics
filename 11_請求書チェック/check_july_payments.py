#!/usr/bin/env python3
"""
7月の入金データを確認
JT ETP関連の入金状況をチェック
"""
import requests
import json
from pathlib import Path
from datetime import datetime

def load_books_token():
    """Booksトークンを読み込み"""
    token_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン" / "zoho_books_tokens.json"
    with open(token_path, 'r') as f:
        tokens = json.load(f)
    return tokens['access_token']

def get_org_id(headers):
    """Books組織IDを取得"""
    response = requests.get("https://www.zohoapis.com/books/v3/organizations", headers=headers)
    if response.status_code == 200:
        orgs = response.json()['organizations']
        for org in orgs:
            if '株式会社シー・ティー・エス' in org.get('name', ''):
                return org['organization_id']
        return orgs[0]['organization_id'] if orgs else None
    return None

def get_july_payments(headers, org_id):
    """7月の入金データを取得"""
    print("📊 7月の入金データを取得中...")
    
    url = "https://www.zohoapis.com/books/v3/customerpayments"
    all_payments = []
    page = 1
    
    while page <= 5:
        params = {
            'organization_id': org_id,
            'per_page': 200,
            'page': page,
            'sort_column': 'date',
            'sort_order': 'D',
            'date_start': '2025-07-01',
            'date_end': '2025-07-31'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                payments = data.get('customerpayments', [])
                
                if payments:
                    all_payments.extend(payments)
                    print(f"  ページ{page}: {len(payments)}件取得")
                    
                    page_context = data.get('page_context', {})
                    if not page_context.get('has_more_page', False):
                        break
                    page += 1
                else:
                    break
            else:
                print(f"  ❌ ページ{page}エラー: {response.status_code}")
                if response.status_code == 400:
                    print(f"     エラー詳細: {response.text}")
                break
                
        except Exception as e:
            print(f"  ❌ ページ{page}例外: {str(e)}")
            break
    
    print(f"✅ 7月入金データ取得完了: {len(all_payments)}件")
    return all_payments

def analyze_july_payments(payments):
    """7月入金データを分析"""
    print(f"\n💰 7月入金分析")
    
    if not payments:
        print("  7月の入金データはありません")
        return
    
    total_amount = 0
    jt_etp_payments = []
    
    for payment in payments:
        amount = payment.get('amount', 0)
        total_amount += amount
        
        # 顧客名やメモでJT ETP関連を判定
        customer_name = payment.get('customer_name', '')
        description = payment.get('description', '')
        reference_number = payment.get('reference_number', '')
        
        if any(keyword in (customer_name + description + reference_number).upper() 
               for keyword in ['JT', 'ETP', 'ジェイティ']):
            jt_etp_payments.append(payment)
    
    print(f"  7月総入金額: ¥{total_amount:,.0f}")
    print(f"  7月入金件数: {len(payments)}件")
    
    if jt_etp_payments:
        jt_etp_amount = sum(p.get('amount', 0) for p in jt_etp_payments)
        print(f"  JT ETP関連入金: {len(jt_etp_payments)}件")
        print(f"  JT ETP関連金額: ¥{jt_etp_amount:,.0f}")
        
        print(f"\n  JT ETP関連入金詳細:")
        for payment in jt_etp_payments[:10]:  # 最初の10件を表示
            date = payment.get('date', '')
            amount = payment.get('amount', 0)
            customer = payment.get('customer_name', 'N/A')
            description = payment.get('description', '')
            print(f"    {date}: ¥{amount:,.0f} - {customer}")
            if description:
                print(f"      メモ: {description}")
    else:
        print(f"  JT ETP関連入金: なし")
    
    # 6月までの差額との比較
    diff_amount = 1534114  # 前回の分析結果
    print(f"\n📊 差額との比較:")
    print(f"  6月まで商談との差額: ¥{diff_amount:,.0f}")
    
    if jt_etp_payments:
        jt_etp_amount = sum(p.get('amount', 0) for p in jt_etp_payments)
        remaining_diff = diff_amount - jt_etp_amount
        print(f"  7月JT ETP入金: ¥{jt_etp_amount:,.0f}")
        print(f"  残り未説明差額: ¥{remaining_diff:,.0f}")
        
        if abs(remaining_diff) < 10000:
            print("  ✅ 差額がほぼ解消されました！")
        elif remaining_diff > 0:
            print("  ⚠️ まだ未入金分があります")
        else:
            print("  ⚠️ 7月入金の方が多いです")
    else:
        print(f"  7月JT ETP入金: ¥0")
        print(f"  未説明差額: ¥{diff_amount:,.0f} (変わらず)")

def main():
    """メイン処理"""
    print("="*80)
    print("📊 7月入金データ確認・JT ETP差額分析")
    print("="*80)
    
    # 1. Booksトークン読み込み
    try:
        access_token = load_books_token()
        headers = {'Authorization': f'Bearer {access_token}'}
        print("✅ Booksトークン読み込み完了")
    except Exception as e:
        print(f"❌ Booksトークン読み込みエラー: {e}")
        return
    
    # 2. 組織ID取得（または直接指定）
    org_id = get_org_id(headers)
    if not org_id:
        # 以前の分析から組織IDを直接指定
        print("⚠️ 組織ID取得失敗、既知のIDを使用")
        org_id = "772044231"  # 設定ファイルから取得
    
    print(f"✅ 組織ID: {org_id}")
    
    # 3. 7月入金データ取得
    july_payments = get_july_payments(headers, org_id)
    
    # 4. 入金分析
    analyze_july_payments(july_payments)
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()