#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zoho Analytics API 最終版クライアント
VERSANTコーチングレポート実行用
"""

import requests
import json
import os
from datetime import datetime
import pandas as pd
import urllib.parse

class ZohoAnalyticsAPIFinal:
    def __init__(self, access_token=None, workspace_id=None, org_id=None):
        """
        Zoho Analytics API 最終版クライアントの初期化
        
        Args:
            access_token (str): Zoho Analytics API アクセストークン
            workspace_id (str): ワークスペースID
            org_id (str): 組織ID
        """
        self.base_url = "https://analyticsapi.zoho.com/restapi/v2"
        self.access_token = access_token or os.getenv('ZOHO_ANALYTICS_ACCESS_TOKEN')
        self.workspace_id = workspace_id or os.getenv('ZOHO_ANALYTICS_WORKSPACE_ID')
        self.org_id = org_id or os.getenv('ZOHO_ANALYTICS_ORG_ID')
        
        if not self.access_token:
            raise ValueError("アクセストークンが設定されていません")
        if not self.workspace_id:
            raise ValueError("ワークスペースIDが設定されていません")
        if not self.org_id:
            raise ValueError("組織IDが設定されていません")
    
    def get_headers(self):
        """
        リクエストヘッダーを取得
        """
        return {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'ZANALYTICS-ORGID': self.org_id,
            'Content-Type': 'application/json'
        }
    
    def execute_query(self, sql_file_path):
        """
        SQLファイルを実行
        
        Args:
            sql_file_path (str): SQLファイルのパス
            
        Returns:
            dict: 実行結果
        """
        print(f"📊 {sql_file_path} を実行中...")
        
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
        url = f"{self.base_url}/bulk/workspaces/{self.workspace_id}/data?CONFIG={config_encoded}"
        
        print(f"🔄 クエリ実行中: {url[:100]}...")
        print(f"   クエリ長: {len(sql_query)}文字")
        
        try:
            response = requests.get(url, headers=self.get_headers(), timeout=60)
            print(f"   ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'jobId' in data['data']:
                    job_id = data['data']['jobId']
                    print(f"   ✅ ジョブ開始成功 (ID: {job_id})")
                    
                    # ジョブの完了を待機
                    return self.wait_for_job_completion(job_id)
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
    
    def wait_for_job_completion(self, job_id, max_wait_time=120):
        """
        ジョブの完了を待機
        
        Args:
            job_id (str): ジョブID
            max_wait_time (int): 最大待機時間（秒）
            
        Returns:
            dict: ジョブ結果
        """
        import time
        
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            # ジョブのステータスを確認
            status_url = f"{self.base_url}/bulk/workspaces/{self.workspace_id}/exportjobs/{job_id}"
            
            try:
                response = requests.get(status_url, headers=self.get_headers(), timeout=30)
                if response.status_code == 200:
                    status_data = response.json()
                    
                    if status_data.get('status') == 'success':
                        # ジョブ完了、データを取得
                        download_url = status_data['data'].get('downloadUrl')
                        if download_url:
                            print(f"   ✅ ジョブ完了、データ取得中...")
                            return self.download_data(download_url)
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
    
    def download_data(self, download_url):
        """
        データをダウンロード
        
        Args:
            download_url (str): ダウンロードURL
            
        Returns:
            dict: ダウンロード結果
        """
        try:
            response = requests.get(download_url, headers=self.get_headers(), timeout=60)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and isinstance(data['data'], list):
                    print(f"   ✅ データ取得完了")
                    print(f"   取得件数: {len(data['data'])}件")
                    
                    # 結果をファイルに保存
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_file = f"versant_report_{timestamp}.json"
                    
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
    print("=== VERSANTコーチングレポート実行（最終版）===")
    
    # 環境変数を設定
    access_token = "1000.8621860282e81be6562d037429111add.01bf659cc6c8f0751ac1cf3915ce2178"
    workspace_id = "2527115000001040002"
    org_id = "772044231"
    
    try:
        # APIクライアントを初期化
        client = ZohoAnalyticsAPIFinal(access_token, workspace_id, org_id)
        print("✅ Zoho Analytics API クライアント初期化完了")
        
        # VERSANTレポートを実行
        result = client.execute_query("versant_coaching_report_final.sql")
        
        if result:
            print("✅ VERSANTコーチングレポート実行完了")
        else:
            print("❌ VERSANTコーチングレポート実行失敗")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main() 