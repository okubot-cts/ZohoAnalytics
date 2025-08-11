#!/usr/bin/env python3
"""
ZohoCRMから商談と商品内訳を紐づけたデータを抽出するスクリプト（代替アプローチ）

要件:
- 商品内訳の原価小計がゼロ
- 商談の完了予定日が2025/4/1以降
- 必要項目: 商談名、取引先名、商談担当者、商品名、単価、数量、原価、小計、原価計
- ID情報: 商談ID、商品内訳ID
"""

import requests
import json
import csv
import pandas as pd
from datetime import datetime
import os
import sys

class ZohoCRMDataExtractor:
    def __init__(self, token_file_path):
        """初期化"""
        self.token_file_path = token_file_path
        self.access_token = None
        self.api_domain = "https://www.zohoapis.com"
        self.load_tokens()
        
    def load_tokens(self):
        """トークンファイルからアクセストークンを読み込み"""
        try:
            with open(self.token_file_path, 'r', encoding='utf-8') as f:
                tokens = json.load(f)
                self.access_token = tokens['access_token']
                self.api_domain = tokens.get('api_domain', self.api_domain)
                print(f"トークンを読み込みました: {self.token_file_path}")
        except Exception as e:
            print(f"トークンファイルの読み込みエラー: {e}")
            sys.exit(1)
    
    def get_headers(self):
        """API呼び出し用のヘッダーを取得"""
        return {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_available_modules(self):
        """利用可能なモジュール一覧を取得"""
        url = f"{self.api_domain}/crm/v2/settings/modules"
        headers = self.get_headers()
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data
        except Exception as e:
            print(f"モジュール情報取得エラー: {e}")
            return None
    
    def get_deals_with_products(self, close_date_from="2025-04-01", limit=1000):
        """
        商談データを取得し、商品情報も含める
        """
        url = f"{self.api_domain}/crm/v2/Deals"
        headers = self.get_headers()
        
        params = {
            'criteria': f'(Close_Date:greater_equal:{close_date_from})',
            'per_page': 200,
            'page': 1,
            'fields': 'Id,Deal_Name,Account_Name,Contact_Name,Close_Date,Amount,Stage,Owner,Product_Details'
        }
        
        all_deals = []
        
        try:
            while len(all_deals) < limit:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if 'data' not in data or not data['data']:
                    break
                    
                deals = data['data']
                all_deals.extend(deals)
                print(f"商談データ取得: {len(deals)}件 (累計: {len(all_deals)}件)")
                
                # 制限件数に達したら終了
                if len(all_deals) >= limit:
                    all_deals = all_deals[:limit]
                    print(f"制限件数({limit}件)に達したため取得を終了します")
                    break
                
                # 次のページがあるかチェック
                info = data.get('info', {})
                if not info.get('more_records', False):
                    break
                    
                params['page'] += 1
                
        except Exception as e:
            print(f"商談データ取得エラー: {e}")
            return []
            
        return all_deals
    
    def get_deal_related_data(self, deal_id):
        """
        特定の商談の関連データを取得
        """
        url = f"{self.api_domain}/crm/v2/Deals/{deal_id}"
        headers = self.get_headers()
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get('data', [{}])[0] if data.get('data') else {}
        except Exception as e:
            print(f"商談詳細取得エラー (ID: {deal_id}): {e}")
            return {}
    
    def extract_product_details(self, deals):
        """
        商談から商品詳細情報を抽出し、原価ゼロのものをフィルタ
        """
        extracted_data = []
        
        for deal in deals:
            deal_id = deal.get('Id', '')
            deal_name = deal.get('Deal_Name', '')
            account_name = deal.get('Account_Name', {}).get('name', '') if isinstance(deal.get('Account_Name'), dict) else deal.get('Account_Name', '')
            owner = deal.get('Owner', {}).get('name', '') if isinstance(deal.get('Owner'), dict) else deal.get('Owner', '')
            close_date = deal.get('Close_Date', '')
            deal_amount = deal.get('Amount', 0)
            stage = deal.get('Stage', '')
            
            # 商品詳細があるかチェック
            product_details = deal.get('Product_Details', [])
            
            if not product_details:
                # Product_Detailsが空の場合、個別に詳細データを取得
                detailed_deal = self.get_deal_related_data(deal_id)
                product_details = detailed_deal.get('Product_Details', [])
            
            if product_details:
                for product in product_details:
                    # 原価関連フィールドをチェック
                    cost_price = product.get('Cost_Price', 0)
                    cost_total = product.get('Cost_Total', 0)
                    
                    # 原価がゼロかチェック
                    if (cost_price == 0 or cost_price == '0' or cost_price == 0.0) or \
                       (cost_total == 0 or cost_total == '0' or cost_total == 0.0):
                        
                        record = {
                            '商談ID': deal_id,
                            '商談名': deal_name,
                            '取引先名': account_name,
                            '商談担当者': owner,
                            '完了予定日': close_date,
                            '商談金額': deal_amount,
                            '商談ステージ': stage,
                            '商品内訳ID': product.get('id', ''),
                            '商品名': product.get('product', {}).get('name', '') if isinstance(product.get('product'), dict) else product.get('Product_Name', ''),
                            '単価': product.get('Unit_Price', 0),
                            '数量': product.get('Quantity', 0),
                            '小計': product.get('Total', 0),
                            '原価': cost_price,
                            '原価計': cost_total,
                            '税額': product.get('Line_Tax', 0)
                        }
                        extracted_data.append(record)
            else:
                # 商品詳細がない場合も記録（デバッグ用）
                print(f"商品詳細なし: {deal_name} (ID: {deal_id})")
        
        return extracted_data
    
    def save_to_files(self, data, base_filename):
        """
        データをCSVとJSONファイルに保存
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # CSV出力
        csv_filename = f"{base_filename}_{timestamp}.csv"
        json_filename = f"{base_filename}_{timestamp}.json"
        excel_filename = f"{base_filename}_{timestamp}.xlsx"
        
        try:
            # CSV出力
            if data:
                df = pd.DataFrame(data)
                df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
                print(f"CSVファイルに保存: {csv_filename}")
                
                # JSON出力
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"JSONファイルに保存: {json_filename}")
                
                # Excel出力
                df.to_excel(excel_filename, index=False)
                print(f"Excelファイルに保存: {excel_filename}")
                
                return csv_filename, json_filename, excel_filename
            else:
                print("保存するデータがありません")
                return None, None, None
                
        except Exception as e:
            print(f"ファイル保存エラー: {e}")
            return None, None, None

def main():
    """メイン処理"""
    print("=== ZohoCRM 商談・商品内訳データ抽出開始（代替アプローチ） ===")
    
    # トークンファイルのパス
    token_file = "/Users/ks1-utakashio/Desktop/CursorProjects/20250726_ZohoAnalytics/01_Zoho_API/認証・トークン/zoho_crm_tokens.json"
    
    # データ抽出クラスのインスタンス化
    extractor = ZohoCRMDataExtractor(token_file)
    
    # 0. 利用可能なモジュールを確認
    print("\n0. 利用可能なモジュールを確認中...")
    modules = extractor.get_available_modules()
    if modules:
        print("主要モジュール:")
        for module in modules.get('modules', [])[:10]:
            print(f"  - {module.get('api_name', 'N/A')}: {module.get('module_name', 'N/A')}")
    
    # 1. 商談データを取得（商品詳細含む）
    print("\n1. 商談データを取得中（完了予定日2025/4/1以降）...")
    deals = extractor.get_deals_with_products(close_date_from="2025-04-01", limit=100)  # まず100件で試す
    print(f"取得した商談数: {len(deals)}件")
    
    if not deals:
        print("商談データが見つかりませんでした")
        return
    
    # 2. 商品詳細を抽出し、原価ゼロのものをフィルタ
    print("\n2. 商品詳細を抽出・フィルタ中...")
    extracted_data = extractor.extract_product_details(deals)
    print(f"原価ゼロの商品内訳: {len(extracted_data)}件")
    
    if not extracted_data:
        print("原価ゼロの商品内訳が見つかりませんでした")
        # デバッグ用に商談の1つをサンプル表示
        if deals:
            print("\nサンプル商談データ:")
            sample_deal = deals[0]
            print(json.dumps(sample_deal, ensure_ascii=False, indent=2))
        return
    
    # 3. ファイル出力
    print("\n3. ファイルに保存中...")
    base_filename = "../データ/商談商品内訳_原価ゼロ_代替"
    csv_file, json_file, excel_file = extractor.save_to_files(extracted_data, base_filename)
    
    print("\n=== 処理完了 ===")
    print(f"抽出件数: {len(extracted_data)}件")
    
    if csv_file:
        print(f"出力ファイル:")
        print(f"  - CSV: {csv_file}")
        print(f"  - JSON: {json_file}")  
        print(f"  - Excel: {excel_file}")

if __name__ == "__main__":
    main()