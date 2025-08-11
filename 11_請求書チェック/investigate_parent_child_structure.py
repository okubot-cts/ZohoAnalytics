#!/usr/bin/env python3
"""
親子構造の詳細調査
なぜ親子関係が見つからないかを調査
"""
import requests
import json
from pathlib import Path
from collections import defaultdict
import time

def load_crm_token():
    """CRMトークンを読み込み"""
    token_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン" / "zoho_crm_tokens.json"
    with open(token_path, 'r') as f:
        tokens = json.load(f)
    return {'Authorization': f'Bearer {tokens["access_token"]}'}

def investigate_field78_structure(headers):
    """field78の構造を詳しく調査"""
    print("🔍 field78構造詳細調査...")
    
    url = "https://www.zohoapis.com/crm/v2/Deals"
    params = {
        'fields': 'id,Deal_Name,Amount,Stage,Closing_Date,field78',
        'per_page': 200,
        'page': 1
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            deals = data.get('data', [])
            
            field78_patterns = {}
            parent_child_pairs = []
            
            for deal in deals[:50]:  # 最初の50件を詳細調査
                field78 = deal.get('field78')
                deal_id = deal['id']
                deal_name = deal.get('Deal_Name', '')
                
                if field78:
                    field78_type = type(field78).__name__
                    if field78_type not in field78_patterns:
                        field78_patterns[field78_type] = []
                    
                    if isinstance(field78, dict):
                        parent_id = field78.get('id')
                        parent_name = field78.get('name', '')
                        
                        field78_patterns[field78_type].append({
                            'child_id': deal_id,
                            'child_name': deal_name,
                            'parent_id': parent_id,
                            'parent_name': parent_name,
                            'full_field78': field78
                        })
                        
                        if parent_id:
                            parent_child_pairs.append((parent_id, deal_id))
                    else:
                        field78_patterns[field78_type].append({
                            'deal_id': deal_id,
                            'deal_name': deal_name,
                            'field78_value': field78
                        })
                else:
                    if 'None' not in field78_patterns:
                        field78_patterns['None'] = []
                    field78_patterns['None'].append({
                        'deal_id': deal_id,
                        'deal_name': deal_name
                    })
            
            print(f"  📊 field78パターン分析:")
            for pattern_type, items in field78_patterns.items():
                print(f"    {pattern_type}: {len(items)}件")
                
                # 詳細表示（最初の3件）
                for i, item in enumerate(items[:3]):
                    if pattern_type == 'dict':
                        print(f"      例{i+1}: 子商談「{item['child_name'][:30]}」→ 親商談「{item['parent_name'][:30]}」")
                        print(f"             親ID: {item['parent_id']}")
                    elif pattern_type == 'None':
                        print(f"      例{i+1}: {item['deal_name'][:40]} (field78なし)")
                    else:
                        print(f"      例{i+1}: {item['deal_name'][:30]} = {item['field78_value']}")
            
            print(f"\n  🔗 発見された親子ペア: {len(parent_child_pairs)}組")
            
            return parent_child_pairs, field78_patterns
    
    except Exception as e:
        print(f"  ❌ 調査エラー: {str(e)}")
        return [], {}

def search_specific_child_deals(headers, parent_ids):
    """特定の親IDを持つ子商談を検索"""
    print(f"🔍 特定親商談の子商談検索（親商談{len(parent_ids)}個）...")
    
    found_children = []
    
    for i, parent_id in enumerate(parent_ids[:5], 1):  # 最初の5個のみ
        print(f"  親商談{i}: {parent_id}")
        
        url = "https://www.zohoapis.com/crm/v2/Deals/search"
        params = {
            'criteria': f'(field78:equals:{parent_id})',
            'fields': 'id,Deal_Name,Amount,Stage,Closing_Date,field78'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                children = data.get('data', [])
                
                if children:
                    print(f"    子商談: {len(children)}件発見")
                    for child in children[:3]:  # 最初の3件を表示
                        print(f"      - {child.get('Deal_Name', '')[:40]}")
                    
                    found_children.extend(children)
                else:
                    print(f"    子商談: 0件")
            elif response.status_code == 204:
                print(f"    子商談: 0件 (204)")
            else:
                print(f"    ❌ エラー: {response.status_code}")
        
        except Exception as e:
            print(f"    ❌ 例外: {str(e)}")
        
        time.sleep(0.5)
    
    print(f"  ✅ 総子商談発見数: {len(found_children)}件")
    return found_children

def analyze_deal_amounts_and_stages(headers):
    """商談金額とステージの分析"""
    print(f"\n📊 商談金額・ステージ詳細分析...")
    
    url = "https://www.zohoapis.com/crm/v2/Deals"
    params = {
        'fields': 'id,Deal_Name,Amount,Stage,Closing_Date,field78',
        'per_page': 200,
        'page': 1
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            deals = data.get('data', [])
            
            # 金額・ステージ分析
            stage_stats = defaultdict(lambda: {'count': 0, 'amount': 0, 'has_parent': 0})
            amount_ranges = defaultdict(int)
            
            for deal in deals:
                stage = deal.get('Stage', '不明')
                amount = deal.get('Amount', 0) or 0
                field78 = deal.get('field78')
                
                stage_stats[stage]['count'] += 1
                stage_stats[stage]['amount'] += amount
                
                if field78 and isinstance(field78, dict) and field78.get('id'):
                    stage_stats[stage]['has_parent'] += 1
                
                # 金額範囲
                if amount == 0:
                    amount_ranges['¥0'] += 1
                elif amount < 100000:
                    amount_ranges['¥1-99,999'] += 1
                elif amount < 1000000:
                    amount_ranges['¥100K-999K'] += 1
                elif amount < 10000000:
                    amount_ranges['¥1M-9.9M'] += 1
                else:
                    amount_ranges['¥10M+'] += 1
            
            print(f"  📋 ステージ別統計:")
            for stage, stats in sorted(stage_stats.items(), key=lambda x: x[1]['amount'], reverse=True):
                count = stats['count']
                amount = stats['amount']
                has_parent = stats['has_parent']
                parent_ratio = has_parent/count*100 if count > 0 else 0
                
                print(f"    {stage}: {count}件 - ¥{amount:,.0f} (親関係: {has_parent}件/{parent_ratio:.1f}%)")
            
            print(f"\n  💰 金額範囲別:")
            for range_name, count in amount_ranges.items():
                print(f"    {range_name}: {count}件")
            
            # 高額商談TOP10
            high_value_deals = sorted([d for d in deals if (d.get('Amount', 0) or 0) > 1000000],
                                    key=lambda x: x.get('Amount', 0) or 0, reverse=True)[:10]
            
            print(f"\n  🏆 高額商談TOP10:")
            for i, deal in enumerate(high_value_deals, 1):
                amount = deal.get('Amount', 0) or 0
                name = deal.get('Deal_Name', '')[:40]
                stage = deal.get('Stage', '')
                field78 = deal.get('field78')
                has_parent = '親あり' if (field78 and isinstance(field78, dict) and field78.get('id')) else '親なし'
                
                print(f"    {i:2}. ¥{amount:,.0f} - {name} ({stage}, {has_parent})")
    
    except Exception as e:
        print(f"  ❌ 分析エラー: {str(e)}")

def investigate_jt_etp_pattern(headers):
    """JT ETEパターンの調査"""
    print(f"\n🔍 JT ETEパターン調査...")
    
    jt_etp_parent_id = '5187347000129692086'
    
    # 1. 親商談詳細
    print(f"  📊 JT ETE親商談詳細:")
    url = f"https://www.zohoapis.com/crm/v2/Deals/{jt_etp_parent_id}"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            parent = data.get('data', [{}])[0]
            
            print(f"    名前: {parent.get('Deal_Name', '')}")
            print(f"    金額: ¥{parent.get('Amount', 0):,.0f}")
            print(f"    ステージ: {parent.get('Stage', '')}")
            print(f"    成約日: {parent.get('Closing_Date', '')}")
    
    except Exception as e:
        print(f"    ❌ 親商談取得エラー: {str(e)}")
    
    # 2. 子商談検索
    print(f"  🔍 JT ETE子商談検索:")
    url = "https://www.zohoapis.com/crm/v2/Deals/search"
    params = {
        'criteria': f'(field78:equals:{jt_etp_parent_id})',
        'fields': 'id,Deal_Name,Amount,Stage,Closing_Date'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            children = data.get('data', [])
            
            print(f"    子商談数: {len(children)}件")
            
            if children:
                total_amount = sum(c.get('Amount', 0) or 0 for c in children)
                print(f"    子商談総額: ¥{total_amount:,.0f}")
                
                stage_breakdown = defaultdict(int)
                for child in children:
                    stage = child.get('Stage', '不明')
                    stage_breakdown[stage] += 1
                
                print(f"    ステージ内訳:")
                for stage, count in stage_breakdown.items():
                    print(f"      {stage}: {count}件")
        else:
            print(f"    ❌ 子商談検索エラー: {response.status_code}")
    
    except Exception as e:
        print(f"    ❌ 子商談検索例外: {str(e)}")

def main():
    """メイン処理"""
    print("="*80)
    print("🔍 親子構造詳細調査")
    print("="*80)
    
    try:
        headers = load_crm_token()
        print("✅ CRMトークン準備完了")
        
        # 1. field78構造調査
        parent_child_pairs, field78_patterns = investigate_field78_structure(headers)
        
        # 2. 特定の親商談の子商談検索
        if parent_child_pairs:
            unique_parent_ids = list(set(pair[0] for pair in parent_child_pairs))
            found_children = search_specific_child_deals(headers, unique_parent_ids)
        
        # 3. 商談金額・ステージ分析
        analyze_deal_amounts_and_stages(headers)
        
        # 4. JT ETEパターン調査
        investigate_jt_etp_pattern(headers)
        
        print(f"\n" + "="*80)
        print("🎯 調査結論")
        print("="*80)
        
        if field78_patterns.get('dict', []):
            dict_count = len(field78_patterns['dict'])
            print(f"✅ 親子関係を持つ商談: {dict_count}件発見")
            print("   親子構造は存在しているが、期間フィルタの影響で分析対象から除外された可能性")
        else:
            print("❌ 現在のサンプルに親子関係を持つ商談が見つかりません")
        
        if parent_child_pairs:
            print(f"✅ 実際の親子ペア: {len(parent_child_pairs)}組確認")
            print("   より大きなサンプルサイズが必要")
        else:
            print("❌ 親子ペアが見つかりませんでした")
        
        print("="*80)
        
    except Exception as e:
        print(f"❌ 調査エラー: {str(e)}")

if __name__ == "__main__":
    main()