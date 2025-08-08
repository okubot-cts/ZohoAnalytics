#!/usr/bin/env python3
"""
2025年1月以降の商談と商品内訳レポート生成
商品内訳IDを含む
"""

from zoho_analytics_helper import ZohoAnalyticsHelper
from token_manager import ZohoTokenManager
import json

def generate_2025_report():
    """2025年1月以降の商談と商品内訳レポートを生成"""
    
    # CRMワークスペースのID
    crm_workspace_id = '2527115000001040002'

    # トークンマネージャー初期化
    token_manager = ZohoTokenManager()
    helper = ZohoAnalyticsHelper(token_manager)

    try:
        print('=== 2025年1月以降の商談と商品内訳レポート（商品内訳ID付き）===\n')
        
        # 英語エイリアスに修正（日本語エイリアスは構文エラーになる）
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
            `商品内訳`.`商品名` as product_name,
            `商品内訳`.`学習開始日（商品内訳）` as study_start_date,
            `商品内訳`.`学習終了日（商品内訳）` as study_end_date,
            `商品内訳`.`ベンダー` as vendor,
            `商品内訳`.`数量` as quantity,
            `商品内訳`.`単価` as unit_price,
            `商品内訳`.`小計` as subtotal,
            `商品内訳`.`原価（税別）` as cost,
            `商品内訳`.`Id` as product_detail_id
        FROM `商談` 
        LEFT JOIN `商品内訳` ON `商談`.`Id` = `商品内訳`.`親データID`
        WHERE `商談`.`完了予定日` >= '2025-01-01'
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
                deal_count = 0
                product_detail_count = 0
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
                        product_detail_count += 1
                        print(f'\n  【商品内訳 {product_detail_count}】')
                        print(f'  ★ 商品内訳ID       : {row.get("product_detail_id")} <- 新規追加項目！')
                        print(f'    商品名           : {row.get("product_name")}')
                        print(f'    学習開始日       : {row.get("study_start_date")}')
                        print(f'    学習終了日       : {row.get("study_end_date")}')
                        print(f'    仕入先           : {row.get("vendor")}')
                        print(f'    数量             : {row.get("quantity")}')
                        print(f'    単価             : {row.get("unit_price")}')
                        print(f'    小計             : {row.get("subtotal")}')
                        print(f'    原価（税別）     : {row.get("cost")}')
                    elif current_deal_id == row.get('deal_id'):
                        print('\n  （この商談には商品内訳がありません）')
                    
                    print()
                
                print('='*60)
                print(f'📊 結果サマリー')
                print(f'  対象期間        : 2025年1月以降')
                print(f'  商談件数        : {deal_count}件')
                print(f'  商品内訳件数    : {product_detail_count}件')
                print(f'  ✅ 商品内訳IDが正常に追加されました！')
                print('='*60)
                
                # ヘッダー（日本語表示）
                display_headers = [
                    "データID", "商談名", "取引先名", "完了予定日", "連絡先名", "レイアウト", "種類",
                    "商談の担当者", "ステージ", "総額", "売上の期待値", "関連キャンペーン", "商品名",
                    "学習開始日（商品内訳）", "学習終了日（商品内訳）", "仕入先", "数量", "単価", "小計",
                    "原価（税別）", "商品内訳ID"
                ]
                # データベースのキー
                db_keys = [
                    "deal_id", "deal_name", "account_name", "close_date", "contact_name", "layout_type", "deal_type",
                    "deal_owner", "stage", "amount", "expected_revenue", "campaign", "product_name",
                    "study_start_date", "study_end_date", "vendor", "quantity", "unit_price", "subtotal",
                    "cost", "product_detail_id"
                ]
                
                # CSVデータを準備
                csv_lines = []
                csv_lines.append(','.join(display_headers))
                
                for row in data:
                    csv_row = []
                    for key in db_keys:
                        value = str(row.get(key, "")).replace(',', '，')  # CSV用カンマ対策
                        csv_row.append(value)
                    csv_lines.append(','.join(csv_row))
                
                # UTF-8版CSVファイル出力
                csv_filename_utf8 = "2025年1月以降_商談_商品内訳_レポート_UTF8.csv"
                with open(csv_filename_utf8, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(csv_lines))
                
                # Shift-JIS版CSVファイル出力
                csv_filename_sjis = "2025年1月以降_商談_商品内訳_レポート_SJIS.csv"
                try:
                    with open(csv_filename_sjis, 'w', encoding='shift_jis', errors='replace') as f:
                        f.write('\n'.join(csv_lines))
                    print(f'📄 UTF-8版CSVファイル: {csv_filename_utf8}')
                    print(f'📄 Shift-JIS版CSVファイル: {csv_filename_sjis}')
                    print('✅ 両方のエンコーディングで出力完了！')
                except UnicodeEncodeError as e:
                    print(f'⚠️ Shift-JIS変換中に文字エラー: {e}')
                    print(f'📄 UTF-8版のみ出力: {csv_filename_utf8}')
                except Exception as e:
                    print(f'❌ Shift-JIS出力エラー: {e}')
                    print(f'📄 UTF-8版のみ出力: {csv_filename_utf8}')
                
            else:
                print('❌ 2025年1月以降の商談データが見つかりませんでした')
                print('   データベース内の商談データを確認してください。')
        else:
            print('❌ データの取得に失敗しました')
            if result:
                print('レスポンス詳細:', json.dumps(result, indent=2, ensure_ascii=False)[:500])
            
    except Exception as e:
        print(f'❌ エラーが発生しました: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_2025_report()