#!/usr/bin/env python3
"""
ZohoBooks 包括的分析
JT ETP関連請求書の完全な紐づけ把握
"""
import requests
import json
from pathlib import Path
import pandas as pd
from datetime import datetime
import time
import re

class ComprehensiveBooksAnalyzer:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン"
        self.load_tokens()
        self.org_id = self.get_org_id()
        self.target_parent_id = "5187347000129692086"

    def load_tokens(self):
        """トークンを読み込み"""
        try:
            with open(self.base_path / "zoho_books_tokens.json", 'r') as f:
                books_tokens = json.load(f)
            self.books_headers = {'Authorization': f'Bearer {books_tokens["access_token"]}'}
        except Exception as e:
            print(f"❌ トークン読み込みエラー: {str(e)}")
            self.books_headers = None

    def get_org_id(self):
        """Books組織IDを取得"""
        if not self.books_headers:
            return None
        
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

    def search_jt_invoices_comprehensive(self):
        """JT関連請求書を包括的に検索"""
        print("📄 JT関連請求書包括検索中...")
        
        if not self.org_id or not self.books_headers:
            print("❌ 認証情報が不正です")
            return [], []

        all_invoices = []
        jt_related_invoices = []
        
        # 複数の検索戦略を実行
        search_strategies = [
            {'name': '全請求書取得', 'params': {}},
            {'name': 'JT顧客検索', 'params': {'customer_name_contains': 'JT'}},
            {'name': 'ETP検索', 'params': {'invoice_number_contains': 'ETP'}},
            {'name': '高額請求書検索', 'params': {'total_greater_than': 1000000}},
        ]
        
        for strategy in search_strategies:
            print(f"\n🔍 {strategy['name']}実行中...")
            strategy_invoices = self._fetch_invoices_with_params(strategy['params'])
            
            # JT関連を特定
            for invoice in strategy_invoices:
                if self._is_jt_related(invoice):
                    # 重複チェック
                    if not any(existing['invoice_id'] == invoice['invoice_id'] for existing in jt_related_invoices):
                        jt_related_invoices.append(invoice)
            
            all_invoices.extend(strategy_invoices)
            time.sleep(0.5)  # API制限対策

        print(f"✅ 全請求書: {len(all_invoices)}件")
        print(f"✅ JT関連請求書: {len(jt_related_invoices)}件")
        
        return all_invoices, jt_related_invoices

    def _fetch_invoices_with_params(self, search_params):
        """指定されたパラメータで請求書を取得"""
        invoices = []
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
            
            # 検索パラメータを追加
            params.update(search_params)
            
            try:
                response = requests.get(url, headers=self.books_headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    page_invoices = data.get('invoices', [])
                    
                    if not page_invoices:
                        break
                    
                    invoices.extend(page_invoices)
                    print(f"  ページ{page}: {len(page_invoices)}件")
                    
                    page_context = data.get('page_context', {})
                    if not page_context.get('has_more_page', False):
                        break
                    page += 1
                    
                elif response.status_code == 401:
                    print(f"❌ 認証エラー（ページ{page}）")
                    break
                else:
                    print(f"❌ エラー（ページ{page}）: {response.status_code}")
                    break
                    
            except Exception as e:
                print(f"❌ 取得エラー（ページ{page}）: {str(e)}")
                break
        
        return invoices

    def _is_jt_related(self, invoice):
        """請求書がJT関連かどうかを判定"""
        # 複数の条件で判定
        jt_indicators = [
            'JT', 'ETP', 'たばこ', 'Tobacco', '日本たばこ',
            '5187347000129692086'  # 親商談ID
        ]
        
        # 検索対象フィールド
        search_fields = [
            invoice.get('customer_name', ''),
            invoice.get('invoice_number', ''),
            invoice.get('reference_number', ''),
            invoice.get('notes', ''),
            invoice.get('terms', ''),
            str(invoice.get('line_items', []))
        ]
        
        search_text = ' '.join(search_fields).upper()
        
        for indicator in jt_indicators:
            if indicator.upper() in search_text:
                return True
        
        return False

    def analyze_jt_invoice_details(self, jt_invoices):
        """JT関連請求書の詳細分析"""
        print(f"\n📊 JT関連請求書詳細分析...")
        
        total_amount = 0
        period_analysis = {'上期': [], '下期': [], '不明': []}
        reference_patterns = {}
        
        detailed_invoices = []
        
        for invoice in jt_invoices:
            # 詳細情報取得
            detailed_invoice = self._get_invoice_details(invoice['invoice_id'])
            if detailed_invoice:
                detailed_invoices.append(detailed_invoice)
                
                amount = detailed_invoice.get('total', 0)
                total_amount += amount
                
                # 期間判定
                invoice_date = detailed_invoice.get('date', '')
                if invoice_date:
                    try:
                        month = int(invoice_date.split('-')[1]) if '-' in invoice_date else 12
                        period = '上期' if month <= 5 else '下期'
                    except:
                        period = '不明'
                else:
                    period = '不明'
                
                period_analysis[period].append(detailed_invoice)
                
                # Reference number パターン分析
                ref_num = detailed_invoice.get('reference_number', '')
                if ref_num:
                    if ref_num not in reference_patterns:
                        reference_patterns[ref_num] = []
                    reference_patterns[ref_num].append(detailed_invoice)
            
            time.sleep(0.2)  # API制限対策
        
        print(f"  JT関連請求書総額: ¥{total_amount:,.0f}")
        
        for period, invoices in period_analysis.items():
            period_amount = sum(inv.get('total', 0) for inv in invoices)
            print(f"  {period}: {len(invoices)}件, ¥{period_amount:,.0f}")
        
        print(f"  Reference パターン: {len(reference_patterns)}種類")
        
        return detailed_invoices, period_analysis, reference_patterns

    def _get_invoice_details(self, invoice_id):
        """個別請求書の詳細情報を取得"""
        url = f"https://www.zohoapis.com/books/v3/invoices/{invoice_id}"
        params = {'organization_id': self.org_id}
        
        try:
            response = requests.get(url, headers=self.books_headers, params=params)
            if response.status_code == 200:
                return response.json()['invoice']
        except Exception as e:
            print(f"  詳細取得エラー（{invoice_id}）: {str(e)}")
        
        return None

    def analyze_reference_patterns(self, reference_patterns):
        """Reference number パターンの詳細分析"""
        print(f"\n🔍 Reference Number パターン分析...")
        
        parent_references = []
        child_references = []
        other_references = []
        
        for ref_num, invoices in reference_patterns.items():
            ref_amount = sum(inv.get('total', 0) for inv in invoices)
            
            print(f"\n  参照番号: {ref_num}")
            print(f"    請求書数: {len(invoices)}件")
            print(f"    合計金額: ¥{ref_amount:,.0f}")
            
            # 親商談IDかどうか
            if ref_num == self.target_parent_id:
                parent_references.extend(invoices)
                print(f"    → 親商談参照 ⭐")
            elif len(ref_num) > 15 and ref_num.startswith('5187347'):
                child_references.extend(invoices)
                print(f"    → 子商談参照")
            else:
                other_references.extend(invoices)
                print(f"    → その他参照")
            
            # 代表的な請求書の詳細表示
            for i, inv in enumerate(invoices[:3]):
                print(f"      {i+1}. {inv.get('invoice_number')} ¥{inv.get('total', 0):,.0f} ({inv.get('date')})")
        
        return parent_references, child_references, other_references

    def comprehensive_summary(self, all_invoices, jt_invoices, detailed_invoices, period_analysis, reference_patterns):
        """包括的まとめ"""
        print(f"\n" + "="*90)
        print(f"📊 ZohoBooks JT ETP 包括分析結果")
        print("="*90)
        
        jt_total = sum(inv.get('total', 0) for inv in detailed_invoices)
        
        print(f"\n【請求書検索結果】")
        print(f"  全請求書数: {len(all_invoices)}件")
        print(f"  JT関連請求書: {len(jt_invoices)}件")
        print(f"  詳細取得成功: {len(detailed_invoices)}件")
        print(f"  JT関連総額: ¥{jt_total:,.0f}")
        
        print(f"\n【期間別内訳】")
        for period, invoices in period_analysis.items():
            period_amount = sum(inv.get('total', 0) for inv in invoices)
            print(f"  {period}: {len(invoices)}件, ¥{period_amount:,.0f}")
        
        print(f"\n【参照パターン】")
        print(f"  参照番号パターン数: {len(reference_patterns)}")
        
        # 最大金額の請求書TOP5
        sorted_invoices = sorted(detailed_invoices, key=lambda x: x.get('total', 0), reverse=True)
        print(f"\n【高額請求書TOP5】")
        for i, inv in enumerate(sorted_invoices[:5], 1):
            print(f"  {i}. {inv.get('invoice_number')} - ¥{inv.get('total', 0):,.0f}")
            print(f"     参照: {inv.get('reference_number', 'N/A')}")
            print(f"     日付: {inv.get('date', 'N/A')}")
        
        # 現在の分析との差異
        previous_analysis_amount = 15501617 - 220  # 110円×2件除外
        difference = jt_total - previous_analysis_amount
        
        print(f"\n【分析結果比較】")
        print(f"  前回分析金額: ¥{previous_analysis_amount:,.0f}")
        print(f"  今回発見金額: ¥{jt_total:,.0f}")
        print(f"  差異: ¥{difference:,.0f}")
        
        if difference > 0:
            print(f"  → 追加で ¥{difference:,.0f} の請求書を発見！")
        
        print("="*90)
        
        return {
            'total_jt_amount': jt_total,
            'invoice_count': len(detailed_invoices),
            'period_breakdown': period_analysis,
            'reference_patterns': reference_patterns,
            'top_invoices': sorted_invoices[:10]
        }

    def export_comprehensive_results(self, detailed_invoices, analysis_summary):
        """包括分析結果をエクスポート"""
        print(f"\n📁 包括分析結果エクスポート...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(__file__).parent / f"ZohoBooks_JT_包括分析_{timestamp}"
        output_dir.mkdir(exist_ok=True)
        
        # JT関連請求書リスト
        invoice_data = []
        for inv in detailed_invoices:
            # 期間判定
            invoice_date = inv.get('date', '')
            period = '不明'
            if invoice_date and '-' in invoice_date:
                try:
                    month = int(invoice_date.split('-')[1])
                    period = '上期' if month <= 5 else '下期'
                except:
                    pass
            
            invoice_data.append({
                'invoice_id': inv.get('invoice_id'),
                'invoice_number': inv.get('invoice_number'),
                'reference_number': inv.get('reference_number'),
                'customer_name': inv.get('customer_name'),
                'total': inv.get('total'),
                'status': inv.get('status'),
                'date': invoice_date,
                'period': period,
                'notes': inv.get('notes', ''),
                'terms': inv.get('terms', '')
            })
        
        df_invoices = pd.DataFrame(invoice_data)
        invoice_file = output_dir / f"JT関連請求書一覧_{timestamp}.csv"
        df_invoices.to_csv(invoice_file, index=False, encoding='utf-8-sig')
        print(f"  請求書一覧: {invoice_file}")
        
        # サマリレポート
        summary_data = {
            '項目': [
                'JT関連請求書数',
                'JT関連総額',
                '上期請求書数',
                '上期金額',
                '下期請求書数', 
                '下期金額',
                '期間不明数',
                '期間不明金額'
            ],
            '値': [
                len(detailed_invoices),
                f"¥{analysis_summary['total_jt_amount']:,.0f}",
                len(analysis_summary['period_breakdown']['上期']),
                f"¥{sum(inv.get('total', 0) for inv in analysis_summary['period_breakdown']['上期']):,.0f}",
                len(analysis_summary['period_breakdown']['下期']),
                f"¥{sum(inv.get('total', 0) for inv in analysis_summary['period_breakdown']['下期']):,.0f}",
                len(analysis_summary['period_breakdown']['不明']),
                f"¥{sum(inv.get('total', 0) for inv in analysis_summary['period_breakdown']['不明']):,.0f}"
            ]
        }
        
        df_summary = pd.DataFrame(summary_data)
        summary_file = output_dir / f"分析サマリ_{timestamp}.csv"
        df_summary.to_csv(summary_file, index=False, encoding='utf-8-sig')
        print(f"  分析サマリ: {summary_file}")
        
        print(f"✅ エクスポート完了: {output_dir}")

def main():
    """メイン処理"""
    print("="*90)
    print("🔍 ZohoBooks JT ETP 包括分析")
    print("="*90)
    
    analyzer = ComprehensiveBooksAnalyzer()
    
    if not analyzer.org_id:
        print("❌ 認証に失敗しました。トークンを確認してください。")
        return
    
    # 1. JT関連請求書の包括検索
    all_invoices, jt_invoices = analyzer.search_jt_invoices_comprehensive()
    
    if not jt_invoices:
        print("❌ JT関連請求書が見つかりませんでした")
        return
    
    # 2. 詳細分析
    detailed_invoices, period_analysis, reference_patterns = analyzer.analyze_jt_invoice_details(jt_invoices)
    
    # 3. Reference パターン分析
    parent_refs, child_refs, other_refs = analyzer.analyze_reference_patterns(reference_patterns)
    
    # 4. 包括まとめ
    analysis_summary = analyzer.comprehensive_summary(
        all_invoices, jt_invoices, detailed_invoices, period_analysis, reference_patterns
    )
    
    # 5. 結果エクスポート
    analyzer.export_comprehensive_results(detailed_invoices, analysis_summary)
    
    print(f"\n✅ ZohoBooks JT ETP 包括分析完了")

if __name__ == "__main__":
    main()