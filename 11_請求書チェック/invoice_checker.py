#!/usr/bin/env python3
"""
ZohoCRMとZohoBooksの請求書チェックツール
商談データと請求書データを照合して不整合を検出します
"""
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import sys

class InvoiceChecker:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン"
        self.crm_tokens_file = self.base_path / "zoho_crm_tokens.json"
        self.books_tokens_file = self.base_path / "zoho_books_tokens.json"
        
        self.crm_headers = None
        self.books_headers = None
        self.organization_id = None
        
        # トークンを読み込み
        self.load_tokens()
    
    def load_tokens(self):
        """トークンファイルを読み込み"""
        # CRMトークン
        if self.crm_tokens_file.exists():
            with open(self.crm_tokens_file, 'r') as f:
                crm_tokens = json.load(f)
                self.crm_headers = {
                    'Authorization': f'Bearer {crm_tokens["access_token"]}'
                }
        else:
            print("❌ CRMトークンファイルが見つかりません")
            print(f"   期待される場所: {self.crm_tokens_file}")
            sys.exit(1)
        
        # Booksトークン
        if self.books_tokens_file.exists():
            with open(self.books_tokens_file, 'r') as f:
                books_tokens = json.load(f)
                self.books_headers = {
                    'Authorization': f'Bearer {books_tokens["access_token"]}'
                }
        else:
            print("⚠️  Booksトークンファイルが見つかりません")
            print(f"   期待される場所: {self.books_tokens_file}")
            print("   Booksデータは取得できません")
    
    def get_organization_id(self) -> Optional[str]:
        """Zoho Books組織IDを取得"""
        if not self.books_headers:
            return None
        
        api_url = "https://books.zoho.com/api/v3/organizations"
        
        try:
            response = requests.get(api_url, headers=self.books_headers)
            if response.status_code == 200:
                data = response.json()
                if 'organizations' in data and data['organizations']:
                    self.organization_id = data['organizations'][0]['organization_id']
                    print(f"✅ 組織ID取得: {self.organization_id}")
                    return self.organization_id
        except Exception as e:
            print(f"❌ 組織ID取得エラー: {str(e)}")
        
        return None
    
    def get_crm_deals(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """CRMから商談データを取得"""
        print("\n📊 CRM商談データを取得中...")
        
        api_url = "https://www.zohoapis.com/crm/v2/Deals"
        params = {
            'fields': 'Deal_Name,Stage,Amount,Closing_Date,Account_Name,Contact_Name,Description',
            'per_page': 200,
            'sort_by': 'Closing_Date',
            'sort_order': 'desc'
        }
        
        # 日付フィルタを追加
        if start_date and end_date:
            # COQLクエリで日付範囲を指定
            params['criteria'] = f"((Closing_Date:between:{start_date}:{end_date}))"
        
        all_deals = []
        page = 1
        
        while True:
            params['page'] = page
            
            try:
                response = requests.get(api_url, headers=self.crm_headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'data' in data and data['data']:
                        all_deals.extend(data['data'])
                        
                        # 次のページがあるか確認
                        if data.get('info', {}).get('more_records', False):
                            page += 1
                        else:
                            break
                    else:
                        break
                elif response.status_code == 204:
                    # データなし
                    break
                else:
                    print(f"❌ CRM APIエラー: {response.status_code}")
                    print(f"   詳細: {response.text}")
                    break
                    
            except Exception as e:
                print(f"❌ CRM接続エラー: {str(e)}")
                break
        
        print(f"✅ {len(all_deals)}件の商談を取得しました")
        return all_deals
    
    def get_books_invoices(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Booksから請求書データを取得"""
        if not self.books_headers or not self.organization_id:
            print("⚠️  Books APIが利用できません")
            return []
        
        print("\n📄 Books請求書データを取得中...")
        
        api_url = "https://books.zoho.com/api/v3/invoices"
        params = {
            'organization_id': self.organization_id,
            'per_page': 200,
            'sort_column': 'date',
            'sort_order': 'D'
        }
        
        # 日付フィルタを追加
        if start_date:
            params['date_start'] = start_date
        if end_date:
            params['date_end'] = end_date
        
        all_invoices = []
        page = 1
        
        while True:
            params['page'] = page
            
            try:
                response = requests.get(api_url, headers=self.books_headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'invoices' in data and data['invoices']:
                        all_invoices.extend(data['invoices'])
                        
                        # 次のページがあるか確認
                        page_context = data.get('page_context', {})
                        if page_context.get('has_more_page', False):
                            page += 1
                        else:
                            break
                    else:
                        break
                else:
                    print(f"❌ Books APIエラー: {response.status_code}")
                    print(f"   詳細: {response.text}")
                    break
                    
            except Exception as e:
                print(f"❌ Books接続エラー: {str(e)}")
                break
        
        print(f"✅ {len(all_invoices)}件の請求書を取得しました")
        return all_invoices
    
    def check_consistency(self, deals: List[Dict], invoices: List[Dict]) -> Dict:
        """商談と請求書の整合性をチェック"""
        print("\n🔍 データ整合性チェック中...")
        
        results = {
            'summary': {},
            'warnings': [],
            'errors': [],
            'matched': [],
            'unmatched_deals': [],
            'unmatched_invoices': []
        }
        
        # 商談データをDataFrameに変換
        if deals:
            deals_df = pd.DataFrame(deals)
            deals_df['Amount'] = pd.to_numeric(deals_df.get('Amount', 0), errors='coerce').fillna(0)
            
            # 完了した商談のみフィルタ
            closed_deals = deals_df[deals_df['Stage'].isin(['Closed Won', '受注', '成約'])] if 'Stage' in deals_df else pd.DataFrame()
        else:
            closed_deals = pd.DataFrame()
        
        # 請求書データをDataFrameに変換
        if invoices:
            invoices_df = pd.DataFrame(invoices)
            invoices_df['total'] = pd.to_numeric(invoices_df.get('total', 0), errors='coerce').fillna(0)
        else:
            invoices_df = pd.DataFrame()
        
        # サマリ情報
        results['summary'] = {
            'total_deals': len(deals),
            'closed_deals': len(closed_deals),
            'total_invoices': len(invoices),
            'total_deal_amount': float(closed_deals['Amount'].sum()) if not closed_deals.empty else 0,
            'total_invoice_amount': float(invoices_df['total'].sum()) if not invoices_df.empty else 0
        }
        
        # 金額差異チェック
        amount_diff = results['summary']['total_deal_amount'] - results['summary']['total_invoice_amount']
        if abs(amount_diff) > 0.01:
            results['warnings'].append({
                'type': '金額不一致',
                'message': f'商談合計と請求書合計に差異があります: ¥{amount_diff:,.2f}',
                'deal_total': results['summary']['total_deal_amount'],
                'invoice_total': results['summary']['total_invoice_amount']
            })
        
        # 商談と請求書のマッチング（簡易版）
        # 実際のマッチングには、顧客名や商談IDなどの関連フィールドが必要
        if not closed_deals.empty and not invoices_df.empty:
            # 顧客名でマッチングを試みる
            for _, deal in closed_deals.iterrows():
                deal_name = deal.get('Deal_Name', '')
                account_name = deal.get('Account_Name', '')
                deal_amount = deal.get('Amount', 0)
                
                # 対応する請求書を探す
                matched = False
                for _, invoice in invoices_df.iterrows():
                    customer_name = invoice.get('customer_name', '')
                    invoice_amount = invoice.get('total', 0)
                    
                    # 顧客名と金額でマッチング（簡易版）
                    if (account_name and customer_name and 
                        account_name.lower() in customer_name.lower() and
                        abs(deal_amount - invoice_amount) < 1):
                        results['matched'].append({
                            'deal_name': deal_name,
                            'customer': account_name,
                            'amount': deal_amount,
                            'invoice_number': invoice.get('invoice_number', ''),
                            'invoice_date': invoice.get('date', '')
                        })
                        matched = True
                        break
                
                if not matched and deal_amount > 0:
                    results['unmatched_deals'].append({
                        'deal_name': deal_name,
                        'customer': account_name,
                        'amount': deal_amount,
                        'closing_date': deal.get('Closing_Date', '')
                    })
        
        # 未マッチの請求書を検出
        if not invoices_df.empty:
            matched_invoice_numbers = [m['invoice_number'] for m in results['matched']]
            for _, invoice in invoices_df.iterrows():
                if invoice.get('invoice_number') not in matched_invoice_numbers:
                    results['unmatched_invoices'].append({
                        'invoice_number': invoice.get('invoice_number', ''),
                        'customer': invoice.get('customer_name', ''),
                        'amount': invoice.get('total', 0),
                        'date': invoice.get('date', ''),
                        'status': invoice.get('status', '')
                    })
        
        return results
    
    def generate_report(self, results: Dict):
        """チェック結果のレポートを生成"""
        print("\n" + "="*60)
        print("📊 請求書チェックレポート")
        print("="*60)
        
        # サマリ
        summary = results['summary']
        print("\n【サマリ】")
        print(f"  商談数: {summary['total_deals']}件 (うち成約: {summary['closed_deals']}件)")
        print(f"  請求書数: {summary['total_invoices']}件")
        print(f"  商談合計金額: ¥{summary['total_deal_amount']:,.0f}")
        print(f"  請求書合計金額: ¥{summary['total_invoice_amount']:,.0f}")
        
        # 警告
        if results['warnings']:
            print("\n⚠️  【警告】")
            for warning in results['warnings']:
                print(f"  - {warning['type']}: {warning['message']}")
        
        # マッチング結果
        print(f"\n✅ マッチした商談-請求書: {len(results['matched'])}件")
        if results['matched'][:5]:  # 最初の5件を表示
            print("  (最初の5件)")
            for match in results['matched'][:5]:
                print(f"    • {match['deal_name']} → 請求書#{match['invoice_number']}")
        
        # 未マッチの商談
        if results['unmatched_deals']:
            print(f"\n❌ 請求書がない商談: {len(results['unmatched_deals'])}件")
            for deal in results['unmatched_deals'][:5]:  # 最初の5件を表示
                print(f"    • {deal['deal_name']} ({deal['customer']}) - ¥{deal['amount']:,.0f}")
        
        # 未マッチの請求書
        if results['unmatched_invoices']:
            print(f"\n❌ 商談がない請求書: {len(results['unmatched_invoices'])}件")
            for invoice in results['unmatched_invoices'][:5]:  # 最初の5件を表示
                print(f"    • 請求書#{invoice['invoice_number']} ({invoice['customer']}) - ¥{invoice['amount']:,.0f}")
        
        # CSVエクスポート
        self.export_to_csv(results)
    
    def export_to_csv(self, results: Dict):
        """結果をCSVファイルにエクスポート"""
        output_dir = Path(__file__).parent / "チェック結果"
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 未マッチ商談をエクスポート
        if results['unmatched_deals']:
            df = pd.DataFrame(results['unmatched_deals'])
            file_path = output_dir / f"未請求商談_{timestamp}.csv"
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"\n📁 未請求商談リストを保存: {file_path}")
        
        # 未マッチ請求書をエクスポート
        if results['unmatched_invoices']:
            df = pd.DataFrame(results['unmatched_invoices'])
            file_path = output_dir / f"商談なし請求書_{timestamp}.csv"
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"📁 商談なし請求書リストを保存: {file_path}")
        
        # サマリをエクスポート
        summary_data = {
            '項目': ['商談数', '成約商談数', '請求書数', '商談合計金額', '請求書合計金額', '差額'],
            '値': [
                results['summary']['total_deals'],
                results['summary']['closed_deals'],
                results['summary']['total_invoices'],
                results['summary']['total_deal_amount'],
                results['summary']['total_invoice_amount'],
                results['summary']['total_deal_amount'] - results['summary']['total_invoice_amount']
            ]
        }
        df = pd.DataFrame(summary_data)
        file_path = output_dir / f"チェックサマリ_{timestamp}.csv"
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"📁 サマリを保存: {file_path}")

def main():
    """メイン処理"""
    print("="*60)
    print("Zoho CRM & Books 請求書チェックツール")
    print("="*60)
    
    checker = InvoiceChecker()
    
    # Books組織IDを取得
    if checker.books_headers:
        checker.get_organization_id()
    
    # 期間を指定（過去3ヶ月）
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)
    
    print(f"\n📅 チェック期間: {start_date} 〜 {end_date}")
    
    # データ取得
    deals = checker.get_crm_deals(
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )
    
    invoices = checker.get_books_invoices(
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )
    
    # 整合性チェック
    if deals or invoices:
        results = checker.check_consistency(deals, invoices)
        checker.generate_report(results)
    else:
        print("\n⚠️  データが取得できませんでした")
        print("   トークンの有効性を確認してください")
        print("   refresh_all_tokens.py を実行して再認証してください")

if __name__ == "__main__":
    main()