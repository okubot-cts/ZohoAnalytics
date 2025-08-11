#!/usr/bin/env python3
"""
ZohoCRM商談の親子構造分析スクリプト
商談の階層関係と請求書への影響を調査
"""
import requests
import json
from pathlib import Path
from collections import defaultdict
import pandas as pd
from datetime import datetime

class DealHierarchyAnalyzer:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン"
        self.load_tokens()
        self.org_id = self.get_org_id()
    
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
    
    def get_deal_fields_info(self):
        """商談モジュールのフィールド情報を取得"""
        print("📋 商談フィールド構造を分析中...")
        
        url = "https://www.zohoapis.com/crm/v2/settings/fields"
        params = {'module': 'Deals'}
        
        try:
            response = requests.get(url, headers=self.crm_headers, params=params)
            if response.status_code == 200:
                field_data = response.json()
                fields = field_data.get('fields', [])
                
                # 親子関係に関連しそうなフィールドを特定
                hierarchy_fields = []
                for field in fields:
                    field_name = field.get('api_name', '')
                    field_label = field.get('field_label', '')
                    field_type = field.get('data_type', '')
                    
                    # 親子関係を示すフィールドを検索
                    if any(keyword in field_name.lower() for keyword in 
                           ['parent', 'child', 'related', 'master', 'sub', 'main', 'group']):
                        hierarchy_fields.append({
                            'api_name': field_name,
                            'label': field_label,
                            'type': field_type,
                            'required': field.get('required', False)
                        })
                
                print(f"✅ 全フィールド数: {len(fields)}個")
                print(f"✅ 階層関係候補フィールド: {len(hierarchy_fields)}個")
                
                if hierarchy_fields:
                    print("\n🔍 階層関係候補フィールド:")
                    for field in hierarchy_fields:
                        print(f"  - {field['api_name']} ({field['label']}) [{field['type']}]")
                
                return fields, hierarchy_fields
        
        except Exception as e:
            print(f"❌ フィールド情報取得エラー: {str(e)}")
        
        return [], []
    
    def get_sample_deals_with_all_fields(self):
        """全フィールド付きサンプル商談を取得"""
        print("\n📊 全フィールド付き商談データを取得中...")
        
        url = "https://www.zohoapis.com/crm/v2/Deals"
        params = {
            'per_page': 50,  # 多めのサンプルを取得
            'sort_by': 'Modified_Time',
            'sort_order': 'desc'
        }
        
        try:
            response = requests.get(url, headers=self.crm_headers, params=params)
            if response.status_code == 200:
                data = response.json()
                deals = data.get('data', [])
                print(f"✅ {len(deals)}件の商談を取得")
                return deals
        
        except Exception as e:
            print(f"❌ 商談データ取得エラー: {str(e)}")
        
        return []
    
    def analyze_hierarchy_patterns(self, deals):
        """商談データから階層パターンを分析"""
        print("\n🔍 階層パターン分析中...")
        
        # 各種パターンを分析
        patterns = {
            'name_patterns': defaultdict(list),        # 商談名のパターン
            'account_groups': defaultdict(list),       # 取引先ごとのグループ
            'amount_relationships': [],                # 金額の関係性
            'date_relationships': [],                  # 日付の関係性
            'potential_parents': [],                   # 親商談候補
            'potential_children': [],                  # 子商談候補
            'field_analysis': {}                       # フィールド分析結果
        }
        
        # 1. 商談名パターン分析
        print("  📝 商談名パターン分析...")
        for deal in deals:
            deal_name = deal.get('Deal_Name', '')
            if deal_name:
                # アンダースコアで分割してパターンを抽出
                parts = deal_name.split('_')
                if len(parts) >= 2:
                    base_pattern = parts[0]  # 最初の部分（会社名など）
                    patterns['name_patterns'][base_pattern].append(deal)
        
        # 2. 取引先ごとのグループ分析
        print("  🏢 取引先グループ分析...")
        for deal in deals:
            account = deal.get('Account_Name', {})
            if isinstance(account, dict) and 'name' in account:
                account_name = account['name']
                patterns['account_groups'][account_name].append(deal)
        
        # 3. 親子関係候補の特定
        print("  👪 親子関係候補の特定...")
        
        # 商談名パターンで親子関係を推測
        for base_pattern, group_deals in patterns['name_patterns'].items():
            if len(group_deals) > 1:  # 複数の商談がある場合
                # 金額順でソート（親商談は通常金額が大きい傾向）
                sorted_deals = sorted(group_deals, key=lambda x: x.get('Amount', 0) or 0, reverse=True)
                
                # 最大金額の商談を親候補とする
                parent_candidate = sorted_deals[0]
                child_candidates = sorted_deals[1:]
                
                patterns['potential_parents'].append({
                    'parent': parent_candidate,
                    'children': child_candidates,
                    'pattern': base_pattern,
                    'total_amount': sum(d.get('Amount', 0) or 0 for d in group_deals),
                    'count': len(group_deals)
                })
        
        # 4. 特殊フィールドの分析
        print("  🔍 特殊フィールド分析...")
        if deals:
            first_deal = deals[0]
            
            # 親子関係に使用されそうなフィールドを探す
            suspected_hierarchy_fields = []
            for field_name, field_value in first_deal.items():
                if any(keyword in field_name.lower() for keyword in 
                       ['parent', 'master', 'main', 'group', 'related']):
                    suspected_hierarchy_fields.append(field_name)
            
            patterns['field_analysis']['suspected_fields'] = suspected_hierarchy_fields
            
            # 実際の値を確認
            for field in suspected_hierarchy_fields:
                field_values = []
                for deal in deals[:10]:  # 最初の10件で確認
                    value = deal.get(field)
                    if value is not None and value != '':
                        field_values.append(value)
                
                patterns['field_analysis'][field] = {
                    'sample_values': field_values[:5],  # 最初の5個の値
                    'unique_count': len(set(str(v) for v in field_values))
                }
        
        return patterns
    
    def analyze_invoice_relationships(self, hierarchy_patterns):
        """請求書との関係性を分析"""
        print("\n💰 請求書との関係性分析...")
        
        # Books請求書データを取得
        url = "https://www.zohoapis.com/books/v3/invoices"
        params = {
            'organization_id': self.org_id,
            'per_page': 100,
            'sort_column': 'date',
            'sort_order': 'D'
        }
        
        try:
            response = requests.get(url, headers=self.books_headers, params=params)
            if response.status_code == 200:
                invoices = response.json().get('invoices', [])
                print(f"✅ {len(invoices)}件の請求書を取得")
                
                # 親子商談と請求書の関係を分析
                invoice_relationships = []
                
                for parent_group in hierarchy_patterns['potential_parents']:
                    parent_deal = parent_group['parent']
                    child_deals = parent_group['children']
                    
                    # この商談グループに関連する請求書を検索
                    related_invoices = []
                    
                    # reference_numberで検索
                    for invoice in invoices:
                        ref_num = invoice.get('reference_number', '').strip()
                        
                        # 親商談IDまたは子商談IDと一致するか
                        if ref_num == parent_deal['id']:
                            related_invoices.append(('parent', invoice))
                        else:
                            for child in child_deals:
                                if ref_num == child['id']:
                                    related_invoices.append(('child', invoice))
                                    break
                    
                    if related_invoices:
                        invoice_relationships.append({
                            'pattern': parent_group['pattern'],
                            'parent_deal': parent_deal,
                            'child_deals': child_deals,
                            'related_invoices': related_invoices,
                            'total_deal_amount': parent_group['total_amount'],
                            'total_invoice_amount': sum(inv[1].get('total', 0) for inv in related_invoices)
                        })
                
                return invoice_relationships
        
        except Exception as e:
            print(f"❌ 請求書分析エラー: {str(e)}")
        
        return []
    
    def generate_hierarchy_report(self, patterns, invoice_relationships):
        """階層分析レポートを生成"""
        print("\n" + "="*70)
        print("📊 ZohoCRM商談階層構造分析レポート")
        print("="*70)
        
        # 1. 商談名パターンサマリ
        print(f"\n【商談名パターン分析】")
        print(f"  検出パターン数: {len(patterns['name_patterns'])}個")
        
        top_patterns = sorted(patterns['name_patterns'].items(), 
                             key=lambda x: len(x[1]), reverse=True)[:10]
        
        for pattern, deals in top_patterns:
            if len(deals) > 1:  # 複数商談があるパターンのみ
                total_amount = sum(d.get('Amount', 0) or 0 for d in deals)
                print(f"  📋 {pattern}: {len(deals)}件 (合計: ¥{total_amount:,.0f})")
                
                for deal in deals[:3]:  # 最初の3件を表示
                    amount = deal.get('Amount', 0) or 0
                    stage = deal.get('Stage', 'N/A')
                    print(f"      - {deal.get('Deal_Name', 'N/A')[:40]} (¥{amount:,.0f}, {stage})")
        
        # 2. 親子関係候補
        print(f"\n【親子関係候補分析】")
        print(f"  親商談候補: {len(patterns['potential_parents'])}グループ")
        
        for i, group in enumerate(patterns['potential_parents'][:5], 1):
            parent = group['parent']
            children = group['children']
            
            print(f"\n  {i}. パターン: {group['pattern']}")
            print(f"     親商談候補: {parent.get('Deal_Name', 'N/A')}")
            print(f"       金額: ¥{parent.get('Amount', 0):,.0f}")
            print(f"       ステージ: {parent.get('Stage', 'N/A')}")
            
            print(f"     子商談候補 ({len(children)}件):")
            for child in children[:3]:
                print(f"       - {child.get('Deal_Name', 'N/A')[:30]} (¥{child.get('Amount', 0):,.0f})")
        
        # 3. フィールド分析
        print(f"\n【フィールド分析】")
        suspected_fields = patterns['field_analysis'].get('suspected_fields', [])
        print(f"  階層関係候補フィールド: {len(suspected_fields)}個")
        
        for field in suspected_fields:
            field_info = patterns['field_analysis'].get(field, {})
            sample_values = field_info.get('sample_values', [])
            unique_count = field_info.get('unique_count', 0)
            
            print(f"    {field}:")
            print(f"      サンプル値: {sample_values}")
            print(f"      ユニーク数: {unique_count}")
        
        # 4. 請求書との関係
        print(f"\n【請求書との関係性】")
        print(f"  関連する請求書グループ: {len(invoice_relationships)}グループ")
        
        for i, rel in enumerate(invoice_relationships, 1):
            print(f"\n  {i}. パターン: {rel['pattern']}")
            print(f"     親商談: {rel['parent_deal'].get('Deal_Name', 'N/A')}")
            print(f"     子商談数: {len(rel['child_deals'])}件")
            print(f"     関連請求書: {len(rel['related_invoices'])}件")
            print(f"     商談合計: ¥{rel['total_deal_amount']:,.0f}")
            print(f"     請求合計: ¥{rel['total_invoice_amount']:,.0f}")
            
            for invoice_type, invoice in rel['related_invoices']:
                print(f"       - {invoice_type}請求: {invoice.get('invoice_number')} "
                      f"(¥{invoice.get('total', 0):,.0f})")
        
        # 5. 課題と提案
        print(f"\n【発見と提案】")
        
        multi_deal_patterns = [p for p in patterns['name_patterns'].values() if len(p) > 1]
        total_multi_deals = sum(len(p) for p in multi_deal_patterns)
        
        print(f"  ✅ 複数商談パターン: {len(multi_deal_patterns)}グループ")
        print(f"  ✅ 階層関係の可能性がある商談: {total_multi_deals}件")
        
        if not suspected_fields:
            print(f"  ⚠️  明示的な親子関係フィールドは検出されませんでした")
            print(f"      → 商談名や取引先による暗黙的なグループ化が行われている可能性")
        
        if invoice_relationships:
            print(f"  ✅ 請求書との関連が確認できたグループ: {len(invoice_relationships)}個")
        else:
            print(f"  ⚠️  現在のデータでは請求書との明確な関連は確認できませんでした")
            print(f"      → より広い期間でのデータ分析が必要な可能性")
    
    def export_hierarchy_data(self, patterns):
        """階層データをCSVにエクスポート"""
        output_dir = Path(__file__).parent / "階層分析結果"
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 親子関係候補をエクスポート
        if patterns['potential_parents']:
            hierarchy_data = []
            for group in patterns['potential_parents']:
                parent = group['parent']
                
                # 親商談の情報
                hierarchy_data.append({
                    'グループパターン': group['pattern'],
                    '関係': '親商談候補',
                    '商談ID': parent['id'],
                    '商談名': parent.get('Deal_Name', ''),
                    '金額': parent.get('Amount', 0),
                    'ステージ': parent.get('Stage', ''),
                    '取引先': parent.get('Account_Name', {}).get('name', '') if isinstance(parent.get('Account_Name'), dict) else '',
                    'グループ商談数': group['count'],
                    'グループ合計金額': group['total_amount']
                })
                
                # 子商談の情報
                for child in group['children']:
                    hierarchy_data.append({
                        'グループパターン': group['pattern'],
                        '関係': '子商談候補',
                        '商談ID': child['id'],
                        '商談名': child.get('Deal_Name', ''),
                        '金額': child.get('Amount', 0),
                        'ステージ': child.get('Stage', ''),
                        '取引先': child.get('Account_Name', {}).get('name', '') if isinstance(child.get('Account_Name'), dict) else '',
                        'グループ商談数': group['count'],
                        'グループ合計金額': group['total_amount']
                    })
            
            df = pd.DataFrame(hierarchy_data)
            file_path = output_dir / f"商談階層分析_{timestamp}.csv"
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"\n📁 階層分析結果を保存: {file_path}")

def main():
    """メイン処理"""
    print("="*70)
    print("ZohoCRM 商談階層構造分析ツール")
    print("="*70)
    
    analyzer = DealHierarchyAnalyzer()
    
    if not analyzer.org_id:
        print("❌ Books組織IDが取得できませんでした")
        return
    
    # 1. フィールド情報の取得
    fields, hierarchy_fields = analyzer.get_deal_fields_info()
    
    # 2. サンプル商談データの取得
    deals = analyzer.get_sample_deals_with_all_fields()
    
    if not deals:
        print("❌ 商談データが取得できませんでした")
        return
    
    # 3. 階層パターンの分析
    patterns = analyzer.analyze_hierarchy_patterns(deals)
    
    # 4. 請求書との関係性分析
    invoice_relationships = analyzer.analyze_invoice_relationships(patterns)
    
    # 5. レポート生成
    analyzer.generate_hierarchy_report(patterns, invoice_relationships)
    
    # 6. データエクスポート
    analyzer.export_hierarchy_data(patterns)
    
    print("\n" + "="*70)
    print("階層構造分析完了")

if __name__ == "__main__":
    main()