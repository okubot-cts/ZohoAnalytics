#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zoho Analytics API v2 クライアント
VERSANTコーチングレポート実行用
"""

import requests
import json
import os
from datetime import datetime
import pandas as pd

class ZohoAnalyticsAPI:
    def __init__(self, access_token=None, workspace_id=None):
        """
        Zoho Analytics API v2 クライアントの初期化
        
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
    
    def execute_query(self, query, output_format='json'):
        """
        SQLクエリを実行
        
        Args:
            query (str): 実行するSQLクエリ
            output_format (str): 出力形式 ('json', 'csv', 'xlsx')
        
        Returns:
            dict: APIレスポンス
        """
        import urllib.parse
        
        # 設定をJSON形式で作成
        config = {
            "responseFormat": output_format,
            "sqlQuery": query
        }
        
        # ConfigをURL エンコード
        config_encoded = urllib.parse.quote(json.dumps(config))
        
        # 非同期エクスポートジョブを作成
        url = f"{self.base_url}/bulk/workspaces/{self.workspace_id}/data?CONFIG={config_encoded}"
        
        try:
            print(f"🔄 クエリ実行中: {url}")
            response = requests.get(url, headers=self.headers, timeout=60)
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
                    job_status = response.json()
                    
                    if 'data' in job_status:
                        status = job_status['data'].get('status')
                        print(f"   ジョブステータス: {status}")
                        
                        if status == 'COMPLETED':
                            # データを取得
                            data_url = f"{self.base_url}/bulk/workspaces/{self.workspace_id}/exportjobs/{job_id}/data"
                            data_response = requests.get(data_url, headers=self.headers, timeout=60)
                            
                            if data_response.status_code == 200:
                                return data_response.json()
                            else:
                                print(f"❌ データ取得失敗: {data_response.status_code}")
                                return None
                        elif status == 'FAILED':
                            print(f"❌ ジョブ失敗: {job_status}")
                            return None
                
                time.sleep(2)  # 2秒待機
                
            except requests.exceptions.RequestException as e:
                print(f"❌ ジョブステータス確認エラー: {e}")
                return None
        
        print("❌ ジョブ完了待機タイムアウト")
        return None
    
    def get_workspaces(self):
        """
        利用可能なワークスペースを取得
        
        Returns:
            dict: ワークスペース一覧
        """
        url = f"{self.base_url}/workspaces"
        
        try:
            print(f"🔄 ワークスペース取得中: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)
            print(f"   ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ ワークスペース取得失敗: {response.status_code}")
                print(f"   レスポンス: {response.text[:500]}...")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ ワークスペース取得エラー: {e}")
            return None
    
    def get_tables(self):
        """
        ワークスペース内のテーブル一覧を取得
        
        Returns:
            dict: テーブル一覧
        """
        url = f"{self.base_url}/workspaces/{self.workspace_id}/views"
        
        try:
            print(f"🔄 テーブル取得中: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)
            print(f"   ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ テーブル取得失敗: {response.status_code}")
                print(f"   レスポンス: {response.text[:500]}...")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ テーブル取得エラー: {e}")
            return None

def load_versant_query(file_path):
    """
    VERSANTコーチングレポートSQLファイルを読み込み
    
    Args:
        file_path (str): SQLファイルのパス
    
    Returns:
        str: SQLクエリ
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"ファイルが見つかりません: {file_path}")
        return None

def save_results_to_file(results, output_file, format_type='json'):
    """
    結果をファイルに保存
    
    Args:
        results (dict): APIレスポンス結果
        output_file (str): 出力ファイル名
        format_type (str): 出力形式
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"versant_report_{timestamp}.{format_type}"
    
    if format_type == 'json':
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    elif format_type == 'csv':
        # CSV形式で保存（結果がDataFrame形式の場合）
        if 'data' in results:
            df = pd.DataFrame(results['data'])
            df.to_csv(filename, index=False, encoding='utf-8-sig')
    
    print(f"結果を保存しました: {filename}")

def main():
    """
    メイン実行関数
    """
    print("=== VERSANTコーチングレポート実行 ===")
    
    # 環境変数の確認
    if not os.getenv('ZOHO_ANALYTICS_ACCESS_TOKEN'):
        print("環境変数 ZOHO_ANALYTICS_ACCESS_TOKEN を設定してください")
        return
    
    if not os.getenv('ZOHO_ANALYTICS_WORKSPACE_ID'):
        print("環境変数 ZOHO_ANALYTICS_WORKSPACE_ID を設定してください")
        return
    
    # APIクライアントの初期化
    try:
        client = ZohoAnalyticsAPI()
        print("✅ Zoho Analytics API クライアント初期化完了")
    except Exception as e:
        print(f"❌ クライアント初期化エラー: {e}")
        return
    
    # ワークスペース情報の確認
    workspaces = client.get_workspaces()
    if workspaces:
        print(f"✅ ワークスペース情報取得完了: {len(workspaces.get('workspaces', []))}件")
    
    # テーブル情報の確認
    tables = client.get_tables()
    if tables:
        print(f"✅ テーブル情報取得完了: {len(tables.get('tables', []))}件")
    
    # VERSANTレポートSQLの読み込み
    sql_files = [
        'versant_coaching_report_zoho.sql',
        'versant_coaching_report_simple.sql',
        'versant_coaching_report_select_only.sql',
        'versant_coaching_report_basic.sql'
    ]
    
    for sql_file in sql_files:
        if os.path.exists(sql_file):
            print(f"\n📊 {sql_file} を実行中...")
            
            # SQLクエリの読み込み
            query = load_versant_query(sql_file)
            if not query:
                continue
            
            # クエリ実行
            results = client.execute_query(query, output_format='json')
            
            if results:
                print(f"✅ {sql_file} 実行成功")
                
                # 結果の保存
                save_results_to_file(results, f"versant_report_{sql_file.replace('.sql', '')}", 'json')
                
                # 結果の概要表示
                if 'data' in results:
                    data_count = len(results['data'])
                    print(f"   取得件数: {data_count}件")
                    
                    if data_count > 0:
                        print("   サンプルデータ:")
                        for i, row in enumerate(results['data'][:3]):
                            print(f"   {i+1}. {row}")
            else:
                print(f"❌ {sql_file} 実行失敗")
        else:
            print(f"⚠️  {sql_file} が見つかりません")

if __name__ == "__main__":
    main() 