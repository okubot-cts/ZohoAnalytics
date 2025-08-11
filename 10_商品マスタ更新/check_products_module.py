#!/usr/bin/env python3
import requests
import json
import sys

def get_products_module_fields():
    with open("/Users/ks1-utakashio/Desktop/CursorProjects/20250726_ZohoAnalytics/01_Zoho_API/認証・トークン/zoho_crm_tokens.json", "r") as f:
        tokens = json.load(f)
    
    access_token = tokens["access_token"]
    api_domain = tokens["api_domain"]
    
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }
    
    url = f"{api_domain}/crm/v2/settings/modules"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            modules_data = response.json()
            
            for module in modules_data.get("modules", []):
                if module.get("api_name") == "Products":
                    print(f"商品モジュール (Products) が見つかりました:")
                    print(f"  - Module ID: {module.get('id')}")
                    print(f"  - Display Label: {module.get('display_label')}")
                    print(f"  - API Name: {module.get('api_name')}")
                    
                    fields_url = f"{api_domain}/crm/v2/settings/fields?module=Products"
                    fields_response = requests.get(fields_url, headers=headers)
                    
                    if fields_response.status_code == 200:
                        fields_data = fields_response.json()
                        print(f"\n商品モジュールのフィールド一覧:")
                        
                        target_fields = ["売上勘定科目", "売上原価項目", "freee品目"]
                        found_fields = []
                        
                        for field in fields_data.get("fields", []):
                            field_label = field.get("display_label", "")
                            field_api_name = field.get("api_name", "")
                            
                            if any(target in field_label or target in field_api_name for target in target_fields):
                                found_fields.append({
                                    "label": field_label,
                                    "api_name": field_api_name,
                                    "data_type": field.get("data_type", ""),
                                    "field_type": field.get("field_type", "")
                                })
                        
                        if found_fields:
                            print(f"\n対象フィールドが見つかりました:")
                            for field in found_fields:
                                print(f"  - {field['label']} ({field['api_name']}) - {field['data_type']}")
                        else:
                            print(f"\n対象フィールドが見つかりませんでした。全フィールドを表示:")
                            for field in fields_data.get("fields", [])[:20]:  # 最初の20フィールドのみ表示
                                print(f"  - {field.get('display_label', 'N/A')} ({field.get('api_name', 'N/A')})")
                            print(f"  ... 他 {len(fields_data.get('fields', [])) - 20} フィールド")
                    else:
                        print(f"フィールド情報の取得に失敗: {fields_response.status_code}")
                        print(fields_response.text)
                    break
            else:
                print("商品モジュール (Products) が見つかりませんでした")
                print("利用可能なモジュール:")
                for module in modules_data.get("modules", []):
                    print(f"  - {module.get('display_label')} ({module.get('api_name')})")
        else:
            print(f"API呼び出しエラー: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    get_products_module_fields()