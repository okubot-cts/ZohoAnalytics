#!/usr/bin/env python3
"""
ZohoCRMから商談と商品内訳を紐づけたデータを抽出するスクリプト

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
    
    def get_deals(self, close_date_from="2025-04-01", max_records=5000):
        """
        商談データを取得（完了予定日でフィルタ）
        """
        url = f"{self.api_domain}/crm/v2/Deals"
        headers = self.get_headers()
        
        # クエリパラメータで日付フィルタを設定
        params = {
            'criteria': f'(Close_Date:greater_equal:{close_date_from})',
            'per_page': 200,
            'page': 1,
            'fields': 'Id,Deal_Name,Account_Name,Contact_Name,Close_Date,Amount,Stage,Owner',
            'sort_by': 'Close_Date',
            'sort_order': 'desc'
        }
        
        all_deals = []
        
        try:
            while len(all_deals) < max_records:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if 'data' not in data or not data['data']:
                    break
                    
                deals = data['data']
                all_deals.extend(deals)
                print(f"商談データ取得: {len(deals)}件 (累計: {len(all_deals)}件)")
                
                # 最大件数に達したら終了
                if len(all_deals) >= max_records:
                    all_deals = all_deals[:max_records]
                    print(f"最大件数({max_records}件)に達したため取得を終了します")
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
    
    def get_deals_by_ids(self, deal_ids, close_date_from="2025-04-01"):
        """
        指定した商談IDリストから商談データを取得（完了予定日でフィルタ）
        """
        if not deal_ids:
            return []
            
        url = f"{self.api_domain}/crm/v2/Deals"
        headers = self.get_headers()
        
        # Deal IDsの条件を作成
        id_criteria = ' or '.join([f'(Id:equals:{deal_id})' for deal_id in deal_ids])
        
        # 日付とIDの複合条件
        criteria = f'(Close_Date:greater_equal:{close_date_from}) and ({id_criteria})'
        
        params = {
            'criteria': criteria,
            'per_page': 200,
            'page': 1,
            'fields': 'Id,Deal_Name,Account_Name,Contact_Name,Close_Date,Amount,Stage,Owner'
        }
        
        all_deals = []
        
        try:
            while True:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if 'data' not in data or not data['data']:
                    break
                    
                deals = data['data']
                all_deals.extend(deals)
                
                # 次のページがあるかチェック
                info = data.get('info', {})
                if not info.get('more_records', False):
                    break
                    
                params['page'] += 1
                
        except Exception as e:
            print(f"商談データ取得エラー（ID指定）: {e}")
            return []
            
        return all_deals
    
    def get_product_line_items_fields(self):
        """
        Product_Line_Itemsのフィールド情報を取得
        """
        url = f"{self.api_domain}/crm/v2/settings/fields?module=Product_Line_Items"
        headers = self.get_headers()
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data
        except Exception as e:
            print(f"フィールド情報取得エラー: {e}")
            return None
    
    def get_product_line_items(self, deal_ids=None, limit=1000):
        """
        商品内訳データを取得（後でPythonでフィルタリング）
        """
        url = f"{self.api_domain}/crm/v2/Product_Line_Items"
        headers = self.get_headers()
        
        params = {
            'per_page': 200,
            'page': 1
        }
        
        # 特定の商談IDに絞り込む場合
        if deal_ids:
            deal_id_criteria = ' or '.join([f'(Deal:equals:{deal_id})' for deal_id in deal_ids[:50]])  # APIの制限を考慮
            params['criteria'] = f'({deal_id_criteria})'
        
        all_products = []
        
        try:
            while len(all_products) < limit:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if 'data' not in data or not data['data']:
                    break
                    
                products = data['data']
                all_products.extend(products)
                print(f"商品内訳データ取得: {len(products)}件 (累計: {len(all_products)}件)")
                
                # 制限件数に達したら終了
                if len(all_products) >= limit:
                    all_products = all_products[:limit]
                    print(f"制限件数({limit}件)に達したため取得を終了します")
                    break
                
                # 次のページがあるかチェック
                info = data.get('info', {})
                if not info.get('more_records', False):
                    break
                    
                params['page'] += 1
                
        except Exception as e:
            print(f"商品内訳データ取得エラー: {e}")
            return []
        
        # Pythonで原価関連のフィールドが0のものをフィルタ
        filtered_products = []
        for product in all_products:
            # 原価関連のフィールドをチェック
            cost_fields = ['Cost_Total', 'Cost_Price', 'cost_total', 'cost_price']
            is_zero_cost = False
            
            for field in cost_fields:
                if field in product:
                    cost_value = product[field]
                    if cost_value == 0 or cost_value == '0' or cost_value == 0.0:
                        is_zero_cost = True
                        break
            
            if is_zero_cost:
                filtered_products.append(product)
        
        print(f"原価ゼロでフィルタ後: {len(filtered_products)}件")
        return filtered_products
    
    def merge_data(self, deals, product_line_items):
        """
        商談と商品内訳データを紐づけ
        """
        # 商談データを辞書化（IDをキーとする）
        deals_dict = {deal['Id']: deal for deal in deals}
        
        merged_data = []
        
        for product in product_line_items:
            deal_id = product.get('Deal', {}).get('id') if isinstance(product.get('Deal'), dict) else product.get('Deal')
            
            if not deal_id or deal_id not in deals_dict:
                continue
                
            deal = deals_dict[deal_id]
            
            # データを結合
            merged_record = {
                # 商談情報
                '商談ID': deal.get('Id', ''),
                '商談名': deal.get('Deal_Name', ''),
                '取引先名': deal.get('Account_Name', {}).get('name', '') if isinstance(deal.get('Account_Name'), dict) else deal.get('Account_Name', ''),
                '商談担当者': deal.get('Owner', {}).get('name', '') if isinstance(deal.get('Owner'), dict) else deal.get('Owner', ''),
                '完了予定日': deal.get('Close_Date', ''),
                '商談金額': deal.get('Amount', 0),
                '商談ステージ': deal.get('Stage', ''),
                
                # 商品内訳情報
                '商品内訳ID': product.get('Id', ''),
                '商品名': product.get('Product_Name', ''),
                '単価': product.get('Unit_Price', 0),
                '数量': product.get('Quantity', 0),
                '小計': product.get('Total', 0),
                '原価': product.get('Cost_Price', 0),
                '原価計': product.get('Cost_Total', 0),
                '税額': product.get('Line_Tax', 0)
            }
            
            merged_data.append(merged_record)
        
        return merged_data
    
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
    print("=== ZohoCRM 商談・商品内訳データ抽出開始 ===")
    
    # トークンファイルのパス
    token_file = "/Users/ks1-utakashio/Desktop/CursorProjects/20250726_ZohoAnalytics/01_Zoho_API/認証・トークン/zoho_crm_tokens.json"
    
    # データ抽出クラスのインスタンス化
    extractor = ZohoCRMDataExtractor(token_file)
    
    # 0. フィールド情報の取得（デバッグ用）
    print("\n0. Product_Line_Itemsフィールド情報を取得中...")
    fields_info = extractor.get_product_line_items_fields()
    if fields_info:
        print("利用可能なフィールド:")
        for field in fields_info.get('fields', [])[:10]:  # 最初の10個だけ表示
            print(f"  - {field.get('api_name', 'N/A')}: {field.get('display_label', 'N/A')}")
    
    # 1. まず商品内訳データ取得（原価小計=0）
    print("\n1. 商品内訳データを取得中...")
    product_line_items = extractor.get_product_line_items(limit=500)  # まず500件で試す
    print(f"取得した商品内訳数: {len(product_line_items)}件")
    
    if not product_line_items:
        print("条件に合致する商品内訳データが見つかりませんでした")
        return
    
    # 2. 商品内訳から商談IDを抽出
    deal_ids_from_products = set()
    for product in product_line_items:
        deal_id = product.get('Deal', {}).get('id') if isinstance(product.get('Deal'), dict) else product.get('Deal')
        if deal_id:
            deal_ids_from_products.add(deal_id)
    
    print(f"関連する商談ID数: {len(deal_ids_from_products)}件")
    
    # 3. 該当する商談データを取得（完了予定日2025/4/1以降でフィルタ）
    print("\n2. 関連する商談データを取得中...")
    deal_ids_list = list(deal_ids_from_products)
    deals = []
    
    # 商談IDを分割して取得（API制限対応）
    batch_size = 100
    for i in range(0, len(deal_ids_list), batch_size):
        batch_ids = deal_ids_list[i:i+batch_size]
        batch_deals = extractor.get_deals_by_ids(batch_ids, close_date_from="2025-04-01")
        deals.extend(batch_deals)
        print(f"商談データ取得: {len(batch_deals)}件 (累計: {len(deals)}件)")
    
    print(f"条件に合致する商談数: {len(deals)}件")
    
    if not deals:
        print("条件に合致する商談データが見つかりませんでした")
        return
    
    # 4. データを紐づけ
    print("\n3. データを紐づけ中...")
    merged_data = extractor.merge_data(deals, product_line_items)
    print(f"紐づけ完了: {len(merged_data)}件")
    
    # 5. ファイル出力
    print("\n4. ファイルに保存中...")
    base_filename = "../データ/商談商品内訳_原価ゼロ"
    csv_file, json_file, excel_file = extractor.save_to_files(merged_data, base_filename)
    
    print("\n=== 処理完了 ===")
    print(f"抽出件数: {len(merged_data)}件")
    
    if csv_file:
        print(f"出力ファイル:")
        print(f"  - CSV: {csv_file}")
        print(f"  - JSON: {json_file}")  
        print(f"  - Excel: {excel_file}")

if __name__ == "__main__":
    main()