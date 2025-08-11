#!/usr/bin/env python3
"""
ZohoCRMから商談データを効率的に抽出するスクリプト（シンプル版）
"""

import requests
import json
import pandas as pd
from datetime import datetime
import sys

class ZohoCRMSimpleExtractor:
    def __init__(self, token_file_path):
        self.token_file_path = token_file_path
        self.access_token = None
        self.api_domain = "https://www.zohoapis.com"
        self.load_tokens()
        
    def load_tokens(self):
        try:
            with open(self.token_file_path, 'r', encoding='utf-8') as f:
                tokens = json.load(f)
                self.access_token = tokens['access_token']
                self.api_domain = tokens.get('api_domain', self.api_domain)
                print(f"トークンを読み込みました")
        except Exception as e:
            print(f"トークンファイルの読み込みエラー: {e}")
            sys.exit(1)
    
    def get_headers(self):
        return {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_recent_deals(self, limit=50):
        """最近の商談データを取得"""
        url = f"{self.api_domain}/crm/v2/Deals"
        headers = self.get_headers()
        
        params = {
            'criteria': '(Close_Date:greater_equal:2025-04-01)',
            'per_page': limit,
            'page': 1,
            'fields': 'Id,Deal_Name,Account_Name,Contact_Name,Close_Date,Amount,Stage,Owner,Created_Time,Modified_Time',
            'sort_by': 'Close_Date',
            'sort_order': 'desc'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and data['data']:
                print(f"商談データ取得: {len(data['data'])}件")
                return data['data']
            else:
                print("商談データが見つかりませんでした")
                return []
                
        except Exception as e:
            print(f"商談データ取得エラー: {e}")
            return []
    
    def get_sample_deal_products(self, limit=20):
        """サンプルのDeal_Productsデータを取得"""
        url = f"{self.api_domain}/crm/v2/Deal_Products"
        headers = self.get_headers()
        
        params = {
            'per_page': limit,
            'page': 1,
            'sort_by': 'Created_Time',
            'sort_order': 'desc'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and data['data']:
                print(f"Deal_Products取得: {len(data['data'])}件")
                return data['data']
            else:
                print("Deal_Productsが見つかりませんでした")
                return []
                
        except Exception as e:
            print(f"Deal_Products取得エラー: {e}")
            return []
    
    def extract_name(self, name_obj):
        if isinstance(name_obj, dict):
            return name_obj.get('name', '')
        return str(name_obj) if name_obj else ''
    
    def process_deals(self, deals):
        """商談データを処理"""
        processed = []
        
        for deal in deals:
            record = {
                '商談ID': deal.get('Id', ''),
                '商談名': deal.get('Deal_Name', ''),
                '取引先名': self.extract_name(deal.get('Account_Name', '')),
                '商談担当者': self.extract_name(deal.get('Owner', '')),
                '連絡先': self.extract_name(deal.get('Contact_Name', '')),
                '完了予定日': deal.get('Close_Date', ''),
                '商談金額': deal.get('Amount', 0),
                '商談ステージ': deal.get('Stage', ''),
                '作成日時': deal.get('Created_Time', ''),
                '更新日時': deal.get('Modified_Time', '')
            }
            processed.append(record)
        
        return processed
    
    def save_to_files(self, data, filename_base):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        csv_file = f"../データ/{filename_base}_{timestamp}.csv"
        json_file = f"../データ/{filename_base}_{timestamp}.json"
        
        try:
            if data:
                # CSV出力
                df = pd.DataFrame(data)
                df.to_csv(csv_file, index=False, encoding='utf-8-sig')
                print(f"CSV保存: {csv_file}")
                
                # JSON出力
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"JSON保存: {json_file}")
                
                return csv_file, json_file
            else:
                print("保存するデータがありません")
                return None, None
                
        except Exception as e:
            print(f"ファイル保存エラー: {e}")
            return None, None

def main():
    print("=== ZohoCRM データ抽出（シンプル版） ===")
    
    token_file = "/Users/ks1-utakashio/Desktop/CursorProjects/20250726_ZohoAnalytics/01_Zoho_API/認証・トークン/zoho_crm_tokens.json"
    extractor = ZohoCRMSimpleExtractor(token_file)
    
    # 1. 商談データ取得
    print("\n1. 商談データを取得中...")
    deals = extractor.get_recent_deals(limit=100)
    
    if deals:
        processed_deals = extractor.process_deals(deals)
        csv_file, json_file = extractor.save_to_files(processed_deals, "今期商談リスト")
        
        print(f"\n=== 商談データ抽出完了 ===")
        print(f"抽出件数: {len(processed_deals)}件")
        
        # サマリー表示
        stages = {}
        for deal in processed_deals:
            stage = deal['商談ステージ']
            stages[stage] = stages.get(stage, 0) + 1
        
        print("\n商談ステージ別分布:")
        for stage, count in sorted(stages.items()):
            print(f"  {stage}: {count}件")
    
    # 2. Deal_Productsサンプル取得
    print("\n2. Deal_Productsサンプルを取得中...")
    products = extractor.get_sample_deal_products(limit=20)
    
    if products:
        print(f"\nDeal_Productsサンプル（最初の3件のフィールド構造）:")
        for i, product in enumerate(products[:3], 1):
            print(f"\n--- サンプル {i} ---")
            important_fields = ['id', 'Name', 'Deal', 'Unit_Price', 'Subtotal', 'Purchase_Price', 'Type', 'Created_Time']
            for field in important_fields:
                if field in product:
                    print(f"  {field}: {product[field]}")

if __name__ == "__main__":
    main()