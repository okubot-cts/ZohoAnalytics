#!/usr/bin/env python3
"""
Zoho Analytics Token Manager
アクセストークンとリフレッシュトークンの管理
"""

import json
import time
import requests
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta

class ZohoTokenManager:
    def __init__(self, config_file: str = "zoho_config.json"):
        self.config_file = Path(config_file)
        self.token_file = Path("zoho_tokens.json")
        self.config = self._load_config()
        self.tokens = self._load_tokens()
    
    def _load_config(self) -> Dict:
        """設定ファイルから認証情報を読み込み"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 初期設定ファイルを作成
            config = {
                "client_id": "",
                "client_secret": "",
                "org_id": "",
                "redirect_uri": "http://localhost:8080/callback"
            }
            self._save_config(config)
            return config
    
    def _save_config(self, config: Dict):
        """設定をファイルに保存"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def _load_tokens(self) -> Dict:
        """トークンファイルから認証トークンを読み込み"""
        if self.token_file.exists():
            with open(self.token_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_tokens(self, tokens: Dict):
        """トークンをファイルに保存"""
        with open(self.token_file, 'w', encoding='utf-8') as f:
            json.dump(tokens, f, indent=2, ensure_ascii=False)
    
    def setup_credentials(self, client_id: str, client_secret: str, org_id: str):
        """認証情報を設定"""
        self.config.update({
            "client_id": client_id,
            "client_secret": client_secret,
            "org_id": org_id
        })
        self._save_config(self.config)
        print("認証情報が保存されました。")
    
    def generate_auth_url(self) -> str:
        """OAuth認証URLを生成"""
        if not self.config.get("client_id"):
            raise ValueError("Client IDが設定されていません。setup_credentials()を実行してください。")
        
        import urllib.parse
        
        scope = 'ZohoAnalytics.fullaccess.all'
        auth_url = (
            f"https://accounts.zoho.com/oauth/v2/auth"
            f"?scope={scope}"
            f"&client_id={self.config['client_id']}"
            f"&response_type=code"
            f"&redirect_uri={urllib.parse.quote(self.config['redirect_uri'])}"
            f"&access_type=offline"
        )
        return auth_url
    
    def exchange_code_for_tokens(self, authorization_code: str) -> Dict:
        """認証コードをアクセストークンとリフレッシュトークンに交換"""
        token_url = 'https://accounts.zoho.com/oauth/v2/token'
        data = {
            'code': authorization_code,
            'grant_type': 'authorization_code',
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret'],
            'redirect_uri': self.config['redirect_uri']
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            
            # トークン情報に有効期限を追加
            expires_at = datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))
            token_data['expires_at'] = expires_at.isoformat()
            token_data['created_at'] = datetime.now().isoformat()
            
            self.tokens = token_data
            self._save_tokens(token_data)
            
            print("トークンが取得・保存されました。")
            return token_data
        else:
            raise Exception(f"トークン取得エラー: {response.status_code} - {response.text}")
    
    def refresh_access_token(self) -> Dict:
        """リフレッシュトークンを使用してアクセストークンを更新"""
        if not self.tokens.get('refresh_token'):
            raise ValueError("リフレッシュトークンが見つかりません。初回認証を行ってください。")
        
        token_url = 'https://accounts.zoho.com/oauth/v2/token'
        data = {
            'refresh_token': self.tokens['refresh_token'],
            'grant_type': 'refresh_token',
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret']
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            new_token_data = response.json()
            
            # 新しいトークン情報を既存の情報と統合
            expires_at = datetime.now() + timedelta(seconds=new_token_data.get('expires_in', 3600))
            new_token_data['expires_at'] = expires_at.isoformat()
            new_token_data['refreshed_at'] = datetime.now().isoformat()
            
            # リフレッシュトークンは通常変更されないので保持
            if 'refresh_token' not in new_token_data and 'refresh_token' in self.tokens:
                new_token_data['refresh_token'] = self.tokens['refresh_token']
            
            self.tokens.update(new_token_data)
            self._save_tokens(self.tokens)
            
            print("アクセストークンが更新されました。")
            return new_token_data
        else:
            raise Exception(f"トークン更新エラー: {response.status_code} - {response.text}")
    
    def is_token_expired(self) -> bool:
        """アクセストークンの有効期限をチェック"""
        if not self.tokens.get('expires_at'):
            return True
        
        expires_at = datetime.fromisoformat(self.tokens['expires_at'])
        # 5分前にリフレッシュ（安全マージン）
        return datetime.now() >= (expires_at - timedelta(minutes=5))
    
    def get_valid_access_token(self) -> str:
        """有効なアクセストークンを取得（必要に応じて自動更新）"""
        if not self.tokens.get('access_token'):
            raise ValueError("アクセストークンが見つかりません。初回認証を行ってください。")
        
        if self.is_token_expired():
            print("アクセストークンの有効期限が切れています。更新中...")
            self.refresh_access_token()
        
        return self.tokens['access_token']
    
    def get_credentials(self) -> Dict:
        """現在の認証情報を取得"""
        return {
            'access_token': self.get_valid_access_token(),
            'org_id': self.config['org_id'],
            'client_id': self.config['client_id']
        }
    
    def get_token_status(self) -> Dict:
        """トークンの状態を取得"""
        if not self.tokens:
            return {"status": "no_tokens", "message": "トークンが設定されていません"}
        
        expires_at = self.tokens.get('expires_at')
        if expires_at:
            expires_datetime = datetime.fromisoformat(expires_at)
            remaining = expires_datetime - datetime.now()
            
            if remaining.total_seconds() > 0:
                return {
                    "status": "valid",
                    "expires_at": expires_at,
                    "remaining_minutes": int(remaining.total_seconds() / 60),
                    "is_expired": self.is_token_expired()
                }
            else:
                return {
                    "status": "expired",
                    "expires_at": expires_at,
                    "has_refresh_token": bool(self.tokens.get('refresh_token'))
                }
        
        return {"status": "unknown", "message": "有効期限情報が見つかりません"}
    
    def interactive_setup(self):
        """対話式セットアップ"""
        print("=== Zoho Analytics Token Manager セットアップ ===\n")
        
        # 既存の設定確認
        if self.config.get('client_id'):
            print("既存の設定:")
            print(f"Client ID: {self.config['client_id']}")
            print(f"Org ID: {self.config['org_id']}")
            
            update = input("\n設定を更新しますか？ (y/N): ")
            if update.lower() != 'y':
                return
        
        # 認証情報入力
        client_id = input("Client ID: ").strip()
        client_secret = input("Client Secret: ").strip()
        org_id = input("Organization ID: ").strip()
        
        if not all([client_id, client_secret, org_id]):
            print("すべての項目を入力してください。")
            return
        
        self.setup_credentials(client_id, client_secret, org_id)
        
        # 初回認証
        auth_url = self.generate_auth_url()
        print(f"\n以下のURLにアクセスして認証を行ってください:")
        print(auth_url)
        print("\n認証後、リダイレクトURLのcodeパラメータの値を入力してください")
        
        code = input("Authorization Code: ").strip()
        if code:
            try:
                self.exchange_code_for_tokens(code)
                print("\nセットアップが完了しました！")
            except Exception as e:
                print(f"エラー: {e}")
        else:
            print("認証コードが入力されませんでした。")

def main():
    """メイン関数"""
    import sys
    
    token_manager = ZohoTokenManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "setup":
            token_manager.interactive_setup()
        elif command == "status":
            status = token_manager.get_token_status()
            print("トークン状態:")
            print(json.dumps(status, indent=2, ensure_ascii=False))
        elif command == "refresh":
            try:
                token_manager.refresh_access_token()
            except Exception as e:
                print(f"エラー: {e}")
        elif command == "token":
            try:
                token = token_manager.get_valid_access_token()
                print(f"有効なアクセストークン: {token}")
            except Exception as e:
                print(f"エラー: {e}")
        else:
            print("使用方法: python token_manager.py [setup|status|refresh|token]")
    else:
        token_manager.interactive_setup()

if __name__ == "__main__":
    main()