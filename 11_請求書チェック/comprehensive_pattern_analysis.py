#!/usr/bin/env python3
"""
商談・請求書パターン分析
5つの主要パターンを検証する包括的分析
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

def get_comprehensive_deals(headers, sample_size=2000):
    """包括的な商談データを取得"""
    print(f"📊 包括的商談データ取得中（最大{sample_size}件）...")
    
    url = "https://www.zohoapis.com/crm/v2/Deals"
    all_deals = []
    page = 1
    
    while len(all_deals) < sample_size and page <= 15:
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
        
        time.sleep(0.3)
    
    print(f"✅ 商談取得完了: {len(all_deals)}件")
    return all_deals

def get_parent_deals_batch(headers, parent_ids):
    """親商談を効率的に取得"""
    print(f"📊 親商談取得中（{len(parent_ids)}件）...")
    
    parent_deals = {}
    parent_id_list = list(parent_ids)
    
    # 50件ずつバッチ処理
    for i in range(0, len(parent_id_list), 50):
        batch = parent_id_list[i:i+50]
        batch_str = ','.join(batch)
        
        try:
            url = "https://www.zohoapis.com/crm/v2/Deals"
            params = {
                'fields': 'id,Deal_Name,Account_Name,Amount,Stage,Closing_Date',
                'ids': batch_str
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                batch_parents = data.get('data', [])
                for parent in batch_parents:
                    parent_deals[parent['id']] = parent
                
                print(f"  バッチ{i//50 + 1}: {len(batch_parents)}件取得")
            
            time.sleep(0.3)
            
        except Exception as e:
            print(f"  バッチ{i//50 + 1}でエラー: {str(e)}")
    
    print(f"✅ 親商談取得完了: {len(parent_deals)}件")
    return parent_deals

def get_relevant_invoices(headers, org_id, deal_ids, sample_size=1000):
    """関連する請求書を効率的に取得"""
    print(f"📄 関連請求書取得中（最大{sample_size}件）...")
    
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
                    # 2024年以降かつ関連する請求書
                    relevant_invoices = []
                    for inv in page_invoices:
                        inv_date = inv.get('date', '')
                        ref_num = inv.get('reference_number', '').strip()
                        
                        if inv_date >= '2024-04-01' and ref_num in deal_ids:
                            relevant_invoices.append(inv)
                    
                    invoices.extend(relevant_invoices)
                    print(f"  ページ{page}: {len(relevant_invoices)}件関連請求書発見（累計: {len(invoices)}件）")
                    
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
        
        time.sleep(0.3)
    
    print(f"✅ 関連請求書取得完了: {len(invoices)}件")
    return invoices

def analyze_deal_patterns(child_deals, parent_deals):
    """5つのパターンで商談を分析"""
    print(f"\n🔍 5パターン分析中...")
    
    patterns = {
        'pattern1_parent_only': [],        # パターン1: 親商談完結
        'pattern2_children_only': [],      # パターン2: 子商談完結  
        'pattern3_parent_統括_no_amount': [], # パターン3: 親統括・親金額なし
        'pattern4_parent_統括_with_amount': [], # パターン4: 親統括・親金額あり
        'pattern5_分担': [],                # パターン5: 自己負担・会社負担分担
        'no_parent_relation': []           # 親子関係なし
    }
    
    # 子商談を親IDでグループ化
    children_by_parent = defaultdict(list)
    no_parent_deals = []
    
    for child in child_deals:
        field78 = child.get('field78')
        if field78 and isinstance(field78, dict):
            parent_id = field78.get('id')
            if parent_id:
                children_by_parent[parent_id].append(child)
            else:
                no_parent_deals.append(child)
        else:
            no_parent_deals.append(child)
    
    patterns['no_parent_relation'] = no_parent_deals
    
    # 親子セットを分析
    for parent_id, children in children_by_parent.items():
        parent = parent_deals.get(parent_id)
        
        if not parent:
            # 親商談が見つからない → 子のみとして扱う
            for child in children:
                patterns['no_parent_relation'].append(child)
            continue
        
        parent_amount = parent.get('Amount', 0) or 0
        children_total = sum(c.get('Amount', 0) or 0 for c in children)
        
        parent_closing_date = parent.get('Closing_Date', '')
        if parent_closing_date < '2024-04-01':
            # 親商談が対象期間外
            for child in children:
                patterns['no_parent_relation'].append(child)
            continue
        
        # パターン判定
        deal_set = {
            'parent': parent,
            'children': children,
            'parent_amount': parent_amount,
            'children_amount': children_total,
            'total_amount': parent_amount + children_total,
            'children_count': len(children)
        }
        
        if len(children) == 0:
            # 子がいない → パターン1候補
            patterns['pattern1_parent_only'].append(deal_set)
        elif parent_amount == 0:
            # 親金額ゼロ
            if children_total > 0:
                # パターン2 or 3候補
                # 商談名で判定を試行
                parent_name = parent.get('Deal_Name', '').upper()
                if any(keyword in parent_name for keyword in ['統括', '事務局', 'OFFICE', 'ADMIN']):
                    patterns['pattern3_parent_統括_no_amount'].append(deal_set)
                else:
                    patterns['pattern2_children_only'].append(deal_set)
            else:
                patterns['pattern2_children_only'].append(deal_set)
        else:
            # 親金額あり
            if children_total > 0:
                # パターン4 or 5候補
                # 金額比率で判定
                ratio = parent_amount / (parent_amount + children_total)
                if 0.1 <= ratio <= 0.9:  # 両方に相応の金額
                    patterns['pattern5_分担'].append(deal_set)
                else:
                    patterns['pattern4_parent_統括_with_amount'].append(deal_set)
            else:
                patterns['pattern1_parent_only'].append(deal_set)
    
    # 統計出力
    print(f"  📋 パターン分類結果:")
    for pattern_name, deals in patterns.items():
        if pattern_name == 'no_parent_relation':
            count = len(deals)
            amount = sum(d.get('Amount', 0) or 0 for d in deals)
        else:
            count = len(deals)
            amount = sum(d['total_amount'] for d in deals)
        
        print(f"    {pattern_name}: {count}組/件 - ¥{amount:,.0f}")
    
    return patterns

def analyze_invoice_matching(patterns, invoices):
    """各パターンの請求書マッチング分析"""
    print(f"\n🔗 パターン別請求書マッチング分析...")
    
    # 請求書をreference_numberでインデックス化
    invoice_map = defaultdict(list)
    for invoice in invoices:
        ref_num = invoice.get('reference_number', '').strip()
        if ref_num:
            invoice_map[ref_num].append(invoice)
    
    results = {}
    
    for pattern_name, pattern_deals in patterns.items():
        print(f"\n  📊 {pattern_name}分析:")
        
        if pattern_name == 'no_parent_relation':
            # 単体商談の分析
            pattern_results = []
            for deal in pattern_deals[:50]:  # 最初の50件のみ
                deal_id = deal['id']
                deal_amount = deal.get('Amount', 0) or 0
                deal_invoices = invoice_map.get(deal_id, [])
                invoice_total = sum(inv.get('total', 0) for inv in deal_invoices)
                
                pattern_results.append({
                    'deal_id': deal_id,
                    'deal_name': deal.get('Deal_Name', '')[:30],
                    'deal_amount': deal_amount,
                    'deal_amount_with_tax': deal_amount * 1.10,
                    'invoice_total': invoice_total,
                    'invoice_count': len(deal_invoices),
                    'difference': deal_amount * 1.10 - invoice_total,
                    'match_status': 'perfect' if abs(deal_amount * 1.10 - invoice_total) < 10 else 'mismatch'
                })
        else:
            # 親子セットの分析
            pattern_results = []
            for deal_set in pattern_deals:
                parent = deal_set['parent']
                children = deal_set['children']
                
                # 関連請求書を収集
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
                
                total_invoice_amount = sum(inv[1].get('total', 0) for inv in related_invoices)
                
                # パターン別の期待値計算
                expected_invoice_amount = 0
                if pattern_name == 'pattern1_parent_only':
                    expected_invoice_amount = deal_set['parent_amount'] * 1.10
                elif pattern_name == 'pattern2_children_only':
                    expected_invoice_amount = deal_set['children_amount'] * 1.10
                elif pattern_name in ['pattern3_parent_統括_no_amount', 'pattern4_parent_統括_with_amount']:
                    # 親から子商談分を請求すると仮定
                    expected_invoice_amount = deal_set['children_amount'] * 1.10
                elif pattern_name == 'pattern5_分担':
                    # 親子両方から請求すると仮定
                    expected_invoice_amount = deal_set['total_amount'] * 1.10
                
                difference = expected_invoice_amount - total_invoice_amount
                
                pattern_results.append({
                    'parent_id': parent['id'],
                    'parent_name': parent.get('Deal_Name', '')[:40],
                    'parent_amount': deal_set['parent_amount'],
                    'children_amount': deal_set['children_amount'],
                    'children_count': deal_set['children_count'],
                    'total_amount': deal_set['total_amount'],
                    'expected_invoice': expected_invoice_amount,
                    'actual_invoice': total_invoice_amount,
                    'difference': difference,
                    'invoice_breakdown': {
                        'parent_invoices': len([inv for type_, inv in related_invoices if type_ == 'parent']),
                        'child_invoices': len([inv for type_, inv in related_invoices if type_ == 'child']),
                        'parent_invoice_amount': sum(inv[1].get('total', 0) for inv in related_invoices if inv[0] == 'parent'),
                        'child_invoice_amount': sum(inv[1].get('total', 0) for inv in related_invoices if inv[0] == 'child')
                    },
                    'match_status': 'perfect' if abs(difference) < 100 else 'mismatch'
                })
        
        results[pattern_name] = pattern_results
        
        # サマリー出力
        if pattern_results:
            total_deals = len(pattern_results)
            perfect_matches = len([r for r in pattern_results if r['match_status'] == 'perfect'])
            total_difference = sum(abs(r['difference']) for r in pattern_results)
            
            print(f"    総件数: {total_deals}")
            print(f"    完全一致: {perfect_matches}件 ({perfect_matches/total_deals*100:.1f}%)")
            print(f"    総差額: ¥{total_difference:,.0f}")
            
            # 大きな差額TOP3
            large_diffs = sorted([r for r in pattern_results if abs(r['difference']) > 10000], 
                                key=lambda x: abs(x['difference']), reverse=True)[:3]
            
            if large_diffs:
                print(f"    大きな差額TOP3:")
                for i, result in enumerate(large_diffs, 1):
                    name = result.get('parent_name') or result.get('deal_name', 'N/A')
                    print(f"      {i}. {name} - 差額: ¥{result['difference']:,.0f}")
    
    return results

def generate_comprehensive_report(patterns, matching_results):
    """包括的なレポート生成"""
    print(f"\n" + "="*100)
    print("📊 包括的パターン分析レポート")
    print("="*100)
    
    # 各パターンの詳細分析
    pattern_explanations = {
        'pattern1_parent_only': 'パターン1: 親商談完結（親商談のみ、親商談総額=請求額）',
        'pattern2_children_only': 'パターン2: 子商談完結（親金額ゼロ、子商談総額=請求額）',
        'pattern3_parent_統括_no_amount': 'パターン3: 親統括・金額なし（親から子商談分請求）',
        'pattern4_parent_統括_with_amount': 'パターン4: 親統括・金額あり（親から子商談分+自分の分請求）',
        'pattern5_分担': 'パターン5: 自己負担・会社負担分担（親子両方で請求）',
        'no_parent_relation': '親子関係なし: 独立した商談'
    }
    
    total_analyzed = 0
    total_perfect_matches = 0
    total_difference_amount = 0
    
    for pattern_name, explanation in pattern_explanations.items():
        results = matching_results.get(pattern_name, [])
        if not results:
            continue
        
        print(f"\n🏷️ {explanation}")
        print("-" * 80)
        
        pattern_deals = patterns[pattern_name]
        total_analyzed += len(results)
        
        if pattern_name == 'no_parent_relation':
            total_amount = sum(r['deal_amount'] for r in results)
            total_invoice = sum(r['invoice_total'] for r in results)
        else:
            total_amount = sum(r['total_amount'] for r in results)
            total_invoice = sum(r['actual_invoice'] for r in results)
        
        perfect_matches = len([r for r in results if r['match_status'] == 'perfect'])
        total_perfect_matches += perfect_matches
        
        pattern_difference = sum(abs(r['difference']) for r in results)
        total_difference_amount += pattern_difference
        
        print(f"  📊 統計:")
        print(f"    対象件数: {len(results)}件")
        print(f"    商談総額: ¥{total_amount:,.0f}")
        print(f"    請求書総額: ¥{total_invoice:,.0f}")
        print(f"    完全一致: {perfect_matches}件 ({perfect_matches/len(results)*100:.1f}%)")
        print(f"    総差額: ¥{pattern_difference:,.0f}")
        
        # パターン固有の分析
        if pattern_name in ['pattern3_parent_統括_no_amount', 'pattern4_parent_統括_with_amount', 'pattern5_分担']:
            parent_invoice_count = sum(r['invoice_breakdown']['parent_invoices'] for r in results)
            child_invoice_count = sum(r['invoice_breakdown']['child_invoices'] for r in results)
            print(f"    親商談請求書: {parent_invoice_count}件")
            print(f"    子商談請求書: {child_invoice_count}件")
    
    # 全体サマリー
    print(f"\n" + "="*100)
    print("🎯 全体サマリー")
    print("="*100)
    print(f"総分析件数: {total_analyzed}件")
    print(f"完全一致件数: {total_perfect_matches}件 ({total_perfect_matches/total_analyzed*100:.1f}%)")
    print(f"総差額: ¥{total_difference_amount:,.0f}")
    
    if total_difference_amount < 1000000:  # 100万円未満
        print("✅ 全体的に商談と請求書は良好に整合しています")
    elif total_difference_amount < 5000000:  # 500万円未満
        print("⚠️ 一部に差額がありますが、概ね整合しています")
    else:
        print("❌ 大きな差額があります。詳細調査が必要です")
    
    print("="*100)

def main():
    """メイン処理"""
    print("="*100)
    print("📊 5パターン包括的商談・請求書整合性分析")
    print("="*100)
    
    try:
        # 1. トークン準備
        tokens = load_tokens()
        print("✅ トークン準備完了")
        
        # 2. 商談データ取得
        child_deals = get_comprehensive_deals(tokens['crm_headers'])
        if not child_deals:
            print("❌ 商談データが取得できませんでした")
            return
        
        # 3. 親商談ID抽出・取得
        parent_ids = set()
        for deal in child_deals:
            field78 = deal.get('field78')
            if field78 and isinstance(field78, dict):
                parent_id = field78.get('id')
                if parent_id:
                    parent_ids.add(parent_id)
        
        parent_deals = get_parent_deals_batch(tokens['crm_headers'], parent_ids)
        
        # 4. パターン分析
        patterns = analyze_deal_patterns(child_deals, parent_deals)
        
        # 5. 関連する全商談IDを収集
        all_deal_ids = set()
        for deal in child_deals:
            all_deal_ids.add(deal['id'])
        for parent_id, parent in parent_deals.items():
            all_deal_ids.add(parent_id)
        
        # 6. 請求書取得
        invoices = get_relevant_invoices(tokens['books_headers'], tokens['org_id'], all_deal_ids)
        
        # 7. マッチング分析
        matching_results = analyze_invoice_matching(patterns, invoices)
        
        # 8. 包括的レポート
        generate_comprehensive_report(patterns, matching_results)
        
        print(f"\n✅ 包括的分析完了")
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()