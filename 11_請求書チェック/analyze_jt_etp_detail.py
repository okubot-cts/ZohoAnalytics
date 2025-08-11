#!/usr/bin/env python3
"""
JT ETP事務局案件の詳細分析
110円請求書除外、上期/下期分離分析
"""
import requests
import json
from pathlib import Path
import pandas as pd
from datetime import datetime

def analyze_jt_etp_detail():
    """JT ETP事務局案件の詳細分析"""
    
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
    org_id = None
    if org_response.status_code == 200:
        orgs = org_response.json()['organizations']
        for org in orgs:
            if '株式会社シー・ティー・エス' in org.get('name', ''):
                org_id = org['organization_id']
                break
        if not org_id and orgs:
            org_id = orgs[0]['organization_id']
    
    print("="*80)
    print("🔍 JT ETP事務局案件 詳細分析")
    print("="*80)
    
    # JT ETP親商談ID
    parent_deal_id = "5187347000129692086"
    
    print(f"📊 親商談ID: {parent_deal_id}")
    print("【2025】JT ETP _事務局\n")
    
    # 親商談の詳細取得
    parent_url = f"https://www.zohoapis.com/crm/v2/Deals/{parent_deal_id}"
    parent_response = requests.get(parent_url, headers=crm_headers)
    
    if parent_response.status_code == 200:
        parent_deal = parent_response.json()['data'][0]
        print(f"✅ 親商談取得成功")
        print(f"   名前: {parent_deal.get('Deal_Name')}")
        print(f"   金額: ¥{parent_deal.get('Amount', 0):,.0f}")
        print(f"   ステージ: {parent_deal.get('Stage')}")
        print(f"   完了予定日: {parent_deal.get('Closing_Date')}")
    else:
        print(f"❌ 親商談取得エラー: {parent_response.status_code}")
        return
    
    # 子商談を取得（field78で親商談IDを参照している商談）
    print(f"\n📋 子商談を検索中...")
    
    all_child_deals = []
    page = 1
    
    while page <= 10:
        deals_url = "https://www.zohoapis.com/crm/v2/Deals"
        params = {
            'fields': 'id,Deal_Name,Amount,Stage,Closing_Date,Created_Time,field78',
            'per_page': 200,
            'page': page
        }
        
        response = requests.get(deals_url, headers=crm_headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            deals = data.get('data', [])
            
            # field78で親商談IDを参照している子商談をフィルタ
            for deal in deals:
                field78 = deal.get('field78')
                if field78 and isinstance(field78, dict):
                    if field78.get('id') == parent_deal_id:
                        all_child_deals.append(deal)
            
            if not data.get('info', {}).get('more_records', False):
                break
            page += 1
        else:
            print(f"❌ 商談取得エラー: {response.status_code}")
            break
    
    print(f"✅ 子商談取得完了: {len(all_child_deals)}件")
    
    # 子商談の詳細分析
    total_child_amount = 0
    child_by_period = {'上期': [], '下期': []}
    
    print(f"\n📊 子商談詳細:")
    for i, child in enumerate(all_child_deals, 1):
        child_amount = child.get('Amount', 0) or 0
        total_child_amount += child_amount
        closing_date = child.get('Closing_Date', '')
        
        # 上期/下期判定（5月まで=上期、6月以降=下期）
        if closing_date:
            month = int(closing_date.split('-')[1]) if '-' in closing_date else 12
            period = '上期' if month <= 5 else '下期'
        else:
            period = '下期'  # デフォルト
        
        child_by_period[period].append({
            'deal': child,
            'amount': child_amount,
            'closing_date': closing_date
        })
        
        if i <= 10:  # 最初の10件だけ表示
            print(f"  {i:2}. {child.get('Deal_Name', 'N/A')[:50]}")
            print(f"      金額: ¥{child_amount:,.0f}, 完了予定: {closing_date}, 期間: {period}")
    
    if len(all_child_deals) > 10:
        print(f"      ... 他{len(all_child_deals) - 10}件")
    
    print(f"\n💰 子商談合計: ¥{total_child_amount:,.0f}")
    print(f"📅 上期商談: {len(child_by_period['上期'])}件")
    print(f"📅 下期商談: {len(child_by_period['下期'])}件")
    
    # 請求書を取得
    print(f"\n📄 関連請求書を検索中...")
    
    # 親商談の請求書
    parent_invoices = []
    child_invoices = []
    excluded_invoices = []  # 110円請求書
    
    # すべての請求書を取得して関連するものを検索
    invoice_url = "https://www.zohoapis.com/books/v3/invoices"
    page = 1
    
    while page <= 10:
        params = {
            'organization_id': org_id,
            'per_page': 200,
            'page': page
        }
        
        response = requests.get(invoice_url, headers=books_headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            invoices = data.get('invoices', [])
            
            for invoice in invoices:
                ref_num = invoice.get('reference_number', '').strip()
                invoice_total = invoice.get('total', 0)
                
                if ref_num:
                    # 親商談への請求書
                    if ref_num == parent_deal_id:
                        if invoice_total == 110:
                            excluded_invoices.append(invoice)
                        else:
                            parent_invoices.append(invoice)
                    
                    # 子商談への請求書
                    for child in all_child_deals:
                        if ref_num == child['id']:
                            if invoice_total == 110:
                                excluded_invoices.append(invoice)
                            else:
                                # 期間判定
                                closing_date = child.get('Closing_Date', '')
                                if closing_date:
                                    month = int(closing_date.split('-')[1]) if '-' in closing_date else 12
                                    period = '上期' if month <= 5 else '下期'
                                else:
                                    period = '下期'
                                
                                child_invoices.append({
                                    'invoice': invoice,
                                    'child_deal': child,
                                    'period': period
                                })
            
            page_context = data.get('page_context', {})
            if not page_context.get('has_more_page', False):
                break
            page += 1
        else:
            print(f"❌ 請求書取得エラー: {response.status_code}")
            break
    
    print(f"✅ 請求書検索完了")
    print(f"   親への請求書: {len(parent_invoices)}件")
    print(f"   子への請求書: {len(child_invoices)}件")
    print(f"   110円除外請求書: {len(excluded_invoices)}件")
    
    # 期間別集計
    print(f"\n📊 期間別集計分析:")
    
    # 上期分析
    upper_child_amount = sum(item['amount'] for item in child_by_period['上期'])
    upper_child_amount_with_tax = upper_child_amount * 1.1
    upper_invoices = [item for item in child_invoices if item['period'] == '上期']
    upper_invoice_amount = sum(item['invoice'].get('total', 0) for item in upper_invoices)
    upper_diff = upper_child_amount_with_tax - upper_invoice_amount
    
    print(f"\n【上期分析（〜5月）】")
    print(f"  子商談数: {len(child_by_period['上期'])}件")
    print(f"  子商談金額（税抜）: ¥{upper_child_amount:,.0f}")
    print(f"  子商談金額（税込）: ¥{upper_child_amount_with_tax:,.0f}")
    print(f"  請求書件数: {len(upper_invoices)}件")
    print(f"  請求書金額: ¥{upper_invoice_amount:,.0f}")
    print(f"  差額: ¥{upper_diff:,.0f}")
    
    # 下期分析
    lower_child_amount = sum(item['amount'] for item in child_by_period['下期'])
    lower_child_amount_with_tax = lower_child_amount * 1.1
    lower_invoices = [item for item in child_invoices if item['period'] == '下期']
    lower_invoice_amount = sum(item['invoice'].get('total', 0) for item in lower_invoices)
    lower_diff = lower_child_amount_with_tax - lower_invoice_amount
    
    print(f"\n【下期分析（6月〜）】")
    print(f"  子商談数: {len(child_by_period['下期'])}件")
    print(f"  子商談金額（税抜）: ¥{lower_child_amount:,.0f}")
    print(f"  子商談金額（税込）: ¥{lower_child_amount_with_tax:,.0f}")
    print(f"  請求書件数: {len(lower_invoices)}件")
    print(f"  請求書金額: ¥{lower_invoice_amount:,.0f}")
    print(f"  差額: ¥{lower_diff:,.0f}")
    
    # 親商談請求書分析
    parent_invoice_amount = sum(inv.get('total', 0) for inv in parent_invoices)
    print(f"\n【親商談請求書】")
    print(f"  請求書件数: {len(parent_invoices)}件")
    print(f"  請求書金額: ¥{parent_invoice_amount:,.0f}")
    
    # 110円除外分析
    excluded_amount = sum(inv.get('total', 0) for inv in excluded_invoices)
    print(f"\n【110円除外請求書】")
    print(f"  除外件数: {len(excluded_invoices)}件")
    print(f"  除外金額: ¥{excluded_amount:,.0f}")
    
    # 総合分析
    total_expected_with_tax = total_child_amount * 1.1
    total_actual_invoice = parent_invoice_amount + upper_invoice_amount + lower_invoice_amount
    total_diff_adjusted = total_expected_with_tax - total_actual_invoice
    
    print(f"\n" + "="*80)
    print(f"📈 総合分析（110円除外後）")
    print("="*80)
    print(f"子商談合計（税抜）: ¥{total_child_amount:,.0f}")
    print(f"子商談合計（税込）: ¥{total_expected_with_tax:,.0f}")
    print(f"請求書合計（110円除外）: ¥{total_actual_invoice:,.0f}")
    print(f"調整後差額: ¥{total_diff_adjusted:,.0f}")
    print(f"")
    print(f"内訳:")
    print(f"  上期差額: ¥{upper_diff:,.0f}")
    print(f"  下期差額: ¥{lower_diff:,.0f}")
    print(f"  親請求: ¥{parent_invoice_amount:,.0f}")
    print(f"  除外分: ¥{excluded_amount:,.0f}")
    print("="*80)
    
    # 詳細結果をCSV出力
    output_data = []
    
    # 上期データ
    for item in child_by_period['上期']:
        child = item['deal']
        related_invoice = next((inv for inv in child_invoices 
                              if inv['child_deal']['id'] == child['id'] and inv['period'] == '上期'), None)
        
        output_data.append({
            'period': '上期',
            'deal_name': child.get('Deal_Name'),
            'deal_id': child['id'],
            'deal_amount': item['amount'],
            'deal_amount_with_tax': item['amount'] * 1.1,
            'closing_date': item['closing_date'],
            'has_invoice': related_invoice is not None,
            'invoice_amount': related_invoice['invoice'].get('total', 0) if related_invoice else 0
        })
    
    # 下期データ
    for item in child_by_period['下期']:
        child = item['deal']
        related_invoice = next((inv for inv in child_invoices 
                              if inv['child_deal']['id'] == child['id'] and inv['period'] == '下期'), None)
        
        output_data.append({
            'period': '下期',
            'deal_name': child.get('Deal_Name'),
            'deal_id': child['id'],
            'deal_amount': item['amount'],
            'deal_amount_with_tax': item['amount'] * 1.1,
            'closing_date': item['closing_date'],
            'has_invoice': related_invoice is not None,
            'invoice_amount': related_invoice['invoice'].get('total', 0) if related_invoice else 0
        })
    
    # CSV出力
    df = pd.DataFrame(output_data)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path(__file__).parent / f"JT_ETP詳細分析_{timestamp}.csv"
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"📁 詳細分析結果を保存: {output_file}")

if __name__ == "__main__":
    analyze_jt_etp_detail()