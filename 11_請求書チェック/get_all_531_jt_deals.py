#!/usr/bin/env python3
"""
JT ETP 531件完全取得
親商談に紐づくすべての子商談を取得
"""
import requests
import json
from pathlib import Path
import pandas as pd
from datetime import datetime
import time

class Complete531DealsGetter:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン"
        self.target_parent_id = "5187347000129692086"
        self.load_tokens()

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
            return False
        return True

    def refresh_token_if_needed(self):
        """必要に応じてトークンをリフレッシュ"""
        print("🔄 トークンリフレッシュを試行中...")
        
        try:
            with open(self.base_path / "zoho_crm_tokens.json", 'r') as f:
                tokens = json.load(f)
            
            refresh_token = tokens.get('refresh_token')
            if not refresh_token:
                print("❌ リフレッシュトークンが見つかりません")
                return False
            
            # リフレッシュ処理
            refresh_url = "https://accounts.zoho.com/oauth/v2/token"
            refresh_data = {
                'refresh_token': refresh_token,
                'client_id': tokens.get('client_id', ''),
                'client_secret': tokens.get('client_secret', ''),
                'grant_type': 'refresh_token'
            }
            
            response = requests.post(refresh_url, data=refresh_data)
            
            if response.status_code == 200:
                new_tokens = response.json()
                tokens['access_token'] = new_tokens['access_token']
                
                # 新しいトークンを保存
                with open(self.base_path / "zoho_crm_tokens.json", 'w') as f:
                    json.dump(tokens, f, indent=2)
                
                self.crm_headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
                print("✅ トークンリフレッシュ成功")
                return True
            else:
                print(f"❌ トークンリフレッシュ失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ トークンリフレッシュエラー: {str(e)}")
            return False

    def get_all_deals_exhaustive(self):
        """すべての商談を徹底的に取得"""
        print(f"📊 JT ETP 531件完全取得開始...")
        print(f"親商談ID: {self.target_parent_id}")
        
        if not self.crm_headers:
            print("❌ 認証情報が不正です")
            return []

        all_child_deals = []
        
        # 複数の検索戦略を試行
        strategies = [
            {'name': '修正時刻降順', 'sort_by': 'Modified_Time', 'sort_order': 'desc'},
            {'name': '作成時刻降順', 'sort_by': 'Created_Time', 'sort_order': 'desc'},
            {'name': '完了予定日降順', 'sort_by': 'Closing_Date', 'sort_order': 'desc'},
            {'name': 'ID降順', 'sort_by': 'id', 'sort_order': 'desc'},
        ]
        
        for strategy in strategies:
            print(f"\n🔍 戦略: {strategy['name']}")
            strategy_deals = self._get_deals_with_strategy(strategy)
            
            # 重複除去して追加
            existing_ids = set(deal['id'] for deal in all_child_deals)
            new_deals = [deal for deal in strategy_deals if deal['id'] not in existing_ids]
            
            all_child_deals.extend(new_deals)
            print(f"  新規追加: {len(new_deals)}件（累計: {len(all_child_deals)}件）")
            
            if len(all_child_deals) >= 531:
                print(f"✅ 目標531件達成！")
                break
            
            time.sleep(1)  # API制限対策
        
        print(f"\n📈 最終取得結果: {len(all_child_deals)}件")
        
        if len(all_child_deals) < 531:
            print(f"⚠️ 目標に{531 - len(all_child_deals)}件不足")
            print("🔧 追加対策を実行...")
            additional_deals = self._try_additional_methods()
            
            existing_ids = set(deal['id'] for deal in all_child_deals)
            new_additional = [deal for deal in additional_deals if deal['id'] not in existing_ids]
            all_child_deals.extend(new_additional)
            
            print(f"📈 追加対策後: {len(all_child_deals)}件")
        
        return all_child_deals

    def _get_deals_with_strategy(self, strategy):
        """特定の戦略で商談を取得"""
        deals = []
        page = 1
        max_pages = 100
        consecutive_empty = 0
        
        while page <= max_pages and consecutive_empty < 3:
            url = "https://www.zohoapis.com/crm/v2/Deals"
            params = {
                'fields': 'id,Deal_Name,Amount,Stage,Closing_Date,Created_Time,Modified_Time,field78',
                'per_page': 200,
                'page': page,
                'sort_by': strategy['sort_by'],
                'sort_order': strategy['sort_order']
            }
            
            try:
                response = requests.get(url, headers=self.crm_headers, params=params)
                
                if response.status_code == 401:
                    print("  🔄 認証エラー - トークンリフレッシュ試行")
                    if self.refresh_token_if_needed():
                        continue
                    else:
                        break
                
                if response.status_code == 200:
                    data = response.json()
                    page_deals = data.get('data', [])
                    
                    if not page_deals:
                        consecutive_empty += 1
                        page += 1
                        continue
                    else:
                        consecutive_empty = 0
                    
                    # JT ETP子商談をフィルタ
                    page_children = 0
                    for deal in page_deals:
                        field78 = deal.get('field78')
                        if field78 and isinstance(field78, dict):
                            parent_ref_id = field78.get('id')
                            if parent_ref_id == self.target_parent_id:
                                deals.append(deal)
                                page_children += 1
                    
                    if page % 10 == 0 or page_children > 0:
                        print(f"    ページ{page}: {page_children}件追加（累計{len(deals)}件）")
                    
                    if not data.get('info', {}).get('more_records', False):
                        break
                    
                    page += 1
                    time.sleep(0.1)
                    
                else:
                    print(f"    エラー: {response.status_code}")
                    if page > 20:  # 20ページ以上取得していれば継続
                        page += 1
                        time.sleep(0.5)
                        continue
                    else:
                        break
                        
            except Exception as e:
                print(f"    エラー: {str(e)}")
                if page > 20:
                    page += 1
                    time.sleep(1)
                    continue
                else:
                    break
        
        return deals

    def _try_additional_methods(self):
        """追加の取得方法を試行"""
        print("🔧 追加取得方法を実行中...")
        additional_deals = []
        
        # 方法1: 日付範囲指定
        date_ranges = [
            ('2024-01-01', '2024-06-30'),
            ('2024-07-01', '2024-12-31'),
            ('2025-01-01', '2025-06-30'),
            ('2025-07-01', '2025-12-31')
        ]
        
        for start_date, end_date in date_ranges:
            print(f"  📅 期間: {start_date} 〜 {end_date}")
            
            url = "https://www.zohoapis.com/crm/v2/Deals"
            params = {
                'fields': 'id,Deal_Name,Amount,Stage,Closing_Date,Created_Time,Modified_Time,field78',
                'criteria': f'(Closing_Date:greater_equal:{start_date})and(Closing_Date:less_equal:{end_date})',
                'per_page': 200
            }
            
            try:
                response = requests.get(url, headers=self.crm_headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    deals = data.get('data', [])
                    
                    period_children = 0
                    for deal in deals:
                        field78 = deal.get('field78')
                        if field78 and isinstance(field78, dict):
                            parent_ref_id = field78.get('id')
                            if parent_ref_id == self.target_parent_id:
                                additional_deals.append(deal)
                                period_children += 1
                    
                    print(f"    追加: {period_children}件")
                    
            except Exception as e:
                print(f"    エラー: {str(e)}")
            
            time.sleep(0.5)
        
        return additional_deals

    def analyze_and_export_all_deals(self, all_deals):
        """全商談を分析してエクスポート"""
        print(f"\n📊 531件分析中...")
        
        total_amount = 0
        deals_with_kouki = []
        deals_without_kouki = []
        
        for deal in all_deals:
            deal_name = deal.get('Deal_Name', '')
            amount = deal.get('Amount', 0) or 0
            
            total_amount += amount
            
            if '後期' in deal_name:
                deals_with_kouki.append(deal)
            else:
                deals_without_kouki.append(deal)
        
        print(f"📈 分析結果:")
        print(f"  全商談数: {len(all_deals)}件")
        print(f"  全商談総額: ¥{total_amount:,.0f}（税抜き）")
        print(f"  「後期」あり: {len(deals_with_kouki)}件")
        print(f"  「後期」なし: {len(deals_without_kouki)}件")
        
        # 「後期」なし商談の集計
        kouki_nashi_amount = sum(deal.get('Amount', 0) or 0 for deal in deals_without_kouki)
        kouki_nashi_amount_with_tax = kouki_nashi_amount * 1.1
        
        print(f"\n🎯 【回答】「後期」なし商談:")
        print(f"  商談数: {len(deals_without_kouki)}件")
        print(f"  総額（税抜き）: ¥{kouki_nashi_amount:,.0f}")
        print(f"  総額（税込み）: ¥{kouki_nashi_amount_with_tax:,.0f}")
        
        # CSV出力
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 全商談
        all_df = pd.DataFrame([{
            'id': d.get('id'),
            'deal_name': d.get('Deal_Name'),
            'amount': d.get('Amount', 0) or 0,
            'stage': d.get('Stage'),
            'closing_date': d.get('Closing_Date'),
            'has_kouki': '後期' in d.get('Deal_Name', '')
        } for d in all_deals])
        
        all_file = f"JT_ETP全531件_{timestamp}.csv"
        all_df.to_csv(all_file, index=False, encoding='utf-8-sig')
        print(f"\n📁 全データ出力: {all_file}")
        
        # 「後期」なし商談
        no_kouki_df = pd.DataFrame([{
            'id': d.get('id'),
            'deal_name': d.get('Deal_Name'),
            'amount': d.get('Amount', 0) or 0,
            'stage': d.get('Stage'),
            'closing_date': d.get('Closing_Date')
        } for d in deals_without_kouki])
        
        no_kouki_file = f"JT_ETP後期なし商談_{timestamp}.csv"
        no_kouki_df.to_csv(no_kouki_file, index=False, encoding='utf-8-sig')
        print(f"📁 後期なし出力: {no_kouki_file}")
        
        return {
            'total_deals': len(all_deals),
            'total_amount': total_amount,
            'kouki_nashi_count': len(deals_without_kouki),
            'kouki_nashi_amount_excluding_tax': kouki_nashi_amount,
            'kouki_nashi_amount_including_tax': kouki_nashi_amount_with_tax
        }

def main():
    """メイン処理"""
    print("="*80)
    print("🎯 JT ETP 531件完全取得")
    print("="*80)
    
    getter = Complete531DealsGetter()
    
    # 1. 531件完全取得
    all_deals = getter.get_all_deals_exhaustive()
    
    if len(all_deals) == 0:
        print("❌ 商談が1件も取得できませんでした")
        print("🔧 手動対処が必要:")
        print("  1. ZohoCRM APIトークンを手動で更新")
        print("  2. ZohoCRM画面で直接確認")
        return
    
    # 2. 分析・エクスポート
    result = getter.analyze_and_export_all_deals(all_deals)
    
    print(f"\n" + "="*80)
    print("📊 最終回答")
    print("="*80)
    print(f"JT ETP 531件のうち商談名に「後期」が含まれない商談:")
    print(f"  商談数: {result['kouki_nashi_count']}件")
    print(f"  総額（税抜き）: ¥{result['kouki_nashi_amount_excluding_tax']:,.0f}")
    print(f"  総額（税込み）: ¥{result['kouki_nashi_amount_including_tax']:,.0f}")
    print("="*80)

if __name__ == "__main__":
    main()