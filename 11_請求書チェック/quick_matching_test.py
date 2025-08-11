#!/usr/bin/env python3
"""
商談-請求書マッチングの簡易テスト
reference_numberの活用を確認
"""
import requests
import json
from pathlib import Path

def quick_matching_test():
    """簡易マッチングテスト"""
    
    # トークン読み込み
    base_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン"
    
    with open(base_path / "zoho_crm_tokens.json", 'r') as f:
        crm_tokens = json.load(f)
    with open(base_path / "zoho_books_tokens.json", 'r') as f:
        books_tokens = json.load(f)
    
    crm_headers = {'Authorization': f'Bearer {crm_tokens["access_token"]}'}
    books_headers = {'Authorization': f'Bearer {books_tokens["access_token"]}'}
    
    # Books組織ID取得
    org_response = requests.get("https://www.zohoapis.com/books/v3/organizations", headers=books_headers)
    org_id = org_response.json()['organizations'][1]['organization_id']  # 株式会社シー・ティー・エス
    
    print("="*60)
    print("商談-請求書マッチング簡易テスト")
    print("="*60)
    
    # 限定データで取得
    print("\n📊 商談データ取得（最新10件）...")
    crm_url = "https://www.zohoapis.com/crm/v2/Deals"
    crm_params = {
        'fields': 'id,Deal_Name,Account_Name,Amount,Stage,Closing_Date',
        'per_page': 10,
        'sort_by': 'Modified_Time',
        'sort_order': 'desc'
    }
    
    crm_response = requests.get(crm_url, headers=crm_headers, params=crm_params)
    deals = crm_response.json().get('data', []) if crm_response.status_code == 200 else []
    
    print("\n📄 請求書データ取得（最新10件）...")
    books_url = "https://www.zohoapis.com/books/v3/invoices"
    books_params = {
        'organization_id': org_id,
        'per_page': 10,
        'sort_column': 'date',
        'sort_order': 'D'
    }
    
    books_response = requests.get(books_url, headers=books_headers, params=books_params)
    invoices = books_response.json().get('invoices', []) if books_response.status_code == 200 else []
    
    print(f"\n取得結果: 商談{len(deals)}件, 請求書{len(invoices)}件")
    
    # reference_number分析
    print("\n🔍 reference_number分析:")
    
    # 商談IDのセット
    deal_ids = {deal['id'] for deal in deals}
    
    matches = []
    for invoice in invoices:
        ref_num = invoice.get('reference_number', '').strip()
        print(f"\n請求書 {invoice.get('invoice_number')}:")
        print(f"  reference_number: '{ref_num}'")
        print(f"  顧客: {invoice.get('customer_name')}")
        print(f"  金額: ¥{invoice.get('total', 0):,.0f}")
        
        # reference_numberが商談IDと一致するかチェック
        if ref_num and ref_num in deal_ids:
            # マッチした商談を探す
            matched_deal = next((d for d in deals if d['id'] == ref_num), None)
            if matched_deal:
                matches.append({
                    'deal': matched_deal,
                    'invoice': invoice
                })
                print(f"  ✅ マッチした商談: {matched_deal.get('Deal_Name')}")
                print(f"     商談金額: ¥{matched_deal.get('Amount', 0):,.0f}")
        else:
            print(f"  ❌ マッチなし")
    
    # マッチング結果サマリ
    print(f"\n{'='*40}")
    print("マッチング結果:")
    print(f"  完全マッチ: {len(matches)}組")
    
    for i, match in enumerate(matches, 1):
        deal = match['deal']
        invoice = match['invoice']
        print(f"\n{i}. {deal.get('Deal_Name')} ↔ {invoice.get('invoice_number')}")
        print(f"   商談金額: ¥{deal.get('Amount', 0):,.0f}")
        print(f"   請求金額: ¥{invoice.get('total', 0):,.0f}")
        print(f"   顧客: {invoice.get('customer_name')}")
    
    # その他のマッチング可能性も簡易チェック
    print(f"\n🔍 その他の紐づけ可能性:")
    
    # 顧客名の部分一致
    customer_matches = []
    for deal in deals:
        account = deal.get('Account_Name', {})
        if isinstance(account, dict):
            deal_customer = account.get('name', '').strip()
            
            for invoice in invoices:
                invoice_customer = invoice.get('customer_name', '').strip()
                
                if deal_customer and invoice_customer:
                    if deal_customer == invoice_customer:
                        customer_matches.append(('完全一致', deal, invoice))
                    elif deal_customer in invoice_customer or invoice_customer in deal_customer:
                        customer_matches.append(('部分一致', deal, invoice))
    
    print(f"  顧客名による候補: {len(customer_matches)}組")
    for match_type, deal, invoice in customer_matches[:3]:  # 最初の3組
        print(f"    {match_type}: {deal.get('Deal_Name')} ↔ {invoice.get('invoice_number')}")
    
    print(f"\n{'='*60}")
    print("テスト完了")

if __name__ == "__main__":
    quick_matching_test()