#!/usr/bin/env python3
"""
field78 (法人商談) フィールドの詳細調査
親子関係の実態を確認
"""
import requests
import json
from pathlib import Path

def investigate_field78():
    """field78フィールドの詳細調査"""
    
    # トークン読み込み
    base_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン"
    with open(base_path / "zoho_crm_tokens.json", 'r') as f:
        crm_tokens = json.load(f)
    
    headers = {'Authorization': f'Bearer {crm_tokens["access_token"]}'}
    
    print("="*70)
    print("🔍 field78 (法人商談) フィールド詳細調査")
    print("="*70)
    
    # より大量のデータを取得してfield78の値を確認
    print("\n📊 大量商談データでfield78の値を調査中...")
    
    url = "https://www.zohoapis.com/crm/v2/Deals"
    all_deals = []
    page = 1
    
    # 複数ページ取得
    while page <= 5:  # 最大5ページ（1000件）
        params = {
            'per_page': 200,
            'page': page,
            'sort_by': 'Created_Time',
            'sort_order': 'desc'
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            deals = data.get('data', [])
            
            if deals:
                all_deals.extend(deals)
                print(f"  ページ{page}: {len(deals)}件取得")
                
                if not data.get('info', {}).get('more_records', False):
                    break
                page += 1
            else:
                break
        else:
            print(f"  ❌ ページ{page}取得エラー: {response.status_code}")
            break
    
    print(f"✅ 総取得件数: {len(all_deals)}件")
    
    # field78の値を分析
    field78_values = {}
    field78_populated = []
    
    for deal in all_deals:
        field78_value = deal.get('field78')
        
        if field78_value:
            # オブジェクト型の場合
            if isinstance(field78_value, dict):
                parent_id = field78_value.get('id')
                parent_name = field78_value.get('name', 'N/A')
                
                field78_populated.append({
                    'child_deal': deal,
                    'parent_id': parent_id,
                    'parent_name': parent_name
                })
                
                if parent_id not in field78_values:
                    field78_values[parent_id] = []
                field78_values[parent_id].append(deal)
            
            # 文字列型の場合
            elif isinstance(field78_value, str) and field78_value.strip():
                field78_populated.append({
                    'child_deal': deal,
                    'parent_id': field78_value,
                    'parent_name': 'N/A'
                })
    
    print(f"\n🎯 field78に値があるレコード: {len(field78_populated)}件")
    
    if field78_populated:
        print("\n📋 親子関係の詳細:")
        
        # 親商談ごとにグループ化
        parent_groups = {}
        for item in field78_populated:
            parent_id = item['parent_id']
            if parent_id not in parent_groups:
                parent_groups[parent_id] = []
            parent_groups[parent_id].append(item)
        
        print(f"  親商談数: {len(parent_groups)}件")
        
        for i, (parent_id, children) in enumerate(parent_groups.items(), 1):
            # 親商談の詳細を取得
            parent_deal = next((d for d in all_deals if d.get('id') == parent_id), None)
            
            print(f"\n  {i}. 親商談ID: {parent_id}")
            if parent_deal:
                print(f"     親商談名: {parent_deal.get('Deal_Name', 'N/A')}")
                print(f"     親金額: ¥{parent_deal.get('Amount', 0):,.0f}")
                print(f"     親ステージ: {parent_deal.get('Stage', 'N/A')}")
                
                account = parent_deal.get('Account_Name', {})
                if isinstance(account, dict):
                    print(f"     取引先: {account.get('name', 'N/A')}")
            else:
                print(f"     ⚠️  親商談が見つかりません")
            
            print(f"     子商談数: {len(children)}件")
            
            total_child_amount = 0
            for j, child_info in enumerate(children[:5], 1):  # 最初の5件
                child = child_info['child_deal']
                child_amount = child.get('Amount', 0) or 0
                total_child_amount += child_amount
                
                print(f"       {j}. {child.get('Deal_Name', 'N/A')[:40]}")
                print(f"          金額: ¥{child_amount:,.0f}")
                print(f"          ステージ: {child.get('Stage', 'N/A')}")
            
            if len(children) > 5:
                remaining_children = children[5:]
                remaining_amount = sum(c['child_deal'].get('Amount', 0) or 0 for c in remaining_children)
                total_child_amount += remaining_amount
                print(f"       ... 他{len(remaining_children)}件 (¥{remaining_amount:,.0f})")
            
            print(f"     子商談合計: ¥{total_child_amount:,.0f}")
            
            # 親商談と子商談の金額比較
            parent_amount = parent_deal.get('Amount', 0) if parent_deal else 0
            if parent_amount > 0 and total_child_amount > 0:
                ratio = total_child_amount / parent_amount * 100
                print(f"     金額比率: 子商談/親商談 = {ratio:.1f}%")
    
    # 商談名パターンとfield78の関係を確認
    print(f"\n🔍 商談名パターンとfield78の関係:")
    
    # 商談名でグループ化
    name_groups = {}
    for deal in all_deals:
        deal_name = deal.get('Deal_Name', '')
        if '_' in deal_name:
            base_pattern = deal_name.split('_')[0]
            if base_pattern not in name_groups:
                name_groups[base_pattern] = []
            name_groups[base_pattern].append(deal)
    
    # 複数商談があるグループでfield78の使用状況を確認
    pattern_with_field78 = []
    
    for pattern, group_deals in name_groups.items():
        if len(group_deals) > 2:  # 3件以上のグループのみ
            field78_count = sum(1 for deal in group_deals if deal.get('field78'))
            
            if field78_count > 0:
                pattern_with_field78.append({
                    'pattern': pattern,
                    'total_deals': len(group_deals),
                    'field78_deals': field78_count,
                    'deals': group_deals
                })
    
    if pattern_with_field78:
        print(f"  field78を使用しているパターン: {len(pattern_with_field78)}個")
        
        for pattern_info in pattern_with_field78[:5]:
            pattern = pattern_info['pattern']
            total = pattern_info['total_deals']
            field78_count = pattern_info['field78_deals']
            
            print(f"\n    📊 {pattern}パターン:")
            print(f"       総商談数: {total}件")
            print(f"       field78使用: {field78_count}件")
            
            # field78を持つ商談の詳細
            for deal in pattern_info['deals']:
                field78_value = deal.get('field78')
                if field78_value:
                    parent_name = field78_value.get('name', 'N/A') if isinstance(field78_value, dict) else 'N/A'
                    print(f"         子: {deal.get('Deal_Name', 'N/A')[:30]}")
                    print(f"         親: {parent_name[:30]}")
    else:
        print("  field78を使用している商談名パターンはありませんでした")
    
    # Books請求書との関連を確認
    print(f"\n💰 Books請求書との関連確認:")
    
    # Books組織ID取得
    with open(base_path / "zoho_books_tokens.json", 'r') as f:
        books_tokens = json.load(f)
    
    books_headers = {'Authorization': f'Bearer {books_tokens["access_token"]}'}
    
    org_response = requests.get("https://www.zohoapis.com/books/v3/organizations", headers=books_headers)
    if org_response.status_code == 200:
        orgs = org_response.json()['organizations']
        org_id = None
        for org in orgs:
            if '株式会社シー・ティー・エス' in org.get('name', ''):
                org_id = org['organization_id']
                break
        
        if not org_id and orgs:
            org_id = orgs[0]['organization_id']
        
        # 請求書データ取得
        invoice_url = "https://www.zohoapis.com/books/v3/invoices"
        params = {
            'organization_id': org_id,
            'per_page': 200
        }
        
        invoice_response = requests.get(invoice_url, headers=books_headers, params=params)
        
        if invoice_response.status_code == 200:
            invoices = invoice_response.json().get('invoices', [])
            print(f"  ✅ {len(invoices)}件の請求書を取得")
            
            # 親商談と請求書の関係を確認
            parent_invoice_relations = []
            child_invoice_relations = []
            
            parent_deal_ids = set(field78_values.keys()) if field78_values else set()
            
            for invoice in invoices:
                ref_num = invoice.get('reference_number', '').strip()
                
                if ref_num:
                    # 親商談のIDと一致するか
                    if ref_num in parent_deal_ids:
                        parent_invoice_relations.append({
                            'invoice': invoice,
                            'parent_id': ref_num,
                            'relation_type': 'parent'
                        })
                    
                    # 子商談のIDと一致するか
                    for child_info in field78_populated:
                        if ref_num == child_info['child_deal'].get('id'):
                            child_invoice_relations.append({
                                'invoice': invoice,
                                'child_deal': child_info['child_deal'],
                                'parent_id': child_info['parent_id'],
                                'relation_type': 'child'
                            })
            
            print(f"  親商談への請求書: {len(parent_invoice_relations)}件")
            print(f"  子商談への請求書: {len(child_invoice_relations)}件")
            
            if parent_invoice_relations or child_invoice_relations:
                print(f"\n  📋 請求書パターン:")
                
                for rel in parent_invoice_relations[:3]:
                    invoice = rel['invoice']
                    print(f"    親請求: {invoice.get('invoice_number')} → 親商談ID {rel['parent_id']}")
                    print(f"           金額: ¥{invoice.get('total', 0):,.0f}")
                
                for rel in child_invoice_relations[:3]:
                    invoice = rel['invoice']
                    child_name = rel['child_deal'].get('Deal_Name', 'N/A')
                    print(f"    子請求: {invoice.get('invoice_number')} → 子商談 {child_name[:20]}")
                    print(f"           金額: ¥{invoice.get('total', 0):,.0f}")
        else:
            print(f"  ❌ 請求書取得エラー: {invoice_response.status_code}")
    
    print(f"\n{'='*70}")
    print("📝 結論:")
    if field78_populated:
        print("✅ field78 (法人商談) が親子関係管理に使用されています！")
        print("✅ 明示的な親商談ID参照による正確な階層構造を確認")
        print("✅ 請求書処理では親商談・子商談の両方が使用される可能性")
    else:
        print("⚠️  現在のデータではfield78の使用例は確認できませんでした")
        print("   より古いデータや特定の企業案件で使用されている可能性")
    print("="*70)

if __name__ == "__main__":
    investigate_field78()