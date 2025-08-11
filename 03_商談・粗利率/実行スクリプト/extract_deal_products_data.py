#!/usr/bin/env python3
"""
ZohoCRMから商談と商品データを抽出するスクリプト（利用可能フィールドベース）

要件調整:
- Deal_Productsの利用可能フィールドを使用
- 商談の完了予定日が2025/4/1以降
- 必要項目: 商談名、取引先名、商談担当者、商品名、単価、数量等の利用可能項目
- ID情報: 商談ID、Deal_ProductsID
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
    
    def get_recent_deal_products(self, limit=1000):
        """
        Deal_Productsから最近の商品データを取得
        """
        url = f"{self.api_domain}/crm/v2/Deal_Products"
        headers = self.get_headers()
        
        params = {
            'per_page': 200,
            'page': 1,
            'sort_by': 'Created_Time',
            'sort_order': 'desc'
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
    
    def merge_and_process_data(self, deals, products):
        """
        商談と商品データを紐づけて処理
        """
        # 商談データを辞書化（IDをキーとする）
        deals_dict = {deal['Id']: deal for deal in deals}
        
        merged_data = []
        
        for product in products:
            # Deal IDを取得
            deal_ref = product.get('Deal', {})
            deal_id = deal_ref.get('id') if isinstance(deal_ref, dict) else None
            
            if not deal_id or deal_id not in deals_dict:
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
                
                # Deal_Products情報
                'Deal_ProductsID': product.get('id', ''),
                '商品名': product.get('Name', ''),
                '単価': product.get('Unit_Price', 0),
                '数量': product.get('Number', 0),
                '小計': product.get('Subtotal', 0),
                '購入価格': product.get('Purchase_Price', 0),
                '購入価格金額': product.get('Purchase_Price_Amount', 0),
                '通貨': product.get('Currency', ''),
                'タイプ': product.get('Type', ''),
                
                # その他の情報
                '担当者': self.extract_name(product.get('Owner', '')),
                '取引先': self.extract_name(product.get('Account', '')),
                '連絡先': self.extract_name(product.get('Contact', '')),
                '作成日時': product.get('Created_Time', ''),
                '更新日時': product.get('Modified_Time', ''),
                
                # カスタムフィールド（必要に応じて）
                'Email': product.get('Email', ''),
                '開始日': product.get('field1', ''),
                '終了日': product.get('field2', ''),
                '期間': product.get('field98', ''),
                '状況': product.get('field', ''),
                '承認状態': product.get('$approval_state', '')
            }
            
            merged_data.append(merged_record)
        
        return merged_data
    
    def extract_name(self, name_obj):
        """名前オブジェクトから名前を抽出"""
        if isinstance(name_obj, dict):
            return name_obj.get('name', '')
        return str(name_obj) if name_obj else ''
    
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
    print("=== ZohoCRM 商談・商品データ抽出（利用可能フィールドベース） ===")
    
    # トークンファイルのパス
    token_file = "/Users/ks1-utakashio/Desktop/CursorProjects/20250726_ZohoAnalytics/01_Zoho_API/認証・トークン/zoho_crm_tokens.json"
    
    # データ抽出クラスのインスタンス化
    extractor = ZohoCRMDataExtractor(token_file)
    
    # 1. Deal_Productsから最近の商品データを取得
    print("\n1. Deal_Products（最近のデータ）を取得中...")
    deal_products = extractor.get_recent_deal_products(limit=200)  # 制限を200件に
    print(f"取得したDeal_Products数: {len(deal_products)}件")
    
    if not deal_products:
        print("Deal_Productsデータが見つかりませんでした")
        return
    
    # 2. 関連する商談IDを抽出
    deal_ids_from_products = set()
    for product in deal_products:
        deal_ref = product.get('Deal', {})
        deal_id = deal_ref.get('id') if isinstance(deal_ref, dict) else None
        if deal_id:
            deal_ids_from_products.add(deal_id)
    
    print(f"関連する商談ID数: {len(deal_ids_from_products)}件")
    
    # 3. 関連する商談データを取得（完了予定日2025/4/1以降でフィルタ）
    print("\n2. 関連する商談データを取得中...")
    deal_ids_list = list(deal_ids_from_products)
    deals = extractor.get_deals_by_ids(deal_ids_list, close_date_from="2025-04-01")
    
    if not deals:
        print("条件に合致する商談データが見つかりませんでした")
        # 条件を緩和して再試行
        print("条件を緩和して全期間で再試行...")
        deals = extractor.get_deals_by_ids(deal_ids_list, close_date_from="2024-01-01")
        if not deals:
            print("商談データが見つかりませんでした")
            return
        print(f"取得した商談数（全期間）: {len(deals)}件")
    
    # 4. データを紐づけて処理
    print("\n3. データを紐づけ・処理中...")
    merged_data = extractor.merge_and_process_data(deals, deal_products)
    print(f"紐づけ完了: {len(merged_data)}件")
    
    # 5. ファイル出力
    print("\n4. ファイルに保存中...")
    base_filename = "../データ/商談商品データ_利用可能フィールド"
    csv_file, json_file, excel_file = extractor.save_to_files(merged_data, base_filename)
    
    # 6. サマリー表示
    print("\n=== 処理完了 ===")
    print(f"抽出件数: {len(merged_data)}件")
    
    if merged_data:
        # 日付範囲を確認
        close_dates = [record['完了予定日'] for record in merged_data if record['完了予定日']]
        if close_dates:
            close_dates_sorted = sorted(close_dates)
            print(f"完了予定日範囲: {close_dates_sorted[0]} ～ {close_dates_sorted[-1]}")
        
        # 商談ステージの分布
        stages = {}
        for record in merged_data:
            stage = record['商談ステージ']
            stages[stage] = stages.get(stage, 0) + 1
        
        print("商談ステージ別分布:")
        for stage, count in sorted(stages.items()):
            print(f"  {stage}: {count}件")
    
    if csv_file:
        print(f"\n出力ファイル:")
        print(f"  - CSV: {csv_file}")
        print(f"  - JSON: {json_file}")  
        print(f"  - Excel: {excel_file}")

if __name__ == "__main__":
    main()