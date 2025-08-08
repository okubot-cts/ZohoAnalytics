#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZohoCRM認証管理スクリプト
n8nで使用するZohoCRM認証情報を管理
"""

import json
import os
import sys
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional

class ZohoCRMAuthManager:
    def __init__(self, config_path: str = None):
        """
        ZohoCRM認証マネージャーの初期化
        
        Args:
            config_path (str): 設定ファイルのパス
        """
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), 
                '../設定/zoho_crm_auth_config.json'
            )
        
        self.config_path = config_path
        self.config = self.load_config()
        self.tokens_path = os.path.join(
            os.path.dirname(__file__), 
            '../設定/zoho_crm_tokens.json'
        )
    
    def load_config(self) -> Dict:
        """設定ファイルを読み込み"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"設定ファイルが見つかりません: {self.config_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"設定ファイルの形式が正しくありません: {e}")
            return {}
    
    def load_tokens(self) -> Dict:
        """トークンファイルを読み込み"""
        try:
            with open(self.tokens_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("トークンファイルが見つかりません")
            return {}
        except json.JSONDecodeError as e:
            print(f"トークンファイルの形式が正しくありません: {e}")
            return {}
    
    def save_tokens(self, tokens: Dict):
        """トークンをファイルに保存"""
        try:
            with open(self.tokens_path, 'w', encoding='utf-8') as f:
                json.dump(tokens, f, indent=2, ensure_ascii=False)
            print(f"トークンを保存しました: {self.tokens_path}")
        except Exception as e:
            print(f"トークンの保存に失敗しました: {e}")
    
    def get_auth_url(self) -> str:
        """認証URLを生成"""
        auth_config = self.config.get('zoho_crm_auth', {})
        
        params = {
            'client_id': auth_config.get('client_id'),
            'response_type': 'code',
            'scope': auth_config.get('scope'),
            'redirect_uri': auth_config.get('redirect_uri'),
            'access_type': 'offline'
        }
        
        auth_url = auth_config.get('auth_url')
        query_string = '&'.join([f"{k}={v}" for k, v in params.items() if v])
        
        return f"{auth_url}?{query_string}"
    
    def exchange_code_for_tokens(self, auth_code: str) -> Dict:
        """認証コードをトークンと交換"""
        auth_config = self.config.get('zoho_crm_auth', {})
        
        data = {
            'client_id': auth_config.get('client_id'),
            'client_secret': auth_config.get('client_secret'),
            'code': auth_code,
            'grant_type': 'authorization_code',
            'redirect_uri': auth_config.get('redirect_uri')
        }
        
        try:
            response = requests.post(
                auth_config.get('token_url'),
                data=data,
                timeout=30
            )
            response.raise_for_status()
            
            tokens = response.json()
            tokens['created_at'] = datetime.now().isoformat()
            tokens['expires_at'] = (
                datetime.now() + timedelta(seconds=tokens.get('expires_in', 3600))
            ).isoformat()
            
            return tokens
            
        except requests.exceptions.RequestException as e:
            print(f"トークン取得エラー: {e}")
            return {}
    
    def refresh_access_token(self, refresh_token: str) -> Dict:
        """アクセストークンを更新"""
        auth_config = self.config.get('zoho_crm_auth', {})
        
        data = {
            'client_id': auth_config.get('client_id'),
            'client_secret': auth_config.get('client_secret'),
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        try:
            response = requests.post(
                auth_config.get('token_url'),
                data=data,
                timeout=30
            )
            response.raise_for_status()
            
            tokens = response.json()
            tokens['created_at'] = datetime.now().isoformat()
            tokens['expires_at'] = (
                datetime.now() + timedelta(seconds=tokens.get('expires_in', 3600))
            ).isoformat()
            
            return tokens
            
        except requests.exceptions.RequestException as e:
            print(f"トークン更新エラー: {e}")
            return {}
    
    def is_token_expired(self, tokens: Dict) -> bool:
        """トークンが期限切れかチェック"""
        if not tokens or 'expires_at' not in tokens:
            return True
        
        try:
            expires_at = datetime.fromisoformat(tokens['expires_at'])
            # 5分前から期限切れとみなす
            return datetime.now() > (expires_at - timedelta(minutes=5))
        except ValueError:
            return True
    
    def get_valid_tokens(self) -> Optional[Dict]:
        """有効なトークンを取得（必要に応じて更新）"""
        tokens = self.load_tokens()
        
        if not tokens:
            print("トークンが見つかりません。認証を実行してください。")
            return None
        
        if self.is_token_expired(tokens):
            print("トークンが期限切れです。更新中...")
            
            refresh_token = tokens.get('refresh_token')
            if not refresh_token:
                print("リフレッシュトークンが見つかりません。再認証が必要です。")
                return None
            
            new_tokens = self.refresh_access_token(refresh_token)
            if new_tokens:
                # リフレッシュトークンを保持
                new_tokens['refresh_token'] = refresh_token
                self.save_tokens(new_tokens)
                return new_tokens
            else:
                print("トークンの更新に失敗しました。")
                return None
        
        return tokens
    
    def setup_initial_auth(self):
        """初期認証のセットアップ"""
        print("=== ZohoCRM初期認証セットアップ ===\n")
        
        # 1. 認証URLを表示
        auth_url = self.get_auth_url()
        print("1. 以下のURLにアクセスして認証を実行してください:")
        print(f"   {auth_url}\n")
        
        # 2. 認証コードの入力
        auth_code = input("2. 認証コードを入力してください: ").strip()
        
        if not auth_code:
            print("認証コードが入力されていません。")
            return False
        
        # 3. トークンを取得
        print("3. トークンを取得中...")
        tokens = self.exchange_code_for_tokens(auth_code)
        
        if not tokens:
            print("トークンの取得に失敗しました。")
            return False
        
        # 4. トークンを保存
        self.save_tokens(tokens)
        print("✅ 認証が完了しました！")
        
        return True
    
    def test_connection(self) -> bool:
        """ZohoCRMとの接続をテスト"""
        tokens = self.get_valid_tokens()
        
        if not tokens:
            return False
        
        access_token = tokens.get('access_token')
        api_domain = self.config.get('zoho_crm_auth', {}).get('api_domain')
        
        headers = {
            'Authorization': f"Zoho-oauthtoken {access_token}",
            'Content-Type': 'application/json'
        }
        
        try:
            # 簡単なAPI呼び出しでテスト
            response = requests.get(
                f"{api_domain}/crm/v2/settings/modules",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            print("✅ ZohoCRMとの接続テスト成功")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 接続テスト失敗: {e}")
            return False

def main():
    """メイン実行関数"""
    auth_manager = ZohoCRMAuthManager()
    
    print("ZohoCRM認証管理ツール\n")
    
    # 設定ファイルの確認
    if not auth_manager.config:
        print("❌ 設定ファイルの読み込みに失敗しました")
        return
    
    # メニュー表示
    print("選択してください:")
    print("1. 初期認証セットアップ")
    print("2. 接続テスト")
    print("3. トークン情報表示")
    print("4. 終了")
    
    choice = input("\n選択 (1-4): ").strip()
    
    if choice == "1":
        auth_manager.setup_initial_auth()
    elif choice == "2":
        auth_manager.test_connection()
    elif choice == "3":
        tokens = auth_manager.load_tokens()
        if tokens:
            print("\n=== トークン情報 ===")
            for key, value in tokens.items():
                if key in ['access_token', 'refresh_token']:
                    print(f"{key}: {str(value)[:20]}...")
                else:
                    print(f"{key}: {value}")
        else:
            print("トークンが見つかりません")
    elif choice == "4":
        print("終了します")
    else:
        print("無効な選択です")

if __name__ == "__main__":
    main() 