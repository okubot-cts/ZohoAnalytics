#!/usr/bin/env python3
"""
ZohoCRMとZohoBooksの簡易チェックツール
"""
import requests
import json
from pathlib import Path
from datetime import datetime, timedelta

def quick_check():
    """CRMとBooksのデータを簡易チェック"""
    
    # トークンファイルの読み込み
    base_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン"
    
    # CRMトークン
    crm_tokens_file = base_path / "zoho_crm_tokens.json"
    with open(crm_tokens_file, 'r') as f:
        crm_tokens = json.load(f)
    
    # Booksトークン
    books_tokens_file = base_path / "zoho_books_tokens.json"
    with open(books_tokens_file, 'r') as f:
        books_tokens = json.load(f)
    
    print("="*60)
    print("Zoho CRM & Books 簡易チェック")
    print("="*60)
    
    # CRM商談データ取得（最新10件）
    print("\n📊 CRM商談データ（最新10件）:")
    crm_headers = {'Authorization': f'Bearer {crm_tokens["access_token"]}'}
    crm_url = "https://www.zohoapis.com/crm/v2/Deals"
    params = {
        'fields': 'Deal_Name,Stage,Amount,Closing_Date,Account_Name',
        'per_page': 10,
        'sort_by': 'Modified_Time',
        'sort_order': 'desc'
    }
    
    try:
        response = requests.get(crm_url, headers=crm_headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                total_amount = 0
                closed_count = 0
                for i, deal in enumerate(data['data'], 1):
                    stage = deal.get('Stage', '')
                    amount = deal.get('Amount', 0) or 0
                    
                    print(f"{i:2}. {deal.get('Deal_Name', 'N/A')[:30]}")
                    print(f"    顧客: {deal.get('Account_Name', 'N/A')}")
                    print(f"    ステージ: {stage}")
                    print(f"    金額: ¥{amount:,.0f}")
                    
                    if stage in ['Closed Won', '受注', '成約']:
                        closed_count += 1
                        total_amount += amount
                
                print(f"\n成約商談: {closed_count}件, 合計金額: ¥{total_amount:,.0f}")
        else:
            print(f"エラー: {response.status_code}")
    except Exception as e:
        print(f"CRM接続エラー: {str(e)}")
    
    # Books組織ID取得
    print("\n" + "-"*60)
    books_headers = {'Authorization': f'Bearer {books_tokens["access_token"]}'}
    # 日本のデータセンターを使用
    org_url = "https://www.zohoapis.jp/books/v3/organizations"
    
    try:
        response = requests.get(org_url, headers=books_headers)
        if response.status_code == 200:
            data = response.json()
            if 'organizations' in data and data['organizations']:
                # 株式会社シー・ティー・エスの組織IDを使用
                org_id = None
                for org in data['organizations']:
                    if '株式会社シー・ティー・エス' in org.get('name', ''):
                        org_id = org['organization_id']
                        print(f"\n✅ 組織: {org['name']} (ID: {org_id})")
                        break
                
                if not org_id and data['organizations']:
                    # デフォルトで最初の組織を使用
                    org_id = data['organizations'][0]['organization_id']
                    print(f"\n✅ 組織: {data['organizations'][0]['name']} (ID: {org_id})")
                
                if org_id:
                    # Books請求書データ取得（最新10件）
                    print("\n📄 Books請求書データ（最新10件）:")
                    invoice_url = "https://www.zohoapis.jp/books/v3/invoices"
                    params = {
                        'organization_id': org_id,
                        'per_page': 10,
                        'sort_column': 'date',
                        'sort_order': 'D'
                    }
                    
                    response = requests.get(invoice_url, headers=books_headers, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        if 'invoices' in data and data['invoices']:
                            total_invoice = 0
                            for i, invoice in enumerate(data['invoices'], 1):
                                amount = invoice.get('total', 0)
                                total_invoice += amount
                                
                                print(f"{i:2}. 請求書#{invoice.get('invoice_number', 'N/A')}")
                                print(f"    顧客: {invoice.get('customer_name', 'N/A')}")
                                print(f"    金額: ¥{amount:,.0f}")
                                print(f"    ステータス: {invoice.get('status', 'N/A')}")
                                print(f"    日付: {invoice.get('date', 'N/A')}")
                            
                            print(f"\n請求書合計金額: ¥{total_invoice:,.0f}")
                        else:
                            print("請求書データがありません")
                    else:
                        print(f"請求書取得エラー: {response.status_code}")
                        if response.text:
                            print(f"詳細: {response.text[:200]}")
        else:
            print(f"組織取得エラー: {response.status_code}")
    except Exception as e:
        print(f"Books接続エラー: {str(e)}")
    
    print("\n" + "="*60)
    print("チェック完了")

if __name__ == "__main__":
    quick_check()