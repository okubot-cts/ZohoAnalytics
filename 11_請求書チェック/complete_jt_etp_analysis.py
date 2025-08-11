#!/usr/bin/env python3
"""
JT ETP事務局 完全分析
親商談 5187347000129692086 に紐づく全子商談531件の完全取得・分析
"""
import requests
import json
from pathlib import Path
import pandas as pd
from datetime import datetime
from collections import defaultdict
import time

class CompleteJTETPAnalyzer:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン"
        self.load_tokens()
        self.org_id = self.get_org_id()
        self.target_parent_id = "5187347000129692086"
        self.tax_rate = 0.10

    def load_tokens(self):
        """トークンを読み込み"""
        with open(self.base_path / "zoho_crm_tokens.json", 'r') as f:
            crm_tokens = json.load(f)
        with open(self.base_path / "zoho_books_tokens.json", 'r') as f:
            books_tokens = json.load(f)
        
        self.crm_headers = {'Authorization': f'Bearer {crm_tokens["access_token"]}'}
        self.books_headers = {'Authorization': f'Bearer {books_tokens["access_token"]}'}

    def get_org_id(self):
        """Books組織IDを取得"""
        try:
            response = requests.get("https://www.zohoapis.com/books/v3/organizations", headers=self.books_headers)
            if response.status_code == 200:
                orgs = response.json()['organizations']
                for org in orgs:
                    if '株式会社シー・ティー・エス' in org.get('name', ''):
                        return org['organization_id']
                return orgs[0]['organization_id'] if orgs else None
        except Exception as e:
            print(f"❌ 組織ID取得エラー: {str(e)}")
        return None

    def get_parent_deal_details(self):
        """親商談の詳細を取得"""
        print(f"📊 親商談詳細取得中...")
        
        url = f"https://www.zohoapis.com/crm/v2/Deals/{self.target_parent_id}"
        
        try:
            response = requests.get(url, headers=self.crm_headers)
            if response.status_code == 200:
                parent_deal = response.json()['data'][0]
                print(f"✅ 親商談: {parent_deal.get('Deal_Name')}")
                print(f"   金額: ¥{parent_deal.get('Amount', 0):,.0f}")
                print(f"   ステージ: {parent_deal.get('Stage')}")
                return parent_deal
            else:
                print(f"❌ 親商談取得エラー: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 親商談取得エラー: {str(e)}")
            return None

    def get_all_child_deals_complete(self):
        """親商談に紐づく全子商談を完全取得（531件目標）"""
        print(f"\\n📋 子商談完全取得中（目標: 531件）...")
        
        all_child_deals = []
        page = 1
        max_pages = 50  # より多くのページを取得
        
        while page <= max_pages:
            url = "https://www.zohoapis.com/crm/v2/Deals"
            params = {
                'fields': 'id,Deal_Name,Amount,Stage,Closing_Date,Created_Time,Modified_Time,field78',
                'per_page': 200,
                'page': page,
                'sort_by': 'Created_Time',
                'sort_order': 'desc'
            }
            
            try:
                response = requests.get(url, headers=self.crm_headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    deals = data.get('data', [])
                    
                    if not deals:
                        break
                    
                    # field78で親商談IDを参照している子商談をフィルタ
                    page_children = 0
                    for deal in deals:
                        field78 = deal.get('field78')
                        if field78 and isinstance(field78, dict):
                            parent_ref_id = field78.get('id')
                            if parent_ref_id == self.target_parent_id:
                                all_child_deals.append(deal)
                                page_children += 1
                    
                    print(f"  ページ{page}: {len(deals)}件中{page_children}件が対象子商談")
                    
                    # より多くの記録がある場合は続行
                    if not data.get('info', {}).get('more_records', False):
                        break
                    
                    page += 1
                    time.sleep(0.1)  # API制限対策
                    
                elif response.status_code == 401:
                    print(f"❌ 認証エラー: トークンを更新してください")
                    break
                else:
                    print(f"❌ ページ{page}取得エラー: {response.status_code}")
                    if page > 10:  # 10ページ以上取得していれば継続
                        break
                    else:
                        break
                        
            except Exception as e:
                print(f"❌ ページ{page}取得エラー: {str(e)}")
                break
        
        print(f"✅ 子商談取得完了: {len(all_child_deals)}件")
        
        if len(all_child_deals) < 500:
            print(f"⚠️  期待される531件より少ないです。以下の可能性があります：")
            print(f"   • トークン期限切れ")
            print(f"   • 異なる検索条件が必要")
            print(f"   • ステージフィルタが影響")
        
        return all_child_deals

    def analyze_child_deals_by_period(self, child_deals):
        """子商談を期間別に分析"""
        print(f"\\n📊 子商談期間別分析...")
        
        period_analysis = {
            '上期(〜5月)': {'deals': [], 'amount': 0},
            '下期(6月〜)': {'deals': [], 'amount': 0},
            '期間不明': {'deals': [], 'amount': 0}
        }
        
        total_amount = 0
        
        for deal in child_deals:
            amount = deal.get('Amount', 0) or 0
            total_amount += amount
            closing_date = deal.get('Closing_Date', '')
            
            # 期間判定
            if closing_date and '-' in closing_date:
                try:
                    month = int(closing_date.split('-')[1])
                    if month <= 5:
                        period = '上期(〜5月)'
                    else:
                        period = '下期(6月〜)'
                except:
                    period = '期間不明'
            else:
                period = '期間不明'
            
            period_analysis[period]['deals'].append(deal)
            period_analysis[period]['amount'] += amount
        
        print(f"  総子商談金額（税抜）: ¥{total_amount:,.0f}")
        print(f"  総子商談金額（税込）: ¥{total_amount * (1 + self.tax_rate):,.0f}")
        
        for period, data in period_analysis.items():
            count = len(data['deals'])
            amount = data['amount']
            amount_with_tax = amount * (1 + self.tax_rate)
            print(f"  {period}: {count}件, ¥{amount:,.0f}(税抜) / ¥{amount_with_tax:,.0f}(税込)")
        
        return period_analysis, total_amount

    def get_all_related_invoices(self, child_deals):
        """関連する全請求書を取得"""
        print(f"\\n📄 関連請求書取得中...")
        
        # 検索対象IDリスト
        target_ids = {self.target_parent_id}  # 親商談ID
        for child in child_deals:
            target_ids.add(child['id'])
        
        print(f"  検索対象ID数: {len(target_ids)}件")
        
        related_invoices = []
        excluded_110yen = []
        page = 1
        max_pages = 20
        
        while page <= max_pages:
            url = "https://www.zohoapis.com/books/v3/invoices"
            params = {
                'organization_id': self.org_id,
                'per_page': 200,
                'page': page,
                'sort_column': 'date',
                'sort_order': 'D'
            }
            
            try:
                response = requests.get(url, headers=self.books_headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    invoices = data.get('invoices', [])
                    
                    if not invoices:
                        break
                    
                    page_matches = 0
                    for invoice in invoices:
                        ref_num = invoice.get('reference_number', '').strip()
                        if ref_num in target_ids:
                            invoice_total = invoice.get('total', 0)
                            if invoice_total == 110:
                                excluded_110yen.append(invoice)
                            else:
                                # 親商談か子商談か判定
                                if ref_num == self.target_parent_id:
                                    invoice['relation_type'] = 'parent'
                                else:
                                    invoice['relation_type'] = 'child'
                                    # 子商談の期間判定
                                    child_deal = next((c for c in child_deals if c['id'] == ref_num), None)
                                    if child_deal:
                                        closing_date = child_deal.get('Closing_Date', '')
                                        if closing_date and '-' in closing_date:
                                            try:
                                                month = int(closing_date.split('-')[1])
                                                invoice['period'] = '上期(〜5月)' if month <= 5 else '下期(6月〜)'
                                            except:
                                                invoice['period'] = '期間不明'
                                        else:
                                            invoice['period'] = '期間不明'
                                
                                related_invoices.append(invoice)
                                page_matches += 1
                    
                    print(f"  ページ{page}: {len(invoices)}件中{page_matches}件が関連請求書")
                    
                    page_context = data.get('page_context', {})
                    if not page_context.get('has_more_page', False):
                        break
                    page += 1
                    time.sleep(0.1)
                    
                else:
                    print(f"❌ 請求書ページ{page}取得エラー: {response.status_code}")
                    break
                    
            except Exception as e:
                print(f"❌ 請求書ページ{page}取得エラー: {str(e)}")
                break
        
        print(f"✅ 関連請求書取得完了: {len(related_invoices)}件")
        print(f"   110円除外請求書: {len(excluded_110yen)}件")
        
        return related_invoices, excluded_110yen

    def comprehensive_analysis(self, child_deals, period_analysis, related_invoices, excluded_110yen):
        """包括的分析"""
        print(f"\\n" + "="*90)
        print(f"📊 JT ETP事務局 完全分析結果")
        print("="*90)
        
        # 基本統計
        total_child_amount = sum(deal.get('Amount', 0) or 0 for deal in child_deals)
        total_child_amount_with_tax = total_child_amount * (1 + self.tax_rate)
        
        print(f"\\n【基本統計】")
        print(f"  親商談ID: {self.target_parent_id}")
        print(f"  取得子商談数: {len(child_deals)}件 (目標: 531件)")
        print(f"  子商談総額（税抜）: ¥{total_child_amount:,.0f}")
        print(f"  子商談総額（税込）: ¥{total_child_amount_with_tax:,.0f}")
        
        # 請求書分析
        parent_invoices = [inv for inv in related_invoices if inv['relation_type'] == 'parent']
        child_invoices = [inv for inv in related_invoices if inv['relation_type'] == 'child']
        
        parent_invoice_amount = sum(inv.get('total', 0) for inv in parent_invoices)
        child_invoice_amount = sum(inv.get('total', 0) for inv in child_invoices)
        total_invoice_amount = parent_invoice_amount + child_invoice_amount
        excluded_amount = sum(inv.get('total', 0) for inv in excluded_110yen)
        
        print(f"\\n【請求書分析】")
        print(f"  親商談請求書: {len(parent_invoices)}件, ¥{parent_invoice_amount:,.0f}")
        print(f"  子商談請求書: {len(child_invoices)}件, ¥{child_invoice_amount:,.0f}")
        print(f"  請求書合計: {len(related_invoices)}件, ¥{total_invoice_amount:,.0f}")
        print(f"  110円除外: {len(excluded_110yen)}件, ¥{excluded_amount:,.0f}")
        
        # 差額分析
        main_diff = total_child_amount_with_tax - total_invoice_amount
        
        print(f"\\n【差額分析】")
        print(f"  予想金額（税込）: ¥{total_child_amount_with_tax:,.0f}")
        print(f"  実請求金額: ¥{total_invoice_amount:,.0f}")
        print(f"  主差額: ¥{main_diff:,.0f}")
        print(f"  110円除外分: ¥{excluded_amount:,.0f}")
        print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        if main_diff > 0:
            print(f"  未請求金額: ¥{main_diff:,.0f} ⚠️")
        else:
            print(f"  過請求金額: ¥{abs(main_diff):,.0f} ⚠️")
        
        # 期間別分析
        print(f"\\n【期間別分析】")
        for period, data in period_analysis.items():
            period_deals = data['deals']
            period_amount = data['amount']
            period_amount_with_tax = period_amount * (1 + self.tax_rate)
            
            # この期間の請求書
            period_invoices = [inv for inv in child_invoices if inv.get('period') == period]
            period_invoice_amount = sum(inv.get('total', 0) for inv in period_invoices)
            period_diff = period_amount_with_tax - period_invoice_amount
            
            print(f"\\n  {period}:")
            print(f"    商談数: {len(period_deals)}件")
            print(f"    商談金額（税込）: ¥{period_amount_with_tax:,.0f}")
            print(f"    請求書: {len(period_invoices)}件, ¥{period_invoice_amount:,.0f}")
            print(f"    差額: ¥{period_diff:,.0f}")
        
        # 未請求分析
        billed_child_ids = set(inv.get('reference_number') for inv in child_invoices)
        unbilled_deals = [deal for deal in child_deals if deal['id'] not in billed_child_ids]
        unbilled_amount = sum(deal.get('Amount', 0) or 0 for deal in unbilled_deals)
        unbilled_amount_with_tax = unbilled_amount * (1 + self.tax_rate)
        
        print(f"\\n【未請求分析】")
        print(f"  未請求商談数: {len(unbilled_deals)}件")
        print(f"  未請求金額（税込）: ¥{unbilled_amount_with_tax:,.0f}")
        
        print("="*90)
        
        return {
            'total_deals': len(child_deals),
            'total_amount': total_child_amount,
            'total_amount_with_tax': total_child_amount_with_tax,
            'total_invoices': len(related_invoices),
            'total_invoice_amount': total_invoice_amount,
            'main_difference': main_diff,
            'unbilled_deals': len(unbilled_deals),
            'unbilled_amount': unbilled_amount_with_tax,
            'period_analysis': period_analysis
        }

    def export_detailed_results(self, child_deals, related_invoices, analysis_result):
        """詳細結果をエクスポート"""
        print(f"\\n📁 詳細結果エクスポート中...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(__file__).parent / f"JT_ETP完全分析_{timestamp}"
        output_dir.mkdir(exist_ok=True)
        
        # 子商談リスト
        child_data = []
        for deal in child_deals:
            amount = deal.get('Amount', 0) or 0
            closing_date = deal.get('Closing_Date', '')
            
            # 期間判定
            if closing_date and '-' in closing_date:
                try:
                    month = int(closing_date.split('-')[1])
                    period = '上期(〜5月)' if month <= 5 else '下期(6月〜)'
                except:
                    period = '期間不明'
            else:
                period = '期間不明'
            
            # 請求書有無
            has_invoice = any(inv.get('reference_number') == deal['id'] for inv in related_invoices)
            
            child_data.append({
                'deal_id': deal['id'],
                'deal_name': deal.get('Deal_Name'),
                'amount': amount,
                'amount_with_tax': amount * (1 + self.tax_rate),
                'stage': deal.get('Stage'),
                'closing_date': closing_date,
                'period': period,
                'has_invoice': has_invoice,
                'created_time': deal.get('Created_Time'),
                'modified_time': deal.get('Modified_Time')
            })
        
        df_child = pd.DataFrame(child_data)
        child_file = output_dir / f"子商談一覧_{timestamp}.csv"
        df_child.to_csv(child_file, index=False, encoding='utf-8-sig')
        print(f"  子商談一覧: {child_file}")
        
        # 請求書リスト
        invoice_data = []
        for inv in related_invoices:
            invoice_data.append({
                'invoice_id': inv.get('invoice_id'),
                'invoice_number': inv.get('invoice_number'),
                'reference_number': inv.get('reference_number'),
                'total': inv.get('total'),
                'status': inv.get('status'),
                'date': inv.get('date'),
                'relation_type': inv.get('relation_type'),
                'period': inv.get('period', 'N/A')
            })
        
        df_invoice = pd.DataFrame(invoice_data)
        invoice_file = output_dir / f"請求書一覧_{timestamp}.csv"
        df_invoice.to_csv(invoice_file, index=False, encoding='utf-8-sig')
        print(f"  請求書一覧: {invoice_file}")
        
        print(f"✅ エクスポート完了: {output_dir}")

def main():
    """メイン処理"""
    print("="*90)
    print("🔍 JT ETP事務局 完全分析ツール")
    print("="*90)
    
    analyzer = CompleteJTETPAnalyzer()
    
    if not analyzer.org_id:
        print("❌ Books組織IDが取得できませんでした")
        return
    
    # 1. 親商談詳細取得
    parent_deal = analyzer.get_parent_deal_details()
    
    # 2. 全子商談取得（531件目標）
    child_deals = analyzer.get_all_child_deals_complete()
    
    if not child_deals:
        print("❌ 子商談が取得できませんでした")
        return
    
    # 3. 期間別分析
    period_analysis, total_amount = analyzer.analyze_child_deals_by_period(child_deals)
    
    # 4. 関連請求書取得
    related_invoices, excluded_110yen = analyzer.get_all_related_invoices(child_deals)
    
    # 5. 包括的分析
    analysis_result = analyzer.comprehensive_analysis(child_deals, period_analysis, related_invoices, excluded_110yen)
    
    # 6. 詳細結果エクスポート
    analyzer.export_detailed_results(child_deals, related_invoices, analysis_result)
    
    print(f"\\n✅ JT ETP事務局 完全分析完了")

if __name__ == "__main__":
    main()