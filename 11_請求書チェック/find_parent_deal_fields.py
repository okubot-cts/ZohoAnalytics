#!/usr/bin/env python3
"""
親商談IDフィールドの詳細調査
子商談に親商談IDを保存するフィールドを特定
"""
import requests
import json
from pathlib import Path

def find_parent_deal_fields():
    """親商談IDを保存するフィールドを詳細調査"""
    
    # トークン読み込み
    base_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン"
    with open(base_path / "zoho_crm_tokens.json", 'r') as f:
        crm_tokens = json.load(f)
    
    headers = {'Authorization': f'Bearer {crm_tokens["access_token"]}'}
    
    print("="*70)
    print("🔍 ZohoCRM 親商談IDフィールド詳細調査")
    print("="*70)
    
    # 1. 全フィールド情報を詳細取得
    print("\n📋 商談モジュールの全フィールドを詳細調査中...")
    
    url = "https://www.zohoapis.com/crm/v2/settings/fields"
    params = {'module': 'Deals'}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        field_data = response.json()
        fields = field_data.get('fields', [])
        
        print(f"✅ 総フィールド数: {len(fields)}個")
        
        # 親子関係候補フィールドを詳細分析
        parent_candidates = []
        lookup_fields = []
        custom_fields = []
        
        for field in fields:
            api_name = field.get('api_name', '')
            field_label = field.get('field_label', '')
            data_type = field.get('data_type', '')
            
            # 親商談関連のキーワードをチェック
            parent_keywords = [
                'parent', 'master', 'main', 'root', 'primary', 
                'related', 'reference', 'deal', 'opportunity'
            ]
            
            # APIネームまたはラベルに親子関係のキーワードが含まれる
            if any(keyword in api_name.lower() for keyword in parent_keywords) or \
               any(keyword in field_label.lower() for keyword in parent_keywords):
                parent_candidates.append(field)
            
            # lookup型フィールド（他のレコードを参照）
            if data_type == 'lookup':
                lookup_fields.append(field)
            
            # カスタムフィールド
            if api_name.startswith('field') or '_' in api_name:
                custom_fields.append(field)
        
        print(f"\n🎯 親子関係候補フィールド: {len(parent_candidates)}個")
        for field in parent_candidates:
            print(f"  📍 {field.get('api_name')} ({field.get('field_label')})")
            print(f"      タイプ: {field.get('data_type')}")
            print(f"      必須: {field.get('required', False)}")
            if field.get('lookup'):
                lookup_info = field.get('lookup', {})
                print(f"      参照先: {lookup_info.get('module', 'N/A')}")
            print()
        
        print(f"🔗 Lookup型フィールド: {len(lookup_fields)}個")
        for field in lookup_fields:
            lookup_info = field.get('lookup', {})
            print(f"  🔗 {field.get('api_name')} ({field.get('field_label')})")
            print(f"      参照先モジュール: {lookup_info.get('module', 'N/A')}")
            print(f"      表示フィールド: {lookup_info.get('display_label', 'N/A')}")
            print()
    
    # 2. 実際の商談データでフィールド値を確認
    print("\n📊 実商談データでのフィールド値確認...")
    
    # より多くの商談データを取得
    deals_url = "https://www.zohoapis.com/crm/v2/Deals"
    params = {
        'per_page': 200,  # 大量取得
        'sort_by': 'Modified_Time',
        'sort_order': 'desc'
    }
    
    response = requests.get(deals_url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        deals = data.get('data', [])
        print(f"✅ {len(deals)}件の商談データを取得")
        
        # 親子関係の可能性が高いフィールドを特定
        suspicious_fields = {}
        
        # 各商談のフィールドを調査
        for deal in deals:
            for field_name, field_value in deal.items():
                # 商談IDの形式（19桁の数値）と一致するフィールドを探す
                if isinstance(field_value, str) and field_value.isdigit() and len(field_value) == 19:
                    # 自分自身のIDではない場合
                    if field_value != deal.get('id'):
                        if field_name not in suspicious_fields:
                            suspicious_fields[field_name] = []
                        suspicious_fields[field_name].append({
                            'deal_id': deal.get('id'),
                            'deal_name': deal.get('Deal_Name'),
                            'field_value': field_value
                        })
        
        print(f"\n🕵️ 他の商談IDらしき値を持つフィールド: {len(suspicious_fields)}個")
        
        for field_name, values in suspicious_fields.items():
            print(f"\n  🎯 {field_name}:")
            print(f"      該当件数: {len(values)}件")
            
            # 参照先商談が実際に存在するかチェック
            referenced_deal_ids = [v['field_value'] for v in values]
            actual_deal_ids = [d.get('id') for d in deals]
            
            valid_references = [ref_id for ref_id in referenced_deal_ids if ref_id in actual_deal_ids]
            
            print(f"      有効な参照: {len(valid_references)}/{len(referenced_deal_ids)}件")
            
            if len(valid_references) > 0:
                print("      📋 参照例:")
                for i, value_info in enumerate(values[:3]):  # 最初の3件
                    child_name = value_info['deal_name']
                    parent_id = value_info['field_value']
                    
                    # 親商談名を取得
                    parent_deal = next((d for d in deals if d.get('id') == parent_id), None)
                    parent_name = parent_deal.get('Deal_Name', 'N/A') if parent_deal else '見つからない'
                    
                    print(f"        {i+1}. 子: {child_name[:30]}")
                    print(f"           親: {parent_name[:30]} (ID: {parent_id})")
        
        # 3. 商談名パターンと親子関係の照合
        print(f"\n🔍 商談名パターンと親子関係フィールドの照合...")
        
        # 商談名でグループ化
        name_groups = {}
        for deal in deals:
            deal_name = deal.get('Deal_Name', '')
            if '_' in deal_name:
                base_pattern = deal_name.split('_')[0]
                if base_pattern not in name_groups:
                    name_groups[base_pattern] = []
                name_groups[base_pattern].append(deal)
        
        # 複数商談があるグループで親子フィールドをチェック
        for pattern, group_deals in name_groups.items():
            if len(group_deals) > 1:
                print(f"\n  📊 {pattern}グループ ({len(group_deals)}件):")
                
                # このグループ内での親子関係を確認
                for deal in group_deals:
                    deal_name = deal.get('Deal_Name', '')
                    
                    # 疑わしいフィールドの値をチェック
                    parent_refs = []
                    for field_name in suspicious_fields.keys():
                        field_value = deal.get(field_name)
                        if field_value and isinstance(field_value, str) and field_value.isdigit():
                            # 同じグループ内の他の商談を参照している可能性
                            referenced_deal = next((d for d in group_deals if d.get('id') == field_value), None)
                            if referenced_deal:
                                parent_refs.append({
                                    'field': field_name,
                                    'parent_name': referenced_deal.get('Deal_Name', '')
                                })
                    
                    if parent_refs:
                        print(f"    🔗 {deal_name[:40]}")
                        for ref in parent_refs:
                            print(f"        → {ref['field']}: {ref['parent_name'][:30]}")
                    else:
                        print(f"    📝 {deal_name[:40]} (参照なし)")

def main():
    find_parent_deal_fields()
    
    print("\n" + "="*70)
    print("🎯 調査完了")
    print("親商談IDを保存する専用フィールドが見つかった場合、")
    print("それを使用して正確な親子関係を把握できます。")
    print("="*70)

if __name__ == "__main__":
    main()