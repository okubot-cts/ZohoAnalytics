#!/usr/bin/env python3
"""
ZohoBooksのサンプルデータ取得スクリプト
各種エンドポイントを試してデータを取得
"""
import requests
import json
from pathlib import Path
from datetime import datetime

def get_books_sample_data():
    """Booksの各種データを取得"""
    
    # トークンファイルの読み込み
    base_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン"
    books_tokens_file = base_path / "zoho_books_tokens.json"
    
    if not books_tokens_file.exists():
        print("❌ Booksトークンファイルが見つかりません")
        return
    
    with open(books_tokens_file, 'r') as f:
        books_tokens = json.load(f)
    
    headers = {'Authorization': f'Bearer {books_tokens["access_token"]}'}
    
    print("="*60)
    print("ZohoBooks サンプルデータ取得")
    print("="*60)
    
    # 複数のAPIドメインを試す
    api_domains = [
        "https://www.zohoapis.com/books/v3",
        "https://books.zoho.com/api/v3",
        "https://www.zohoapis.jp/books/v3",
        "https://books.zoho.jp/api/v3"
    ]
    
    # 組織一覧を取得（正しいドメインを見つける）
    org_id = None
    working_domain = None
    
    print("\n🔍 APIドメインの確認中...")
    for domain in api_domains:
        print(f"\n試行中: {domain}")
        try:
            response = requests.get(f"{domain}/organizations", headers=headers, timeout=5)
            print(f"  ステータス: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'organizations' in data and data['organizations']:
                    working_domain = domain
                    print(f"  ✅ 成功！このドメインを使用します")
                    
                    # 組織情報を表示
                    print("\n📊 組織一覧:")
                    for org in data['organizations']:
                        print(f"  - {org.get('name', 'N/A')}")
                        print(f"    ID: {org.get('organization_id', 'N/A')}")
                        print(f"    通貨: {org.get('currency_code', 'N/A')}")
                        print(f"    プラン: {org.get('plan_name', 'N/A')}")
                        
                        # 株式会社シー・ティー・エスを優先
                        if '株式会社シー・ティー・エス' in org.get('name', ''):
                            org_id = org['organization_id']
                    
                    # org_idが設定されていない場合は最初の組織を使用
                    if not org_id and data['organizations']:
                        org_id = data['organizations'][0]['organization_id']
                    
                    break
            elif response.status_code == 401:
                print(f"  ❌ 認証エラー")
            else:
                print(f"  ❌ エラー: {response.text[:100] if response.text else 'No details'}")
                
        except requests.exceptions.Timeout:
            print(f"  ❌ タイムアウト")
        except Exception as e:
            print(f"  ❌ 接続エラー: {str(e)}")
    
    if not working_domain or not org_id:
        print("\n❌ 有効なAPIドメインが見つかりませんでした")
        return
    
    print(f"\n✅ 使用する組織ID: {org_id}")
    print(f"✅ 使用するAPIドメイン: {working_domain}")
    
    # 各種データを取得
    endpoints = [
        ("請求書", "/invoices"),
        ("顧客", "/contacts"),
        ("商品", "/items"),
        ("見積書", "/estimates"),
        ("販売注文", "/salesorders")
    ]
    
    for data_type, endpoint in endpoints:
        print(f"\n{'='*40}")
        print(f"📄 {data_type}データ（最大5件）:")
        
        url = f"{working_domain}{endpoint}"
        params = {
            'organization_id': org_id,
            'per_page': 5
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # データのキーを動的に取得（invoices, contacts, items など）
                data_key = endpoint[1:]  # /を除去
                
                if data_key in data and data[data_key]:
                    print(f"✅ {len(data[data_key])}件取得")
                    
                    for i, item in enumerate(data[data_key], 1):
                        print(f"\n  {i}. ", end="")
                        
                        # データタイプごとに表示内容を変える
                        if data_key == "invoices":
                            print(f"請求書番号: {item.get('invoice_number', 'N/A')}")
                            print(f"     顧客: {item.get('customer_name', 'N/A')}")
                            print(f"     金額: ¥{item.get('total', 0):,.0f}")
                            print(f"     ステータス: {item.get('status', 'N/A')}")
                            print(f"     日付: {item.get('date', 'N/A')}")
                            
                        elif data_key == "contacts":
                            print(f"顧客名: {item.get('contact_name', 'N/A')}")
                            print(f"     会社名: {item.get('company_name', 'N/A')}")
                            print(f"     メール: {item.get('email', 'N/A')}")
                            print(f"     タイプ: {item.get('contact_type', 'N/A')}")
                            
                        elif data_key == "items":
                            print(f"商品名: {item.get('name', 'N/A')}")
                            print(f"     SKU: {item.get('sku', 'N/A')}")
                            print(f"     単価: ¥{item.get('rate', 0):,.0f}")
                            print(f"     在庫: {item.get('stock_on_hand', 'N/A')}")
                            
                        elif data_key == "estimates":
                            print(f"見積番号: {item.get('estimate_number', 'N/A')}")
                            print(f"     顧客: {item.get('customer_name', 'N/A')}")
                            print(f"     金額: ¥{item.get('total', 0):,.0f}")
                            print(f"     日付: {item.get('date', 'N/A')}")
                            
                        elif data_key == "salesorders":
                            print(f"注文番号: {item.get('salesorder_number', 'N/A')}")
                            print(f"     顧客: {item.get('customer_name', 'N/A')}")
                            print(f"     金額: ¥{item.get('total', 0):,.0f}")
                            print(f"     日付: {item.get('date', 'N/A')}")
                        else:
                            # その他のデータ
                            print(json.dumps(item, indent=2, ensure_ascii=False)[:200])
                else:
                    print(f"  データなし")
                    
            elif response.status_code == 400:
                # モジュールが有効でない可能性
                error_data = response.json() if response.text else {}
                if error_data.get('code') == 1003:
                    print(f"  ⚠️  このモジュールは有効化されていません")
                else:
                    print(f"  ❌ エラー: {error_data.get('message', response.text[:100])}")
            else:
                print(f"  ❌ エラー: {response.status_code}")
                if response.text:
                    print(f"     詳細: {response.text[:200]}")
                    
        except Exception as e:
            print(f"  ❌ 取得エラー: {str(e)}")
    
    # 統計情報を取得
    print(f"\n{'='*40}")
    print("📊 ダッシュボード統計:")
    
    dashboard_url = f"{working_domain}/dashboard"
    params = {'organization_id': org_id}
    
    try:
        response = requests.get(dashboard_url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'dashboard' in data:
                dashboard = data['dashboard']
                print(f"  売上合計: ¥{dashboard.get('total_receivables', 0):,.0f}")
                print(f"  未払い請求: ¥{dashboard.get('total_payables', 0):,.0f}")
                
    except Exception as e:
        print(f"  取得エラー: {str(e)}")
    
    print("\n" + "="*60)
    print("取得完了")

if __name__ == "__main__":
    get_books_sample_data()