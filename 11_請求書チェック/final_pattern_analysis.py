#!/usr/bin/env python3
"""
最終パターン分析
親子構造が確認されたデータで5パターンを正しく分析
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

def get_representative_parent_child_sets(headers):
    """代表的な親子セットを取得して分析"""
    print("📊 代表的な親子セット取得中...")
    
    # 既知の親商談ID（調査で発見された）
    known_parent_ids = [
        '5187347000129692086',  # JT ETE (¥0親、子200件)
        '5187347000097906475',  # アイホン (51件)
        '5187347000057451366',  # GSK (200件)
        '5187347000176119064',  # 野村證券 (99件)
        '5187347000116916356',  # 東電設計 (62件)
        '5187347000145334425'   # SMM (141件)
    ]
    
    parent_child_sets = []
    
    for parent_id in known_parent_ids:
        print(f"  📊 親商談 {parent_id} を分析中...")
        
        # 1. 親商談詳細取得
        parent_url = f"https://www.zohoapis.com/crm/v2/Deals/{parent_id}"
        try:
            response = requests.get(parent_url, headers=headers, timeout=30)
            if response.status_code == 200:
                parent_data = response.json()
                parent = parent_data.get('data', [{}])[0]
            else:
                print(f"    ❌ 親商談取得エラー: {response.status_code}")
                continue
        except Exception as e:
            print(f"    ❌ 親商談例外: {str(e)}")
            continue
        
        # 2. 子商談検索
        search_url = "https://www.zohoapis.com/crm/v2/Deals/search"
        params = {
            'criteria': f'(field78:equals:{parent_id})',
            'fields': 'id,Deal_Name,Amount,Stage,Closing_Date',
            'per_page': 200
        }
        
        try:
            response = requests.get(search_url, headers=headers, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                children = data.get('data', [])
            elif response.status_code == 204:
                children = []
            else:
                print(f"    ❌ 子商談検索エラー: {response.status_code}")
                children = []
        except Exception as e:
            print(f"    ❌ 子商談例外: {str(e)}")
            children = []
        
        parent_amount = parent.get('Amount', 0) or 0
        children_amount = sum(c.get('Amount', 0) or 0 for c in children)
        
        parent_child_sets.append({
            'parent_id': parent_id,
            'parent': parent,
            'children': children,
            'parent_amount': parent_amount,
            'children_amount': children_amount,
            'total_amount': parent_amount + children_amount,
            'children_count': len(children)
        })
        
        print(f"    ✅ 親商談: ¥{parent_amount:,.0f}, 子商談: {len(children)}件/¥{children_amount:,.0f}")
        
        time.sleep(0.5)
    
    print(f"✅ 代表親子セット取得完了: {len(parent_child_sets)}組")
    return parent_child_sets

def classify_into_5_patterns(parent_child_sets):
    """5つのパターンに分類"""
    print(f"\n🔍 5パターン分類中...")
    
    patterns = {
        'pattern1_parent_only': [],        # パターン1: 親商談完結
        'pattern2_children_only': [],      # パターン2: 子商談完結  
        'pattern3_parent_統括_no_amount': [], # パターン3: 親統括・親金額なし
        'pattern4_parent_統括_with_amount': [], # パターン4: 親統括・親金額あり
        'pattern5_分担': []                 # パターン5: 自己負担・会社負担分担
    }
    
    for pc_set in parent_child_sets:
        parent_amount = pc_set['parent_amount']
        children_amount = pc_set['children_amount']
        children_count = pc_set['children_count']
        parent_name = pc_set['parent'].get('Deal_Name', '').upper()
        
        # パターン判定ロジック
        if children_count == 0:
            # 子商談がない
            patterns['pattern1_parent_only'].append(pc_set)
            
        elif parent_amount == 0:
            # 親商談の金額がゼロ
            if any(keyword in parent_name for keyword in ['事務局', '統括', 'OFFICE', 'DESK', 'サポート']):
                patterns['pattern3_parent_統括_no_amount'].append(pc_set)
            else:
                patterns['pattern2_children_only'].append(pc_set)
                
        else:
            # 親商談に金額あり
            if children_amount == 0:
                # 子商談の金額がゼロ
                patterns['pattern1_parent_only'].append(pc_set)
            else:
                # 両方に金額あり
                total = parent_amount + children_amount
                parent_ratio = parent_amount / total
                
                if 0.2 <= parent_ratio <= 0.8:  # 両方に相応の金額
                    patterns['pattern5_分担'].append(pc_set)
                else:
                    patterns['pattern4_parent_統括_with_amount'].append(pc_set)
    
    # 分類結果表示
    print(f"  📋 分類結果:")
    for pattern_name, sets in patterns.items():
        total_amount = sum(s['total_amount'] for s in sets)
        print(f"    {pattern_name}: {len(sets)}組 - ¥{total_amount:,.0f}")
        
        # 代表例を表示
        for i, pc_set in enumerate(sets[:2]):  # 最初の2組
            parent_name = pc_set['parent'].get('Deal_Name', '')[:40]
            parent_amount = pc_set['parent_amount']
            children_count = pc_set['children_count']
            children_amount = pc_set['children_amount']
            
            print(f"      例{i+1}: {parent_name}")
            print(f"           親: ¥{parent_amount:,.0f}, 子: {children_count}件/¥{children_amount:,.0f}")
    
    return patterns

def get_sample_invoices_by_reference(headers, org_id, deal_ids):
    """特定の商談IDの請求書を効率的に取得"""
    print(f"\n📄 特定商談の請求書取得中（{len(deal_ids)}件の商談）...")
    
    deal_id_set = set(deal_ids)
    matched_invoices = []
    
    url = "https://www.zohoapis.com/books/v3/invoices"
    page = 1
    
    while page <= 15:  # 最大15ページ
        params = {
            'organization_id': org_id,
            'per_page': 200,
            'page': page,
            'sort_column': 'date',
            'sort_order': 'D'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                invoices = data.get('invoices', [])
                
                if invoices:
                    page_matches = 0
                    for invoice in invoices:
                        ref_num = invoice.get('reference_number', '').strip()
                        if ref_num in deal_id_set:
                            matched_invoices.append(invoice)
                            page_matches += 1
                    
                    print(f"  ページ{page}: {page_matches}件マッチ（累計: {len(matched_invoices)}件）")
                    
                    if not data.get('page_context', {}).get('has_more_page', False):
                        break
                    page += 1
                else:
                    break
            else:
                print(f"  ❌ ページ{page}エラー: {response.status_code}")
                break
        
        except Exception as e:
            print(f"  ❌ ページ{page}例外: {str(e)}")
            break
        
        time.sleep(0.3)
    
    print(f"✅ 請求書取得完了: {len(matched_invoices)}件")
    return matched_invoices

def analyze_pattern_invoice_matching(patterns, invoices):
    """パターン別請求書マッチング詳細分析"""
    print(f"\n🔗 パターン別詳細マッチング分析...")
    
    # 請求書をreference_numberでインデックス化
    invoice_map = defaultdict(list)
    for invoice in invoices:
        ref_num = invoice.get('reference_number', '').strip()
        if ref_num:
            invoice_map[ref_num].append(invoice)
    
    pattern_results = {}
    
    pattern_explanations = {
        'pattern1_parent_only': 'パターン1: 親商談完結',
        'pattern2_children_only': 'パターン2: 子商談完結',  
        'pattern3_parent_統括_no_amount': 'パターン3: 親統括・金額なし',
        'pattern4_parent_統括_with_amount': 'パターン4: 親統括・金額あり',
        'pattern5_分担': 'パターン5: 分担（自己負担・会社負担）'
    }
    
    for pattern_name, explanation in pattern_explanations.items():
        print(f"\n  📊 {explanation}")
        
        pattern_sets = patterns.get(pattern_name, [])
        if not pattern_sets:
            print(f"    該当なし")
            continue
        
        results = []
        
        for pc_set in pattern_sets:
            parent = pc_set['parent']
            children = pc_set['children']
            
            # 請求書収集
            parent_invoices = invoice_map.get(parent['id'], [])
            child_invoices = []
            for child in children:
                child_invoices.extend(invoice_map.get(child['id'], []))
            
            parent_invoice_amount = sum(inv.get('total', 0) for inv in parent_invoices)
            child_invoice_amount = sum(inv.get('total', 0) for inv in child_invoices)
            total_invoice_amount = parent_invoice_amount + child_invoice_amount
            
            # パターン別期待値計算
            if pattern_name == 'pattern1_parent_only':
                # 親商談から請求されるはず
                expected_amount = pc_set['parent_amount'] * 1.10
            elif pattern_name == 'pattern2_children_only':
                # 子商談から請求されるはず
                expected_amount = pc_set['children_amount'] * 1.10
            elif pattern_name == 'pattern3_parent_統括_no_amount':
                # 親商談から子商談分を請求されるはず
                expected_amount = pc_set['children_amount'] * 1.10
            elif pattern_name == 'pattern4_parent_統括_with_amount':
                # 親商談から全体を請求される可能性
                expected_amount = pc_set['total_amount'] * 1.10
            elif pattern_name == 'pattern5_分担':
                # 親子両方から請求される
                expected_amount = pc_set['total_amount'] * 1.10
            
            difference = expected_amount - total_invoice_amount
            
            result = {
                'parent_name': parent.get('Deal_Name', '')[:50],
                'parent_amount': pc_set['parent_amount'],
                'children_count': pc_set['children_count'],
                'children_amount': pc_set['children_amount'],
                'total_amount': pc_set['total_amount'],
                'expected_invoice': expected_amount,
                'actual_invoice': total_invoice_amount,
                'parent_invoice_amount': parent_invoice_amount,
                'child_invoice_amount': child_invoice_amount,
                'parent_invoice_count': len(parent_invoices),
                'child_invoice_count': len(child_invoices),
                'difference': difference,
                'match_status': 'perfect' if abs(difference) < 1000 else 'mismatch'
            }
            
            results.append(result)
        
        pattern_results[pattern_name] = results
        
        # パターン別サマリー
        if results:
            perfect_matches = len([r for r in results if r['match_status'] == 'perfect'])
            total_difference = sum(abs(r['difference']) for r in results)
            
            print(f"    件数: {len(results)}組")
            print(f"    完全一致: {perfect_matches}組 ({perfect_matches/len(results)*100:.1f}%)")
            print(f"    総差額: ¥{total_difference:,.0f}")
            
            # 詳細表示
            for result in results:
                print(f"    - {result['parent_name']}")
                print(f"      商談: 親¥{result['parent_amount']:,.0f} + 子¥{result['children_amount']:,.0f} = ¥{result['total_amount']:,.0f}")
                print(f"      請求: 親¥{result['parent_invoice_amount']:,.0f} + 子¥{result['child_invoice_amount']:,.0f} = ¥{result['actual_invoice']:,.0f}")
                print(f"      差額: ¥{result['difference']:,.0f} ({'✅' if result['match_status'] == 'perfect' else '❌'})")
    
    return pattern_results

def generate_final_report(patterns, pattern_results):
    """最終レポート生成"""
    print(f"\n" + "="*100)
    print("🎯 5パターン最終分析レポート")
    print("="*100)
    
    total_sets = 0
    total_perfect_matches = 0
    total_difference = 0
    
    pattern_explanations = {
        'pattern1_parent_only': 'パターン1: 親商談完結（親商談のみ、親商談総額=請求額）',
        'pattern2_children_only': 'パターン2: 子商談完結（親金額ゼロ、子商談総額=請求額）',
        'pattern3_parent_統括_no_amount': 'パターン3: 親統括・金額なし（親から子商談分請求）',
        'pattern4_parent_統括_with_amount': 'パターン4: 親統括・金額あり（親から全体請求）',
        'pattern5_分担': 'パターン5: 自己負担・会社負担分担（親子両方で請求）'
    }
    
    for pattern_name, explanation in pattern_explanations.items():
        results = pattern_results.get(pattern_name, [])
        pattern_sets = patterns.get(pattern_name, [])
        
        if not results:
            continue
        
        print(f"\n📋 {explanation}")
        print("-" * 80)
        
        perfect_matches = len([r for r in results if r['match_status'] == 'perfect'])
        pattern_difference = sum(abs(r['difference']) for r in results)
        
        total_sets += len(results)
        total_perfect_matches += perfect_matches
        total_difference += pattern_difference
        
        print(f"  対象組数: {len(results)}組")
        print(f"  完全一致: {perfect_matches}組 ({perfect_matches/len(results)*100:.1f}%)")
        print(f"  総差額: ¥{pattern_difference:,.0f}")
        
        if pattern_name == 'pattern3_parent_統括_no_amount':
            print(f"  ✅ 仮説検証: JT ETEのように親商談¥0、子商談分を親から請求")
        elif pattern_name == 'pattern5_分担':
            print(f"  ✅ 仮説検証: 自己負担は子商談、会社負担は親商談で請求分担")
    
    print(f"\n" + "="*100)
    print("🏆 総合評価")
    print("="*100)
    print(f"総分析組数: {total_sets}組")
    print(f"完全一致組数: {total_perfect_matches}組 ({total_perfect_matches/total_sets*100:.1f}%)")
    print(f"総差額: ¥{total_difference:,.0f}")
    
    if total_perfect_matches/total_sets >= 0.8:
        print("🎉 素晴らしい！商談・請求書の整合性は非常に高いです")
    elif total_perfect_matches/total_sets >= 0.6:
        print("👍 良好！商談・請求書の整合性は概ね良好です")
    else:
        print("⚠️ 注意！商談・請求書に不整合が多く見られます")
    
    print("="*100)

def main():
    """メイン処理"""
    print("="*100)
    print("🎯 最終5パターン包括分析")
    print("="*100)
    
    try:
        # 1. トークン準備
        tokens = load_tokens()
        print("✅ トークン準備完了")
        
        # 2. 代表的な親子セット取得
        parent_child_sets = get_representative_parent_child_sets(tokens['crm_headers'])
        
        # 3. 5パターン分類
        patterns = classify_into_5_patterns(parent_child_sets)
        
        # 4. 全関連商談IDを収集
        all_deal_ids = set()
        for pc_set in parent_child_sets:
            all_deal_ids.add(pc_set['parent']['id'])
            for child in pc_set['children']:
                all_deal_ids.add(child['id'])
        
        # 5. 関連請求書取得
        invoices = get_sample_invoices_by_reference(tokens['books_headers'], tokens['org_id'], all_deal_ids)
        
        # 6. パターン別マッチング分析
        pattern_results = analyze_pattern_invoice_matching(patterns, invoices)
        
        # 7. 最終レポート
        generate_final_report(patterns, pattern_results)
        
        print(f"\n✅ 最終分析完了")
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()