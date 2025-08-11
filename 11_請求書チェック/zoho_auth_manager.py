#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zoho CRM と Zoho Books 統合認証マネージャー
請求書チェックプロジェクト用
"""

import requests
import json
import os
from datetime import datetime
from urllib.parse import urlencode

class ZohoAuthManager:
    def __init__(self, client_id, client_secret, redirect_uri, org_id):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.org_id = org_id
        self.base_url = "https://accounts.zoho.com/oauth/v2"
        
    def get_authorization_url(self, scope="ZohoCRM.modules.ALL,ZohoCRM.settings.modules.READ,ZohoCRM.settings.fields.READ,ZohoBooks.fullaccess.all"):
        """CRMとBooks両方のスコープを含む認証URLを生成"""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'scope': scope,
            'redirect_uri': self.redirect_uri,
            'access_type': 'offline'
        }
        
        auth_url = f"{self.base_url}/auth?{urlencode(params)}"
        return auth_url
    
    def get_access_token(self, authorization_code):
        """認証コードからアクセストークンを取得"""
        token_url = f"{self.base_url}/token"
        
        data = {
            'code': authorization_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"トークン取得エラー: {response.status_code} - {response.text}")
    
    def refresh_access_token(self, refresh_token):
        """リフレッシュトークンから新しいアクセストークンを取得"""
        token_url = f"{self.base_url}/token"
        
        data = {
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"トークン更新エラー: {response.status_code} - {response.text}")
    
    def save_tokens(self, token_data, filename='zoho_tokens.json'):
        """トークンをファイルに保存"""
        token_data['saved_at'] = datetime.now().isoformat()
        token_data['org_id'] = self.org_id
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(token_data, f, indent=2, ensure_ascii=False)
        print(f"✓ トークンを {filename} に保存しました")
    
    def load_tokens(self, filename='zoho_tokens.json'):
        """保存されたトークンを読み込み"""
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

class ZohoCRMAPI:
    def __init__(self, access_token, org_id):
        self.access_token = access_token
        self.org_id = org_id
        self.base_url = f"https://www.zohoapis.com/crm/v3"
        
    def get_headers(self):
        """APIリクエスト用のヘッダーを取得"""
        return {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_modules(self):
        """利用可能なモジュール一覧を取得"""
        url = f"{self.base_url}/settings/modules"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"モジュール取得エラー: {response.status_code} - {response.text}")
    
    def get_module_fields(self, module_name):
        """指定モジュールのフィールド一覧を取得"""
        url = f"{self.base_url}/settings/modules/{module_name}/fields"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"フィールド取得エラー: {response.status_code} - {response.text}")
    
    def get_records(self, module_name, params=None):
        """指定モジュールのレコードを取得"""
        url = f"{self.base_url}/{module_name}"
        if params:
            url += "?" + urlencode(params)
        
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"レコード取得エラー: {response.status_code} - {response.text}")

class ZohoBooksAPI:
    def __init__(self, access_token, org_id):
        self.access_token = access_token
        self.org_id = org_id
        self.base_url = f"https://books.zoho.com/api/v3"
        
    def get_headers(self):
        """APIリクエスト用のヘッダーを取得"""
        return {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'Content-Type': 'application/json',
            'organization-id': self.org_id
        }
    
    def get_organizations(self):
        """組織一覧を取得"""
        url = f"{self.base_url}/organizations"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"組織取得エラー: {response.status_code} - {response.text}")
    
    def get_invoices(self, params=None):
        """請求書一覧を取得"""
        url = f"{self.base_url}/invoices"
        if params:
            url += "?" + urlencode(params)
        
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"請求書取得エラー: {response.status_code} - {response.text}")
    
    def get_invoice(self, invoice_id):
        """特定の請求書を取得"""
        url = f"{self.base_url}/invoices/{invoice_id}"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"請求書取得エラー: {response.status_code} - {response.text}")
    
    def get_customers(self, params=None):
        """顧客一覧を取得"""
        url = f"{self.base_url}/contacts"
        if params:
            url += "?" + urlencode(params)
        
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"顧客取得エラー: {response.status_code} - {response.text}")

def main():
    print("=== Zoho CRM & Books 統合認証 ===")
    print("請求書チェックプロジェクト用の認証を行います\n")
    
    # 設定ファイルから認証情報を読み込み
    config_file = "../01_Zoho_API/設定ファイル/zoho_config.json"
    
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        CLIENT_ID = config['client_id']
        CLIENT_SECRET = config['client_secret']
        ORG_ID = config['org_id']
        REDIRECT_URI = config['redirect_uri']
    else:
        print("設定ファイルが見つかりません。手動で認証情報を入力してください。")
        CLIENT_ID = input("Client ID: ")
        CLIENT_SECRET = input("Client Secret: ")
        ORG_ID = input("Organization ID: ")
        REDIRECT_URI = input("Redirect URI: ")
    
    auth_manager = ZohoAuthManager(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, ORG_ID)
    
    print("1. 以下のURLにアクセスしてCRM & Books API認証を行ってください:")
    print(auth_manager.get_authorization_url())
    print("\n2. 認証後のリダイレクトURLから認証コードを取得してください")
    print("   例: http://localhost:8080/callback?code=1000.abc123...")
    print("\n認証コードを入力してください: ", end="")
    
    # 実際の使用時はここでinputを使用
    print("\n[注意] 実際の認証コードを入力してスクリプトを実行してください")

if __name__ == "__main__":
    main()

