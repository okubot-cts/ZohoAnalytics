#!/usr/bin/env python3
"""
ZohoCRMとZohoBooksの商談と請求書の関連分析スクリプト
テーブル構造、フィールド、紐づけロジックを調査
"""
import requests
import json
from pathlib import Path
from datetime import datetime
import pandas as pd

def analyze_crm_books_relations():
    """CRMとBooksのテーブル関連を分析"""
    
    # トークンファイルの読み込み
    base_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン"
    
    with open(base_path / "zoho_crm_tokens.json", 'r') as f:
        crm_tokens = json.load(f)
    
    with open(base_path / "zoho_books_tokens.json", 'r') as f:
        books_tokens = json.load(f)
    
    crm_headers = {'Authorization': f'Bearer {crm_tokens["access_token"]}'}
    books_headers = {'Authorization': f'Bearer {books_tokens["access_token"]}'}
    
    print("="*70)
    print("ZohoCRM & Books テーブル関連分析")
    print("="*70)
    
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
    
    print(f"使用する組織ID: {org_id}\n")
    
    # === CRM商談データの詳細分析 ===
    print("📊 1. CRM商談データの構造分析")
    print("="*50)
    
    crm_deals_url = "https://www.zohoapis.com/crm/v2/Deals"
    params = {'per_page': 3}
    
    crm_response = requests.get(crm_deals_url, headers=crm_headers, params=params)
    
    if crm_response.status_code == 200:
        crm_data = crm_response.json()
        if 'data' in crm_data and crm_data['data']:
            print("✅ 商談サンプルデータ:")
            
            # 最初の商談の全フィールドを表示
            first_deal = crm_data['data'][0]
            print(f"\n商談ID: {first_deal.get('id')}")
            print(f"商談名: {first_deal.get('Deal_Name')}")
            
            # 重要なフィールドのリスト
            important_fields = [
                'id', 'Deal_Name', 'Account_Name', 'Contact_Name', 'Amount', 
                'Stage', 'Closing_Date', 'Owner', 'Created_Time', 'Modified_Time',
                'Description', 'Lead_Source', 'Campaign_Source', 'Type',
                'Next_Step', 'Probability', 'Expected_Revenue'
            ]
            
            print("\n🔍 商談の主要フィールド:")
            for field in important_fields:
                value = first_deal.get(field, 'N/A')
                if isinstance(value, dict):
                    # Account_NameやOwnerなどのオブジェクト型フィールド
                    if 'name' in value:
                        value = f"{value['name']} (ID: {value.get('id', 'N/A')})"
                    elif 'full_name' in value:
                        value = f"{value['full_name']} (ID: {value.get('id', 'N/A')})"
                print(f"  {field}: {value}")
            
            # 全フィールド名を表示
            print(f"\n📝 全フィールド一覧 ({len(first_deal)}個):")
            field_names = sorted(first_deal.keys())
            for i, field in enumerate(field_names, 1):
                print(f"  {i:2}. {field}")
                if i % 5 == 0:  # 5個ごとに改行
                    print()
    
    # === Books請求書データの詳細分析 ===
    print("\n\n📄 2. Books請求書データの構造分析")
    print("="*50)
    
    books_invoices_url = "https://www.zohoapis.com/books/v3/invoices"
    params = {'organization_id': org_id, 'per_page': 3}
    
    books_response = requests.get(books_invoices_url, headers=books_headers, params=params)
    
    if books_response.status_code == 200:
        books_data = books_response.json()
        if 'invoices' in books_data and books_data['invoices']:
            print("✅ 請求書サンプルデータ:")
            
            # 最初の請求書の全フィールドを表示
            first_invoice = books_data['invoices'][0]
            print(f"\n請求書ID: {first_invoice.get('invoice_id')}")
            print(f"請求書番号: {first_invoice.get('invoice_number')}")
            
            # 重要なフィールドのリスト
            important_fields = [
                'invoice_id', 'invoice_number', 'customer_id', 'customer_name',
                'contact_id', 'status', 'date', 'due_date', 'reference_number',
                'total', 'balance', 'created_time', 'last_modified_time',
                'currency_code', 'exchange_rate', 'discount', 'shipping_charge',
                'adjustment', 'write_off_amount', 'payment_made'
            ]
            
            print("\n🔍 請求書の主要フィールド:")
            for field in important_fields:
                value = first_invoice.get(field, 'N/A')
                print(f"  {field}: {value}")
            
            # 全フィールド名を表示
            print(f"\n📝 全フィールド一覧 ({len(first_invoice)}個):")
            field_names = sorted(first_invoice.keys())
            for i, field in enumerate(field_names, 1):
                print(f"  {i:2}. {field}")
                if i % 5 == 0:  # 5個ごとに改行
                    print()
    
    # === Books顧客データの分析 ===
    print("\n\n👥 3. Books顧客データの構造分析")
    print("="*50)
    
    books_contacts_url = "https://www.zohoapis.com/books/v3/contacts"
    params = {'organization_id': org_id, 'per_page': 3}
    
    contacts_response = requests.get(books_contacts_url, headers=books_headers, params=params)
    
    if contacts_response.status_code == 200:
        contacts_data = contacts_response.json()
        if 'contacts' in contacts_data and contacts_data['contacts']:
            first_contact = contacts_data['contacts'][0]
            
            print("✅ 顧客データサンプル:")
            print(f"\n顧客ID: {first_contact.get('contact_id')}")
            print(f"顧客名: {first_contact.get('contact_name')}")
            
            # 重要フィールド
            important_fields = [
                'contact_id', 'contact_name', 'company_name', 'contact_type',
                'email', 'phone', 'mobile', 'website', 'currency_code',
                'payment_terms', 'credit_limit', 'created_time', 'last_modified_time'
            ]
            
            print("\n🔍 顧客の主要フィールド:")
            for field in important_fields:
                value = first_contact.get(field, 'N/A')
                print(f"  {field}: {value}")
    
    # === 紐づけ可能性の分析 ===
    print("\n\n🔗 4. 紐づけ可能性の分析")
    print("="*50)
    
    print("💡 商談→請求書の紐づけ方法:")
    print("\n【方法1: 顧客名による紐づけ】")
    print("  CRM: Account_Name['name'] ↔ Books: customer_name")
    print("  精度: 中程度（表記揺れの可能性）")
    
    print("\n【方法2: 金額による紐づけ】")  
    print("  CRM: Amount ↔ Books: total")
    print("  精度: 低（同額の取引が複数ある可能性）")
    
    print("\n【方法3: 日付による紐づけ】")
    print("  CRM: Closing_Date ↔ Books: date")
    print("  精度: 中程度（成約日と請求日にズレがある可能性）")
    
    print("\n【方法4: カスタムフィールドによる紐づけ】")
    print("  CRM: カスタムフィールドに請求書番号を保存")
    print("  Books: reference_numberに商談IDを保存")
    print("  精度: 高（手動設定が必要）")
    
    # === 実際の紐づけ分析 ===
    print("\n\n🎯 5. 実データでの紐づけ分析")
    print("="*50)
    
    # より多くのデータを取得して分析
    crm_deals = get_crm_deals_detailed(crm_headers)
    books_invoices = get_books_invoices_detailed(books_headers, org_id)
    books_contacts = get_books_contacts_detailed(books_headers, org_id)
    
    analyze_matching_possibilities(crm_deals, books_invoices, books_contacts)
    
    print("\n" + "="*70)
    print("分析完了")

def get_crm_deals_detailed(headers):
    """詳細な商談データを取得"""
    url = "https://www.zohoapis.com/crm/v2/Deals"
    params = {
        'fields': 'Deal_Name,Account_Name,Contact_Name,Amount,Stage,Closing_Date,Created_Time,Modified_Time,Description',
        'per_page': 20,
        'sort_by': 'Modified_Time',
        'sort_order': 'desc'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
    except Exception as e:
        print(f"CRM取得エラー: {str(e)}")
    return []

def get_books_invoices_detailed(headers, org_id):
    """詳細な請求書データを取得"""
    url = "https://www.zohoapis.com/books/v3/invoices"
    params = {
        'organization_id': org_id,
        'per_page': 20,
        'sort_column': 'date',
        'sort_order': 'D'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('invoices', [])
    except Exception as e:
        print(f"Books請求書取得エラー: {str(e)}")
    return []

def get_books_contacts_detailed(headers, org_id):
    """詳細な顧客データを取得"""
    url = "https://www.zohoapis.com/books/v3/contacts"
    params = {
        'organization_id': org_id,
        'per_page': 50
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('contacts', [])
    except Exception as e:
        print(f"Books顧客取得エラー: {str(e)}")
    return []

def analyze_matching_possibilities(deals, invoices, contacts):
    """実データを使った紐づけ可能性分析"""
    
    print(f"📊 分析対象データ:")
    print(f"  商談: {len(deals)}件")
    print(f"  請求書: {len(invoices)}件") 
    print(f"  顧客: {len(contacts)}件")
    
    # 顧客名の一致分析
    print(f"\n📋 顧客名マッチング分析:")
    
    # CRMの顧客名を抽出
    crm_customers = set()
    for deal in deals:
        account = deal.get('Account_Name', {})
        if isinstance(account, dict) and 'name' in account:
            crm_customers.add(account['name'].strip())
    
    # Booksの顧客名を抽出
    books_customers = set()
    for invoice in invoices:
        customer = invoice.get('customer_name', '')
        if customer:
            books_customers.add(customer.strip())
    
    # 完全一致
    exact_matches = crm_customers & books_customers
    print(f"  完全一致: {len(exact_matches)}社")
    for match in sorted(exact_matches):
        print(f"    - {match}")
    
    # 部分一致の分析
    partial_matches = []
    for crm_customer in crm_customers:
        for books_customer in books_customers:
            if crm_customer != books_customer:
                # 部分文字列の一致をチェック
                if (crm_customer in books_customer or 
                    books_customer in crm_customer or
                    any(word in books_customer for word in crm_customer.split() if len(word) > 2)):
                    partial_matches.append((crm_customer, books_customer))
    
    if partial_matches:
        print(f"\n  部分一致候補: {len(partial_matches)}組")
        for crm, books in partial_matches[:5]:  # 最初の5組を表示
            print(f"    CRM: {crm}")
            print(f"    Books: {books}")
            print()
    
    # 金額の分析
    print(f"\n💰 金額分析:")
    
    # 成約商談の金額
    closed_deals = [d for d in deals if d.get('Stage') in ['Closed Won', '受注', '成約']]
    deal_amounts = [d.get('Amount', 0) for d in closed_deals if d.get('Amount', 0) > 0]
    
    # 請求書の金額
    invoice_amounts = [i.get('total', 0) for i in invoices if i.get('total', 0) > 0]
    
    print(f"  成約商談金額: {len(deal_amounts)}件 (合計: ¥{sum(deal_amounts):,.0f})")
    print(f"  請求書金額: {len(invoice_amounts)}件 (合計: ¥{sum(invoice_amounts):,.0f})")
    
    # 金額の一致分析
    amount_matches = []
    for deal in closed_deals:
        deal_amount = deal.get('Amount', 0)
        if deal_amount > 0:
            for invoice in invoices:
                invoice_amount = invoice.get('total', 0)
                if abs(deal_amount - invoice_amount) <= 1:  # 1円以下の差異は一致とみなす
                    amount_matches.append({
                        'deal_name': deal.get('Deal_Name'),
                        'invoice_number': invoice.get('invoice_number'),
                        'amount': deal_amount
                    })
    
    print(f"  金額一致: {len(amount_matches)}組")
    for match in amount_matches[:3]:  # 最初の3組を表示
        print(f"    {match['deal_name']} → {match['invoice_number']} (¥{match['amount']:,.0f})")

if __name__ == "__main__":
    analyze_crm_books_relations()