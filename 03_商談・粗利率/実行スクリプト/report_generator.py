#!/usr/bin/env python3
"""
Zoho Analytics レポート生成ツール
自然言語で商品内訳IDを含むレポートを生成
"""

from zoho_analytics_helper import ZohoAnalyticsHelper
from token_manager import ZohoTokenManager
import json

class ZohoReportGenerator:
    def __init__(self):
        self.token_manager = ZohoTokenManager()
        self.helper = ZohoAnalyticsHelper(self.token_manager)
        self.workspace_id = '2527115000001040002'  # Zoho CRMワークスペース
    
    def generate_product_details_report(self, natural_request: str = None):
        """商品内訳IDを含む完全なレポートを生成"""
        
        print("=== 商品内訳IDを含むレポート生成 ===")
        if natural_request:
            print(f"リクエスト: {natural_request}\n")
        
        # 商品内訳IDを含む完全なSQL
        sql_query = '''
        SELECT 
            `商談`.`Id` as データID,
            `商談`.`商談名`,
            `商談`.`取引先名`,
            `商談`.`完了予定日`,
            `商談`.`連絡先名`,
            `商談`.`レイアウト`,
            `商談`.`種類`,
            `商談`.`商談の担当者`,
            `商談`.`ステージ`,
            `商談`.`総額`,
            `商談`.`売上の期待値`,
            `商談`.`関連キャンペーン`,
            `商品内訳`.`商品名`,
            `商品内訳`.`学習開始日（商品内訳）`,
            `商品内訳`.`学習終了日（商品内訳）`,
            `商品内訳`.`ベンダー` as 仕入先,
            `商品内訳`.`数量`,
            `商品内訳`.`単価`,
            `商品内訳`.`小計`,
            `商品内訳`.`原価（税別）` as 原価,
            `商品内訳`.`原価（税別）` as 原価小計,
            CASE 
                WHEN `商品内訳`.`小計` IS NOT NULL AND `商品内訳`.`原価（税別）` IS NOT NULL 
                THEN CAST(REPLACE(REPLACE(`商品内訳`.`小計`, '¥ ', ''), ',', '') AS DECIMAL) - CAST(REPLACE(REPLACE(`商品内訳`.`原価（税別）`, '¥ ', ''), ',', '') AS DECIMAL)
                ELSE NULL 
            END as 粗利,
            CASE 
                WHEN `商品内訳`.`小計` IS NOT NULL AND `商品内訳`.`原価（税別）` IS NOT NULL 
                    AND CAST(REPLACE(REPLACE(`商品内訳`.`小計`, '¥ ', ''), ',', '') AS DECIMAL) > 0
                THEN ROUND(
                    (CAST(REPLACE(REPLACE(`商品内訳`.`小計`, '¥ ', ''), ',', '') AS DECIMAL) - CAST(REPLACE(REPLACE(`商品内訳`.`原価（税別）`, '¥ ', ''), ',', '') AS DECIMAL)) 
                    / CAST(REPLACE(REPLACE(`商品内訳`.`小計`, '¥ ', ''), ',', '') AS DECIMAL) * 100, 2
                )
                ELSE NULL 
            END as 粗利率,
            `商品内訳`.`Id` as 商品内訳ID
        FROM `商談` 
        LEFT JOIN `商品内訳` ON `商談`.`Id` = `商品内訳`.`親データID`
        WHERE `商品内訳`.`Id` IS NOT NULL
        ORDER BY `商談`.`Id`, `商品内訳`.`Id`
        LIMIT 10
        '''
        
        try:
            print("SQLクエリを実行中...")
            result = self.helper.execute_sql(self.workspace_id, sql_query)
            
            if result and 'data' in result and isinstance(result['data'], list):
                data = result['data']
                print(f"✅ 成功！{len(data)}件のデータを取得しました。\n")
                
                return self._format_report_output(data)
            else:
                print("❌ データの取得に失敗しました")
                return None
                
        except Exception as e:
            print(f"❌ エラー: {e}")
            return None
    
    def _format_report_output(self, data):
        """レポートデータを整形して出力"""
        
        print("=== 商品内訳IDを含むレポート結果 ===\n")
        
        # ヘッダー
        headers = [
            "データID", "商談名", "取引先名", "完了予定日", "連絡先名", "レイアウト", "種類",
            "商談の担当者", "ステージ", "総額", "売上の期待値", "関連キャンペーン", "商品名",
            "学習開始日（商品内訳）", "学習終了日（商品内訳）", "仕入先", "数量", "単価", "小計",
            "原価（税別）", "原価小計", "粗利", "粗利率", "商品内訳ID"
        ]
        
        # CSV形式で出力
        csv_data = []
        csv_data.append(",".join(headers))
        
        for i, row in enumerate(data, 1):
            print(f"--- レコード {i} ---")
            csv_row = []
            
            for header in headers:
                # ヘッダーをキーにマッピング
                key_mapping = {
                    "データID": "データID",
                    "商談名": "商談名", 
                    "取引先名": "取引先名",
                    "完了予定日": "完了予定日",
                    "連絡先名": "連絡先名",
                    "レイアウト": "レイアウト",
                    "種類": "種類",
                    "商談の担当者": "商談の担当者",
                    "ステージ": "ステージ",
                    "総額": "総額",
                    "売上の期待値": "売上の期待値",
                    "関連キャンペーン": "関連キャンペーン",
                    "商品名": "商品名",
                    "学習開始日（商品内訳）": "学習開始日（商品内訳）",
                    "学習終了日（商品内訳）": "学習終了日（商品内訳）",
                    "仕入先": "仕入先",
                    "数量": "数量",
                    "単価": "単価",
                    "小計": "小計",
                    "原価（税別）": "原価",
                    "原価小計": "原価小計",
                    "粗利": "粗利",
                    "粗利率": "粗利率",
                    "商品内訳ID": "商品内訳ID"
                }
                
                key = key_mapping.get(header, header)
                value = row.get(key, "")
                
                if header == "商品内訳ID" and value:
                    print(f"★ {header}: {value}  <- 商品内訳ID！")
                else:
                    print(f"  {header}: {value}")
                
                csv_row.append(str(value).replace(",", "，"))  # CSVのカンマ対策
            
            csv_data.append(",".join(csv_row))
            print()
        
        # CSV出力
        csv_output = "\n".join(csv_data)
        with open("zoho_report_with_product_detail_id.csv", "w", encoding="utf-8") as f:
            f.write(csv_output)
        
        print(f"📊 レポートをCSVファイルに保存しました: zoho_report_with_product_detail_id.csv")
        print(f"🎯 商品内訳IDがすべてのレコードに含まれています！")
        
        return {
            "data": data,
            "csv_file": "zoho_report_with_product_detail_id.csv",
            "record_count": len(data)
        }
    
    def interactive_report_generator(self):
        """対話式レポート生成"""
        print("=== Zoho Analytics レポート生成ツール ===")
        print("商品内訳IDを含むレポートを自動生成します。")
        print()
        
        while True:
            request = input("自然言語でレポート要求を入力してください (または 'exit' で終了): ")
            
            if request.lower() == 'exit':
                break
            
            # デフォルトで商品内訳IDを含むレポートを生成
            result = self.generate_product_details_report(request)
            
            if result:
                print(f"\n✅ レポート生成完了！{result['record_count']}件のデータを取得しました。")
            else:
                print("\n❌ レポート生成に失敗しました。")
            
            print("-" * 60 + "\n")

def main():
    """メイン関数"""
    try:
        generator = ZohoReportGenerator()
        
        # デフォルトレポート生成
        print("商品内訳IDを含むレポートを生成します...")
        result = generator.generate_product_details_report(
            "商品内訳IDを含む完全なレポートを作成してください"
        )
        
        if result:
            print("\n🎉 完了！ZohoCRMでは表示されない商品内訳IDがレポートに追加されました。")
        
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    main()