#!/usr/bin/env python3
"""
包括的な商談・請求書分析
2024/4/1以降の全商談を親子構造で分析し、請求書との照合を行う
JT ETEケースで学んだ知見を活用
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

def get_all_deals_since_april(headers, limit_pages=20):
    """2024/4/1以降の全商談を取得（ページ制限付き）"""
    print("📊 2024/4/1以降の全商談取得中...")
    
    url = "https://www.zohoapis.com/crm/v2/Deals"
    all_deals = []
    page = 1
    
    while page <= limit_pages:
        params = {
            'fields': 'id,Deal_Name,Account_Name,Amount,Stage,Closing_Date,field78',
            'per_page': 200,
            'page': page,
            'sort_by': 'Closing_Date',
            'sort_order': 'desc'
        }
        
        try:
            print(f"  ページ{page}/{limit_pages}を取得中...")
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                deals = data.get('data', [])
                
                if deals:
                    # 2024/4/1以降でフィルタ
                    filtered_deals = []
                    old_deals_count = 0
                    
                    for deal in deals:
                        closing_date = deal.get('Closing_Date')
                        if closing_date and closing_date >= '2024-04-01':
                            filtered_deals.append(deal)
                        else:
                            old_deals_count += 1
                    
                    all_deals.extend(filtered_deals)
                    print(f"    対象: {len(filtered_deals)}件, 古い: {old_deals_count}件")
                    
                    # 古いデータが多くなったら終了
                    if old_deals_count > 150:
                        print("    古いデータが多いため終了")
                        break
                    
                    if not data.get('info', {}).get('more_records', False):
                        break
                    page += 1
                else:
                    print("    データなし")
                    break
            else:
                print(f"    ❌ エラー: {response.status_code}")
                break
                
        except Exception as e:
            print(f"    ❌ 例外: {str(e)}")
            break
        
        time.sleep(0.5)  # API制限対策
    
    print(f"✅ 商談取得完了: {len(all_deals)}件")
    return all_deals

def analyze_parent_child_structure(deals):
    """親子構造を分析"""
    print("\n🔍 親子構造分析中...")
    
    # 親IDを抽出
    parent_ids = set()
    children_by_parent = defaultdict(list)
    no_parent_deals = []
    
    for deal in deals:
        field78 = deal.get('field78')
        if field78 and isinstance(field78, dict):
            parent_id = field78.get('id')
            if parent_id:
                parent_ids.add(parent_id)
                children_by_parent[parent_id].append(deal)
            else:
                no_parent_deals.append(deal)
        else:
            no_parent_deals.append(deal)
    
    print(f"  親商談候補: {len(parent_ids)}個")
    print(f"  親子関係ありグループ: {len(children_by_parent)}組")
    print(f"  親子関係なし商談: {len(no_parent_deals)}件")
    
    # 実際の親商談を取得（バッチ処理）
    parent_deals = {}
    if parent_ids:
        print(f"  親商談詳細取得中...")
        
        # 50件ずつバッチ処理
        parent_id_list = list(parent_ids)
        for i in range(0, len(parent_id_list), 50):
            batch = parent_id_list[i:i+50]
            batch_str = ','.join(batch)
            
            try:
                url = "https://www.zohoapis.com/crm/v2/Deals"
                params = {
                    'fields': 'id,Deal_Name,Account_Name,Amount,Stage,Closing_Date',
                    'ids': batch_str
                }
                
                response = requests.get(url, headers={'Authorization': headers['Authorization']}, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    batch_parents = data.get('data', [])
                    for parent in batch_parents:
                        parent_deals[parent['id']] = parent
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    バッチ{i//50 + 1}でエラー: {str(e)}")
    
    print(f"  親商談取得完了: {len(parent_deals)}件")
    
    # 構造分析
    analysis = {
        'parent_child_sets': [],
        'parent_only': [],
        'child_only': [],
        'no_structure': no_parent_deals,
        'stats': {}
    }
    
    # 親子セット作成
    for parent_id, children in children_by_parent.items():
        parent = parent_deals.get(parent_id)
        
        if parent and parent.get('Closing_Date', '') >= '2024-04-01':
            # 親も対象期間内
            parent_amount = parent.get('Amount', 0) or 0
            children_amount = sum(c.get('Amount', 0) or 0 for c in children)
            
            analysis['parent_child_sets'].append({
                'parent': parent,
                'children': children,
                'parent_amount': parent_amount,
                'children_amount': children_amount,
                'total_amount': parent_amount + children_amount,
                'children_count': len(children)
            })
        else:
            # 親が対象外 → 子のみとして処理
            for child in children:
                analysis['child_only'].append(child)
    
    # 統計
    total_amount = 0
    total_deals = 0
    
    for category in ['parent_child_sets', 'parent_only', 'child_only', 'no_structure']:
        if category == 'parent_child_sets':
            amount = sum(pc['total_amount'] for pc in analysis[category])
            count = sum(1 + pc['children_count'] for pc in analysis[category])
        else:
            items = analysis[category]
            amount = sum(item.get('Amount', 0) or 0 for item in items)
            count = len(items)
        
        total_amount += amount
        total_deals += count
        
        analysis['stats'][category] = {'count': count, 'amount': amount}
    
    analysis['stats']['total'] = {'count': total_deals, 'amount': total_amount}
    
    return analysis

def get_sample_invoices(headers, org_id, sample_size=500):
    """サンプル請求書を取得"""
    print(f"\n📄 請求書サンプル取得中（最大{sample_size}件）...")
    
    url = "https://www.zohoapis.com/books/v3/invoices"
    invoices = []
    page = 1
    
    while len(invoices) < sample_size and page <= 10:
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
                    # 2024年以降の請求書のみ
                    recent_invoices = [inv for inv in page_invoices 
                                     if inv.get('date', '') >= '2024-04-01']
                    invoices.extend(recent_invoices)
                    
                    print(f"  ページ{page}: {len(recent_invoices)}件追加（累計: {len(invoices)}件）")
                    
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

def match_deals_with_invoices(structure_analysis, invoices):
    """商談と請求書のマッチング"""
    print(f"\n🔗 商談・請求書マッチング分析中...")
    
    # 請求書をreference_numberでインデックス化
    invoice_map = {}
    for invoice in invoices:
        ref_num = invoice.get('reference_number', '').strip()
        if ref_num:
            if ref_num not in invoice_map:
                invoice_map[ref_num] = []
            invoice_map[ref_num].append(invoice)
    
    print(f"  請求書参照番号: {len(invoice_map)}種類")
    
    results = {
        'parent_child_analysis': [],
        'no_structure_analysis': [],
        'summary': {}
    }
    
    total_deal_amount = 0
    total_invoice_amount = 0
    matched_deals = 0
    
    # 親子セット分析
    for pc_set in structure_analysis['parent_child_sets']:
        parent = pc_set['parent']
        children = pc_set['children']
        deal_total = pc_set['total_amount']
        
        # 関連請求書検索
        related_invoices = []
        
        # 親商談の請求書
        parent_invoices = invoice_map.get(parent['id'], [])
        for inv in parent_invoices:
            related_invoices.append(('parent', inv))
        
        # 子商談の請求書
        for child in children:
            child_invoices = invoice_map.get(child['id'], [])
            for inv in child_invoices:
                related_invoices.append(('child', inv))
        
        invoice_total = sum(inv[1].get('total', 0) for inv in related_invoices)
        deal_total_with_tax = deal_total * 1.10
        
        results['parent_child_analysis'].append({
            'parent_name': parent.get('Deal_Name'),
            'parent_id': parent['id'],
            'deal_total': deal_total,
            'deal_total_with_tax': deal_total_with_tax,
            'invoice_total': invoice_total,
            'invoice_count': len(related_invoices),
            'children_count': len(children),
            'difference': deal_total_with_tax - invoice_total
        })
        
        total_deal_amount += deal_total_with_tax
        total_invoice_amount += invoice_total
        if related_invoices:
            matched_deals += 1
    
    # 単体商談分析（サンプル）
    sample_singles = structure_analysis['no_structure'][:100]  # 最初の100件のみ
    
    for deal in sample_singles:
        deal_amount = deal.get('Amount', 0) or 0
        deal_invoices = invoice_map.get(deal['id'], [])
        
        invoice_total = sum(inv.get('total', 0) for inv in deal_invoices)
        deal_amount_with_tax = deal_amount * 1.10
        
        results['no_structure_analysis'].append({
            'deal_name': deal.get('Deal_Name'),
            'deal_id': deal['id'],
            'deal_amount': deal_amount,
            'deal_amount_with_tax': deal_amount_with_tax,
            'invoice_total': invoice_total,
            'invoice_count': len(deal_invoices),
            'difference': deal_amount_with_tax - invoice_total
        })
        
        total_deal_amount += deal_amount_with_tax
        total_invoice_amount += invoice_total
        if deal_invoices:
            matched_deals += 1
    
    results['summary'] = {
        'total_deal_amount': total_deal_amount,
        'total_invoice_amount': total_invoice_amount,
        'total_difference': total_deal_amount - total_invoice_amount,
        'matched_deals': matched_deals,
        'analyzed_deals': len(structure_analysis['parent_child_sets']) + len(sample_singles)
    }
    
    return results

def generate_summary_report(structure_analysis, matching_results):
    """サマリーレポート生成"""
    print(f"\n" + "="*80)
    print("📊 2024/4/1以降 商談・請求書分析レポート")
    print("="*80)
    
    # 商談構造サマリー
    print("🏗️ 商談構造:")
    for category, stats in structure_analysis['stats'].items():
        if category != 'total':
            count = stats['count']
            amount = stats['amount']
            amount_with_tax = amount * 1.10
            print(f"  {category}: {count}件 - ¥{amount:,.0f}（税抜き）¥{amount_with_tax:,.0f}（税込み）")
    
    total_stats = structure_analysis['stats']['total']
    print(f"\n  合計: {total_stats['count']}件 - ¥{total_stats['amount']:,.0f}（税抜き）¥{total_stats['amount'] * 1.10:,.0f}（税込み）")
    
    # マッチング結果
    summary = matching_results['summary']
    print(f"\n💰 請求書マッチング:")
    print(f"  分析対象商談: {summary['analyzed_deals']}件")
    print(f"  請求書マッチング: {summary['matched_deals']}件")
    print(f"  商談総額（税込み）: ¥{summary['total_deal_amount']:,.0f}")
    print(f"  請求書総額: ¥{summary['total_invoice_amount']:,.0f}")
    print(f"  差額: ¥{summary['total_difference']:,.0f}")
    
    # 大きな差額がある親子セット
    print(f"\n🔍 大きな差額がある親子セット（TOP 10）:")
    large_diffs = sorted(matching_results['parent_child_analysis'], 
                        key=lambda x: abs(x['difference']), reverse=True)[:10]
    
    for i, item in enumerate(large_diffs, 1):
        if abs(item['difference']) > 100000:  # 10万円以上
            print(f"  {i:2}. {item['parent_name'][:50]}")
            print(f"      差額: ¥{item['difference']:,.0f}")
            print(f"      商談: ¥{item['deal_total_with_tax']:,.0f} / 請求書: ¥{item['invoice_total']:,.0f}")
    
    print("="*80)

def main():
    """メイン処理"""
    print("="*80)
    print("📊 包括的商談・請求書分析（2024/4/1以降）")
    print("="*80)
    
    try:
        # 1. トークン準備
        tokens = load_tokens()
        print("✅ トークン準備完了")
        
        # 2. 商談取得
        deals = get_all_deals_since_april(tokens['crm_headers'])
        
        if not deals:
            print("❌ 商談が取得できませんでした")
            return
        
        # 3. 親子構造分析
        structure_analysis = analyze_parent_child_structure(deals)
        
        # 4. 請求書サンプル取得
        invoices = get_sample_invoices(tokens['books_headers'], tokens['org_id'])
        
        # 5. マッチング分析
        matching_results = match_deals_with_invoices(structure_analysis, invoices)
        
        # 6. レポート生成
        generate_summary_report(structure_analysis, matching_results)
        
        print(f"\n✅ 分析完了")
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")

if __name__ == "__main__":
    main()