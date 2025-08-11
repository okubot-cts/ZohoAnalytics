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

def read_excel_data():
    """Excelファイルからデータを読み込み、処理用に変換"""
    print("Excelファイルを読み込み中...")
    
    df = pd.read_excel("/Users/ks1-utakashio/Desktop/CursorProjects/20250726_ZohoAnalytics/10_商品マスタ更新/商品マスタ.xlsx")
    
    # 必要なカラムの存在確認
    required_columns = ['データID', '売上', '売上原価', 'freee品目']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"エラー: 必要なカラムが見つかりません: {missing_columns}")
        return None
    
    # データを処理
    products_data = []
    for index, row in df.iterrows():
        data_id = row['データID']
        if pd.isna(data_id):
            continue
            
        product_id = extract_product_id(data_id)
        
        # 各フィールドの値を取得（NaNの場合は空文字）
        uriage = str(row['売上']) if pd.notna(row['売上']) else ""
        uriage_genka = str(row['売上原価']) if pd.notna(row['売上原価']) else ""
        freee_hinmoku = str(row['freee品目']) if pd.notna(row['freee品目']) else ""
        
        products_data.append({
            'product_id': product_id,
            'original_data_id': data_id,
            'uriage_kanjokamoku': uriage,  # 売上 → 売上勘定科目
            'uriage_genka_komoku': uriage_genka,  # 売上原価 → 売上原価項目
            'freee_hinmoku': freee_hinmoku  # freee品目 → freee品目
        })
    
    print(f"処理対象商品数: {len(products_data)}")
    return products_data

def update_products_batch(products_batch, tokens):
    """ZohoCRMの商品を一括更新（最大100件）"""
    access_token = tokens["access_token"]
    api_domain = tokens["api_domain"]
    
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }
    
    # バッチ更新データを準備
    data_list = []
    for product_data in products_batch:
        data_list.append({
            "id": product_data['product_id'],
            "field19": product_data['uriage_kanjokamoku'],  # 売上勘定科目
            "field18": product_data['uriage_genka_komoku'],  # 売上原価項目
            "freee": product_data['freee_hinmoku']  # freee品目
        })
    
    update_data = {"data": data_list}
    
    url = f"{api_domain}/crm/v2/Products"
    
    try:
        response = requests.put(url, headers=headers, json=update_data)
        
        if response.status_code == 200:
            result = response.json()
            return {"success": True, "data": result.get("data", [])}
        else:
            return {"success": False, "message": f"API エラー: {response.status_code} - {response.text}"}
            
    except Exception as e:
        return {"success": False, "message": f"例外エラー: {str(e)}"}

def batch_update_products():
    """商品マスタの一括更新処理（バッチ処理版）"""
    print("=== 商品マスタ更新処理開始 ===")
    
    # トークン読み込み
    tokens = load_tokens()
    
    # Excelデータ読み込み
    products_data = read_excel_data()
    if not products_data:
        return
    
    # バッチサイズ（ZohoAPIは最大100件）
    batch_size = 100
    success_count = 0
    error_count = 0
    errors = []
    
    print(f"\n商品更新開始: {len(products_data)}件（バッチサイズ: {batch_size}）")
    
    # バッチごとに処理
    for i in range(0, len(products_data), batch_size):
        batch_start = i
        batch_end = min(i + batch_size, len(products_data))
        batch = products_data[batch_start:batch_end]
        batch_num = (i // batch_size) + 1
        total_batches = (len(products_data) + batch_size - 1) // batch_size
        
        print(f"\nバッチ {batch_num}/{total_batches}: {len(batch)}件処理中...")
        
        result = update_products_batch(batch, tokens)
        
        if result["success"]:
            # 個別の結果をチェック
            batch_success = 0
            batch_errors = 0
            
            for j, item_result in enumerate(result["data"]):
                product_data = batch[j]
                if item_result.get("status") == "success":
                    batch_success += 1
                    success_count += 1
                else:
                    batch_errors += 1
                    error_count += 1
                    error_info = {
                        "product_id": product_data["product_id"],
                        "original_data_id": product_data["original_data_id"],
                        "error": item_result.get("message", "不明なエラー")
                    }
                    errors.append(error_info)
            
            print(f"  バッチ結果: 成功 {batch_success}件, エラー {batch_errors}件")
        else:
            # バッチ全体がエラー
            error_count += len(batch)
            for product_data in batch:
                error_info = {
                    "product_id": product_data["product_id"],
                    "original_data_id": product_data["original_data_id"],
                    "error": result["message"]
                }
                errors.append(error_info)
            print(f"  バッチエラー: {result['message']}")
        
        # API制限対策（バッチ間で2秒待機）
        if batch_end < len(products_data):
            time.sleep(2)
    
    # 結果レポート
    print(f"\n=== 更新結果 ===")
    print(f"総処理件数: {len(products_data)}")
    print(f"成功: {success_count}件")
    print(f"エラー: {error_count}件")
    
    if errors:
        print(f"\nエラー詳細（最初の10件）:")
        for error in errors[:10]:
            print(f"  商品ID: {error['product_id']} - {error['error']}")
        
        if len(errors) > 10:
            print(f"  ... 他 {len(errors) - 10} 件のエラー")
        
        # エラーログをファイルに保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_file = f"/Users/ks1-utakashio/Desktop/CursorProjects/20250726_ZohoAnalytics/10_商品マスタ更新/update_errors_{timestamp}.json"
        with open(error_file, "w", encoding="utf-8") as f:
            json.dump(errors, f, indent=2, ensure_ascii=False)
        print(f"\nエラーログ保存: {error_file}")
    
    print("\n=== 処理完了 ===")

if __name__ == "__main__":
    batch_update_products()