#!/usr/bin/env python3
"""
CRMトークン更新後に包括的分析を実行
"""
import requests
import json
from pathlib import Path
from datetime import datetime
import time

def load_config():
    """設定ファイルを読み込み"""
    config_path = Path(__file__).parent.parent / "01_Zoho_API" / "設定ファイル" / "zoho_config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def refresh_crm_token():
    """CRMトークンを更新"""
    print("🔄 ZohoCRMトークンを更新中...")
    
    try:
        config = load_config()
        
        # 既存のトークンを読み込み
        token_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン" / "zoho_crm_tokens.json"
        with open(token_path, 'r') as f:
            old_tokens = json.load(f)
        
        url = "https://accounts.zoho.com/oauth/v2/token"
        
        payload = {
            'refresh_token': old_tokens['refresh_token'],
            'client_id': config['client_id'],
            'client_secret': config['client_secret'],
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(url, data=payload, timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            
            # タイムスタンプ追加
            token_data['expires_at'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
            token_data['updated_at'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
            
            # リフレッシュトークン保持
            if 'refresh_token' not in token_data:
                token_data['refresh_token'] = old_tokens['refresh_token']
            
            # 保存
            with open(token_path, 'w', encoding='utf-8') as f:
                json.dump(token_data, f, ensure_ascii=False, indent=2)
            
            print("✅ CRMトークン更新成功")
            return token_data
        else:
            print(f"❌ CRMトークン更新エラー: {response.status_code}")
            return None
    
    except Exception as e:
        print(f"❌ CRMトークン更新例外: {str(e)}")
        return None

def get_sample_deals(headers, sample_size=1000):
    """サンプル商談を取得（2024/4/1以降）"""
    print(f"📊 商談サンプル取得中（最大{sample_size}件）...")
    
    url = "https://www.zohoapis.com/crm/v2/Deals"
    all_deals = []
    page = 1
    
    while len(all_deals) < sample_size and page <= 10:
        params = {
            'fields': 'id,Deal_Name,Account_Name,Amount,Stage,Closing_Date,field78',
            'per_page': min(200, sample_size - len(all_deals)),
            'page': page,
            'sort_by': 'Closing_Date',
            'sort_order': 'desc'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                deals = data.get('data', [])
                
                if deals:
                    # 2024/4/1以降でフィルタ
                    target_deals = []
                    for d in deals:
                        closing_date = d.get('Closing_Date')
                        if closing_date and closing_date >= '2024-04-01':
                            target_deals.append(d)
                    all_deals.extend(target_deals)
                    
                    print(f"  ページ{page}: {len(target_deals)}件追加（累計: {len(all_deals)}件）")
                    
                    if not data.get('info', {}).get('more_records', False):
                        break
                    page += 1
                else:
                    break
            else:
                print(f"  ❌ エラー: {response.status_code}")
                break
        
        except Exception as e:
            print(f"  ❌ 例外: {str(e)}")
            break
        
        time.sleep(0.5)
    
    print(f"✅ 商談取得完了: {len(all_deals)}件")
    return all_deals

def analyze_deal_structure_simple(deals):
    """シンプルな商談構造分析"""
    print(f"\n🔍 商談構造分析中（{len(deals)}件）...")
    
    # ステージ別集計
    stage_stats = {}
    # 親子関係集計
    has_parent = 0
    no_parent = 0
    parent_ids = set()
    
    total_amount = 0
    
    for deal in deals:
        stage = deal.get('Stage', '不明')
        amount = deal.get('Amount', 0) or 0
        total_amount += amount
        
        # ステージ別
        if stage not in stage_stats:
            stage_stats[stage] = {'count': 0, 'amount': 0}
        stage_stats[stage]['count'] += 1
        stage_stats[stage]['amount'] += amount
        
        # 親子関係
        field78 = deal.get('field78')
        if field78 and isinstance(field78, dict) and field78.get('id'):
            has_parent += 1
            parent_ids.add(field78.get('id'))
        else:
            no_parent += 1
    
    print(f"  📋 ステージ別統計:")
    for stage, stats in sorted(stage_stats.items(), key=lambda x: x[1]['amount'], reverse=True):
        count = stats['count']
        amount = stats['amount']
        amount_with_tax = amount * 1.10
        print(f"    {stage}: {count}件 - ¥{amount:,.0f}（税抜き）¥{amount_with_tax:,.0f}（税込み）")
    
    print(f"\n  🏗️ 親子関係:")
    print(f"    親子関係あり: {has_parent}件")
    print(f"    親子関係なし: {no_parent}件")
    print(f"    親商談候補: {len(parent_ids)}個")
    
    print(f"\n  💰 総計:")
    print(f"    総額（税抜き）: ¥{total_amount:,.0f}")
    print(f"    総額（税込み）: ¥{total_amount * 1.10:,.0f}")
    
    return {
        'stage_stats': stage_stats,
        'parent_child_stats': {
            'has_parent': has_parent,
            'no_parent': no_parent,
            'parent_ids_count': len(parent_ids)
        },
        'total_amount': total_amount,
        'total_deals': len(deals)
    }

def get_sample_invoices_simple(headers, org_id, sample_size=300):
    """シンプルな請求書取得"""
    print(f"\n📄 請求書サンプル取得中（最大{sample_size}件）...")
    
    url = "https://www.zohoapis.com/books/v3/invoices"
    invoices = []
    page = 1
    
    while len(invoices) < sample_size and page <= 5:
        params = {
            'organization_id': org_id,
            'per_page': min(200, sample_size - len(invoices)),
            'page': page,
            'sort_column': 'date',
            'sort_order': 'D'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                page_invoices = data.get('invoices', [])
                
                if page_invoices:
                    # 2024年以降
                    target_invoices = [inv for inv in page_invoices 
                                     if inv.get('date', '') >= '2024-04-01']
                    invoices.extend(target_invoices)
                    
                    print(f"  ページ{page}: {len(target_invoices)}件追加（累計: {len(invoices)}件）")
                    
                    if not data.get('page_context', {}).get('has_more_page', False):
                        break
                    page += 1
                else:
                    break
            else:
                print(f"  ❌ エラー: {response.status_code}")
                break
        
        except Exception as e:
            print(f"  ❌ 例外: {str(e)}")
            break
        
        time.sleep(0.5)
    
    print(f"✅ 請求書取得完了: {len(invoices)}件")
    return invoices

def simple_matching_analysis(deals, invoices):
    """シンプルなマッチング分析"""
    print(f"\n🔗 シンプルマッチング分析...")
    
    # 請求書をreference_numberでインデックス化
    invoice_map = {}
    total_invoice_amount = 0
    
    for invoice in invoices:
        ref_num = invoice.get('reference_number', '').strip()
        amount = invoice.get('total', 0)
        total_invoice_amount += amount
        
        if ref_num:
            if ref_num not in invoice_map:
                invoice_map[ref_num] = []
            invoice_map[ref_num].append(invoice)
    
    # 商談とのマッチング
    matched_deals = 0
    matched_amount = 0
    unmatched_amount = 0
    
    for deal in deals[:200]:  # 最初の200件のみ
        deal_id = deal['id']
        deal_amount = deal.get('Amount', 0) or 0
        
        if deal_id in invoice_map:
            matched_deals += 1
            matched_amount += deal_amount
        else:
            unmatched_amount += deal_amount
    
    print(f"  分析対象商談: 200件（サンプル）")
    print(f"  マッチした商談: {matched_deals}件")
    print(f"  マッチ率: {matched_deals/200*100:.1f}%")
    print(f"  マッチ商談額（税抜き）: ¥{matched_amount:,.0f}")
    print(f"  未マッチ商談額（税抜き）: ¥{unmatched_amount:,.0f}")
    print(f"  請求書総額: ¥{total_invoice_amount:,.0f}")
    
    return {
        'matched_deals': matched_deals,
        'match_rate': matched_deals/200*100,
        'matched_amount': matched_amount,
        'unmatched_amount': unmatched_amount,
        'total_invoice_amount': total_invoice_amount
    }

def main():
    """メイン処理"""
    print("="*80)
    print("📊 CRMトークン更新 + 簡易商談・請求書分析")
    print("="*80)
    
    # 1. CRMトークン更新
    new_crm_token = refresh_crm_token()
    if not new_crm_token:
        print("❌ CRMトークン更新に失敗しました")
        return
    
    # 2. Booksトークン読み込み
    try:
        books_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン" / "zoho_books_tokens.json"
        with open(books_path, 'r') as f:
            books_tokens = json.load(f)
        
        headers = {
            'crm': {'Authorization': f'Bearer {new_crm_token["access_token"]}'},
            'books': {'Authorization': f'Bearer {books_tokens["access_token"]}'}
        }
        org_id = "772043849"
        
        print("✅ 両方のトークン準備完了")
    
    except Exception as e:
        print(f"❌ トークン準備エラー: {str(e)}")
        return
    
    # 3. 商談サンプル取得
    deals = get_sample_deals(headers['crm'])
    if not deals:
        print("❌ 商談が取得できませんでした")
        return
    
    # 4. 商談構造分析
    deal_analysis = analyze_deal_structure_simple(deals)
    
    # 5. 請求書サンプル取得
    invoices = get_sample_invoices_simple(headers['books'], org_id)
    
    # 6. マッチング分析
    if invoices:
        matching_analysis = simple_matching_analysis(deals, invoices)
        
        # 7. 総合レポート
        print(f"\n" + "="*80)
        print("🎯 総合分析結果")
        print("="*80)
        
        total_deals = deal_analysis['total_deals']
        total_amount = deal_analysis['total_amount']
        total_amount_with_tax = total_amount * 1.10
        
        print(f"📊 商談サマリー（2024/4/1以降）:")
        print(f"  総商談数: {total_deals:,.0f}件")
        print(f"  総額（税抜き）: ¥{total_amount:,.0f}")
        print(f"  総額（税込み）: ¥{total_amount_with_tax:,.0f}")
        
        print(f"\n📄 請求書サマリー:")
        print(f"  サンプル請求書: {len(invoices)}件")
        print(f"  請求書総額: ¥{matching_analysis['total_invoice_amount']:,.0f}")
        
        print(f"\n🔗 マッチング結果:")
        print(f"  マッチ率: {matching_analysis['match_rate']:.1f}%")
        print(f"  推定請求済み額: ¥{matching_analysis['matched_amount'] * 1.10:,.0f}（税込み）")
        
        coverage = matching_analysis['total_invoice_amount'] / total_amount_with_tax * 100
        print(f"  請求書カバー率: {coverage:.1f}%")
        
        print("="*80)
    else:
        print("❌ 請求書が取得できませんでした")

if __name__ == "__main__":
    main()