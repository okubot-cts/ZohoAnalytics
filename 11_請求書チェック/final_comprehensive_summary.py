#!/usr/bin/env python3
"""
最終包括サマリー
全データを抽出して「総額」「総額（税込み）」「請求金額」を算出
"""
import requests
import json
from pathlib import Path
from collections import defaultdict
import time

def load_tokens():
    """CRMとBooksトークンを読み込み"""
    base_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン"
    
    with open(base_path / "zoho_crm_tokens.json", 'r') as f:
        crm_tokens = json.load(f)
    
    with open(base_path / "zoho_books_tokens.json", 'r') as f:
        books_tokens = json.load(f)
    
    return {
        'crm_headers': {'Authorization': f'Bearer {crm_tokens["access_token"]}'},
        'books_headers': {'Authorization': f'Bearer {books_tokens["access_token"]}'},
        'org_id': "772043849"
    }

def get_all_deals_comprehensive(headers, max_pages=100):
    """2024/4/1以降の全商談を包括的に取得"""
    print("📊 2024/4/1以降の全商談を包括的に取得中...")
    
    url = "https://www.zohoapis.com/crm/v2/Deals"
    all_deals = []
    page = 1
    
    while page <= max_pages:
        params = {
            'fields': 'id,Deal_Name,Account_Name,Amount,Stage,Closing_Date,field78',
            'per_page': 200,
            'page': page,
            'sort_by': 'Closing_Date',
            'sort_order': 'desc'
        }
        
        try:
            if page % 10 == 1:  # 10ページごとに進捗表示
                print(f"  ページ{page}-{min(page+9, max_pages)}を処理中...")
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                deals = data.get('data', [])
                
                if deals:
                    # 2024/4/1以降でフィルタ
                    target_deals = []
                    old_deals_count = 0
                    
                    for deal in deals:
                        closing_date = deal.get('Closing_Date')
                        if closing_date and closing_date >= '2024-04-01':
                            target_deals.append(deal)
                        elif closing_date:
                            old_deals_count += 1
                    
                    all_deals.extend(target_deals)
                    
                    # 古いデータが多くなったら終了
                    if old_deals_count > 150:
                        print(f"  古いデータが多いため終了（ページ{page}）")
                        break
                    
                    if not data.get('info', {}).get('more_records', False):
                        print(f"  全データ取得完了（ページ{page}）")
                        break
                    page += 1
                else:
                    print(f"  データなし（ページ{page}）")
                    break
            else:
                print(f"  ❌ エラー: {response.status_code}（ページ{page}）")
                break
                
        except Exception as e:
            print(f"  ❌ 例外: {str(e)}（ページ{page}）")
            break
        
        if page % 5 == 0:  # 5ページごとに休憩
            time.sleep(1)
        else:
            time.sleep(0.2)
    
    print(f"✅ 商談取得完了: {len(all_deals)}件")
    return all_deals

def get_comprehensive_invoices(headers, org_id, max_pages=50):
    """2024/4/1以降の全請求書を取得"""
    print(f"📄 2024/4/1以降の全請求書を取得中...")
    
    url = "https://www.zohoapis.com/books/v3/invoices"
    all_invoices = []
    page = 1
    
    while page <= max_pages:
        params = {
            'organization_id': org_id,
            'per_page': 200,
            'page': page,
            'sort_column': 'date',
            'sort_order': 'D'
        }
        
        try:
            if page % 10 == 1:
                print(f"  ページ{page}-{min(page+9, max_pages)}を処理中...")
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                invoices = data.get('invoices', [])
                
                if invoices:
                    # 2024/4/1以降でフィルタ
                    target_invoices = []
                    for invoice in invoices:
                        inv_date = invoice.get('date', '')
                        if inv_date >= '2024-04-01':
                            # void以外の有効な請求書のみ
                            if invoice.get('status') != 'void':
                                target_invoices.append(invoice)
                    
                    all_invoices.extend(target_invoices)
                    
                    if not data.get('page_context', {}).get('has_more_page', False):
                        print(f"  全請求書取得完了（ページ{page}）")
                        break
                    page += 1
                else:
                    print(f"  データなし（ページ{page}）")
                    break
            else:
                print(f"  ❌ エラー: {response.status_code}（ページ{page}）")
                if response.status_code == 401:
                    print("  トークンの有効期限切れの可能性があります")
                break
        
        except Exception as e:
            print(f"  ❌ 例外: {str(e)}（ページ{page}）")
            break
        
        if page % 5 == 0:
            time.sleep(1)
        else:
            time.sleep(0.3)
    
    print(f"✅ 請求書取得完了: {len(all_invoices)}件")
    return all_invoices

def analyze_deals_by_stage_and_structure(deals):
    """商談をステージと構造で詳細分析"""
    print(f"\n🔍 商談の詳細分析中（{len(deals)}件）...")
    
    # ステージ別統計
    stage_stats = defaultdict(lambda: {'count': 0, 'amount': 0, 'has_parent': 0, 'no_parent': 0})
    
    # 親子構造分析
    parent_ids = set()
    children_by_parent = defaultdict(list)
    standalone_deals = []
    
    for deal in deals:
        stage = deal.get('Stage', '不明')
        amount = deal.get('Amount', 0) or 0
        
        stage_stats[stage]['count'] += 1
        stage_stats[stage]['amount'] += amount
        
        # 親子関係チェック
        field78 = deal.get('field78')
        if field78 and isinstance(field78, dict):
            parent_id = field78.get('id')
            if parent_id:
                parent_ids.add(parent_id)
                children_by_parent[parent_id].append(deal)
                stage_stats[stage]['has_parent'] += 1
            else:
                standalone_deals.append(deal)
                stage_stats[stage]['no_parent'] += 1
        else:
            standalone_deals.append(deal)
            stage_stats[stage]['no_parent'] += 1
    
    # 統計出力
    total_amount = sum(stats['amount'] for stats in stage_stats.values())
    total_count = sum(stats['count'] for stats in stage_stats.values())
    
    print(f"  📊 ステージ別統計:")
    for stage, stats in sorted(stage_stats.items(), key=lambda x: x[1]['amount'], reverse=True):
        count = stats['count']
        amount = stats['amount']
        has_parent = stats['has_parent']
        no_parent = stats['no_parent']
        amount_ratio = amount / total_amount * 100 if total_amount > 0 else 0
        
        print(f"    {stage}: {count}件 - ¥{amount:,.0f} ({amount_ratio:.1f}%)")
        print(f"      └ 親子関係あり: {has_parent}件, なし: {no_parent}件")
    
    print(f"\n  🏗️ 構造統計:")
    print(f"    親商談候補: {len(parent_ids)}個")
    print(f"    親子関係グループ: {len(children_by_parent)}組")
    print(f"    独立商談: {len(standalone_deals)}件")
    
    return {
        'total_count': total_count,
        'total_amount': total_amount,
        'stage_stats': dict(stage_stats),
        'parent_ids': parent_ids,
        'children_by_parent': children_by_parent,
        'standalone_deals': standalone_deals
    }

def analyze_invoices_comprehensive(invoices):
    """請求書を包括的に分析"""
    print(f"\n📄 請求書の包括的分析中（{len(invoices)}件）...")
    
    # ステータス別統計
    status_stats = defaultdict(lambda: {'count': 0, 'amount': 0})
    
    # 月別統計
    month_stats = defaultdict(lambda: {'count': 0, 'amount': 0})
    
    # reference_number統計
    has_reference = 0
    no_reference = 0
    
    total_amount = 0
    
    for invoice in invoices:
        amount = invoice.get('total', 0)
        status = invoice.get('status', '不明')
        date = invoice.get('date', '')
        ref_num = invoice.get('reference_number', '').strip()
        
        total_amount += amount
        
        # ステータス別
        status_stats[status]['count'] += 1
        status_stats[status]['amount'] += amount
        
        # 月別（YYYY-MM形式）
        if date:
            month = date[:7]  # YYYY-MM
            month_stats[month]['count'] += 1
            month_stats[month]['amount'] += amount
        
        # reference_number統計
        if ref_num:
            has_reference += 1
        else:
            no_reference += 1
    
    print(f"  📊 請求書統計:")
    print(f"    総件数: {len(invoices)}件")
    print(f"    総額: ¥{total_amount:,.0f}")
    print(f"    参照番号あり: {has_reference}件, なし: {no_reference}件")
    
    print(f"\n  📋 ステータス別:")
    for status, stats in sorted(status_stats.items(), key=lambda x: x[1]['amount'], reverse=True):
        count = stats['count']
        amount = stats['amount']
        amount_ratio = amount / total_amount * 100 if total_amount > 0 else 0
        print(f"    {status}: {count}件 - ¥{amount:,.0f} ({amount_ratio:.1f}%)")
    
    print(f"\n  📅 月別統計（上位6ヶ月）:")
    for month, stats in sorted(month_stats.items(), key=lambda x: x[1]['amount'], reverse=True)[:6]:
        count = stats['count']
        amount = stats['amount']
        print(f"    {month}: {count}件 - ¥{amount:,.0f}")
    
    return {
        'total_count': len(invoices),
        'total_amount': total_amount,
        'status_stats': dict(status_stats),
        'month_stats': dict(month_stats),
        'has_reference': has_reference,
        'no_reference': no_reference
    }

def match_deals_with_invoices(deals_analysis, invoices):
    """商談と請求書のマッチング分析"""
    print(f"\n🔗 商談・請求書マッチング分析中...")
    
    # 請求書をreference_numberでインデックス化
    invoice_map = {}
    for invoice in invoices:
        ref_num = invoice.get('reference_number', '').strip()
        if ref_num:
            if ref_num not in invoice_map:
                invoice_map[ref_num] = []
            invoice_map[ref_num].append(invoice)
    
    print(f"  参照番号付き請求書: {len(invoice_map)}種類")
    
    # 全商談ID収集
    all_deal_ids = set()
    
    # 独立商談のID
    for deal in deals_analysis['standalone_deals']:
        all_deal_ids.add(deal['id'])
    
    # 親子関係商談のID
    for parent_id, children in deals_analysis['children_by_parent'].items():
        all_deal_ids.add(parent_id)  # 親商談ID
        for child in children:
            all_deal_ids.add(child['id'])  # 子商談ID
    
    # マッチング統計
    matched_deals = 0
    matched_invoice_amount = 0
    unmatched_deals = 0
    
    for deal_id in all_deal_ids:
        if deal_id in invoice_map:
            matched_deals += 1
            matched_invoice_amount += sum(inv.get('total', 0) for inv in invoice_map[deal_id])
        else:
            unmatched_deals += 1
    
    match_rate = matched_deals / len(all_deal_ids) * 100 if all_deal_ids else 0
    
    print(f"  📊 マッチング結果:")
    print(f"    総商談ID数: {len(all_deal_ids)}個")
    print(f"    マッチした商談: {matched_deals}個 ({match_rate:.1f}%)")
    print(f"    未マッチ商談: {unmatched_deals}個")
    print(f"    マッチした請求書金額: ¥{matched_invoice_amount:,.0f}")
    
    return {
        'total_deals': len(all_deal_ids),
        'matched_deals': matched_deals,
        'unmatched_deals': unmatched_deals,
        'match_rate': match_rate,
        'matched_invoice_amount': matched_invoice_amount
    }

def generate_final_summary(deals_analysis, invoices_analysis, matching_analysis):
    """最終サマリー生成"""
    print(f"\n" + "="*100)
    print("🎯 2024/4/1以降 全データ最終サマリー")
    print("="*100)
    
    # 基本統計
    deals_count = deals_analysis['total_count']
    deals_amount_excluding_tax = deals_analysis['total_amount']
    deals_amount_including_tax = deals_amount_excluding_tax * 1.10
    
    invoices_count = invoices_analysis['total_count']
    invoices_amount = invoices_analysis['total_amount']
    
    print(f"📊 基本統計:")
    print(f"  対象期間: 2024年4月1日以降")
    print(f"  商談総数: {deals_count:,.0f}件")
    print(f"  請求書総数: {invoices_count:,.0f}件")
    
    print(f"\n💰 金額サマリー:")
    print(f"  商談総額（税抜き）: ¥{deals_amount_excluding_tax:,.0f}")
    print(f"  商談総額（税込み）: ¥{deals_amount_including_tax:,.0f}")
    print(f"  請求書総額: ¥{invoices_amount:,.0f}")
    
    # 差額分析
    difference = deals_amount_including_tax - invoices_amount
    coverage_rate = invoices_amount / deals_amount_including_tax * 100 if deals_amount_including_tax > 0 else 0
    
    print(f"\n📈 整合性分析:")
    print(f"  差額: ¥{difference:,.0f}")
    print(f"  請求書カバー率: {coverage_rate:.1f}%")
    
    if abs(difference) < deals_amount_including_tax * 0.05:  # 5%以内
        print("  ✅ 非常に良好な整合性")
    elif abs(difference) < deals_amount_including_tax * 0.15:  # 15%以内
        print("  👍 良好な整合性")
    else:
        print("  ⚠️ 整合性に課題あり")
    
    # マッチング分析
    print(f"\n🔗 マッチング分析:")
    print(f"  商談・請求書マッチ率: {matching_analysis['match_rate']:.1f}%")
    print(f"  マッチした請求書金額: ¥{matching_analysis['matched_invoice_amount']:,.0f}")
    
    # 主要ステージ
    print(f"\n📋 主要ステージ（金額順）:")
    for stage, stats in sorted(deals_analysis['stage_stats'].items(), 
                              key=lambda x: x[1]['amount'], reverse=True)[:5]:
        amount = stats['amount']
        count = stats['count']
        amount_ratio = amount / deals_amount_excluding_tax * 100
        print(f"  {stage}: {count}件 - ¥{amount:,.0f} ({amount_ratio:.1f}%)")
    
    # 主要請求書ステータス
    print(f"\n📄 主要請求書ステータス:")
    for status, stats in sorted(invoices_analysis['status_stats'].items(), 
                               key=lambda x: x[1]['amount'], reverse=True)[:5]:
        amount = stats['amount']
        count = stats['count']
        amount_ratio = amount / invoices_amount * 100
        print(f"  {status}: {count}件 - ¥{amount:,.0f} ({amount_ratio:.1f}%)")
    
    print("="*100)
    
    return {
        'deals_count': deals_count,
        'deals_amount_excluding_tax': deals_amount_excluding_tax,
        'deals_amount_including_tax': deals_amount_including_tax,
        'invoices_count': invoices_count,
        'invoices_amount': invoices_amount,
        'difference': difference,
        'coverage_rate': coverage_rate,
        'match_rate': matching_analysis['match_rate']
    }

def save_final_summary(summary_data, deals_analysis, invoices_analysis):
    """最終サマリーをJSONで保存"""
    output_file = Path(__file__).parent / f"final_comprehensive_summary_{int(time.time())}.json"
    
    final_data = {
        'analysis_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'analysis_period': '2024-04-01以降',
        'summary': summary_data,
        'deals_stage_breakdown': deals_analysis['stage_stats'],
        'invoices_status_breakdown': invoices_analysis['status_stats'],
        'invoices_monthly_breakdown': invoices_analysis['month_stats']
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 最終サマリー保存: {output_file}")

def main():
    """メイン処理"""
    print("="*100)
    print("🎯 最終包括サマリー：総額・総額（税込み）・請求金額")
    print("="*100)
    
    try:
        # 1. トークン準備
        tokens = load_tokens()
        print("✅ トークン準備完了")
        
        # 2. 全商談取得
        all_deals = get_all_deals_comprehensive(tokens['crm_headers'])
        if not all_deals:
            print("❌ 商談データが取得できませんでした")
            return
        
        # 3. 全請求書取得
        all_invoices = get_comprehensive_invoices(tokens['books_headers'], tokens['org_id'])
        
        # 4. 商談詳細分析
        deals_analysis = analyze_deals_by_stage_and_structure(all_deals)
        
        # 5. 請求書詳細分析
        invoices_analysis = analyze_invoices_comprehensive(all_invoices)
        
        # 6. マッチング分析
        matching_analysis = match_deals_with_invoices(deals_analysis, all_invoices)
        
        # 7. 最終サマリー
        summary_data = generate_final_summary(deals_analysis, invoices_analysis, matching_analysis)
        
        # 8. サマリー保存
        save_final_summary(summary_data, deals_analysis, invoices_analysis)
        
        print(f"\n✅ 最終包括分析完了")
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()