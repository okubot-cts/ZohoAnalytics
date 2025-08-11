#!/usr/bin/env python3
"""
改良版 ZohoCRM・Books 商談-請求書マッチングツール
reference_numberを活用した高精度な紐づけを実装
"""
import requests
import json
from pathlib import Path
from datetime import datetime
import pandas as pd

class ImprovedInvoiceMatcher:
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
    
    def get_all_deals(self):
        """全商談データを取得"""
        print("📊 商談データを取得中...")
        
        url = "https://www.zohoapis.com/crm/v2/Deals"
        all_deals = []
        page = 1
        
        while True:
            params = {
                'fields': 'id,Deal_Name,Account_Name,Contact_Name,Amount,Stage,Closing_Date,Created_Time,Modified_Time',
                'per_page': 200,
                'page': page,
                'sort_by': 'Modified_Time',
                'sort_order': 'desc'
            }
            
            response = requests.get(url, headers=self.crm_headers, params=params)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    all_deals.extend(data['data'])
                    if data.get('info', {}).get('more_records', False):
                        page += 1
                    else:
                        break
                else:
                    break
            else:
                break
        
        print(f"✅ {len(all_deals)}件の商談を取得")
        return all_deals
    
    def get_all_invoices(self):
        """全請求書データを取得"""
        print("📄 請求書データを取得中...")
        
        url = "https://www.zohoapis.com/books/v3/invoices"
        all_invoices = []
        page = 1
        
        while True:
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
                if 'invoices' in data and data['invoices']:
                    all_invoices.extend(data['invoices'])
                    page_context = data.get('page_context', {})
                    if page_context.get('has_more_page', False):
                        page += 1
                    else:
                        break
                else:
                    break
            else:
                break
        
        print(f"✅ {len(all_invoices)}件の請求書を取得")
        return all_invoices
    
    def match_deals_invoices(self, deals, invoices):
        """商談と請求書をマッチング"""
        print("\n🔗 商談-請求書マッチング実行中...")
        
        results = {
            'exact_matches': [],      # reference_number完全一致
            'partial_matches': [],    # 部分的マッチング
            'unmatched_deals': [],    # 未マッチ商談
            'unmatched_invoices': [], # 未マッチ請求書
            'statistics': {}
        }
        
        # 商談IDをキーとする辞書を作成
        deals_dict = {deal['id']: deal for deal in deals}
        
        # マッチング実行
        matched_deal_ids = set()
        matched_invoice_ids = set()
        
        print("  方法1: reference_number による完全マッチング...")
        for invoice in invoices:
            reference_number = invoice.get('reference_number', '').strip()
            
            if reference_number and reference_number in deals_dict:
                deal = deals_dict[reference_number]
                
                results['exact_matches'].append({
                    'deal_id': deal['id'],
                    'deal_name': deal.get('Deal_Name', 'N/A'),
                    'deal_amount': deal.get('Amount', 0),
                    'deal_stage': deal.get('Stage', 'N/A'),
                    'invoice_id': invoice['invoice_id'],
                    'invoice_number': invoice.get('invoice_number', 'N/A'),
                    'invoice_amount': invoice.get('total', 0),
                    'customer_name': invoice.get('customer_name', 'N/A'),
                    'match_type': 'reference_number'
                })
                
                matched_deal_ids.add(deal['id'])
                matched_invoice_ids.add(invoice['invoice_id'])
        
        print(f"    ✅ {len(results['exact_matches'])}組の完全マッチ")
        
        # 部分マッチング（顧客名＋金額＋日付の組み合わせ）
        print("  方法2: 顧客名・金額・日付による部分マッチング...")
        
        unmatched_deals = [d for d in deals if d['id'] not in matched_deal_ids]
        unmatched_invoices = [i for i in invoices if i['invoice_id'] not in matched_invoice_ids]
        
        for deal in unmatched_deals:
            # 成約した商談のみ対象
            if deal.get('Stage') not in ['Closed Won', '受注', '成約']:
                continue
            
            deal_account = deal.get('Account_Name', {})
            deal_customer = deal_account.get('name', '') if isinstance(deal_account, dict) else ''
            deal_amount = deal.get('Amount', 0) or 0
            
            best_match = None
            best_score = 0
            
            for invoice in unmatched_invoices:
                if invoice['invoice_id'] in matched_invoice_ids:
                    continue
                
                score = 0
                match_details = []
                
                # 顧客名マッチング
                invoice_customer = invoice.get('customer_name', '')
                if deal_customer and invoice_customer:
                    if deal_customer == invoice_customer:
                        score += 50
                        match_details.append('顧客名完全一致')
                    elif deal_customer in invoice_customer or invoice_customer in deal_customer:
                        score += 30
                        match_details.append('顧客名部分一致')
                
                # 金額マッチング
                invoice_amount = invoice.get('total', 0) or 0
                if deal_amount > 0 and invoice_amount > 0:
                    if abs(deal_amount - invoice_amount) <= 1:
                        score += 40
                        match_details.append('金額完全一致')
                    elif abs(deal_amount - invoice_amount) <= deal_amount * 0.05:  # 5%以内
                        score += 20
                        match_details.append('金額近似一致')
                
                # 日付マッチング（簡易）
                deal_date = deal.get('Closing_Date', '')
                invoice_date = invoice.get('date', '')
                if deal_date and invoice_date:
                    # 日付の詳細比較は省略（文字列レベルでの簡易チェック）
                    if deal_date == invoice_date:
                        score += 20
                        match_details.append('日付一致')
                
                if score > best_score and score >= 30:  # 最低30点以上
                    best_match = {
                        'invoice': invoice,
                        'score': score,
                        'match_details': match_details
                    }
                    best_score = score
            
            if best_match:
                invoice = best_match['invoice']
                results['partial_matches'].append({
                    'deal_id': deal['id'],
                    'deal_name': deal.get('Deal_Name', 'N/A'),
                    'deal_amount': deal_amount,
                    'deal_stage': deal.get('Stage', 'N/A'),
                    'invoice_id': invoice['invoice_id'],
                    'invoice_number': invoice.get('invoice_number', 'N/A'),
                    'invoice_amount': invoice.get('total', 0),
                    'customer_name': invoice.get('customer_name', 'N/A'),
                    'match_type': 'partial',
                    'match_score': best_match['score'],
                    'match_details': ', '.join(best_match['match_details'])
                })
                
                matched_deal_ids.add(deal['id'])
                matched_invoice_ids.add(invoice['invoice_id'])
        
        print(f"    ✅ {len(results['partial_matches'])}組の部分マッチ")
        
        # 未マッチの商談と請求書
        for deal in deals:
            if deal['id'] not in matched_deal_ids:
                results['unmatched_deals'].append({
                    'deal_id': deal['id'],
                    'deal_name': deal.get('Deal_Name', 'N/A'),
                    'deal_amount': deal.get('Amount', 0),
                    'deal_stage': deal.get('Stage', 'N/A'),
                    'account_name': deal.get('Account_Name', {}).get('name', 'N/A') if isinstance(deal.get('Account_Name'), dict) else 'N/A'
                })
        
        for invoice in invoices:
            if invoice['invoice_id'] not in matched_invoice_ids:
                results['unmatched_invoices'].append({
                    'invoice_id': invoice['invoice_id'],
                    'invoice_number': invoice.get('invoice_number', 'N/A'),
                    'invoice_amount': invoice.get('total', 0),
                    'customer_name': invoice.get('customer_name', 'N/A'),
                    'status': invoice.get('status', 'N/A')
                })
        
        # 統計情報
        results['statistics'] = {
            'total_deals': len(deals),
            'total_invoices': len(invoices),
            'exact_matches': len(results['exact_matches']),
            'partial_matches': len(results['partial_matches']),
            'unmatched_deals': len(results['unmatched_deals']),
            'unmatched_invoices': len(results['unmatched_invoices']),
            'match_rate': (len(results['exact_matches']) + len(results['partial_matches'])) / len(deals) * 100 if deals else 0
        }
        
        return results
    
    def generate_report(self, results):
        """マッチング結果レポート生成"""
        stats = results['statistics']
        
        print("\n" + "="*70)
        print("📊 商談-請求書マッチング結果レポート")
        print("="*70)
        
        print(f"\n【統計サマリ】")
        print(f"  総商談数: {stats['total_deals']}件")
        print(f"  総請求書数: {stats['total_invoices']}件")
        print(f"  完全マッチ: {stats['exact_matches']}件")
        print(f"  部分マッチ: {stats['partial_matches']}件") 
        print(f"  マッチ率: {stats['match_rate']:.1f}%")
        print(f"  未マッチ商談: {stats['unmatched_deals']}件")
        print(f"  未マッチ請求書: {stats['unmatched_invoices']}件")
        
        # 完全マッチ
        if results['exact_matches']:
            print(f"\n✅ 【完全マッチ ({len(results['exact_matches'])}件)】")
            for match in results['exact_matches']:
                print(f"  • {match['deal_name']} → {match['invoice_number']}")
                print(f"    商談金額: ¥{match['deal_amount']:,.0f} | 請求金額: ¥{match['invoice_amount']:,.0f}")
                print(f"    顧客: {match['customer_name']}")
        
        # 部分マッチ（スコア高い順）
        if results['partial_matches']:
            print(f"\n🔍 【部分マッチ ({len(results['partial_matches'])}件)】")
            partial_sorted = sorted(results['partial_matches'], key=lambda x: x['match_score'], reverse=True)
            for match in partial_sorted[:10]:  # 上位10件
                print(f"  • {match['deal_name']} → {match['invoice_number']} (スコア: {match['match_score']})")
                print(f"    商談金額: ¥{match['deal_amount']:,.0f} | 請求金額: ¥{match['invoice_amount']:,.0f}")
                print(f"    マッチ理由: {match['match_details']}")
        
        # 未マッチ商談（成約済みのもの）
        unmatched_closed = [d for d in results['unmatched_deals'] if d['deal_stage'] in ['Closed Won', '受注', '成約']]
        if unmatched_closed:
            print(f"\n❌ 【未請求の成約商談 ({len(unmatched_closed)}件)】")
            for deal in unmatched_closed[:10]:
                print(f"  • {deal['deal_name']} (¥{deal['deal_amount']:,.0f})")
                print(f"    顧客: {deal['account_name']} | ステージ: {deal['deal_stage']}")
        
        # CSVエクスポート
        self.export_results_to_csv(results)
    
    def export_results_to_csv(self, results):
        """結果をCSVにエクスポート"""
        output_dir = Path(__file__).parent / "マッチング結果"
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 完全マッチ
        if results['exact_matches']:
            df = pd.DataFrame(results['exact_matches'])
            file_path = output_dir / f"完全マッチ_{timestamp}.csv"
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"\n📁 完全マッチリストを保存: {file_path}")
        
        # 部分マッチ
        if results['partial_matches']:
            df = pd.DataFrame(results['partial_matches'])
            file_path = output_dir / f"部分マッチ_{timestamp}.csv"
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"📁 部分マッチリストを保存: {file_path}")
        
        # 未マッチ商談
        if results['unmatched_deals']:
            df = pd.DataFrame(results['unmatched_deals'])
            file_path = output_dir / f"未マッチ商談_{timestamp}.csv"
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"📁 未マッチ商談リストを保存: {file_path}")

def main():
    """メイン処理"""
    print("="*70)
    print("ZohoCRM・Books 改良版マッチングツール")
    print("="*70)
    
    matcher = ImprovedInvoiceMatcher()
    
    if not matcher.org_id:
        print("❌ Books組織IDが取得できませんでした")
        return
    
    # データ取得
    deals = matcher.get_all_deals()
    invoices = matcher.get_all_invoices()
    
    if not deals and not invoices:
        print("❌ データが取得できませんでした")
        return
    
    # マッチング実行
    results = matcher.match_deals_invoices(deals, invoices)
    
    # レポート生成
    matcher.generate_report(results)
    
    print("\n" + "="*70)
    print("マッチング完了")

if __name__ == "__main__":
    main()