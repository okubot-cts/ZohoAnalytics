#!/usr/bin/env python3
"""
2024/4/1以降の全商談を完全抽出して5パターン分析
完了予定日(Closing_Date)でフィルタして包括的に分析
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

def get_all_deals_since_april_comprehensive(headers):
    """2024/4/1以降の全商談を包括的に取得"""
    print("📊 2024/4/1以降の全商談を包括的に取得中...")
    
    url = "https://www.zohoapis.com/crm/v2/Deals"
    all_deals = []
    page = 1
    max_pages = 50  # 最大50ページまで取得
    
    while page <= max_pages:
        params = {
            'fields': 'id,Deal_Name,Account_Name,Amount,Stage,Closing_Date,field78',
            'per_page': 200,
            'page': page,
            'sort_by': 'Closing_Date',
            'sort_order': 'desc'
        }
        
        try:
            print(f"  ページ{page}/{max_pages}を取得中...")
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
                        elif closing_date:  # 古いデータをカウント
                            old_deals_count += 1
                    
                    all_deals.extend(target_deals)
                    print(f"    対象: {len(target_deals)}件, 古い: {old_deals_count}件（累計: {len(all_deals)}件）")
                    
                    # 古いデータが多くなったら終了判定
                    if old_deals_count > 180:
                        print("    古いデータが多いため取得終了")
                        break
                    
                    if not data.get('info', {}).get('more_records', False):
                        break
                    page += 1
                else:
                    print("    データなし")
                    break
            else:
                print(f"    ❌ エラー: {response.status_code}")
                if response.status_code == 401:
                    print("    トークンが無効です")
                break
                
        except Exception as e:
            print(f"    ❌ 例外: {str(e)}")
            break
        
        time.sleep(0.2)  # API制限対策
    
    print(f"✅ 全商談取得完了: {len(all_deals)}件")
    return all_deals

def analyze_deal_structure_comprehensive(deals):
    """全商談の親子構造を包括的に分析"""
    print(f"\n🔍 全商談の親子構造分析（{len(deals)}件）...")
    
    # 親IDを抽出
    parent_ids = set()
    children_by_parent = defaultdict(list)
    standalone_deals = []
    
    for deal in deals:
        field78 = deal.get('field78')
        if field78 and isinstance(field78, dict):
            parent_id = field78.get('id')
            if parent_id:
                parent_ids.add(parent_id)
                children_by_parent[parent_id].append(deal)
            else:
                standalone_deals.append(deal)
        else:
            standalone_deals.append(deal)
    
    print(f"  親商談ID候補: {len(parent_ids)}個")
    print(f"  親子関係あり: {len(children_by_parent)}組")
    print(f"  独立商談: {len(standalone_deals)}件")
    
    return children_by_parent, parent_ids, standalone_deals

def get_parent_deals_efficient(headers, parent_ids):
    """親商談を効率的に取得"""
    print(f"📊 親商談詳細取得中（{len(parent_ids)}件）...")
    
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

def classify_all_deals_into_patterns(children_by_parent, parent_deals, standalone_deals):
    """全商談を5パターンに分類"""
    print(f"\n🔍 全商談の5パターン分類中...")
    
    patterns = {
        'pattern1_parent_only': [],        # パターン1: 親商談完結
        'pattern2_children_only': [],      # パターン2: 子商談完結  
        'pattern3_parent_統括_no_amount': [], # パターン3: 親統括・親金額なし
        'pattern4_parent_統括_with_amount': [], # パターン4: 親統括・親金額あり
        'pattern5_分担': [],                # パターン5: 自己負担・会社負担分担
        'standalone_deals': []             # 独立商談
    }
    
    # 独立商談を分類
    patterns['standalone_deals'] = standalone_deals
    
    # 親子セットを分析
    for parent_id, children in children_by_parent.items():
        parent = parent_deals.get(parent_id)
        
        if not parent:
            # 親商談が見つからない → 独立商談として扱う
            for child in children:
                patterns['standalone_deals'].append(child)
            continue
        
        # 期間フィルタ（親商談も2024/4/1以降かチェック）
        parent_closing_date = parent.get('Closing_Date', '')
        if parent_closing_date < '2024-04-01':
            # 親商談が対象期間外 → 子商談のみを独立として扱う
            for child in children:
                patterns['standalone_deals'].append(child)
            continue
        
        parent_amount = parent.get('Amount', 0) or 0
        children_amount = sum(c.get('Amount', 0) or 0 for c in children)
        
        deal_set = {
            'parent_id': parent_id,
            'parent': parent,
            'children': children,
            'parent_amount': parent_amount,
            'children_amount': children_amount,
            'total_amount': parent_amount + children_amount,
            'children_count': len(children)
        }
        
        # パターン判定
        if len(children) == 0:
            # 子商談がない（実際には発生しないはず）
            patterns['pattern1_parent_only'].append(deal_set)
            
        elif parent_amount == 0:
            # 親商談の金額がゼロ
            parent_name = parent.get('Deal_Name', '').upper()
            if any(keyword in parent_name for keyword in ['事務局', '統括', 'OFFICE', 'DESK', 'サポート', '_事務局']):
                patterns['pattern3_parent_統括_no_amount'].append(deal_set)
            else:
                patterns['pattern2_children_only'].append(deal_set)
                
        else:
            # 親商談に金額あり
            if children_amount == 0:
                # 子商談の金額がゼロ
                patterns['pattern1_parent_only'].append(deal_set)
            else:
                # 両方に金額あり
                total = parent_amount + children_amount
                parent_ratio = parent_amount / total
                
                if 0.15 <= parent_ratio <= 0.85:  # 両方に相応の金額
                    patterns['pattern5_分担'].append(deal_set)
                else:
                    patterns['pattern4_parent_統括_with_amount'].append(deal_set)
    
    # 統計出力
    print(f"  📋 最終分類結果:")
    for pattern_name, items in patterns.items():
        if pattern_name == 'standalone_deals':
            count = len(items)
            amount = sum(d.get('Amount', 0) or 0 for d in items)
        else:
            count = len(items)
            amount = sum(s['total_amount'] for s in items)
        
        print(f"    {pattern_name}: {count}組/件 - ¥{amount:,.0f}")
    
    return patterns

def generate_detailed_pattern_report(patterns):
    """詳細なパターンレポート生成"""
    print(f"\n" + "="*100)
    print("📊 2024/4/1以降 全商談 5パターン分析レポート")
    print("="*100)
    
    pattern_explanations = {
        'pattern1_parent_only': 'パターン1: 親商談完結（親商談のみで請求）',
        'pattern2_children_only': 'パターン2: 子商談完結（親金額ゼロ、子商談で請求）',
        'pattern3_parent_統括_no_amount': 'パターン3: 親統括・金額なし（親から子商談分を一括請求）',
        'pattern4_parent_統括_with_amount': 'パターン4: 親統括・金額あり（親から全体を請求）',
        'pattern5_分担': 'パターン5: 自己負担・会社負担分担（親子両方で請求）',
        'standalone_deals': '独立商談: 親子関係なし'
    }
    
    total_deals = 0
    total_amount = 0
    
    for pattern_name, explanation in pattern_explanations.items():
        items = patterns.get(pattern_name, [])
        if not items:
            continue
        
        print(f"\n🏷️ {explanation}")
        print("-" * 80)
        
        if pattern_name == 'standalone_deals':
            count = len(items)
            amount = sum(d.get('Amount', 0) or 0 for d in items)
            
            # ステージ別統計
            stage_stats = defaultdict(lambda: {'count': 0, 'amount': 0})
            for deal in items:
                stage = deal.get('Stage', '不明')
                deal_amount = deal.get('Amount', 0) or 0
                stage_stats[stage]['count'] += 1
                stage_stats[stage]['amount'] += deal_amount
            
            print(f"  📊 統計:")
            print(f"    総件数: {count}件")
            print(f"    総額（税抜き）: ¥{amount:,.0f}")
            print(f"    総額（税込み）: ¥{amount * 1.10:,.0f}")
            
            print(f"  📋 ステージ別内訳:")
            for stage, stats in sorted(stage_stats.items(), key=lambda x: x[1]['amount'], reverse=True):
                print(f"    {stage}: {stats['count']}件 - ¥{stats['amount']:,.0f}")
        
        else:
            # 親子セット
            count = len(items)
            amount = sum(s['total_amount'] for s in items)
            parent_amount = sum(s['parent_amount'] for s in items)
            children_amount = sum(s['children_amount'] for s in items)
            children_count = sum(s['children_count'] for s in items)
            
            print(f"  📊 統計:")
            print(f"    親子セット数: {count}組")
            print(f"    総子商談数: {children_count}件")
            print(f"    親商談総額: ¥{parent_amount:,.0f}")
            print(f"    子商談総額: ¥{children_amount:,.0f}")
            print(f"    合計総額（税抜き）: ¥{amount:,.0f}")
            print(f"    合計総額（税込み）: ¥{amount * 1.10:,.0f}")
            
            # 代表例を表示（上位3組）
            sorted_items = sorted(items, key=lambda x: x['total_amount'], reverse=True)
            print(f"  🏆 主要案件（TOP 3）:")
            for i, item in enumerate(sorted_items[:3], 1):
                parent_name = item['parent'].get('Deal_Name', '')[:50]
                print(f"    {i}. {parent_name}")
                print(f"       親: ¥{item['parent_amount']:,.0f}, 子: {item['children_count']}件/¥{item['children_amount']:,.0f}")
        
        total_deals += count if pattern_name == 'standalone_deals' else sum(1 + s['children_count'] for s in items)
        total_amount += amount
    
    # 全体サマリー
    print(f"\n" + "="*100)
    print("🎯 全体サマリー")
    print("="*100)
    print(f"総商談数: {total_deals:,.0f}件")
    print(f"総額（税抜き）: ¥{total_amount:,.0f}")
    print(f"総額（税込み）: ¥{total_amount * 1.10:,.0f}")
    
    # パターン比率
    print(f"\n📊 パターン別比率:")
    for pattern_name, items in patterns.items():
        if not items:
            continue
        
        if pattern_name == 'standalone_deals':
            pattern_amount = sum(d.get('Amount', 0) or 0 for d in items)
        else:
            pattern_amount = sum(s['total_amount'] for s in items)
        
        ratio = pattern_amount / total_amount * 100 if total_amount > 0 else 0
        print(f"  {pattern_name}: {ratio:.1f}%")
    
    print("="*100)

def analyze_stage_distribution(patterns):
    """ステージ分布の詳細分析"""
    print(f"\n🔍 ステージ分布詳細分析")
    print("="*60)
    
    all_stage_stats = defaultdict(lambda: {'count': 0, 'amount': 0})
    
    # 独立商談のステージ分析
    for deal in patterns.get('standalone_deals', []):
        stage = deal.get('Stage', '不明')
        amount = deal.get('Amount', 0) or 0
        all_stage_stats[stage]['count'] += 1
        all_stage_stats[stage]['amount'] += amount
    
    # 親子セットのステージ分析
    for pattern_name in ['pattern1_parent_only', 'pattern2_children_only', 'pattern3_parent_統括_no_amount', 'pattern4_parent_統括_with_amount', 'pattern5_分担']:
        for pc_set in patterns.get(pattern_name, []):
            # 親商談のステージ
            parent_stage = pc_set['parent'].get('Stage', '不明')
            parent_amount = pc_set['parent_amount']
            
            all_stage_stats[f"{parent_stage}(親)"]["count"] += 1
            all_stage_stats[f"{parent_stage}(親)"]["amount"] += parent_amount
            
            # 子商談のステージ
            for child in pc_set['children']:
                child_stage = child.get('Stage', '不明')
                child_amount = child.get('Amount', 0) or 0
                all_stage_stats[f"{child_stage}(子)"]["count"] += 1
                all_stage_stats[f"{child_stage}(子)"]["amount"] += child_amount
    
    print("📋 全体ステージ分布:")
    for stage, stats in sorted(all_stage_stats.items(), key=lambda x: x[1]['amount'], reverse=True):
        print(f"  {stage}: {stats['count']}件 - ¥{stats['amount']:,.0f}")

def main():
    """メイン処理"""
    print("="*100)
    print("📊 2024/4/1以降 全商談完全抽出・5パターン分析")
    print("="*100)
    
    try:
        # 1. CRMトークン準備
        headers = load_crm_token()
        print("✅ CRMトークン準備完了")
        
        # 2. 全商談取得
        all_deals = get_all_deals_since_april_comprehensive(headers)
        if not all_deals:
            print("❌ 商談データが取得できませんでした")
            return
        
        # 3. 親子構造分析
        children_by_parent, parent_ids, standalone_deals = analyze_deal_structure_comprehensive(all_deals)
        
        # 4. 親商談取得
        parent_deals = get_parent_deals_efficient(headers, parent_ids)
        
        # 5. パターン分類
        patterns = classify_all_deals_into_patterns(children_by_parent, parent_deals, standalone_deals)
        
        # 6. 詳細レポート生成
        generate_detailed_pattern_report(patterns)
        
        # 7. ステージ分布分析
        analyze_stage_distribution(patterns)
        
        print(f"\n✅ 完全分析完了")
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()