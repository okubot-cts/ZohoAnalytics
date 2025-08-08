#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zoho Analytics API v2 クライアント（POST版）
VERSANTコーチングレポート実行用
"""

import requests
import json
import os
from datetime import datetime
import pandas as pd

class ZohoAnalyticsAPIv2:
    def __init__(self, access_token=None, workspace_id=None):
        """
        Zoho Analytics API v2 クライアントの初期化（POST版）
        
        Args:
            access_token (str): Zoho Analytics API アクセストークン
            workspace_id (str): ワークスペースID
        """
        self.base_url = "https://analyticsapi.zoho.com/restapi/v2"
        self.access_token = access_token or os.getenv('ZOHO_ANALYTICS_ACCESS_TOKEN')
        self.workspace_id = workspace_id or os.getenv('ZOHO_ANALYTICS_WORKSPACE_ID')
        self.org_id = os.getenv('ZOHO_ANALYTICS_ORG_ID', '772044231')
        
        if not self.access_token:
            raise ValueError("アクセストークンが必要です。環境変数 ZOHO_ANALYTICS_ACCESS_TOKEN を設定してください。")
        
        if not self.workspace_id:
            raise ValueError("ワークスペースIDが必要です。環境変数 ZOHO_ANALYTICS_WORKSPACE_ID を設定してください。")
        
        self.headers = {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'ZANALYTICS-ORGID': self.org_id,
            'Content-Type': 'application/json'
        }
    
    def execute_query_post(self, query, output_format='json'):
        """
        SQLクエリをPOSTリクエストで実行
        
        Args:
            query (str): 実行するSQLクエリ
            output_format (str): 出力形式 ('json', 'csv', 'xlsx')
        
        Returns:
            dict: APIレスポンス
        """
        # 設定をJSON形式で作成
        config = {
            "responseFormat": output_format,
            "sqlQuery": query
        }
        
        # POSTリクエストでエクスポートジョブを作成
        url = f"{self.base_url}/bulk/workspaces/{self.workspace_id}/data"
        
        try:
            print(f"🔄 クエリ実行中（POST）: {url}")
            print(f"   クエリ長: {len(query)}文字")
            
            response = requests.post(url, headers=self.headers, json=config, timeout=60)
            print(f"   ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                job_data = response.json()
                if 'data' in job_data and 'jobId' in job_data['data']:
                    job_id = job_data['data']['jobId']
                    print(f"   ✅ エクスポートジョブ開始 (ID: {job_id})")
                    return self._wait_for_job_completion(job_id)
                else:
                    return job_data
            else:
                print(f"❌ クエリ実行失敗: {response.status_code}")
                print(f"   レスポンス: {response.text[:500]}...")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ APIリクエストエラー: {e}")
            return None
    
    def _wait_for_job_completion(self, job_id, max_wait_time=60):
        """
        ジョブの完了を待機してデータを取得
        """
        import time
        
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            # ジョブのステータスを確認
            status_url = f"{self.base_url}/bulk/workspaces/{self.workspace_id}/exportjobs/{job_id}"
            
            try:
                response = requests.get(status_url, headers=self.headers, timeout=30)
                if response.status_code == 200:
                    status_data = response.json()
                    
                    if status_data.get('status') == 'success':
                        # ジョブ完了、データを取得
                        download_url = status_data['data'].get('downloadUrl')
                        if download_url:
                            print(f"   ✅ ジョブ完了、データ取得中...")
                            return self._download_data(download_url)
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
    
    def _download_data(self, download_url):
        """
        データをダウンロード
        """
        try:
            response = requests.get(download_url, headers=self.headers, timeout=60)
            if response.status_code == 200:
                print(f"   ✅ データ取得完了")
                return response.json()
            else:
                print(f"   ❌ データダウンロード失敗: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"   ❌ データダウンロードエラー: {e}")
            return None
    
    def get_workspaces(self):
        """
        ワークスペース一覧を取得
        """
        url = f"{self.base_url}/workspaces"
        
        try:
            print(f"🔄 ワークスペース取得中: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)
            print(f"   ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                workspaces = data.get('data', {}).get('ownedWorkspaces', [])
                print(f"✅ ワークスペース情報取得完了: {len(workspaces)}件")
                return workspaces
            else:
                print(f"❌ ワークスペース取得失敗: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ ワークスペース取得エラー: {e}")
            return None
    
    def get_tables(self):
        """
        テーブル一覧を取得
        """
        url = f"{self.base_url}/workspaces/{self.workspace_id}/views"
        
        try:
            print(f"🔄 テーブル取得中: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)
            print(f"   ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                tables = data.get('data', {}).get('views', [])
                print(f"✅ テーブル情報取得完了: {len(tables)}件")
                return tables
            else:
                print(f"❌ テーブル取得失敗: {response.status_code}")
                print(f"   レスポンス: {response.text[:500]}...")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ テーブル取得エラー: {e}")
            return None

def load_versant_query(file_path):
    """
    VERSANTクエリファイルを読み込み
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"❌ ファイルが見つかりません: {file_path}")
        return None
    except Exception as e:
        print(f"❌ ファイル読み込みエラー: {e}")
        return None

def save_results_to_file(results, output_file, format_type='json'):
    """
    結果をファイルに保存
    """
    try:
        if format_type == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
        elif format_type == 'csv':
            if 'data' in results and isinstance(results['data'], list):
                df = pd.DataFrame(results['data'])
                df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"✅ 結果を保存しました: {output_file}")
        return True
    except Exception as e:
        print(f"❌ ファイル保存エラー: {e}")
        return False

def main():
    """
    メイン実行関数
    """
    print("=== VERSANTコーチングレポート実行（POST版）===")
    
    # APIクライアントの初期化
    try:
        client = ZohoAnalyticsAPIv2()
        print("✅ Zoho Analytics API クライアント初期化完了")
    except Exception as e:
        print(f"❌ クライアント初期化エラー: {e}")
        return
    
    # ワークスペース情報の確認
    workspaces = client.get_workspaces()
    if workspaces:
        print("📋 利用可能なワークスペース:")
        for ws in workspaces:
            print(f"   - {ws['workspaceName']} (ID: {ws['workspaceId']})")
    
    # テーブル情報の確認
    tables = client.get_tables()
    if tables:
        print("📋 利用可能なテーブル:")
        for table in tables[:10]:  # 最初の10件のみ表示
            print(f"   - {table.get('viewName', 'Unknown')}")
    
    # VERSANTクエリの実行
    sql_files = [
        'versant_coaching_report_new.sql',
        'versant_coaching_report_simple.sql',
        'versant_coaching_report_basic.sql'
    ]
    
    for sql_file in sql_files:
        print(f"\n📊 {sql_file} を実行中...")
        
        query = load_versant_query(sql_file)
        if not query:
            print(f"❌ {sql_file} の読み込みに失敗")
            continue
        
        results = client.execute_query_post(query, output_format='json')
        
        if results:
            print(f"✅ {sql_file} 実行成功")
            
            # 結果を保存
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"versant_report_{timestamp}.json"
            save_results_to_file(results, output_file)
            
            # 結果の概要を表示
            if 'data' in results and isinstance(results['data'], list):
                print(f"   取得件数: {len(results['data'])}件")
                if results['data']:
                    print(f"   最初のレコード: {list(results['data'][0].keys())}")
        else:
            print(f"❌ {sql_file} 実行失敗")

if __name__ == "__main__":
    main() 