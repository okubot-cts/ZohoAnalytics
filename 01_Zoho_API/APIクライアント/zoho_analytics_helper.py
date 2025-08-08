#!/usr/bin/env python3
"""
Zoho Analytics SQL Helper
自然言語でSQL生成をサポートするヘルパーツール
"""

import requests
import json
from typing import Dict, List, Optional
from token_manager import ZohoTokenManager

class ZohoAnalyticsHelper:
    def __init__(self, token_manager: ZohoTokenManager = None):
        if token_manager is None:
            token_manager = ZohoTokenManager()
        
        self.token_manager = token_manager
        self.base_url = "https://analyticsapi.zoho.com/restapi/v2"
    
    def _get_headers(self) -> Dict:
        """認証ヘッダーを取得（トークンを自動更新）"""
        credentials = self.token_manager.get_credentials()
        return {
            'Authorization': f'Zoho-oauthtoken {credentials["access_token"]}',
            'ZANALYTICS-ORGID': credentials['org_id'],
            'Content-Type': 'application/json'
        }
    
    def get_workspaces(self) -> Dict:
        """ワークスペース一覧を取得"""
        url = f"{self.base_url}/workspaces"
        response = requests.get(url, headers=self._get_headers())
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    def get_tables(self, workspace_id: str) -> Dict:
        """指定ワークスペースのテーブル一覧を取得"""
        url = f"{self.base_url}/workspaces/{workspace_id}/views"
        response = requests.get(url, headers=self._get_headers())
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    def get_table_metadata(self, workspace_id: str, table_id: str) -> Dict:
        """テーブルのメタデータ（カラム情報等）を取得"""
        url = f"{self.base_url}/views/{table_id}"
        params = {"withInvolvedMetaInfo": "true"}
        response = requests.get(url, headers=self._get_headers(), params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    def execute_sql(self, workspace_id: str, sql_query: str) -> Dict:
        """SQLクエリを実行（非同期）"""
        import urllib.parse
        import json as jsonlib
        import time
        
        # 設定をJSON形式で作成
        config = {
            "responseFormat": "json",
            "sqlQuery": sql_query
        }
        
        # ConfigをURL エンコード
        config_encoded = urllib.parse.quote(jsonlib.dumps(config))
        
        # 非同期エクスポートジョブを作成
        url = f"{self.base_url}/bulk/workspaces/{workspace_id}/data?CONFIG={config_encoded}"
        response = requests.get(url, headers=self._get_headers())
        
        if response.status_code == 200:
            job_data = response.json()
            if 'data' in job_data and 'jobId' in job_data['data']:
                job_id = job_data['data']['jobId']
                print(f"エクスポートジョブを開始しました (ID: {job_id})")
                
                # ジョブの完了を待機
                return self._wait_for_job_completion(job_id, workspace_id)
            else:
                return job_data
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    def _wait_for_job_completion(self, job_id: str, workspace_id: str = None, max_wait_time: int = 60) -> Dict:
        """ジョブの完了を待機してデータを取得"""
        import time
        
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            # ジョブのステータスを確認 (workspace_idを含める)
            if workspace_id:
                status_url = f"{self.base_url}/bulk/workspaces/{workspace_id}/exportjobs/{job_id}"
            else:
                status_url = f"{self.base_url}/bulk/exportjobs/{job_id}"
            
            status_response = requests.get(status_url, headers=self._get_headers())
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                
                if 'data' in status_data and 'jobStatus' in status_data['data']:
                    job_status = status_data['data']['jobStatus']
                    print(f"ジョブステータス: {job_status}")
                    
                    if job_status in ['Success', 'JOB COMPLETED']:
                        # データをダウンロード
                        download_url = status_data['data'].get('downloadUrl')
                        print(f"ダウンロードURL: {download_url}")
                        print(f"ステータスデータ: {status_data}")
                        
                        if download_url:
                            download_response = requests.get(download_url, headers=self._get_headers())
                            if download_response.status_code == 200:
                                return download_response.json()
                        else:
                            # ダウンロードURLがない場合、レスポンス全体を返す
                            return status_data
                        break
                    elif job_status in ['Failure', 'JOB FAILED']:
                        raise Exception(f"ジョブが失敗しました: {status_data}")
                    elif job_status in ['JOB IN PROGRESS', 'In Progress']:
                        # 進行中の場合は継続
                        pass
                    
                time.sleep(2)  # 2秒待機
            else:
                raise Exception(f"ジョブステータス取得エラー: {status_response.status_code} - {status_response.text}")
        
        raise Exception(f"ジョブの完了待機がタイムアウトしました (Job ID: {job_id})")
    
    def natural_language_to_sql(self, workspace_id: str, natural_query: str) -> str:
        """
        自然言語からSQLを生成（簡易版）
        実際のプロダクションでは、より高度なNLP処理が必要
        """
        # まずテーブル情報を取得
        tables = self.get_tables(workspace_id)
        
        # 基本的なキーワードマッピング
        sql_keywords = {
            '選択': 'SELECT',
            '取得': 'SELECT',
            '表示': 'SELECT',
            'から': 'FROM',
            '条件': 'WHERE',
            '並び順': 'ORDER BY',
            'グループ': 'GROUP BY',
            '件数': 'COUNT(*)',
            '合計': 'SUM',
            '平均': 'AVG',
            '最大': 'MAX',
            '最小': 'MIN',
        }
        
        # 簡易的なSQL生成ロジック
        sql_parts = []
        
        if any(keyword in natural_query for keyword in ['選択', '取得', '表示']):
            sql_parts.append('SELECT')
            
            if '件数' in natural_query:
                sql_parts.append('COUNT(*)')
            elif '全て' in natural_query or 'すべて' in natural_query:
                sql_parts.append('*')
            else:
                sql_parts.append('*')
        
        # テーブル名を推測
        table_names = []
        if 'data' in tables and 'views' in tables['data']:
            for view in tables['data']['views']:
                if view.get('viewType') == 'Table':
                    table_name = view.get('viewName', '')
                    if any(name in natural_query for name in [table_name, table_name.lower()]):
                        table_names.append(table_name)
        
        if table_names:
            sql_parts.extend(['FROM', table_names[0]])
        
        return ' '.join(sql_parts)
    
    def interactive_sql_builder(self):
        """対話式SQLビルダー"""
        print("=== Zoho Analytics SQL Helper ===")
        print("自然言語でSQLクエリを生成します\n")
        
        # ワークスペース選択
        workspaces = self.get_workspaces()
        print("利用可能なワークスペース:")
        all_workspaces = []
        
        if 'ownedWorkspaces' in workspaces['data']:
            all_workspaces.extend(workspaces['data']['ownedWorkspaces'])
        if 'sharedWorkspaces' in workspaces['data']:
            all_workspaces.extend(workspaces['data']['sharedWorkspaces'])
        
        for i, ws in enumerate(all_workspaces):
            print(f"{i+1}. {ws['workspaceName']} (ID: {ws['workspaceId']})")
        
        while True:
            try:
                choice = int(input("\nワークスペースを選択してください (番号): ")) - 1
                if 0 <= choice < len(all_workspaces):
                    selected_workspace = all_workspaces[choice]
                    break
                else:
                    print("無効な番号です。")
            except ValueError:
                print("数値を入力してください。")
        
        workspace_id = selected_workspace['workspaceId']
        print(f"\n選択されたワークスペース: {selected_workspace['workspaceName']}")
        
        # テーブル情報表示
        try:
            tables = self.get_tables(workspace_id)
            print("\n利用可能なテーブル:")
            if 'data' in tables and 'views' in tables['data']:
                for view in tables['data']['views']:
                    if view.get('viewType') == 'Table':
                        print(f"- {view.get('viewName', 'Unknown')}")
        except Exception as e:
            print(f"テーブル情報の取得に失敗: {e}")
        
        # 自然言語クエリ入力
        while True:
            natural_query = input("\n自然言語でクエリを入力してください (exitで終了): ")
            if natural_query.lower() == 'exit':
                break
            
            try:
                # SQL生成
                sql_query = self.natural_language_to_sql(workspace_id, natural_query)
                print(f"\n生成されたSQL: {sql_query}")
                
                # 実行確認
                execute = input("このSQLを実行しますか？ (y/N): ")
                if execute.lower() == 'y':
                    result = self.execute_sql(workspace_id, sql_query)
                    print("\n実行結果:")
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                
            except Exception as e:
                print(f"エラー: {e}")

def main():
    """メイン関数"""
    try:
        token_manager = ZohoTokenManager()
        
        # トークンの状態確認
        status = token_manager.get_token_status()
        if status['status'] == 'no_tokens':
            print("初回セットアップが必要です。")
            token_manager.interactive_setup()
            return
        elif status['status'] == 'expired' and not status.get('has_refresh_token'):
            print("トークンの有効期限が切れています。再認証が必要です。")
            token_manager.interactive_setup()
            return
        
        # SQL Helper実行
        helper = ZohoAnalyticsHelper(token_manager)
        helper.interactive_sql_builder()
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        if "トークン" in str(e) or "認証" in str(e):
            print("\n認証に問題があります。以下のコマンドでセットアップを実行してください:")
            print("python token_manager.py setup")

if __name__ == "__main__":
    main()