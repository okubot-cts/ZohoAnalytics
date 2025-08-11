#!/usr/bin/env python3
"""
Zoho CRMとZoho Booksへの接続テストスクリプト
"""
import requests
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class ZohoConnector:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.crm_tokens_file = self.base_path / "zoho_crm_tokens.json"
        self.books_tokens_file = self.base_path / "zoho_books_tokens.json"
        self.config_file = self.base_path / "zoho_config.json"
        
        # 設定読み込み
        self.load_config()
        
    def load_config(self):
        """設定ファイルを読み込む"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            # デフォルト設定
            self.config = {
                "client_id": "1000.YN0LA88XQRCDTARO3FO5PWCOEY2IFZ",
                "client_secret": "25549573ace167da7319c6b561a8ea477ca235e0ef",
                "redirect_uri": "http://localhost:8080/callback"
            }
    
    def refresh_token_if_needed(self, service="crm"):
        """必要に応じてトークンをリフレッシュ"""
        tokens_file = self.crm_tokens_file if service == "crm" else self.books_tokens_file
        
        if not tokens_file.exists():
            print(f"❌ {service.upper()}トークンファイルが見つかりません: {tokens_file}")
            return None
            
        with open(tokens_file, 'r') as f:
            tokens = json.load(f)
        
        # 有効期限チェック
        if 'expires_at' in tokens:
            expires_at = datetime.fromisoformat(tokens['expires_at'])
            if datetime.now() >= expires_at:
                print(f"🔄 {service.upper()}トークンの有効期限が切れています。リフレッシュします...")
                return self.refresh_access_token(tokens, service)
        
        return tokens
    
    def refresh_access_token(self, tokens, service="crm"):
        """アクセストークンをリフレッシュ"""
        refresh_url = "https://accounts.zoho.com/oauth/v2/token"
        
        data = {
            'refresh_token': tokens.get('refresh_token'),
            'client_id': self.config.get('client_id'),
            'client_secret': self.config.get('client_secret'),
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(refresh_url, data=data)
        
        if response.status_code == 200:
            new_tokens = response.json()
            # 既存のトークン情報を更新
            tokens['access_token'] = new_tokens['access_token']
            tokens['expires_in'] = new_tokens.get('expires_in', 3600)
            tokens['expires_at'] = (datetime.now() + timedelta(seconds=tokens['expires_in'])).isoformat()
            tokens['updated_at'] = datetime.now().isoformat()
            
            # ファイルに保存
            tokens_file = self.crm_tokens_file if service == "crm" else self.books_tokens_file
            with open(tokens_file, 'w') as f:
                json.dump(tokens, f, indent=2)
            
            print(f"✅ {service.upper()}トークンを更新しました")
            return tokens
        else:
            print(f"❌ トークンリフレッシュ失敗: {response.status_code} - {response.text}")
            return None
    
    def test_crm_connection(self):
        """ZohoCRMへの接続テスト"""
        print("\n=== Zoho CRM 接続テスト ===")
        
        tokens = self.refresh_token_if_needed("crm")
        if not tokens:
            return False
        
        # CRM APIにテストリクエスト（組織情報を取得）
        headers = {
            'Authorization': f'Bearer {tokens["access_token"]}'
        }
        
        # 商談（Deals）モジュールの情報を取得
        api_url = "https://www.zohoapis.com/crm/v2/Deals"
        params = {
            'fields': 'Deal_Name,Stage,Amount,Closing_Date',
            'per_page': 5  # 最初の5件のみ
        }
        
        try:
            response = requests.get(api_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ CRM接続成功!")
                
                if 'data' in data and data['data']:
                    print(f"\n最新の商談 (最大5件):")
                    for i, deal in enumerate(data['data'][:5], 1):
                        print(f"  {i}. {deal.get('Deal_Name', 'N/A')}")
                        print(f"     ステージ: {deal.get('Stage', 'N/A')}")
                        print(f"     金額: ¥{deal.get('Amount', 0):,.0f}")
                        print(f"     完了予定日: {deal.get('Closing_Date', 'N/A')}")
                else:
                    print("  商談データが見つかりません")
                
                return True
            else:
                print(f"❌ CRM APIエラー: {response.status_code}")
                print(f"   詳細: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ CRM接続エラー: {str(e)}")
            return False
    
    def setup_books_auth(self):
        """Zoho Books用の認証URLを生成"""
        from urllib.parse import urlencode
        
        scope = "ZohoBooks.fullaccess.all"
        
        params = {
            'response_type': 'code',
            'client_id': self.config.get('client_id'),
            'scope': scope,
            'redirect_uri': self.config.get('redirect_uri'),
            'access_type': 'offline'
        }
        
        auth_url = f"https://accounts.zoho.com/oauth/v2/auth?{urlencode(params)}"
        return auth_url
    
    def get_books_token(self, auth_code):
        """Zoho Books用のアクセストークンを取得"""
        token_url = "https://accounts.zoho.com/oauth/v2/token"
        
        data = {
            'code': auth_code,
            'client_id': self.config.get('client_id'),
            'client_secret': self.config.get('client_secret'),
            'redirect_uri': self.config.get('redirect_uri'),
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            token_data['expires_at'] = (datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))).isoformat()
            token_data['updated_at'] = datetime.now().isoformat()
            
            # トークンを保存
            with open(self.books_tokens_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            print("✅ Zoho Booksトークンを保存しました")
            return token_data
        else:
            print(f"❌ トークン取得エラー: {response.status_code} - {response.text}")
            return None
    
    def test_books_connection(self):
        """ZohoBooksへの接続テスト"""
        print("\n=== Zoho Books 接続テスト ===")
        
        if not self.books_tokens_file.exists():
            print("⚠️  Zoho Booksトークンがありません。認証が必要です。")
            print("\n以下のURLにアクセスして認証してください:")
            print(self.setup_books_auth())
            print("\n認証コードを取得したら、get_books_token()メソッドで設定してください。")
            return False
        
        tokens = self.refresh_token_if_needed("books")
        if not tokens:
            return False
        
        # Books APIにテストリクエスト（組織情報を取得）
        headers = {
            'Authorization': f'Bearer {tokens["access_token"]}'
        }
        
        # 組織一覧を取得
        api_url = "https://books.zoho.com/api/v3/organizations"
        
        try:
            response = requests.get(api_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Books接続成功!")
                
                if 'organizations' in data and data['organizations']:
                    print(f"\n組織情報:")
                    for org in data['organizations']:
                        print(f"  - {org.get('name', 'N/A')} (ID: {org.get('organization_id', 'N/A')})")
                        
                    # 最初の組織IDを使用して請求書を取得
                    org_id = data['organizations'][0]['organization_id']
                    self.get_invoices(tokens['access_token'], org_id)
                    
                return True
            else:
                print(f"❌ Books APIエラー: {response.status_code}")
                print(f"   詳細: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Books接続エラー: {str(e)}")
            return False
    
    def get_invoices(self, access_token, org_id):
        """請求書リストを取得"""
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        api_url = f"https://books.zoho.com/api/v3/invoices"
        params = {
            'organization_id': org_id,
            'per_page': 5  # 最初の5件のみ
        }
        
        try:
            response = requests.get(api_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'invoices' in data and data['invoices']:
                    print(f"\n最新の請求書 (最大5件):")
                    for i, invoice in enumerate(data['invoices'][:5], 1):
                        print(f"  {i}. 請求書番号: {invoice.get('invoice_number', 'N/A')}")
                        print(f"     顧客: {invoice.get('customer_name', 'N/A')}")
                        print(f"     金額: ¥{invoice.get('total', 0):,.0f}")
                        print(f"     ステータス: {invoice.get('status', 'N/A')}")
                        print(f"     日付: {invoice.get('date', 'N/A')}")
                else:
                    print("  請求書データが見つかりません")
                    
        except Exception as e:
            print(f"請求書取得エラー: {str(e)}")

def main():
    """メイン処理"""
    connector = ZohoConnector()
    
    # CRM接続テスト
    crm_success = connector.test_crm_connection()
    
    # Books接続テスト
    books_success = connector.test_books_connection()
    
    # 結果サマリ
    print("\n" + "="*50)
    print("接続テスト結果:")
    print(f"  Zoho CRM: {'✅ 成功' if crm_success else '❌ 失敗'}")
    print(f"  Zoho Books: {'✅ 成功' if books_success else '❌ 失敗または未設定'}")
    
    if not books_success and not connector.books_tokens_file.exists():
        print("\n📝 Zoho Books設定方法:")
        print("1. 上記の認証URLにアクセス")
        print("2. 認証コードを取得")
        print("3. 以下のコードを実行:")
        print("   connector.get_books_token('取得した認証コード')")

if __name__ == "__main__":
    main()