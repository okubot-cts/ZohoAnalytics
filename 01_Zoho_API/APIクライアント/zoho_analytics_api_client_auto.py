#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zoho Analytics API v2 クライアント（自動トークン更新機能付き）
VERSANTコーチングレポート実行用
"""

import requests
import json
import os
from datetime import datetime
import pandas as pd
import sys
from pathlib import Path

# 自動トークン管理システムをインポート
sys.path.append(str(Path(__file__).parent.parent / "認証・トークン"))
try:
    from auto_token_manager import AutoTokenManager
except ImportError:
    print("警告: auto_token_manager.py が見つかりません。自動トークン更新機能は無効です。")
    AutoTokenManager = None

class ZohoAnalyticsAPIAuto:
    def __init__(self, access_token=None, workspace_id=None, auto_refresh=True):
        """
        Zoho Analytics API v2 クライアントの初期化（自動トークン更新機能付き）
        
        Args:
            access_token (str): Zoho Analytics API アクセストークン
            workspace_id (str): ワークスペースID
            auto_refresh (bool): 自動トークン更新を有効にするか
        """
        self.base_url = "https://analyticsapi.zoho.com/restapi/v2"
        self.auto_refresh = auto_refresh
        self.token_manager = None
        
        # 自動トークン更新が有効な場合
        if auto_refresh and AutoTokenManager:
            try:
                self.token_manager = AutoTokenManager()
                # 自動トークン更新を実行
                if self.token_manager.auto_refresh():
                    print("✅ 自動トークン更新が完了しました")
                else:
                    print("⚠️ 自動トークン更新に失敗しました。手動設定を使用します。")
            except Exception as e:
                print(f"⚠️ 自動トークン管理システムの初期化に失敗: {e}")
        
        # トークンとワークスペースIDを設定
        if self.token_manager:
            # 自動トークン管理から取得
            self.access_token = self.token_manager.get_current_token()
            if not self.access_token:
                raise ValueError("有効なアクセストークンを取得できませんでした")
            
            # 設定ファイルからワークスペースIDを取得
            try:
                config = self.token_manager.load_config()
                self.workspace_id = workspace_id or config.get('org_id')
            except:
                self.workspace_id = workspace_id or os.getenv('ZOHO_ANALYTICS_WORKSPACE_ID')
        else:
            # 手動設定
            self.access_token = access_token or os.getenv('ZOHO_ANALYTICS_ACCESS_TOKEN')
            self.workspace_id = workspace_id or os.getenv('ZOHO_ANALYTICS_WORKSPACE_ID')
        
        if not self.access_token:
            raise ValueError("アクセストークンが必要です。環境変数 ZOHO_ANALYTICS_ACCESS_TOKEN を設定してください。")
        
        if not self.workspace_id:
            raise ValueError("ワークスペースIDが必要です。環境変数 ZOHO_ANALYTICS_WORKSPACE_ID を設定してください。")
        
        self.org_id = os.getenv('ZOHO_ANALYTICS_ORG_ID', '772044231')
        
        self.headers = {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'ZANALYTICS-ORGID': self.org_id,
            'Content-Type': 'application/json'
        }
        
        print(f"✅ APIクライアント初期化完了")
        print(f"   ワークスペースID: {self.workspace_id}")
        print(f"   組織ID: {self.org_id}")
        print(f"   自動トークン更新: {'有効' if auto_refresh else '無効'}")
    
    def _refresh_token_if_needed(self):
        """必要に応じてトークンを更新"""
        if self.auto_refresh and self.token_manager:
            try:
                # トークンの有効期限をチェック
                tokens = self.token_manager.load_tokens()
                if tokens and self.token_manager.is_token_expired(tokens):
                    print("🔄 トークンが期限切れのため、自動更新を実行します")
                    if self.token_manager.auto_refresh():
                        # 新しいトークンを取得
                        new_token = self.token_manager.get_current_token()
                        if new_token:
                            self.access_token = new_token
                            self.headers['Authorization'] = f'Zoho-oauthtoken {self.access_token}'
                            print("✅ トークンが自動更新されました")
                            return True
                        else:
                            print("❌ トークンの自動更新に失敗しました")
                            return False
                    else:
                        print("❌ トークンの自動更新に失敗しました")
                        return False
                else:
                    return True
            except Exception as e:
                print(f"⚠️ トークン更新チェックでエラー: {e}")
                return True
        return True
    
    def execute_query(self, query, output_format='json'):
        """
        SQLクエリを実行（自動トークン更新機能付き）
        
        Args:
            query (str): 実行するSQLクエリ
            output_format (str): 出力形式 ('json', 'csv', 'xlsx')
        
        Returns:
            dict: APIレスポンス
        """
        import urllib.parse
        
        # トークン更新チェック
        if not self._refresh_token_if_needed():
            return None
        
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
            elif response.status_code == 401:
                # 認証エラーの場合、トークン更新を試行
                print("❌ 認証エラー（401）。トークン更新を試行します")
                if self.auto_refresh and self.token_manager:
                    if self.token_manager.auto_refresh():
                        # 新しいトークンで再試行
                        new_token = self.token_manager.get_current_token()
                        if new_token:
                            self.access_token = new_token
                            self.headers['Authorization'] = f'Zoho-oauthtoken {self.access_token}'
                            print("🔄 トークン更新後、クエリを再実行します")
                            return self.execute_query(query, output_format)
                
                print(f"❌ クエリ実行失敗: {response.status_code}")
                print(f"   レスポンス: {response.text[:500]}...")
                return None
            else:
                print(f"❌ クエリ実行失敗: {response.status_code}")
                print(f"   レスポンス: {response.text[:500]}...")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ APIリクエストエラー: {e}")
            return None
    
    def _wait_for_job_completion(self, job_id, max_wait_time=120):
        """
        ジョブの完了を待機してデータを取得（タイムアウト時間を延長）
        """
        import time
        
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            # トークン更新チェック
            if not self._refresh_token_if_needed():
                return None
            
            # ジョブのステータスを確認
            status_url = f"{self.base_url}/bulk/workspaces/{self.workspace_id}/exportjobs/{job_id}"
            
            try:
                response = requests.get(status_url, headers=self.headers, timeout=30)
                if response.status_code == 200:
                    status_data = response.json()
                    status = status_data.get('data', {}).get('status')
                    print(f"   ジョブステータス: {status}")
                    
                    if status == 'COMPLETED':
                        # データを取得
                        data_url = f"{self.base_url}/bulk/workspaces/{self.workspace_id}/exportjobs/{job_id}/data"
                        data_response = requests.get(data_url, headers=self.headers, timeout=60)
                        
                        if data_response.status_code == 200:
                            print("✅ データ取得完了")
                            return data_response.json()
                        else:
                            print(f"❌ データ取得失敗: {data_response.status_code}")
                            return None
                    
                    elif status == 'FAILED':
                        print("❌ ジョブが失敗しました")
                        return None
                    
                    elif status in ['IN_PROGRESS', 'QUEUED']:
                        # 10秒待機
                        time.sleep(10)
                        continue
                    
                    else:
                        print(f"⚠️ 不明なステータス: {status}")
                        time.sleep(10)
                        continue
                        
                elif response.status_code == 401:
                    # 認証エラーの場合、トークン更新を試行
                    print("❌ 認証エラー（401）。トークン更新を試行します")
                    if self.auto_refresh and self.token_manager:
                        if self.token_manager.auto_refresh():
                            new_token = self.token_manager.get_current_token()
                            if new_token:
                                self.access_token = new_token
                                self.headers['Authorization'] = f'Zoho-oauthtoken {self.access_token}'
                                print("🔄 トークン更新後、ジョブステータス確認を再実行します")
                                continue
                    
                    print("❌ ジョブステータス確認失敗")
                    return None
                else:
                    print(f"❌ ジョブステータス確認失敗: {response.status_code}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ ジョブステータス確認エラー: {e}")
                time.sleep(10)
                continue
        
        print("❌ ジョブ完了待機タイムアウト")
        return None
    
    def get_workspaces(self):
        """
        利用可能なワークスペースを取得
        """
        # トークン更新チェック
        if not self._refresh_token_if_needed():
            return None
        
        url = f"{self.base_url}/workspaces"
        
        try:
            print(f"🔄 ワークスペース取得中: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)
            print(f"   ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                # 認証エラーの場合、トークン更新を試行
                print("❌ 認証エラー（401）。トークン更新を試行します")
                if self.auto_refresh and self.token_manager:
                    if self.token_manager.auto_refresh():
                        new_token = self.token_manager.get_current_token()
                        if new_token:
                            self.access_token = new_token
                            self.headers['Authorization'] = f'Zoho-oauthtoken {self.access_token}'
                            print("🔄 トークン更新後、ワークスペース取得を再実行します")
                            return self.get_workspaces()
                
                print(f"❌ ワークスペース取得失敗: {response.status_code}")
                print(f"   レスポンス: {response.text[:500]}...")
                return None
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
        """
        # トークン更新チェック
        if not self._refresh_token_if_needed():
            return None
        
        url = f"{self.base_url}/workspaces/{self.workspace_id}/views"
        
        try:
            print(f"🔄 テーブル取得中: {url}")
            response = requests.get(url, headers=self.headers, timeout=30)
            print(f"   ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                # 認証エラーの場合、トークン更新を試行
                print("❌ 認証エラー（401）。トークン更新を試行します")
                if self.auto_refresh and self.token_manager:
                    if self.token_manager.auto_refresh():
                        new_token = self.token_manager.get_current_token()
                        if new_token:
                            self.access_token = new_token
                            self.headers['Authorization'] = f'Zoho-oauthtoken {self.access_token}'
                            print("🔄 トークン更新後、テーブル取得を再実行します")
                            return self.get_tables()
                
                print(f"❌ テーブル取得失敗: {response.status_code}")
                print(f"   レスポンス: {response.text[:500]}...")
                return None
            else:
                print(f"❌ テーブル取得失敗: {response.status_code}")
                print(f"   レスポンス: {response.text[:500]}...")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ テーブル取得エラー: {e}")
            return None
    
    def get_token_status(self):
        """トークンの状態を取得"""
        if self.token_manager:
            return self.token_manager.status()
        else:
            print("自動トークン管理システムが無効です")
            return False

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
    print("=== VERSANTコーチングレポート実行（自動トークン更新機能付き） ===")
    
    try:
        # APIクライアントを初期化（自動トークン更新有効）
        client = ZohoAnalyticsAPIAuto(auto_refresh=True)
        
        # トークン状態を表示
        print("\n=== トークン状態 ===")
        client.get_token_status()
        
        # ワークスペースアクセステスト
        print("\n=== ワークスペースアクセステスト ===")
        workspaces = client.get_workspaces()
        if workspaces and 'data' in workspaces:
            owned_workspaces = workspaces['data'].get('ownedWorkspaces', [])
            shared_workspaces = workspaces['data'].get('sharedWorkspaces', [])
            total_workspaces = len(owned_workspaces) + len(shared_workspaces)
            
            print(f"✅ ワークスペース取得成功: {total_workspaces}件")
            print(f"   所有ワークスペース: {len(owned_workspaces)}件")
            print(f"   共有ワークスペース: {len(shared_workspaces)}件")
        else:
            print("❌ ワークスペース取得に失敗しました")
            return
        
        # 簡単なクエリテスト
        print("\n=== 簡単なクエリテスト ===")
        simple_query = "SELECT COUNT(*) as total_count FROM 連絡先 LIMIT 1"
        result = client.execute_query(simple_query)
        
        if result:
            print("✅ クエリ実行成功")
            print(f"結果: {result}")
        else:
            print("❌ クエリ実行失敗")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main() 