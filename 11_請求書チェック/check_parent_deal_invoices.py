#!/usr/bin/env python3
"""
JT ETP親商談から発行された請求書を確認
親商談ID: 5187347000129692086 の請求書を特定
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

def search_invoices_by_reference(headers, org_id, reference_number):
    """参照番号で請求書を検索"""
    print(f"📄 参照番号「{reference_number}」で請求書検索中...")
    
    url = "https://www.zohoapis.com/books/v3/invoices"
    page = 1
    found_invoices = []
    
    while page <= 20:
        params = {
            'organization_id': org_id,
            'per_page': 200,
            'page': page,
            'sort_column': 'date',
            'sort_order': 'D'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                invoices = data.get('invoices', [])
                
                if invoices:
                    # 参照番号でフィルタ
                    for invoice in invoices:
                        inv_ref = invoice.get('reference_number', '').strip()
                        if inv_ref == reference_number:
                            found_invoices.append(invoice)
                            print(f"  ✅ 発見: {invoice.get('invoice_number')} - ¥{invoice.get('total', 0):,.0f}")
                    
                    page_context = data.get('page_context', {})
                    if not page_context.get('has_more_page', False):
                        break
                    page += 1
                else:
                    break
            else:
                print(f"  ❌ ページ{page}エラー: {response.status_code}")
                break
                
        except Exception as e:
            print(f"  ❌ ページ{page}例外: {str(e)}")
            break
    
    print(f"  検索完了: {len(found_invoices)}件の請求書を発見")
    return found_invoices

def search_all_invoices_with_jt_etp_reference(headers, org_id):
    """JT ETP関連の参照番号を持つ請求書を全検索"""
    print(f"📄 JT ETP関連請求書を全検索中...")
    
    url = "https://www.zohoapis.com/books/v3/invoices"
    page = 1
    jt_etp_invoices = []
    
    parent_id = '5187347000129692086'
    
    while page <= 50:  # より多くのページを検索
        params = {
            'organization_id': org_id,
            'per_page': 200,
            'page': page,
            'sort_column': 'date',
            'sort_order': 'D'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                invoices = data.get('invoices', [])
                
                if invoices:
                    print(f"  ページ{page}: {len(invoices)}件を検索中...")
                    
                    # JT ETP関連を検索
                    for invoice in invoices:
                        inv_ref = invoice.get('reference_number', '').strip()
                        customer_name = invoice.get('customer_name', '').upper()
                        
                        # 親商談IDまたはJT関連で判定
                        is_jt_etp = (
                            inv_ref == parent_id or
                            'JT ETP' in customer_name or
                            'JT' in customer_name or
                            '日本たばこ' in customer_name
                        )
                        
                        if is_jt_etp:
                            jt_etp_invoices.append(invoice)
                            print(f"    ✅ 発見: {invoice.get('invoice_number')} - ¥{invoice.get('total', 0):,.0f}")
                            print(f"        顧客: {invoice.get('customer_name', 'N/A')}")
                            print(f"        参照番号: {inv_ref}")
                            print(f"        日付: {invoice.get('date', 'N/A')}")
                            print(f"        ステータス: {invoice.get('status', 'N/A')}")
                    
                    page_context = data.get('page_context', {})
                    if not page_context.get('has_more_page', False):
                        break
                    page += 1
                else:
                    print(f"  ページ{page}: データなし")
                    break
            else:
                print(f"  ❌ ページ{page}エラー: {response.status_code}")
                break
                
        except Exception as e:
            print(f"  ❌ ページ{page}例外: {str(e)}")
            break
    
    print(f"✅ JT ETP関連請求書検索完了: {len(jt_etp_invoices)}件")
    return jt_etp_invoices

def analyze_jt_etp_invoices(invoices):
    """JT ETP請求書を分析"""
    if not invoices:
        print("📊 JT ETP関連請求書が見つかりませんでした")
        return
    
    print(f"\n📊 JT ETP請求書分析 ({len(invoices)}件)")
    print("="*60)
    
    total_amount = 0
    status_count = {}
    by_parent_ref = {'parent': [], 'children': [], 'other': []}
    
    parent_id = '5187347000129692086'
    
    for invoice in invoices:
        amount = invoice.get('total', 0)
        total_amount += amount
        status = invoice.get('status', 'unknown')
        ref_num = invoice.get('reference_number', '').strip()
        
        # ステータス別集計
        if status not in status_count:
            status_count[status] = {'count': 0, 'amount': 0}
        status_count[status]['count'] += 1
        status_count[status]['amount'] += amount
        
        # 参照番号別分類
        if ref_num == parent_id:
            by_parent_ref['parent'].append(invoice)
        elif ref_num and len(ref_num) > 15:  # 子商談IDらしき長いID
            by_parent_ref['children'].append(invoice)
        else:
            by_parent_ref['other'].append(invoice)
    
    print(f"総額: ¥{total_amount:,.0f}")
    print(f"件数: {len(invoices)}件")
    
    # ステータス別
    print(f"\n📋 ステータス別:")
    for status, data in status_count.items():
        print(f"  {status}: {data['count']}件 - ¥{data['amount']:,.0f}")
    
    # 参照番号別
    print(f"\n📋 参照番号別:")
    print(f"  親商談参照: {len(by_parent_ref['parent'])}件 - ¥{sum(inv.get('total', 0) for inv in by_parent_ref['parent']):,.0f}")
    print(f"  子商談参照: {len(by_parent_ref['children'])}件 - ¥{sum(inv.get('total', 0) for inv in by_parent_ref['children']):,.0f}")
    print(f"  その他参照: {len(by_parent_ref['other'])}件 - ¥{sum(inv.get('total', 0) for inv in by_parent_ref['other']):,.0f}")
    
    # 詳細表示（最初の10件）
    print(f"\n📄 請求書詳細 (最初の10件):")
    for i, invoice in enumerate(invoices[:10], 1):
        print(f"  {i:2}. {invoice.get('invoice_number', 'N/A')}")
        print(f"      金額: ¥{invoice.get('total', 0):,.0f}")
        print(f"      顧客: {invoice.get('customer_name', 'N/A')}")
        print(f"      日付: {invoice.get('date', 'N/A')}")
        print(f"      ステータス: {invoice.get('status', 'N/A')}")
        print(f"      参照番号: {invoice.get('reference_number', 'N/A')}")
        print()
    
    return total_amount, status_count, by_parent_ref

def main():
    """メイン処理"""
    print("="*80)
    print("📊 JT ETP親商談から発行された請求書確認")
    print("="*80)
    
    parent_id = '5187347000129692086'
    print(f"親商談ID: {parent_id}")
    print(f"親商談名: 【2025】JT ETP _事務局")
    
    # Booksトークン読み込み
    try:
        access_token = load_books_token()
        headers = {'Authorization': f'Bearer {access_token}'}
        org_id = "772043849"
        print("✅ Booksトークン準備完了")
    except Exception as e:
        print(f"❌ トークン準備エラー: {e}")
        return
    
    # 1. 親商談IDで請求書を直接検索
    parent_invoices = search_invoices_by_reference(headers, org_id, parent_id)
    
    # 2. JT ETP関連請求書を全検索
    all_jt_etp_invoices = search_all_invoices_with_jt_etp_reference(headers, org_id)
    
    # 3. 分析
    if parent_invoices:
        print(f"\n🎯 親商談直接参照の請求書:")
        analyze_jt_etp_invoices(parent_invoices)
    
    if all_jt_etp_invoices:
        print(f"\n🎯 JT ETP関連全請求書:")
        total_amount, status_count, by_parent_ref = analyze_jt_etp_invoices(all_jt_etp_invoices)
        
        # 商談総額との比較
        deal_amount = 92613274
        print(f"\n📊 商談総額との比較:")
        print(f"  商談総額（税込み）: ¥{deal_amount:,.0f}")
        print(f"  請求書総額: ¥{total_amount:,.0f}")
        print(f"  差額: ¥{deal_amount - total_amount:,.0f}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()