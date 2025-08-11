#!/usr/bin/env python3
"""
ZohoCRMから商談と商品内訳を紐づけたデータを抽出するスクリプト（Deal_Productsモジュール使用）

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
    
    def get_deal_products(self, limit=1000):
        """
        Deal_Productsモジュールから商品内訳データを取得
        """
        url = f"{self.api_domain}/crm/v2/Deal_Products"
        headers = self.get_headers()
        
        params = {
            'per_page': 200,
            'page': 1
        }
        
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
                print(f"Deal_Products取得: {len(products)}件 (累計: {len(all_products)}件)")
                
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
            print(f"Deal_Products取得エラー: {e}")
            return []
        
        return all_products
    
    def get_deals_by_ids(self, deal_ids, close_date_from="2025-04-01"):
        """
        指定した商談IDリストから商談データを取得（完了予定日でフィルタ）
        """
        if not deal_ids:
            return []
            
        all_deals = []
        
        # IDを分割して取得（API制限対応）
        batch_size = 50
        for i in range(0, len(deal_ids), batch_size):
            batch_ids = deal_ids[i:i+batch_size]
            
            url = f"{self.api_domain}/crm/v2/Deals"
            headers = self.get_headers()
            
            # Deal IDsの条件を作成
            id_criteria = ' or '.join([f'(Id:equals:{deal_id})' for deal_id in batch_ids])
            
            # 日付とIDの複合条件
            criteria = f'(Close_Date:greater_equal:{close_date_from}) and ({id_criteria})'
            
            params = {
                'criteria': criteria,
                'per_page': 200,
                'page': 1,
                'fields': 'Id,Deal_Name,Account_Name,Contact_Name,Close_Date,Amount,Stage,Owner'
            }
            
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
                continue
        
        print(f"取得した商談数: {len(all_deals)}件")
        return all_deals
    
    def filter_zero_cost_products(self, products):
        """
        原価関連フィールドが0の商品をフィルタ
        """
        filtered_products = []
        
        for product in products:
            # 原価関連のフィールドをチェック（可能性のあるフィールド名）
            cost_fields = ['Cost_Total', 'Cost_Price', 'cost_total', 'cost_price', 
                          'Unit_Cost', 'Line_Cost', 'Total_Cost']
            
            is_zero_cost = False
            cost_values = {}
            
            # すべての原価関連フィールドをチェック
            for field in cost_fields:
                if field in product:
                    cost_value = product[field]
                    cost_values[field] = cost_value
                    if cost_value == 0 or cost_value == '0' or cost_value == 0.0 or cost_value is None:
                        is_zero_cost = True
            
            # デバッグ情報を追加
            product['_cost_fields_found'] = cost_values
            product['_is_zero_cost'] = is_zero_cost
            
            if is_zero_cost:
                filtered_products.append(product)
        
        print(f"原価ゼロでフィルタ後: {len(filtered_products)}件")
        
        # デバッグ：最初の数件のフィールド情報を表示
        if products:
            print("\nサンプル商品データのフィールド:")
            sample = products[0]
            for key, value in sample.items():
                if not key.startswith('_'):
                    print(f"  {key}: {value}")
        
        return filtered_products
    
    def merge_data(self, deals, products):
        """
        商談と商品データを紐づけ
        """
        # 商談データを辞書化（IDをキーとする）
        deals_dict = {deal['Id']: deal for deal in deals}
        
        merged_data = []
        
        for product in products:
            # Deal IDを取得（様々な可能性を試す）
            deal_id = None
            possible_deal_fields = ['Deal', 'Deal_Id', 'deal', 'deal_id', 'Related_Deal', 'Parent_Deal']
            
            for field in possible_deal_fields:
                if field in product:
                    deal_ref = product[field]
                    if isinstance(deal_ref, dict):
                        deal_id = deal_ref.get('id') or deal_ref.get('Id')
                    else:
                        deal_id = deal_ref
                    if deal_id:
                        break
            
            if not deal_id or deal_id not in deals_dict:
                print(f"商談IDが見つからない商品: {product.get('Id', 'N/A')}")
                continue
                
            deal = deals_dict[deal_id]
            
            # データを結合
            merged_record = {
                # 商談情報
                '商談ID': deal.get('Id', ''),
                '商談名': deal.get('Deal_Name', ''),
                '取引先名': self.extract_name(deal.get('Account_Name', '')),
                '商談担当者': self.extract_name(deal.get('Owner', '')),
                '完了予定日': deal.get('Close_Date', ''),
                '商談金額': deal.get('Amount', 0),
                '商談ステージ': deal.get('Stage', ''),
                
                # 商品内訳情報
                '商品内訳ID': product.get('Id', ''),
                '商品名': self.extract_product_name(product),
                '単価': product.get('Unit_Price', 0),
                '数量': product.get('Quantity', 0),
                '小計': product.get('Total', 0),
                '原価': product.get('Cost_Price', 0),
                '原価計': product.get('Cost_Total', 0),
                '税額': product.get('Line_Tax', 0),
                
                # デバッグ情報
                '_原価フィールド': str(product.get('_cost_fields_found', {})),
                '_原価ゼロ判定': product.get('_is_zero_cost', False)
            }
            
            merged_data.append(merged_record)
        
        return merged_data
    
    def extract_name(self, name_obj):
        """名前オブジェクトから名前を抽出"""
        if isinstance(name_obj, dict):
            return name_obj.get('name', '')
        return str(name_obj) if name_obj else ''
    
    def extract_product_name(self, product):
        """商品名を抽出"""
        # 可能性のあるフィールド名
        name_fields = ['Product_Name', 'Name', 'product_name', 'name']
        
        for field in name_fields:
            if field in product:
                name_obj = product[field]
                if isinstance(name_obj, dict):
                    return name_obj.get('name', '')
                return str(name_obj) if name_obj else ''
        
        # Productオブジェクトから名前を取得
        if 'Product' in product:
            product_obj = product['Product']
            if isinstance(product_obj, dict):
                return product_obj.get('name', '')
        
        return ''
    
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
    print("=== ZohoCRM 商談・商品内訳データ抽出開始（Deal_Products使用） ===")
    
    # トークンファイルのパス
    token_file = "/Users/ks1-utakashio/Desktop/CursorProjects/20250726_ZohoAnalytics/01_Zoho_API/認証・トークン/zoho_crm_tokens.json"
    
    # データ抽出クラスのインスタンス化
    extractor = ZohoCRMDataExtractor(token_file)
    
    # 1. Deal_Productsから商品内訳データを取得
    print("\n1. Deal_Products（商品内訳）データを取得中...")
    deal_products = extractor.get_deal_products(limit=500)  # まず500件で試す
    print(f"取得したDeal_Products数: {len(deal_products)}件")
    
    if not deal_products:
        print("Deal_Productsデータが見つかりませんでした")
        return
    
    # 2. 原価ゼロの商品をフィルタ
    print("\n2. 原価ゼロの商品をフィルタ中...")
    zero_cost_products = extractor.filter_zero_cost_products(deal_products)
    
    if not zero_cost_products:
        print("原価ゼロの商品が見つかりませんでした")
        print("\nサンプルDeal_Productデータ:")
        if deal_products:
            print(json.dumps(deal_products[0], ensure_ascii=False, indent=2))
        return
    
    # 3. 関連する商談IDを抽出
    deal_ids_from_products = set()
    for product in zero_cost_products:
        # Deal IDを取得（様々な可能性を試す）
        deal_id = None
        possible_deal_fields = ['Deal', 'Deal_Id', 'deal', 'deal_id', 'Related_Deal', 'Parent_Deal']
        
        for field in possible_deal_fields:
            if field in product:
                deal_ref = product[field]
                if isinstance(deal_ref, dict):
                    deal_id = deal_ref.get('id') or deal_ref.get('Id')
                else:
                    deal_id = deal_ref
                if deal_id:
                    break
        
        if deal_id:
            deal_ids_from_products.add(deal_id)
    
    print(f"関連する商談ID数: {len(deal_ids_from_products)}件")
    
    # 4. 関連する商談データを取得（完了予定日2025/4/1以降でフィルタ）
    print("\n3. 関連する商談データを取得中...")
    deal_ids_list = list(deal_ids_from_products)
    deals = extractor.get_deals_by_ids(deal_ids_list, close_date_from="2025-04-01")
    
    if not deals:
        print("条件に合致する商談データが見つかりませんでした")
        return
    
    # 5. データを紐づけ
    print("\n4. データを紐づけ中...")
    merged_data = extractor.merge_data(deals, zero_cost_products)
    print(f"紐づけ完了: {len(merged_data)}件")
    
    # 6. ファイル出力
    print("\n5. ファイルに保存中...")
    base_filename = "../データ/商談商品内訳_原価ゼロ_最終"
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