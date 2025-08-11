#!/usr/bin/env python3
"""
レイアウトと親子構造のデバッグスクリプト
"""
import requests
import json
from pathlib import Path
from collections import Counter

def debug_layouts_and_structure():
    """レイアウトと親子構造のデバッグ"""
    
    # トークン読み込み
    base_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン"
    with open(base_path / "zoho_crm_tokens.json", 'r') as f:
        crm_tokens = json.load(f)
    
    headers = {'Authorization': f'Bearer {crm_tokens["access_token"]}'}
    
    print("="*60)
    print("🔍 レイアウトと親子構造デバッグ")
    print("="*60)
    
    # 1. レイアウト情報の詳細取得
    print("\n📋 レイアウト情報詳細:")
    url = "https://www.zohoapis.com/crm/v2/settings/layouts"
    params = {'module': 'Deals'}
    
    response = requests.get(url, headers=headers, params=params)
    layouts = {}
    
    if response.status_code == 200:
        data = response.json()
        layout_list = data.get('layouts', [])
        
        for layout in layout_list:
            layout_id = layout.get('id')
            layout_name = layout.get('name')
            layouts[layout_id] = layout_name
            
            print(f"  ID: {layout_id}")
            print(f"  名前: {layout_name}")
            print(f"  表示名: {layout.get('display_label', 'N/A')}")
            print(f"  ステータス: {layout.get('status', 'N/A')}")
            print()
    
    # 2. サンプル商談でレイアウト確認
    print("📊 サンプル商談のレイアウト確認:")
    
    deals_url = "https://www.zohoapis.com/crm/v2/Deals"
    params = {
        'fields': 'id,Deal_Name,Stage,field78,$layout_id',
        'per_page': 20
    }
    
    response = requests.get(deals_url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        deals = data.get('data', [])
        
        layout_counts = Counter()
        field78_counts = {'有り': 0, '無し': 0}
        
        for i, deal in enumerate(deals, 1):
            layout_id_raw = deal.get('$layout_id')
            
            # layout_idの形式を確認
            if isinstance(layout_id_raw, dict):
                layout_id = layout_id_raw.get('id')
            else:
                layout_id = layout_id_raw
            
            layout_name = layouts.get(layout_id, f'Unknown({layout_id})')
            field78 = deal.get('field78')
            
            layout_counts[layout_name] += 1
            
            if field78:
                field78_counts['有り'] += 1
            else:
                field78_counts['無し'] += 1
            
            print(f"  {i:2}. {deal.get('Deal_Name', 'N/A')[:40]}")
            print(f"      レイアウト: {layout_name}")
            print(f"      field78: {'有り' if field78 else '無し'}")
            if field78 and isinstance(field78, dict):
                print(f"      親ID: {field78.get('id', 'N/A')}")
                print(f"      親名: {field78.get('name', 'N/A')}")
        
        print(f"\n📈 レイアウト統計:")
        for layout_name, count in layout_counts.most_common():
            print(f"  {layout_name}: {count}件")
        
        print(f"\n📈 field78統計:")
        for status, count in field78_counts.items():
            print(f"  {status}: {count}件")
    
    # 3. 「法人」「語学サポート」レイアウトの商談を検索
    print(f"\n🔍 レイアウト別商談検索:")
    
    target_layouts = []
    for layout_id, layout_name in layouts.items():
        if '法人' in layout_name or '語学' in layout_name or 'サポート' in layout_name:
            target_layouts.append((layout_id, layout_name))
    
    if target_layouts:
        print(f"  対象レイアウト: {len(target_layouts)}個")
        for layout_id, layout_name in target_layouts:
            print(f"    - {layout_name} (ID: {layout_id})")
        
        # 各レイアウトで商談を検索
        for layout_id, layout_name in target_layouts:
            print(f"\n  📊 {layout_name} の商談:")
            
            search_params = {
                'fields': 'id,Deal_Name,Stage,Amount,field78',
                'per_page': 10,
                'criteria': f'($layout_id:equals:{layout_id})'
            }
            
            try:
                response = requests.get(deals_url, headers=headers, params=search_params)
                
                if response.status_code == 200:
                    search_data = response.json()
                    layout_deals = search_data.get('data', [])
                    
                    print(f"    該当商談: {len(layout_deals)}件")
                    
                    for deal in layout_deals[:5]:  # 最初の5件
                        field78 = deal.get('field78')
                        parent_info = ""
                        if field78 and isinstance(field78, dict):
                            parent_info = f" → 親: {field78.get('name', 'N/A')[:20]}"
                        
                        print(f"      • {deal.get('Deal_Name', 'N/A')[:35]}{parent_info}")
                        print(f"        ステージ: {deal.get('Stage', 'N/A')}, 金額: ¥{deal.get('Amount', 0):,.0f}")
                else:
                    print(f"    ❌ 検索エラー: {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ 検索エラー: {str(e)}")
    else:
        print("  対象レイアウトが見つかりませんでした")
        print("  利用可能なレイアウト:")
        for layout_name in layouts.values():
            print(f"    - {layout_name}")
    
    print(f"\n{'='*60}")
    print("デバッグ完了")

if __name__ == "__main__":
    debug_layouts_and_structure()