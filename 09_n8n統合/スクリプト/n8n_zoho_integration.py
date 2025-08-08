#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
n8n経由でZohoCRMにアクセスする統合スクリプト
ZohoCRM認証マネージャーと統合
"""

import requests
import json
import time
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# ZohoCRM認証マネージャーをインポート
sys.path.append(os.path.dirname(__file__))
from zoho_crm_auth_manager import ZohoCRMAuthManager

class N8nZohoIntegration:
    def __init__(self, n8n_base_url: str, api_key: str, auth_manager: ZohoCRMAuthManager = None):
        """
        n8n統合クラスの初期化
        
        Args:
            n8n_base_url (str): n8nインスタンスのベースURL
            api_key (str): n8nのAPIキー
            auth_manager (ZohoCRMAuthManager): ZohoCRM認証マネージャー
        """
        self.n8n_base_url = n8n_base_url.rstrip('/')
        self.api_key = api_key
        self.auth_manager = auth_manager or ZohoCRMAuthManager()
        
        self.headers = {
            'X-N8N-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
    
    def get_workflows(self) -> List[Dict]:
        """利用可能なワークフロー一覧を取得"""
        url = f"{self.n8n_base_url}/api/v1/workflows"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"ワークフロー一覧取得エラー: {e}")
            return []
    
    def execute_workflow(self, workflow_id: str, data: Dict = None) -> Dict:
        """
        ワークフローを実行
        
        Args:
            workflow_id (str): ワークフローのID
            data (Dict): ワークフローに渡すデータ
        
        Returns:
            Dict: 実行結果
        """
        url = f"{self.n8n_base_url}/api/v1/workflows/{workflow_id}/execute"
        
        payload = {
            "data": data or {}
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"ワークフロー実行エラー: {e}")
            return {"error": str(e)}
    
    def execute_webhook(self, webhook_path: str, data: Dict = None) -> Dict:
        """
        Webhookを直接実行
        
        Args:
            webhook_path (str): Webhookのパス
            data (Dict): 送信データ
        
        Returns:
            Dict: 実行結果
        """
        url = f"{self.n8n_base_url}/webhook/{webhook_path}"
        
        try:
            response = requests.post(url, json=data or {}, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Webhook実行エラー: {e}")
            return {"error": str(e)}
    
    def get_workflow_executions(self, workflow_id: str, limit: int = 10) -> List[Dict]:
        """ワークフローの実行履歴を取得"""
        url = f"{self.n8n_base_url}/api/v1/workflows/{workflow_id}/executions"
        params = {"limit": limit}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"実行履歴取得エラー: {e}")
            return []
    
    def create_zoho_deals_workflow_data(self, from_date: str = "2025-04-01") -> Dict:
        """
        ZohoCRM商談取得用のワークフローデータを作成
        
        Args:
            from_date (str): 取得開始日（YYYY-MM-DD形式）
        
        Returns:
            Dict: ワークフロー用データ
        """
        return {
            "date_from": from_date,
            "timestamp": datetime.now().isoformat(),
            "request_type": "get_deals",
            "filters": {
                "stage": "all",
                "include_products": True
            }
        }
    
    def get_current_period_deals_via_n8n(self, workflow_id: str = None, from_date: str = "2025-04-01") -> Dict:
        """
        n8n経由で今期の商談データを取得
        
        Args:
            workflow_id (str): 商談取得ワークフローのID（Noneの場合はWebhookを使用）
            from_date (str): 取得開始日
        
        Returns:
            Dict: 商談データ
        """
        print(f"n8n経由で商談データを取得中... (開始日: {from_date})")
        
        # ワークフロー実行用データを作成
        workflow_data = self.create_zoho_deals_workflow_data(from_date)
        
        if workflow_id:
            # ワークフローIDが指定されている場合はAPI経由で実行
            result = self.execute_workflow(workflow_id, workflow_data)
        else:
            # Webhook経由で実行
            result = self.execute_webhook("zoho-deals", workflow_data)
        
        if "error" in result:
            print(f"ワークフロー実行エラー: {result['error']}")
            return result
        
        print("ワークフロー実行完了")
        return result
    
    def get_products_for_deal(self, deal_id: str) -> Dict:
        """
        特定の商談の商品内訳を取得
        
        Args:
            deal_id (str): 商談ID
        
        Returns:
            Dict: 商品内訳データ
        """
        print(f"商談ID {deal_id} の商品内訳を取得中...")
        
        data = {
            "deal_id": deal_id,
            "timestamp": datetime.now().isoformat()
        }
        
        result = self.execute_webhook("zoho-products", data)
        
        if "error" in result:
            print(f"商品内訳取得エラー: {result['error']}")
            return result
        
        print("商品内訳取得完了")
        return result
    
    def create_new_deal(self, deal_data: Dict) -> Dict:
        """
        新規商談を作成
        
        Args:
            deal_data (Dict): 商談データ
        
        Returns:
            Dict: 作成結果
        """
        print("新規商談を作成中...")
        
        data = {
            **deal_data,
            "timestamp": datetime.now().isoformat()
        }
        
        result = self.execute_webhook("zoho-create-deal", data)
        
        if "error" in result:
            print(f"商談作成エラー: {result['error']}")
            return result
        
        print("商談作成完了")
        return result
    
    def test_zoho_connection(self) -> bool:
        """ZohoCRMとの接続をテスト"""
        print("ZohoCRMとの接続をテスト中...")
        
        if not self.auth_manager:
            print("認証マネージャーが設定されていません")
            return False
        
        return self.auth_manager.test_connection()
    
    def save_results(self, data: Dict, filename_prefix: str = "n8n_result"):
        """結果をファイルに保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"../データ/{filename_prefix}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"結果を保存しました: {filename}")
        except Exception as e:
            print(f"ファイル保存エラー: {e}")

def main():
    """メイン実行関数"""
    
    # 設定ファイルから設定を読み込み
    config_path = os.path.join(
        os.path.dirname(__file__), 
        '../設定/zoho_crm_auth_config.json'
    )
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"設定ファイルが見つかりません: {config_path}")
        return
    except json.JSONDecodeError as e:
        print(f"設定ファイルの形式が正しくありません: {e}")
        return
    
    # n8n設定
    n8n_config = config.get('n8n_config', {})
    N8N_BASE_URL = n8n_config.get('base_url', 'http://localhost:5678')
    N8N_API_KEY = n8n_config.get('api_key')
    
    if not N8N_API_KEY:
        print("n8n APIキーが設定されていません")
        return
    
    # ZohoCRM認証マネージャーを初期化
    auth_manager = ZohoCRMAuthManager()
    
    # n8n統合インスタンスを作成
    n8n_integration = N8nZohoIntegration(N8N_BASE_URL, N8N_API_KEY, auth_manager)
    
    print("=== n8n ZohoCRM統合テスト ===\n")
    
    # 1. ZohoCRM接続テスト
    print("1. ZohoCRM接続テスト...")
    if not n8n_integration.test_zoho_connection():
        print("❌ ZohoCRMとの接続に失敗しました")
        print("認証設定を確認してください")
        return
    
    # 2. 利用可能なワークフロー一覧を取得
    print("\n2. ワークフロー一覧を取得中...")
    workflows = n8n_integration.get_workflows()
    
    if workflows:
        print(f"利用可能なワークフロー数: {len(workflows)}")
        for i, workflow in enumerate(workflows[:5], 1):
            print(f"  {i}. ID: {workflow.get('id')}, 名前: {workflow.get('name')}")
    else:
        print("ワークフローが見つかりません")
        print("n8nでワークフローを作成してください")
        return
    
    # 3. 今期の商談データを取得（Webhook経由）
    print("\n3. 商談データを取得中...")
    deals_result = n8n_integration.get_current_period_deals_via_n8n(
        from_date="2025-04-01"
    )
    
    # 4. 結果を表示・保存
    print("\n4. 取得結果:")
    if "error" not in deals_result:
        print("✅ 商談データの取得に成功しました")
        
        # 結果を保存
        n8n_integration.save_results(deals_result, "n8n_zoho_deals")
        
        # 結果の概要を表示
        if isinstance(deals_result, dict) and 'data' in deals_result:
            data = deals_result['data']
            if isinstance(data, list):
                print(f"取得件数: {len(data)}件")
                if data:
                    print("最初の商談:")
                    first_deal = data[0]
                    print(f"  - 商談名: {first_deal.get('deal_name', 'N/A')}")
                    print(f"  - 金額: {first_deal.get('amount', 'N/A')}")
                    print(f"  - ステージ: {first_deal.get('stage', 'N/A')}")
    else:
        print(f"❌ エラーが発生しました: {deals_result['error']}")
    
    # 5. 商品内訳取得のテスト（サンプル）
    print("\n5. 商品内訳取得テスト...")
    # 実際の商談IDを使用する場合は、上記で取得したデータから取得
    sample_deal_id = "5187347000192553190"  # サンプルID
    products_result = n8n_integration.get_products_for_deal(sample_deal_id)
    
    if "error" not in products_result:
        print("✅ 商品内訳の取得に成功しました")
        n8n_integration.save_results(products_result, "n8n_zoho_products")
    else:
        print(f"❌ 商品内訳取得エラー: {products_result['error']}")

if __name__ == "__main__":
    main() 