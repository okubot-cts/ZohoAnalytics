#!/usr/bin/env python3
"""
修正版 請求漏れ分析ツール
レイアウトに依存しない親子構造分析
"""
import requests
import json
from pathlib import Path
from collections import defaultdict
import pandas as pd
from datetime import datetime

class CorrectInvoiceLeakageAnalyzer:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン"
        self.load_tokens()
        self.org_id = self.get_org_id()
        
        # 受注ステージの定義
        self.closed_stages = ['受注', '入金待ち', '開講準備', '開講待ち']
        
        # 無効な請求書ステータス
        self.invalid_invoice_statuses = ['void']
        
        # 対象期間
        self.target_start_date = '2024-04-01'
        
        # 消費税率（10%）
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
        response = requests.get("https://www.zohoapis.com/books/v3/organizations", headers=self.books_headers)
        if response.status_code == 200:
            orgs = response.json()['organizations']
            for org in orgs:
                if '株式会社シー・ティー・エス' in org.get('name', ''):
                    return org['organization_id']
            return orgs[0]['organization_id'] if orgs else None
        return None
    
    def get_all_closed_deals(self):
        """受注済み商談を全件取得"""
        print("📊 受注済み商談を取得中（2024/4/1以降）...")
        
        url = "https://www.zohoapis.com/crm/v2/Deals"
        all_deals = []
        page = 1
        
        while page <= 15:
            params = {
                'fields': 'id,Deal_Name,Account_Name,Amount,Stage,Closing_Date,field78',
                'per_page': 200,
                'page': page,
                'sort_by': 'Closing_Date',
                'sort_order': 'desc'
            }
            
            response = requests.get(url, headers=self.crm_headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                deals = data.get('data', [])
                
                if deals:
                    # 受注済み＋期間フィルタ
                    filtered_deals = []
                    for deal in deals:
                        stage = deal.get('Stage')
                        closing_date = deal.get('Closing_Date')
                        
                        if (stage in self.closed_stages and 
                            closing_date and closing_date >= self.target_start_date):
                            filtered_deals.append(deal)
                    
                    all_deals.extend(filtered_deals)
                    print(f"  ページ{page}: {len(deals)}件中{len(filtered_deals)}件が対象")
                    
                    # 古いデータが多い場合は終了
                    old_deals = [d for d in deals if d.get('Closing_Date', '9999') < self.target_start_date]
                    if len(old_deals) > 150:
                        print(f"    古いデータが多くなったため取得終了")
                        break
                    
                    if not data.get('info', {}).get('more_records', False):
                        break
                    page += 1
                else:
                    break
            else:
                print(f"  ❌ ページ{page}取得エラー: {response.status_code}")
                break
        
        print(f"✅ 対象商談: {len(all_deals)}件")
        return all_deals
    
    def get_parent_deals(self, child_deals):
        """子商談から親商談IDを抽出し、親商談を取得"""
        print("\n📊 親商談を取得中...")
        
        # 親商談IDを抽出
        parent_ids = set()
        for deal in child_deals:
            field78 = deal.get('field78')
            if field78 and isinstance(field78, dict):
                parent_id = field78.get('id')
                if parent_id:
                    parent_ids.add(parent_id)
        
        print(f"  親商談ID: {len(parent_ids)}個を発見")
        
        # 親商談を取得
        parent_deals = {}
        
        if parent_ids:
            # バッチで親商談を取得（IDリストで検索）
            # 50個ずつバッチ処理
            parent_id_batches = [list(parent_ids)[i:i+50] for i in range(0, len(parent_ids), 50)]
            
            for batch_num, id_batch in enumerate(parent_id_batches, 1):
                print(f"  バッチ{batch_num}/{len(parent_id_batches)}: {len(id_batch)}件")
                
                # CRMのIDリスト検索を使用
                id_list = ','.join(id_batch)
                url = "https://www.zohoapis.com/crm/v2/Deals"
                params = {
                    'fields': 'id,Deal_Name,Account_Name,Amount,Stage,Closing_Date',
                    'ids': id_list
                }
                
                try:
                    response = requests.get(url, headers=self.crm_headers, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        batch_parents = data.get('data', [])
                        
                        for parent in batch_parents:
                            parent_deals[parent['id']] = parent
                        
                        print(f"    取得: {len(batch_parents)}件")
                    else:
                        print(f"    ❌ エラー: {response.status_code}")
                
                except Exception as e:
                    print(f"    ❌ エラー: {str(e)}")
        
        print(f"✅ 親商談取得完了: {len(parent_deals)}件")
        return parent_deals
    
    def categorize_deals_by_structure(self, child_deals, parent_deals):
        """商談を親子構造で分類"""
        print("\n🔍 商談の親子構造分析...")
        
        categories = {
            'parent_child_sets': [],      # 親子セット
            'parent_only': [],            # 親のみ
            'child_only': [],            # 子のみ（孤児）
            'no_structure': []           # 構造なし
        }
        
        # 子商談をグループ化
        children_by_parent = defaultdict(list)
        
        for child in child_deals:
            field78 = child.get('field78')
            if field78 and isinstance(field78, dict):
                parent_id = field78.get('id')
                if parent_id:
                    children_by_parent[parent_id].append(child)
                else:
                    # field78はあるが親IDがない
                    categories['no_structure'].append(child)
            else:
                # field78がない
                categories['no_structure'].append(child)
        
        # 親子関係の分析
        for parent_id, children in children_by_parent.items():
            parent = parent_deals.get(parent_id)
            
            if parent:
                # 親商談が存在し、受注済みかチェック
                parent_stage = parent.get('Stage')
                parent_closing_date = parent.get('Closing_Date')
                
                is_parent_closed = (
                    parent_stage in self.closed_stages and
                    parent_closing_date and parent_closing_date >= self.target_start_date
                )
                
                if is_parent_closed:
                    # 親子セット
                    parent_amount = parent.get('Amount', 0) or 0
                    children_amount = sum(c.get('Amount', 0) or 0 for c in children)
                    total_amount = parent_amount + children_amount
                    
                    categories['parent_child_sets'].append({
                        'parent': parent,
                        'children': children,
                        'total_amount': total_amount,
                        'parent_amount': parent_amount,
                        'children_amount': children_amount,
                        'deal_count': 1 + len(children)
                    })
                else:
                    # 親が受注済みでない → 子のみ（孤児）
                    for child in children:
                        categories['child_only'].append(child)
            else:
                # 親商談が見つからない → 子のみ（孤児）
                for child in children:
                    categories['child_only'].append(child)
        
        # 親のみ（子商談がない受注済み親商談）
        child_parent_ids = set(children_by_parent.keys())
        for parent_id, parent in parent_deals.items():
            if parent_id not in child_parent_ids:
                # この親商談に対応する受注済み子商談がない
                parent_stage = parent.get('Stage')
                parent_closing_date = parent.get('Closing_Date')
                
                is_parent_closed = (
                    parent_stage in self.closed_stages and
                    parent_closing_date and parent_closing_date >= self.target_start_date
                )
                
                if is_parent_closed:
                    categories['parent_only'].append(parent)
        
        print(f"  親子セット: {len(categories['parent_child_sets'])}組")
        print(f"  親のみ: {len(categories['parent_only'])}件")
        print(f"  子のみ（孤児）: {len(categories['child_only'])}件")
        print(f"  構造なし: {len(categories['no_structure'])}件")
        
        return categories
    
    def get_all_invoices(self):
        """全請求書を取得"""
        print("\n📄 請求書データを取得中...")
        
        url = "https://www.zohoapis.com/books/v3/invoices"
        all_invoices = []
        page = 1
        
        while page <= 10:
            params = {
                'organization_id': self.org_id,
                'per_page': 200,
                'page': page,
                'sort_column': 'date',
                'sort_order': 'D'
            }
            
            response = requests.get(url, headers=self.books_headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                invoices = data.get('invoices', [])
                
                if invoices:
                    # 有効な請求書のみフィルタ
                    valid_invoices = [inv for inv in invoices 
                                    if inv.get('status') not in self.invalid_invoice_statuses]
                    all_invoices.extend(valid_invoices)
                    
                    print(f"  ページ{page}: {len(invoices)}件中{len(valid_invoices)}件が有効")
                    
                    page_context = data.get('page_context', {})
                    if not page_context.get('has_more_page', False):
                        break
                    page += 1
                else:
                    break
            else:
                print(f"  ❌ ページ{page}取得エラー: {response.status_code}")
                break
        
        print(f"✅ 有効な請求書: {len(all_invoices)}件")
        return all_invoices
    
    def match_deals_with_invoices(self, categories, invoices):
        """商談と請求書をマッチング"""
        print("\n🔗 請求漏れ分析中...")
        
        # 請求書をreference_numberでインデックス化
        invoice_map = {}
        for invoice in invoices:
            ref_num = invoice.get('reference_number', '').strip()
            if ref_num:
                invoice_map[ref_num] = invoice
        
        analysis_results = {
            'parent_child_analysis': [],
            'parent_only_analysis': [],
            'child_only_analysis': [],
            'no_structure_analysis': []
        }
        
        # 1. 親子セット分析
        print("  📊 親子セット分析...")
        for pc_set in categories['parent_child_sets']:
            parent = pc_set['parent']
            children = pc_set['children']
            total_deal_amount = pc_set['total_amount']
            parent_amount = pc_set['parent_amount']
            children_amount = pc_set['children_amount']
            
            # 関連する請求書を検索
            related_invoices = []
            
            # 親商談の請求書
            parent_invoice = invoice_map.get(parent['id'])
            if parent_invoice:
                related_invoices.append(('parent', parent_invoice))
            
            # 子商談の請求書
            for child in children:
                child_invoice = invoice_map.get(child['id'])
                if child_invoice:
                    related_invoices.append(('child', child_invoice))
            
            total_invoice_amount = sum(inv[1].get('total', 0) for inv in related_invoices)
            # 商談金額を税込みに変換して比較
            total_deal_amount_with_tax = total_deal_amount * (1 + self.tax_rate)
            amount_diff = total_deal_amount_with_tax - total_invoice_amount
            
            analysis_results['parent_child_analysis'].append({
                'parent_name': parent.get('Deal_Name'),
                'parent_id': parent['id'],
                'parent_amount': parent_amount,
                'children_count': len(children),
                'children_amount': children_amount,
                'total_deal_amount': total_deal_amount,
                'total_deal_amount_with_tax': total_deal_amount_with_tax,
                'invoice_count': len(related_invoices),
                'total_invoice_amount': total_invoice_amount,
                'amount_difference': amount_diff,
                'is_leakage': abs(amount_diff) > 1,
                'invoice_types': [inv[0] for inv in related_invoices]
            })
        
        # 2. 親のみ分析
        print("  📊 親のみ分析...")
        for parent in categories['parent_only']:
            deal_amount = parent.get('Amount', 0) or 0
            deal_amount_with_tax = deal_amount * (1 + self.tax_rate)
            invoice = invoice_map.get(parent['id'])
            
            if invoice:
                invoice_amount = invoice.get('total', 0)
                amount_diff = deal_amount_with_tax - invoice_amount
            else:
                invoice_amount = 0
                amount_diff = deal_amount_with_tax
            
            analysis_results['parent_only_analysis'].append({
                'deal_name': parent.get('Deal_Name'),
                'deal_id': parent['id'],
                'deal_amount': deal_amount,
                'deal_amount_with_tax': deal_amount_with_tax,
                'invoice_amount': invoice_amount,
                'amount_difference': amount_diff,
                'is_leakage': abs(amount_diff) > 1,
                'has_invoice': invoice is not None
            })
        
        # 3. 子のみ分析
        print("  📊 子のみ（孤児）分析...")
        for child in categories['child_only']:
            deal_amount = child.get('Amount', 0) or 0
            deal_amount_with_tax = deal_amount * (1 + self.tax_rate)
            invoice = invoice_map.get(child['id'])
            
            if invoice:
                invoice_amount = invoice.get('total', 0)
                amount_diff = deal_amount_with_tax - invoice_amount
            else:
                invoice_amount = 0
                amount_diff = deal_amount_with_tax
            
            analysis_results['child_only_analysis'].append({
                'deal_name': child.get('Deal_Name'),
                'deal_id': child['id'],
                'deal_amount': deal_amount,
                'deal_amount_with_tax': deal_amount_with_tax,
                'invoice_amount': invoice_amount,
                'amount_difference': amount_diff,
                'is_leakage': abs(amount_diff) > 1,
                'has_invoice': invoice is not None
            })
        
        # 4. 構造なし分析
        print("  📊 構造なし分析...")
        for deal in categories['no_structure']:
            deal_amount = deal.get('Amount', 0) or 0
            deal_amount_with_tax = deal_amount * (1 + self.tax_rate)
            invoice = invoice_map.get(deal['id'])
            
            if invoice:
                invoice_amount = invoice.get('total', 0)
                amount_diff = deal_amount_with_tax - invoice_amount
            else:
                invoice_amount = 0
                amount_diff = deal_amount_with_tax
            
            analysis_results['no_structure_analysis'].append({
                'deal_name': deal.get('Deal_Name'),
                'deal_id': deal['id'],
                'deal_amount': deal_amount,
                'deal_amount_with_tax': deal_amount_with_tax,
                'invoice_amount': invoice_amount,
                'amount_difference': amount_diff,
                'is_leakage': abs(amount_diff) > 1,
                'has_invoice': invoice is not None
            })
        
        return analysis_results
    
    def generate_leakage_report(self, analysis_results):
        """請求漏れレポートを生成"""
        print("\n" + "="*70)
        print("📊 請求漏れ分析レポート")
        print("="*70)
        
        total_leakages = 0
        total_leakage_amount = 0
        
        categories = [
            ('parent_child_analysis', '親子セット'),
            ('parent_only_analysis', '親のみ'),
            ('child_only_analysis', '子のみ（孤児）'),
            ('no_structure_analysis', '構造なし')
        ]
        
        for category_key, category_name in categories:
            category_data = analysis_results[category_key]
            leakages = [item for item in category_data if item['is_leakage']]
            leakage_amount = sum(abs(item['amount_difference']) for item in leakages)
            
            total_leakages += len(leakages)
            total_leakage_amount += leakage_amount
            
            print(f"\n【{category_name}】")
            print(f"  総件数: {len(category_data)}件")
            print(f"  請求漏れ: {len(leakages)}件")
            print(f"  漏れ金額: ¥{leakage_amount:,.0f}")
            
            if leakages:
                print(f"  主な漏れ (上位5件):")
                sorted_leakages = sorted(leakages, key=lambda x: abs(x['amount_difference']), reverse=True)
                for leak in sorted_leakages[:5]:
                    deal_name = leak.get('deal_name') or leak.get('parent_name', 'N/A')
                    amount_diff = leak['amount_difference']
                    has_invoice = leak.get('has_invoice', False)
                    status = "請求書あり" if has_invoice else "請求書なし"
                    
                    print(f"    • {deal_name[:40]}")
                    print(f"      差額: ¥{amount_diff:,.0f} ({status})")
        
        print(f"\n" + "="*70)
        print(f"📈 総合サマリ")
        print(f"  総請求漏れ件数: {total_leakages}件")
        print(f"  総請求漏れ金額: ¥{total_leakage_amount:,.0f}")
        print("="*70)
        
        return analysis_results
    
    def export_analysis_results(self, analysis_results):
        """分析結果をCSVエクスポート"""
        output_dir = Path(__file__).parent / "請求漏れ分析結果_税込み修正版"
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        categories = [
            ('parent_child_analysis', '親子セット'),
            ('parent_only_analysis', '親のみ'),
            ('child_only_analysis', '子のみ孤児'),
            ('no_structure_analysis', '構造なし')
        ]
        
        for category_key, category_name in categories:
            data = analysis_results[category_key]
            if data:
                df = pd.DataFrame(data)
                file_path = output_dir / f"{category_name}_分析_{timestamp}.csv"
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
                print(f"📁 {category_name}分析結果を保存: {file_path}")

def main():
    """メイン処理"""
    print("="*70)
    print("修正版 請求漏れ分析ツール（消費税対応）")
    print("="*70)
    
    analyzer = CorrectInvoiceLeakageAnalyzer()
    
    if not analyzer.org_id:
        print("❌ Books組織IDが取得できませんでした")
        return
    
    print("\n📋 分析設定:")
    print(f"  受注ステージ: {analyzer.closed_stages}")
    print(f"  無効請求書ステータス: {analyzer.invalid_invoice_statuses}")
    print(f"  対象期間: {analyzer.target_start_date}以降")
    print(f"  消費税率: {analyzer.tax_rate * 100:.0f}% (商談=税抜き、請求書=税込みで比較)")
    
    # 1. 受注済み商談（子商談）取得
    child_deals = analyzer.get_all_closed_deals()
    
    if not child_deals:
        print("❌ 受注済み商談が見つかりませんでした")
        return
    
    # 2. 親商談取得
    parent_deals = analyzer.get_parent_deals(child_deals)
    
    # 3. 親子構造分類
    categories = analyzer.categorize_deals_by_structure(child_deals, parent_deals)
    
    # 4. 請求書取得
    invoices = analyzer.get_all_invoices()
    
    # 5. 請求漏れ分析
    analysis_results = analyzer.match_deals_with_invoices(categories, invoices)
    
    # 6. レポート生成
    analyzer.generate_leakage_report(analysis_results)
    
    # 7. 結果エクスポート
    analyzer.export_analysis_results(analysis_results)
    
    print(f"\n✅ 請求漏れ分析完了")

if __name__ == "__main__":
    main()