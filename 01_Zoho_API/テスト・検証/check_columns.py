#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テーブルの列名を確認するスクリプト
"""

import requests
import json
import urllib.parse
import time

def check_table_columns(workspace_id, org_id, access_token, table_name):
    """
    テーブルの列名を確認
    """
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'ZANALYTICS-ORGID': org_id,
        'Content-Type': 'application/json'
    }
    
    # 簡単なクエリを実行
    query = f'SELECT * FROM "{table_name}" LIMIT 1'
    
    config = {
        "responseFormat": "json",
        "sqlQuery": query
    }
    
    config_encoded = urllib.parse.quote(json.dumps(config))
    url = f"https://analyticsapi.zoho.com/restapi/v2/bulk/workspaces/{workspace_id}/data?CONFIG={config_encoded}"
    
    print(f"🔄 {table_name} の列名確認中...")
    response = requests.get(url, headers=headers, timeout=60)
    
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'jobId' in data['data']:
            job_id = data['data']['jobId']
            print(f"   ✅ ジョブ開始成功 (ID: {job_id})")
            
            # ジョブの完了を待機
            return wait_for_job_completion(workspace_id, org_id, access_token, job_id)
        else:
            print(f"   ❌ 予期しないレスポンス形式")
            return False
    else:
        print(f"   ❌ クエリ実行失敗: {response.status_code}")
        print(f"   レスポンス: {response.text[:500]}...")
        return False

def wait_for_job_completion(workspace_id, org_id, access_token, job_id, max_wait_time=60):
    """
    ジョブの完了を待機してデータを取得
    """
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'ZANALYTICS-ORGID': org_id,
        'Content-Type': 'application/json'
    }
    
    start_time = time.time()
    while time.time() - start_time < max_wait_time:
        # ジョブのステータスを確認
        status_url = f"https://analyticsapi.zoho.com/restapi/v2/bulk/workspaces/{workspace_id}/exportjobs/{job_id}"
        
        try:
            response = requests.get(status_url, headers=headers, timeout=30)
            if response.status_code == 200:
                status_data = response.json()
                
                if status_data.get('status') == 'success':
                    # ジョブ完了、データを取得
                    download_url = status_data['data'].get('downloadUrl')
                    if download_url:
                        print(f"   ✅ ジョブ完了、データ取得中...")
                        return download_data(download_url, headers)
                    else:
                        print(f"   ❌ ダウンロードURLが見つかりません")
                        return None
                elif status_data.get('status') == 'failure':
                    print(f"   ❌ ジョブ失敗: {status_data}")
                    return None
                else:
                    print(f"   ⏳ ジョブ実行中... ({status_data.get('status', 'unknown')})")
                    time.sleep(2)
            else:
                print(f"   ❌ ジョブステータス確認失敗: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ ジョブステータス確認エラー: {e}")
            return None
    
    print(f"   ⏰ タイムアウト: {max_wait_time}秒経過")
    return None

def download_data(download_url, headers):
    """
    データをダウンロード
    """
    try:
        response = requests.get(download_url, headers=headers, timeout=60)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
                print(f"   ✅ データ取得完了")
                print(f"   列名: {list(data['data'][0].keys())}")
                return data['data'][0].keys()
            else:
                print(f"   ⚠️ データが空です")
                return []
        else:
            print(f"   ❌ データダウンロード失敗: {response.status_code}")
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
    
    # 確認したいテーブル
    tables_to_check = [
        "Versant",
        "連絡先",
        "手配"
    ]
    
    for table_name in tables_to_check:
        print(f"\n{'='*50}")
        columns = check_table_columns(workspace_id, org_id, access_token, table_name)
        if columns:
            print(f"   📊 {table_name} の列名:")
            for col in columns:
                print(f"      - {col}")

if __name__ == "__main__":
    main() 