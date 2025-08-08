#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプルクエリのジョブステータスを確認するスクリプト
"""

import requests
import json
import time

def check_job_status(workspace_id, org_id, access_token, job_id):
    """
    ジョブのステータスを詳しく確認
    """
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'ZANALYTICS-ORGID': org_id,
        'Content-Type': 'application/json'
    }
    
    status_url = f"https://analyticsapi.zoho.com/restapi/v2/bulk/workspaces/{workspace_id}/exportjobs/{job_id}"
    
    print(f"🔄 ジョブ {job_id} のステータス確認中...")
    
    # 複数回チェック
    for i in range(15):
        try:
            response = requests.get(status_url, headers=headers, timeout=30)
            if response.status_code == 200:
                status_data = response.json()
                print(f"   📊 チェック {i+1}:")
                print(f"      status: {status_data.get('status')}")
                print(f"      summary: {status_data.get('summary')}")
                
                if 'data' in status_data:
                    data = status_data['data']
                    print(f"      jobStatus: {data.get('jobStatus')}")
                    print(f"      downloadUrl: {data.get('downloadUrl', 'なし')}")
                    
                    if data.get('downloadUrl'):
                        print(f"      ✅ ダウンロードURL発見!")
                        return data.get('downloadUrl')
                
                if status_data.get('status') == 'success' and data.get('downloadUrl'):
                    return data.get('downloadUrl')
                elif status_data.get('status') == 'failure':
                    print(f"      ❌ ジョブ失敗")
                    return None
                else:
                    print(f"      ⏳ ジョブ実行中...")
                    time.sleep(4)
            else:
                print(f"   ❌ ジョブステータス確認失敗: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ ジョブステータス確認エラー: {e}")
            return None
    
    print(f"   ⏰ タイムアウト: 15回チェック完了")
    return None

def download_data(download_url, headers):
    """
    データをダウンロード
    """
    print(f"🔄 データダウンロード中: {download_url}")
    
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
                output_file = f"versant_simple_result_{timestamp}.json"
                
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
    
    # 確認したいジョブID
    job_id = "2527115000016772005"
    
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'ZANALYTICS-ORGID': org_id,
        'Content-Type': 'application/json'
    }
    
    print(f"=== シンプルクエリジョブステータス確認 ===")
    download_url = check_job_status(workspace_id, org_id, access_token, job_id)
    
    if download_url:
        print(f"\n✅ ダウンロードURL取得成功: {download_url}")
        download_data(download_url, headers)
    else:
        print(f"\n❌ ダウンロードURL取得失敗")

if __name__ == "__main__":
    main() 