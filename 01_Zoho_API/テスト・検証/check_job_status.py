#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ジョブのステータスを詳しく確認するスクリプト
"""

import requests
import json
import urllib.parse
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
    
    try:
        response = requests.get(status_url, headers=headers, timeout=30)
        if response.status_code == 200:
            status_data = response.json()
            print(f"   📊 ジョブステータス詳細:")
            print(f"      status: {status_data.get('status')}")
            print(f"      summary: {status_data.get('summary')}")
            
            if 'data' in status_data:
                data = status_data['data']
                print(f"      data: {json.dumps(data, indent=6, ensure_ascii=False)}")
            
            return status_data
        else:
            print(f"   ❌ ジョブステータス確認失敗: {response.status_code}")
            print(f"   レスポンス: {response.text[:500]}...")
            return None
    except requests.exceptions.RequestException as e:
        print(f"   ❌ ジョブステータス確認エラー: {e}")
        return None

def main():
    """
    メイン実行関数
    """
    access_token = "1000.8621860282e81be6562d037429111add.01bf659cc6c8f0751ac1cf3915ce2178"
    workspace_id = "2527115000001040002"
    org_id = "772044231"
    
    # 確認したいジョブID
    job_ids = [
        "2527115000016772001",  # Versant
        "2527115000016773001",  # 連絡先
        "2527115000016774001"   # 手配
    ]
    
    for job_id in job_ids:
        print(f"\n{'='*50}")
        print(f"🔄 ジョブ {job_id} のステータス確認中...")
        check_job_status(workspace_id, org_id, access_token, job_id)

if __name__ == "__main__":
    main() 