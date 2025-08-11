#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
今期（2025/4/1以降）の商談と商品内訳リスト取得
商談の完了予定日が2025年4月1日以降のものを抽出
"""

import sys
import os
import pandas as pd
from datetime import datetime
import json
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '../../01_Zoho_API/APIクライアント/'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../01_Zoho_API/認証・トークン/'))

from zoho_analytics_helper import ZohoAnalyticsHelper
from token_manager import ZohoTokenManager

def get_current_period_deals():
    """今期（2025/4/1以降）の商談と商品内訳を取得"""
    
    # CRMワークスペースのID
    crm_workspace_id = '2527115000001040002'

    # トークンマネージャー初期化（正しいパスを指定）
    config_path = os.path.join(os.path.dirname(__file__), '../../01_Zoho_API/設定ファイル/zoho_config.json')
    token_path = os.path.join(os.path.dirname(__file__), '../../01_Zoho_API/設定ファイル/zoho_tokens.json')
    
    # 現在のディレクトリを変更してトークンマネージャーを初期化
    original_dir = os.getcwd()
    os.chdir(os.path.dirname(config_path))
    
    try:
        token_manager = ZohoTokenManager()
        helper = ZohoAnalyticsHelper(token_manager)
    finally:
        os.chdir(original_dir)

    try:
        print('=== 今期（2025/4/1以降）の商談と商品内訳リスト取得 ===\n')
        
        # 今期の商談と商品内訳を取得するSQLクエリ
        sql_query = '''
        SELECT 
            `商談`.`Id` as deal_id,
            `商談`.`商談名` as deal_name,
            `商談`.`取引先名` as account_name,
            `商談`.`完了予定日` as close_date,
            `商談`.`連絡先名` as contact_name,
            `商談`.`レイアウト` as layout_type,
            `商談`.`種類` as deal_type,
            `商談`.`商談の担当者` as deal_owner,
            `商談`.`ステージ` as stage,
            `商談`.`総額` as amount,
            `商談`.`売上の期待値` as expected_revenue,
            `商談`.`関連キャンペーン` as campaign,
            `商品内訳`.`Id` as product_detail_id,
            `商品内訳`.`商品名` as product_name,
            `商品内訳`.`学習開始日（商品内訳）` as study_start_date,
            `商品内訳`.`学習終了日（商品内訳）` as study_end_date,
            `商品内訳`.`ベンダー` as vendor,
            `商品内訳`.`数量` as quantity,
            `商品内訳`.`単価` as unit_price,
            `商品内訳`.`小計` as subtotal,
            `商品内訳`.`原価（税別）` as cost
        FROM `商談` 
        LEFT JOIN `商品内訳` ON `商談`.`Id` = `商品内訳`.`親データID`
        WHERE `商談`.`完了予定日` >= '2025-04-01'
        ORDER BY `商談`.`完了予定日`, `商談`.`Id`, `商品内訳`.`Id`
        '''
        
        print('実行するSQL:')
        print(sql_query)
        print()
        
        result = helper.execute_sql(crm_workspace_id, sql_query)
        
        if result and 'data' in result and isinstance(result['data'], list):
            data = result['data']
            print(f'=== 取得データ件数: {len(data)}件 ===\n')
            
            if len(data) > 0:
                # データをDataFrameに変換
                df = pd.DataFrame(data)
                
                # 商談数と商品内訳数を集計
                unique_deals = df['deal_id'].nunique()
                unique_products = df['product_detail_id'].dropna().nunique()
                
                print(f'=== 集計結果 ===')
                print(f'商談数: {unique_deals}件')
                print(f'商品内訳数: {unique_products}件')
                print(f'総レコード数: {len(data)}件')
                print()
                
                # 商談別にグループ化して表示
                deal_count = 0
                current_deal_id = None
                
                for i, row in enumerate(data, 1):
                    # 新しい商談の場合
                    if row.get('deal_id') != current_deal_id:
                        current_deal_id = row.get('deal_id')
                        deal_count += 1
                        print(f'【商談 {deal_count}】' + '='*50)
                        print(f'データID       : {row.get("deal_id")}')
                        print(f'商談名         : {row.get("deal_name")}')
                        print(f'取引先名       : {row.get("account_name")}')
                        print(f'完了予定日     : {row.get("close_date")}')
                        print(f'連絡先名       : {row.get("contact_name")}')
                        print(f'レイアウト     : {row.get("layout_type")}')
                        print(f'種類           : {row.get("deal_type")}')
                        print(f'商談の担当者   : {row.get("deal_owner")}')
                        print(f'ステージ       : {row.get("stage")}')
                        print(f'総額           : {row.get("amount")}')
                        print(f'売上の期待値   : {row.get("expected_revenue")}')
                        print(f'関連キャンペーン: {row.get("campaign")}')
                    
                    # 商品内訳情報
                    if row.get('product_detail_id'):
                        print(f'\n  【商品内訳】')
                        print(f'  ★ 商品内訳ID       : {row.get("product_detail_id")}')
                        print(f'    商品名           : {row.get("product_name")}')
                        print(f'    学習開始日       : {row.get("study_start_date")}')
                        print(f'    学習終了日       : {row.get("study_end_date")}')
                        print(f'    仕入先           : {row.get("vendor")}')
                        print(f'    数量             : {row.get("quantity")}')
                        print(f'    単価             : {row.get("unit_price")}')
                        print(f'    小計             : {row.get("subtotal")}')
                        print(f'    原価（税別）     : {row.get("cost")}')
                
                # CSVファイルとして保存
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                csv_filename = f'../データ/今期商談商品内訳_{timestamp}.csv'
                df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
                print(f'\n=== データ保存 ===')
                print(f'CSVファイル: {csv_filename}')
                
                # Excelファイルとしても保存
                excel_filename = f'../データ/今期商談商品内訳_{timestamp}.xlsx'
                df.to_excel(excel_filename, index=False, engine='openpyxl')
                print(f'Excelファイル: {excel_filename}')
                
                # JSONファイルとしても保存
                json_filename = f'../データ/今期商談商品内訳_{timestamp}.json'
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f'JSONファイル: {json_filename}')
                
                return {
                    'success': True,
                    'deal_count': unique_deals,
                    'product_count': unique_products,
                    'total_records': len(data),
                    'csv_file': csv_filename,
                    'excel_file': excel_filename,
                    'json_file': json_filename
                }
            else:
                print('今期（2025/4/1以降）の商談データが見つかりませんでした')
                return {'success': False, 'message': 'データが見つかりません'}
        else:
            print('データの取得に失敗しました')
            print(f'結果: {result}')
            return {'success': False, 'message': 'データ取得失敗'}
            
    except Exception as e:
        print(f'エラーが発生しました: {e}')
        return {'success': False, 'error': str(e)}

def main():
    """メイン実行関数"""
    print('今期（2025/4/1以降）の商談と商品内訳リスト取得を開始します...\n')
    
    result = get_current_period_deals()
    
    if result.get('success'):
        print(f'\n✅ 処理が完了しました')
        print(f'商談数: {result["deal_count"]}件')
        print(f'商品内訳数: {result["product_count"]}件')
        print(f'総レコード数: {result["total_records"]}件')
    else:
        print(f'\n❌ 処理に失敗しました')
        if 'message' in result:
            print(f'エラー: {result["message"]}')
        if 'error' in result:
            print(f'エラー: {result["error"]}')

if __name__ == "__main__":
    main() 