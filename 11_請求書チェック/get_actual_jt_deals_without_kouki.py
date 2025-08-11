#!/usr/bin/env python3
"""
JT ETP 実際の商談金額集計
531件の子商談のうち、商談名に「後期」が含まれない商談の実際の総額を集計
"""
import requests
import json
from pathlib import Path
import pandas as pd
from datetime import datetime
import time

class ActualJTDealsAnalyzer:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン"
        self.load_tokens()
        self.target_parent_id = "5187347000129692086"
        self.tax_rate = 0.10

    def load_tokens(self):
        """トークンを読み込み"""
        try:
            with open(self.base_path / "zoho_crm_tokens.json", 'r') as f:
                crm_tokens = json.load(f)
            self.crm_headers = {'Authorization': f'Bearer {crm_tokens["access_token"]}'}
            print("✅ CRMトークン読み込み成功")
        except Exception as e:
            print(f"❌ トークン読み込みエラー: {str(e)}")
            self.crm_headers = None

    def get_all_jt_child_deals_complete(self):
        """JT ETP親商談に紐づく全子商談を完全取得（531件目標）"""
        print(f"\n📊 JT ETP全子商談取得中（目標: 531件）...")
        print(f"親商談ID: {self.target_parent_id}")
        
        if not self.crm_headers:
            print("❌ 認証情報が不正です")
            return []

        all_child_deals = []
        page = 1
        max_pages = 50
        consecutive_empty_pages = 0
        
        while page <= max_pages and consecutive_empty_pages < 5:
            url = "https://www.zohoapis.com/crm/v2/Deals"
            params = {
                'fields': 'id,Deal_Name,Amount,Stage,Closing_Date,Created_Time,Modified_Time,field78',
                'per_page': 200,
                'page': page,
                'sort_by': 'Modified_Time',
                'sort_order': 'desc'
            }
            
            try:
                print(f"  ページ{page}取得中...", end=" ")
                response = requests.get(url, headers=self.crm_headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    deals = data.get('data', [])
                    
                    if not deals:
                        consecutive_empty_pages += 1
                        print("空ページ")
                        page += 1
                        continue
                    else:
                        consecutive_empty_pages = 0
                    
                    # field78で親商談IDを参照している子商談をフィルタ
                    page_children = 0
                    for deal in deals:
                        field78 = deal.get('field78')
                        if field78 and isinstance(field78, dict):
                            parent_ref_id = field78.get('id')
                            if parent_ref_id == self.target_parent_id:
                                all_child_deals.append(deal)
                                page_children += 1
                    
                    print(f"{len(deals)}件中{page_children}件がJT ETP子商談")
                    
                    # より多くの記録がある場合は続行
                    if not data.get('info', {}).get('more_records', False):
                        print("  最終ページに到達")
                        break
                    
                    page += 1
                    time.sleep(0.2)  # API制限対策
                    
                elif response.status_code == 401:
                    print("❌ 認証エラー: トークンを更新してください")
                    break
                else:
                    print(f"❌ エラー: {response.status_code}")
                    if page > 10:  # 10ページ以上取得していれば継続
                        page += 1
                        time.sleep(0.5)
                        continue
                    else:
                        break
                        
            except Exception as e:
                print(f"❌ 取得エラー: {str(e)}")
                if page > 10:
                    page += 1
                    time.sleep(1)
                    continue
                else:
                    break
        
        print(f"\n✅ JT ETP子商談取得完了: {len(all_child_deals)}件")
        
        if len(all_child_deals) < 500:
            print(f"⚠️ 期待される531件より少ないです:")
            print(f"   • 取得件数: {len(all_child_deals)}件")
            print(f"   • 不足: {531 - len(all_child_deals)}件")
            print(f"   • トークン期限切れまたは検索条件の問題の可能性")
        
        return all_child_deals

    def filter_deals_without_kouki(self, all_deals):
        """商談名に「後期」が含まれない商談をフィルタ"""
        print(f"\n🔍 「後期」フィルタリング中...")
        
        deals_without_kouki = []
        deals_with_kouki = []
        
        for deal in all_deals:
            deal_name = deal.get('Deal_Name', '')
            if '後期' in deal_name:
                deals_with_kouki.append(deal)
            else:
                deals_without_kouki.append(deal)
        
        print(f"  全商談数: {len(all_deals)}件")
        print(f"  「後期」を含む: {len(deals_with_kouki)}件")
        print(f"  「後期」を含まない: {len(deals_without_kouki)}件")
        
        # サンプル表示
        if deals_with_kouki:
            print(f"\n  「後期」を含む商談例:")
            for i, deal in enumerate(deals_with_kouki[:3], 1):
                print(f"    {i}. {deal.get('Deal_Name', 'N/A')[:60]}")
        
        if deals_without_kouki:
            print(f"\n  「後期」を含まない商談例:")
            for i, deal in enumerate(deals_without_kouki[:3], 1):
                print(f"    {i}. {deal.get('Deal_Name', 'N/A')[:60]}")
        
        return deals_without_kouki, deals_with_kouki

    def calculate_actual_totals(self, deals_without_kouki):
        """実際の商談総額を計算"""
        print(f"\n📊 実際の商談総額計算中...")
        
        total_amount_excluding_tax = 0
        valid_deals = 0
        zero_amount_deals = 0
        
        deal_details = []
        
        for deal in deals_without_kouki:
            amount = deal.get('Amount', 0) or 0
            deal_name = deal.get('Deal_Name', 'N/A')
            deal_id = deal.get('id', 'N/A')
            closing_date = deal.get('Closing_Date', '')
            stage = deal.get('Stage', 'N/A')
            
            if amount > 0:
                total_amount_excluding_tax += amount
                valid_deals += 1
            else:
                zero_amount_deals += 1
            
            deal_details.append({
                'id': deal_id,
                'name': deal_name,
                'amount': amount,
                'closing_date': closing_date,
                'stage': stage
            })
        
        total_amount_including_tax = total_amount_excluding_tax * (1 + self.tax_rate)
        
        print(f"📈 集計結果:")
        print(f"  対象商談数: {len(deals_without_kouki)}件")
        print(f"  金額有りの商談: {valid_deals}件")
        print(f"  金額ゼロの商談: {zero_amount_deals}件")
        print(f"  総額（税抜き）: ¥{total_amount_excluding_tax:,.0f}")
        print(f"  総額（税込み）: ¥{total_amount_including_tax:,.0f}")
        
        return {
            'deals_count': len(deals_without_kouki),
            'valid_deals': valid_deals,
            'zero_amount_deals': zero_amount_deals,
            'total_excluding_tax': total_amount_excluding_tax,
            'total_including_tax': total_amount_including_tax,
            'deal_details': deal_details
        }

    def compare_with_payments(self, calculation_result):
        """入金額との比較"""
        print(f"\n" + "="*90)
        print("🔍 実際の商談総額 vs 入金額比較")
        print("="*90)
        
        # 入金データ（確認済み）
        payments_until_june = 91079160  # 6月までの入金（6月分除く）
        
        total_excluding_tax = calculation_result['total_excluding_tax']
        total_including_tax = calculation_result['total_including_tax']
        deals_count = calculation_result['deals_count']
        
        print(f"📊 実数による比較:")
        print(f"  商談名に「後期」なしの商談数: {deals_count}件")
        print(f"  実際の商談総額（税抜き）: ¥{total_excluding_tax:,.0f}")
        print(f"  実際の商談総額（税込み）: ¥{total_including_tax:,.0f}")
        print(f"  6月までの入金額: ¥{payments_until_june:,.0f}")
        
        # 差額分析
        diff_including_tax = payments_until_june - total_including_tax
        diff_ratio = (diff_including_tax / total_including_tax * 100) if total_including_tax > 0 else 0
        
        print(f"\n💡 差額分析:")
        print(f"  入金額 - 商談額（税込）: ¥{diff_including_tax:,.0f}")
        print(f"  差異率: {diff_ratio:.1f}%")
        
        if abs(diff_including_tax) <= total_including_tax * 0.02:  # 2%以内
            status = "✅ ほぼ完全一致（優秀）"
        elif abs(diff_including_tax) <= total_including_tax * 0.05:  # 5%以内
            status = "✅ 概ね適正（良好）"
        elif diff_including_tax > 0:  # 入金の方が多い
            status = "⚠️ 入金超過（前受金等の可能性）"
        else:  # 商談の方が多い
            status = "🚨 未入金あり（要確認）"
        
        print(f"  評価: {status}")
        
        return calculation_result

    def export_detailed_results(self, calculation_result, deals_with_kouki):
        """詳細結果をエクスポート"""
        print(f"\n📁 詳細結果エクスポート中...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 「後期」なし商談リスト
        df_without_kouki = pd.DataFrame(calculation_result['deal_details'])
        file_without_kouki = f"JT_ETP後期なし商談_{timestamp}.csv"
        df_without_kouki.to_csv(file_without_kouki, index=False, encoding='utf-8-sig')
        print(f"  後期なし商談: {file_without_kouki}")
        
        # 「後期」あり商談リスト（比較用）
        if deals_with_kouki:
            kouki_details = []
            for deal in deals_with_kouki:
                kouki_details.append({
                    'id': deal.get('id'),
                    'name': deal.get('Deal_Name', 'N/A'),
                    'amount': deal.get('Amount', 0) or 0,
                    'closing_date': deal.get('Closing_Date', ''),
                    'stage': deal.get('Stage', 'N/A')
                })
            
            df_with_kouki = pd.DataFrame(kouki_details)
            file_with_kouki = f"JT_ETP後期あり商談_{timestamp}.csv"
            df_with_kouki.to_csv(file_with_kouki, index=False, encoding='utf-8-sig')
            print(f"  後期あり商談: {file_with_kouki}")
        
        print(f"✅ エクスポート完了")

def main():
    """メイン処理"""
    print("="*90)
    print("🔍 JT ETP実際の商談金額集計")
    print("  商談名に「後期」が含まれない商談の実際の総額")
    print("="*90)
    
    analyzer = ActualJTDealsAnalyzer()
    
    # 1. 全子商談取得（531件目標）
    all_child_deals = analyzer.get_all_jt_child_deals_complete()
    
    if not all_child_deals:
        print("❌ 子商談が取得できませんでした")
        print("🔧 対処法:")
        print("  1. ZohoCRM APIトークンを更新")
        print("  2. ZohoCRM画面で手動確認")
        print("  3. 検索条件を調整")
        return
    
    # 2. 「後期」フィルタリング
    deals_without_kouki, deals_with_kouki = analyzer.filter_deals_without_kouki(all_child_deals)
    
    if not deals_without_kouki:
        print("❌ 「後期」を含まない商談が見つかりませんでした")
        return
    
    # 3. 実際の総額計算
    calculation_result = analyzer.calculate_actual_totals(deals_without_kouki)
    
    # 4. 入金額との比較
    analyzer.compare_with_payments(calculation_result)
    
    # 5. 詳細結果エクスポート
    analyzer.export_detailed_results(calculation_result, deals_with_kouki)
    
    print(f"\n" + "="*90)
    print("📊 最終回答")
    print("="*90)
    print(f"JT ETP子商談のうち商談名に「後期」が含まれない商談:")
    print(f"  商談数: {calculation_result['deals_count']}件")
    print(f"  総額（税抜き）: ¥{calculation_result['total_excluding_tax']:,.0f}")
    print(f"  総額（税込み）: ¥{calculation_result['total_including_tax']:,.0f}")
    print("="*90)

if __name__ == "__main__":
    main()