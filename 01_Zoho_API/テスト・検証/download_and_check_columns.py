#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
実際にデータをダウンロードして列名を確認するスクリプト
"""

import requests
import json

def download_and_check_columns(workspace_id, org_id, access_token, job_id, table_name):
    """
    データをダウンロードして列名を確認
    """
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'ZANALYTICS-ORGID': org_id,
        'Content-Type': 'application/json'
    }
    
    download_url = f"https://analyticsapi.zoho.com/restapi/v2/bulk/workspaces/{workspace_id}/exportjobs/{job_id}/data"
    
    print(f"🔄 {table_name} のデータダウンロード中...")
    print(f"   URL: {download_url}")
    
    try:
        response = requests.get(download_url, headers=headers, timeout=60)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and isinstance(data['data'], list):
                if len(data['data']) > 0:
                    print(f"   ✅ データ取得完了")
                    print(f"   取得件数: {len(data['data'])}件")
                    print(f"   列名: {list(data['data'][0].keys())}")
                    
                    # 最初のレコードの内容も表示
                    first_record = data['data'][0]
                    print(f"   最初のレコード:")
                    for key, value in first_record.items():
                        print(f"      {key}: {value}")
                    
                    return list(data['data'][0].keys())
                else:
                    print(f"   ⚠️ データが空です")
                    return []
            else:
                print(f"   ❌ 予期しないデータ形式")
                print(f"   レスポンス: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return None
        else:
            print(f"   ❌ データダウンロード失敗: {response.status_code}")
            print(f"   レスポンス: {response.text[:500]}...")
            return None
    except requests.exceptions.RequestException as e:
        print(f"   ❌ データダウンロードエラー: {e}")
        return None

def main():
    """
    メイン実行関数
    """
    access_token = "1000.8621860282e81be6562d037429111add.01bf659cc6c8f0751ac1cf3915ce2178"
    workspace_id = "2527115000001040002"
    org_id = "772044231"
    
    # ジョブIDとテーブル名の対応
    job_table_mapping = [
        ("2527115000016772001", "Versant"),
        ("2527115000016773001", "連絡先"),
        ("2527115000016774001", "手配")
    ]
    
    all_columns = {}
    
    for job_id, table_name in job_table_mapping:
        print(f"\n{'='*50}")
        columns = download_and_check_columns(workspace_id, org_id, access_token, job_id, table_name)
        if columns:
            all_columns[table_name] = columns
    
    # 結果のまとめ
    print(f"\n{'='*50}")
    print("📊 テーブル列名まとめ:")
    for table_name, columns in all_columns.items():
        print(f"\n{table_name}:")
        for col in columns:
            print(f"  - {col}")

if __name__ == "__main__":
    main() 