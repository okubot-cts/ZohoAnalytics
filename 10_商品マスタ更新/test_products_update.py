#!/usr/bin/env python3
import pandas as pd
import json
import requests
from datetime import datetime
import time

def load_tokens():
    """ZohoCRMトークンを読み込み"""
    with open("/Users/ks1-utakashio/Desktop/CursorProjects/20250726_ZohoAnalytics/01_Zoho_API/認証・トークン/zoho_crm_tokens.json", "r") as f:
        return json.load(f)

def extract_product_id(data_id):
    """データIDからzcrm_プリフィックスを除去して商品IDを取得"""
    if isinstance(data_id, str) and data_id.startswith("zcrm_"):
        return data_id.replace("zcrm_", "")
    return str(data_id)

def format_multiselect_value(value):
    """multiselectpicklist用に値を配列形式に変換"""
    if pd.isna(value) or value == "" or value == "nan":
        return []
    
    # 文字列として処理
    str_value = str(value).strip()
    if not str_value:
        return []
    
    # カンマ区切りの場合は分割、そうでなければ単一要素の配列
    if "," in str_value:
        return [item.strip() for item in str_value.split(",") if item.strip()]
    else:
        return [str_value]

def test_single_product():
    """単一商品でのテスト実行"""
    print("=== 単一商品テスト ===")
    
    # トークン読み込み
    tokens = load_tokens()
    
    # 最初の1件でテスト
    df = pd.read_excel("/Users/ks1-utakashio/Desktop/CursorProjects/20250726_ZohoAnalytics/10_商品マスタ更新/商品マスタ.xlsx")
    row = df.iloc[0]
    
    product_id = extract_product_id(row['データID'])
    uriage_list = format_multiselect_value(row['売上'])
    uriage_genka_list = format_multiselect_value(row['売上原価'])
    freee_hinmoku = str(row['freee品目']) if pd.notna(row['freee品目']) else ""
    
    print(f"テスト対象商品:")
    print(f"  商品ID: {product_id}")
    print(f"  売上勘定科目: {uriage_list}")
    print(f"  売上原価項目: {uriage_genka_list}")
    print(f"  freee品目: {freee_hinmoku}")
    
    # API更新実行
    access_token = tokens["access_token"]
    api_domain = tokens["api_domain"]
    
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }
    
    update_record = {
        "id": product_id
    }
    
    # 売上勘定科目（field19）- multiselectpicklist
    if uriage_list:
        update_record["field19"] = uriage_list
    
    # 売上原価項目（field18）- multiselectpicklist
    if uriage_genka_list:
        update_record["field18"] = uriage_genka_list
    
    # freee品目（freee）- text
    if freee_hinmoku:
        update_record["freee"] = freee_hinmoku
    
    update_data = {"data": [update_record]}
    
    print(f"\n送信データ:")
    print(json.dumps(update_data, indent=2, ensure_ascii=False))
    
    url = f"{api_domain}/crm/v2/Products"
    
    try:
        response = requests.put(url, headers=headers, json=update_data)
        
        print(f"\nAPIレスポンス:")
        print(f"ステータスコード: {response.status_code}")
        print(f"レスポンス内容:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            result = response.json()
            if result.get("data") and len(result["data"]) > 0:
                item_result = result["data"][0]
                if item_result.get("status") == "success":
                    print("\n✓ 更新成功！")
                else:
                    print(f"\n✗ 更新失敗: {item_result.get('message', 'Unknown error')}")
            else:
                print("\n✗ レスポンスデータが空です")
        else:
            print(f"\n✗ API エラー: {response.status_code}")
            
    except Exception as e:
        print(f"\n✗ 例外エラー: {str(e)}")

if __name__ == "__main__":
    test_single_product()