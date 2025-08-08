#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
詳細なVERSANTクエリをテストするスクリプト
"""

import requests
import json
import urllib.parse
import time

def test_detailed_query(workspace_id, org_id, access_token, sql_file_path):
    """
    詳細なクエリをテスト
    """
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'ZANALYTICS-ORGID': org_id,
        'Content-Type': 'application/json'
    }
    
    # SQLファイルを読み込み
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_query = f.read()
    except FileNotFoundError:
        print(f"❌ SQLファイルが見つかりません: {sql_file_path}")
        return None
    
    # クエリを実行
    config = {
        "responseFormat": "json",
        "sqlQuery": sql_query
    }
    
    config_encoded = urllib.parse.quote(json.dumps(config))
    url = f"https://analyticsapi.zoho.com/restapi/v2/bulk/workspaces/{workspace_id}/data?CONFIG={config_encoded}"
    
    print(f"🔄 詳細クエリ実行中: {sql_file_path}")
    print(f"   クエリ長: {len(sql_query)}文字")
    
    try:
        response = requests.get(url, headers=headers, timeout=60)
        print(f"   ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'jobId' in data['data']:
                job_id = data['data']['jobId']
                print(f"   ✅ ジョブ開始成功 (ID: {job_id})")
                
                # ジョブの完了を待機
                return wait_for_job_completion(workspace_id, org_id, access_token, job_id)
            else:
                print(f"   ❌ 予期しないレスポンス形式")
                print(f"   レスポンス: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return None
        else:
            print(f"   ❌ クエリ実行失敗: {response.status_code}")
            print(f"   レスポンス: {response.text[:500]}...")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ リクエストエラー: {e}")
        return None

def wait_for_job_completion(workspace_id, org_id, access_token, job_id, max_wait_time=120):
    """
    ジョブの完了を待機
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
                    time.sleep(3)
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
            if 'data' in data and isinstance(data['data'], list):
                print(f"   ✅ データ取得完了")
                print(f"   取得件数: {len(data['data'])}件")
                
                # 結果をファイルに保存
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"versant_detailed_{timestamp}.json"
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                print(f"   💾 結果を保存: {output_file}")
                
                # 最初の数件を表示
                if len(data['data']) > 0:
                    print(f"   📋 サンプルデータ:")
                    for i, record in enumerate(data['data'][:3]):
                        print(f"      {i+1}件目: {record}")
                
                return data
            else:
                print(f"   ⚠️ データが空です")
                return data
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
    
    # 詳細なクエリをテスト
    result = test_detailed_query(workspace_id, org_id, access_token, "versant_coaching_report_detailed.sql")
    
    if result:
        print("✅ 詳細クエリ実行成功")
    else:
        print("❌ 詳細クエリ実行失敗")

if __name__ == "__main__":
    main() 