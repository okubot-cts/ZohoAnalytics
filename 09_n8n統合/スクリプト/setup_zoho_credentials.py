#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZohoCRM認証情報設定スクリプト
n8nにZohoCRMのOAuth2認証情報を設定
"""

import requests
import json
import os
from typing import Dict, Optional

class ZohoCredentialsSetup:
    def __init__(self):
        """初期化"""
        self.n8n_base_url = "https://cts-automation.onrender.com"
        self.n8n_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
        
        self.headers = {
            'X-N8N-API-KEY': self.n8n_api_key,
            'Content-Type': 'application/json'
        }
        
        # 設定ファイルパス
        self.config_path = os.path.join(
            os.path.dirname(__file__),
            '../設定/zoho_crm_auth_config.json'
        )
    
    def load_config(self) -> Dict:
        """設定ファイルを読み込み"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ 設定ファイルが見つかりません: {self.config_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ 設定ファイルの形式が正しくありません: {e}")
            return {}
    
    def create_oauth2_credentials(self) -> Dict:
        """OAuth2認証情報を作成"""
        
        config = self.load_config()
        zoho_config = config.get('zoho_crm_auth', {})
        
        credentials = {
            "name": "Zoho CRM OAuth2",
            "type": "zohoCrmOAuth2Api",
            "data": {
                "clientId": zoho_config.get('client_id', ''),
                "clientSecret": zoho_config.get('client_secret', ''),
                "scope": zoho_config.get('scope', 'ZohoCRM.modules.ALL,ZohoCRM.settings.ALL'),
                "authUrl": zoho_config.get('auth_url', 'https://accounts.zoho.com/oauth/v2/auth'),
                "tokenUrl": zoho_config.get('token_url', 'https://accounts.zoho.com/oauth/v2/token'),
                "redirectUri": zoho_config.get('redirect_uri', 'https://www.zohoapis.com/oauth/v2/auth')
            }
        }
        
        return credentials
    
    def deploy_credentials(self, credentials: Dict) -> bool:
        """認証情報をn8nにデプロイ"""
        
        try:
            url = f"{self.n8n_base_url}/api/v1/credentials"
            
            response = requests.post(
                url,
                headers=self.headers,
                json=credentials
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ 認証情報作成成功: {result.get('name')}")
                print(f"   ID: {result.get('id')}")
                return True
            else:
                print(f"❌ 認証情報作成失敗: {response.status_code}")
                print(f"   エラー: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ デプロイエラー: {e}")
            return False
    
    def get_existing_credentials(self) -> Optional[Dict]:
        """既存の認証情報を取得"""
        
        try:
            url = f"{self.n8n_base_url}/api/v1/credentials"
            
            response = requests.get(
                url,
                headers=self.headers
            )
            
            if response.status_code == 200:
                credentials = response.json()
                
                # ZohoCRM認証情報を検索
                for cred in credentials:
                    if cred.get('type') == 'zohoCrmOAuth2Api':
                        return cred
                
                return None
            else:
                print(f"❌ 認証情報取得失敗: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 取得エラー: {e}")
            return None
    
    def update_credentials(self, credential_id: str, credentials: Dict) -> bool:
        """認証情報を更新"""
        
        try:
            url = f"{self.n8n_base_url}/api/v1/credentials/{credential_id}"
            
            response = requests.put(
                url,
                headers=self.headers,
                json=credentials
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 認証情報更新成功: {result.get('name')}")
                return True
            else:
                print(f"❌ 認証情報更新失敗: {response.status_code}")
                print(f"   エラー: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 更新エラー: {e}")
            return False
    
    def delete_credentials(self, credential_id: str) -> bool:
        """認証情報を削除"""
        
        try:
            url = f"{self.n8n_base_url}/api/v1/credentials/{credential_id}"
            
            response = requests.delete(
                url,
                headers=self.headers
            )
            
            if response.status_code == 200:
                print(f"✅ 認証情報削除成功: {credential_id}")
                return True
            else:
                print(f"❌ 認証情報削除失敗: {response.status_code}")
                print(f"   エラー: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 削除エラー: {e}")
            return False
    
    def test_credentials(self, credential_id: str) -> bool:
        """認証情報をテスト"""
        
        try:
            # 簡単なテスト用ワークフローを作成
            test_workflow = {
                "name": "Zoho CRM - Credential Test",
                "description": "認証情報テスト用ワークフロー",
                "active": False,
                "nodes": [
                    {
                        "id": "test-node",
                        "name": "Zoho CRM Test",
                        "type": "n8n-nodes-base.zohoCrm",
                        "typeVersion": 1,
                        "position": [240, 300],
                        "parameters": {
                            "operation": "getAll",
                            "resource": "deals",
                            "limit": 1
                        },
                        "credentials": {
                            "zohoCrmOAuth2Api": {
                                "id": credential_id,
                                "name": "Zoho CRM OAuth2"
                            }
                        }
                    }
                ],
                "connections": {}
            }
            
            # テストワークフローを作成
            url = f"{self.n8n_base_url}/api/v1/workflows"
            
            response = requests.post(
                url,
                headers=self.headers,
                json=test_workflow
            )
            
            if response.status_code == 201:
                workflow_result = response.json()
                workflow_id = workflow_result.get('id')
                
                print(f"✅ テストワークフロー作成成功: {workflow_id}")
                
                # テストワークフローを削除
                delete_url = f"{self.n8n_base_url}/api/v1/workflows/{workflow_id}"
                delete_response = requests.delete(delete_url, headers=self.headers)
                
                if delete_response.status_code == 200:
                    print("✅ テストワークフロー削除完了")
                
                return True
            else:
                print(f"❌ テストワークフロー作成失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ テストエラー: {e}")
            return False
    
    def setup_complete(self) -> bool:
        """完全なセットアップを実行"""
        
        print("=== ZohoCRM認証情報セットアップ ===\n")
        
        # 設定ファイル確認
        config = self.load_config()
        if not config:
            print("❌ 設定ファイルの読み込みに失敗しました")
            return False
        
        print("📋 設定ファイル読み込み完了")
        
        # 既存の認証情報を確認
        existing_cred = self.get_existing_credentials()
        
        if existing_cred:
            print(f"⚠️  既存の認証情報が見つかりました: {existing_cred.get('name')}")
            choice = input("更新しますか？ (y/n): ").lower()
            
            if choice == 'y':
                # 認証情報を更新
                new_credentials = self.create_oauth2_credentials()
                if self.update_credentials(existing_cred.get('id'), new_credentials):
                    print("✅ 認証情報更新完了")
                else:
                    print("❌ 認証情報更新失敗")
                    return False
            else:
                print("ℹ️  既存の認証情報をそのまま使用します")
                credential_id = existing_cred.get('id')
        else:
            # 新しい認証情報を作成
            print("🆕 新しい認証情報を作成中...")
            new_credentials = self.create_oauth2_credentials()
            
            if self.deploy_credentials(new_credentials):
                print("✅ 認証情報作成完了")
                
                # 作成された認証情報のIDを取得
                created_cred = self.get_existing_credentials()
                if created_cred:
                    credential_id = created_cred.get('id')
                else:
                    print("❌ 作成された認証情報の取得に失敗")
                    return False
            else:
                print("❌ 認証情報作成失敗")
                return False
        
        # 認証情報をテスト
        print("\n🧪 認証情報をテスト中...")
        if self.test_credentials(credential_id):
            print("✅ 認証情報テスト成功")
        else:
            print("❌ 認証情報テスト失敗")
            return False
        
        print("\n🎉 セットアップ完了！")
        print(f"認証情報ID: {credential_id}")
        print("ワークフローで使用可能です")
        
        return True

def main():
    """メイン実行関数"""
    
    setup = ZohoCredentialsSetup()
    setup.setup_complete()

if __name__ == "__main__":
    main() 