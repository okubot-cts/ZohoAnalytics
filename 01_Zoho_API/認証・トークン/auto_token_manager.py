#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zoho Analytics API 自動トークン管理システム
作業開始時に自動的にアクセストークンを更新・管理
"""

import os
import json
import requests
import time
from datetime import datetime, timedelta
import logging
from pathlib import Path

class AutoTokenManager:
    def __init__(self, config_dir="01_Zoho_API/設定ファイル", token_dir="01_Zoho_API/認証・トークン"):
        """
        自動トークン管理システムの初期化
        
        Args:
            config_dir (str): 設定ファイルのディレクトリ
            token_dir (str): トークンファイルのディレクトリ
        """
        self.config_dir = Path(config_dir)
        self.token_dir = Path(token_dir)
        self.config_file = self.config_dir / "zoho_config.json"
        self.tokens_file = self.config_dir / "zoho_tokens.json"
        self.env_file = Path(".env")
        
        # ログ設定
        self.setup_logging()
        
        # 設定ファイルの存在確認
        if not self.config_file.exists():
            self.logger.error(f"設定ファイルが見つかりません: {self.config_file}")
            raise FileNotFoundError(f"設定ファイルが見つかりません: {self.config_file}")
    
    def setup_logging(self):
        """ログ設定"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "token_manager.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self):
        """設定ファイルを読み込み"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.logger.info("設定ファイルを読み込みました")
            return config
        except Exception as e:
            self.logger.error(f"設定ファイルの読み込みに失敗: {e}")
            raise
    
    def load_tokens(self):
        """トークンファイルを読み込み"""
        try:
            if self.tokens_file.exists():
                with open(self.tokens_file, 'r', encoding='utf-8') as f:
                    tokens = json.load(f)
                self.logger.info("トークンファイルを読み込みました")
                return tokens
            else:
                self.logger.warning("トークンファイルが見つかりません")
                return None
        except Exception as e:
            self.logger.error(f"トークンファイルの読み込みに失敗: {e}")
            return None
    
    def save_tokens(self, tokens):
        """トークンをファイルに保存"""
        try:
            # バックアップを作成
            if self.tokens_file.exists():
                backup_file = self.tokens_file.with_suffix('.json.backup')
                with open(self.tokens_file, 'r', encoding='utf-8') as f:
                    backup_data = f.read()
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(backup_data)
                self.logger.info(f"トークンファイルをバックアップしました: {backup_file}")
            
            # 新しいトークンを保存
            with open(self.tokens_file, 'w', encoding='utf-8') as f:
                json.dump(tokens, f, ensure_ascii=False, indent=2)
            
            # タイムスタンプ付きファイルも作成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            timestamp_file = self.token_dir / f"zoho_tokens_updated_{timestamp}.json"
            with open(timestamp_file, 'w', encoding='utf-8') as f:
                json.dump(tokens, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"トークンを保存しました: {self.tokens_file}")
            self.logger.info(f"タイムスタンプ付きファイルを作成: {timestamp_file}")
            
            return True
        except Exception as e:
            self.logger.error(f"トークンの保存に失敗: {e}")
            return False
    
    def is_token_expired(self, tokens):
        """トークンの有効期限をチェック"""
        if not tokens or 'access_token' not in tokens:
            return True
        
        # 有効期限の確認（デフォルト1時間）
        expires_in = tokens.get('expires_in', 3600)
        created_at = tokens.get('created_at')
        
        if not created_at:
            # 作成時刻がない場合は期限切れとみなす
            return True
        
        try:
            created_time = datetime.fromisoformat(created_at)
            expiry_time = created_time + timedelta(seconds=expires_in)
            
            # 5分のマージンを設ける
            margin = timedelta(minutes=5)
            is_expired = datetime.now() > (expiry_time - margin)
            
            if is_expired:
                self.logger.info("アクセストークンが期限切れまたは間もなく期限切れです")
            else:
                remaining = expiry_time - datetime.now()
                self.logger.info(f"アクセストークンは有効です（残り時間: {remaining}")
            
            return is_expired
        except Exception as e:
            self.logger.error(f"トークン有効期限の確認に失敗: {e}")
            return True
    
    def refresh_access_token(self, refresh_token, client_id, client_secret):
        """リフレッシュトークンを使用してアクセストークンを更新"""
        url = "https://accounts.zoho.com/oauth/v2/token"
        
        payload = {
            'refresh_token': refresh_token,
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'refresh_token'
        }
        
        try:
            self.logger.info("アクセストークンを更新中...")
            response = requests.post(url, data=payload, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            
            # 作成時刻を追加
            token_data['created_at'] = datetime.now().isoformat()
            token_data['refreshed_at'] = datetime.now().isoformat()
            
            self.logger.info("アクセストークンの更新が完了しました")
            return token_data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"トークン更新エラー: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"レスポンス: {e.response.text}")
            return None
    
    def update_environment_variables(self, tokens, config):
        """環境変数を更新"""
        try:
            if 'access_token' in tokens:
                access_token = tokens['access_token']
                
                # .envファイルに保存
                env_content = f"ZOHO_ANALYTICS_ACCESS_TOKEN={access_token}\n"
                
                if 'refresh_token' in tokens:
                    env_content += f"ZOHO_ANALYTICS_REFRESH_TOKEN={tokens['refresh_token']}\n"
                
                if config and 'org_id' in config:
                    env_content += f"ZOHO_ANALYTICS_WORKSPACE_ID={config['org_id']}\n"
                    env_content += f"ZOHO_ANALYTICS_ORG_ID={config['org_id']}\n"
                
                with open(self.env_file, 'w', encoding='utf-8') as f:
                    f.write(env_content)
                
                # 環境変数を設定
                os.environ['ZOHO_ANALYTICS_ACCESS_TOKEN'] = access_token
                if config and 'org_id' in config:
                    os.environ['ZOHO_ANALYTICS_WORKSPACE_ID'] = config['org_id']
                    os.environ['ZOHO_ANALYTICS_ORG_ID'] = config['org_id']
                
                self.logger.info("環境変数を更新しました")
                return True
            else:
                self.logger.error("アクセストークンが取得できませんでした")
                return False
        except Exception as e:
            self.logger.error(f"環境変数の更新に失敗: {e}")
            return False
    
    def auto_refresh(self):
        """自動トークン更新のメイン処理"""
        try:
            self.logger.info("=== 自動トークン更新開始 ===")
            
            # 設定ファイルを読み込み
            config = self.load_config()
            self.logger.info(f"クライアントID: {config.get('client_id', 'N/A')[:10]}...")
            self.logger.info(f"組織ID: {config.get('org_id', 'N/A')}")
            
            # 既存のトークンを読み込み
            tokens = self.load_tokens()
            if not tokens:
                self.logger.error("既存のトークンが見つかりません")
                return False
            
            self.logger.info(f"リフレッシュトークン: {tokens.get('refresh_token', 'N/A')[:10]}...")
            
            # トークンの有効期限をチェック
            if not self.is_token_expired(tokens):
                self.logger.info("アクセストークンは有効です。更新は不要です。")
                # 環境変数は更新しておく
                self.update_environment_variables(tokens, config)
                return True
            
            # リフレッシュトークンを取得
            refresh_token = tokens.get('refresh_token')
            if not refresh_token:
                self.logger.error("リフレッシュトークンが見つかりません")
                return False
            
            # クライアント情報を取得
            client_id = config.get('client_id')
            client_secret = config.get('client_secret')
            
            if not client_id or not client_secret:
                self.logger.error("クライアントIDまたはクライアントシークレットが見つかりません")
                return False
            
            # 新しいアクセストークンを取得
            new_tokens = self.refresh_access_token(refresh_token, client_id, client_secret)
            if not new_tokens:
                self.logger.error("アクセストークンの更新に失敗しました")
                return False
            
            # リフレッシュトークンを保持（新しいトークンに含まれていない場合）
            if 'refresh_token' not in new_tokens and 'refresh_token' in tokens:
                new_tokens['refresh_token'] = tokens['refresh_token']
            
            # トークンを保存
            if not self.save_tokens(new_tokens):
                self.logger.error("トークンの保存に失敗しました")
                return False
            
            # 環境変数を更新
            if not self.update_environment_variables(new_tokens, config):
                self.logger.error("環境変数の更新に失敗しました")
                return False
            
            self.logger.info("=== 自動トークン更新完了 ===")
            return True
            
        except Exception as e:
            self.logger.error(f"自動トークン更新でエラーが発生: {e}")
            return False
    
    def get_current_token(self):
        """現在の有効なアクセストークンを取得"""
        try:
            tokens = self.load_tokens()
            if tokens and 'access_token' in tokens and not self.is_token_expired(tokens):
                return tokens['access_token']
            else:
                # トークンが無効な場合は自動更新を試行
                if self.auto_refresh():
                    tokens = self.load_tokens()
                    return tokens.get('access_token') if tokens else None
                return None
        except Exception as e:
            self.logger.error(f"現在のトークン取得に失敗: {e}")
            return None
    
    def status(self):
        """トークンの状態を表示"""
        try:
            tokens = self.load_tokens()
            if not tokens:
                print("❌ トークンファイルが見つかりません")
                return False
            
            print("=== トークン状態 ===")
            print(f"アクセストークン: {'✅ 有効' if 'access_token' in tokens else '❌ なし'}")
            print(f"リフレッシュトークン: {'✅ 有効' if 'refresh_token' in tokens else '❌ なし'}")
            
            if 'access_token' in tokens:
                is_expired = self.is_token_expired(tokens)
                print(f"有効期限: {'❌ 期限切れ' if is_expired else '✅ 有効'}")
                
                if 'created_at' in tokens:
                    created_time = datetime.fromisoformat(tokens['created_at'])
                    print(f"作成時刻: {created_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return True
        except Exception as e:
            print(f"❌ 状態確認に失敗: {e}")
            return False

def main():
    """メイン実行関数"""
    print("=== Zoho Analytics API 自動トークン管理システム ===")
    
    try:
        # トークン管理システムを初期化
        manager = AutoTokenManager()
        
        # 自動更新を実行
        if manager.auto_refresh():
            print("✅ 自動トークン更新が完了しました")
            print("\n📋 次のステップ:")
            print("1. API接続テストを実行")
            print("2. VERSANTレポートを実行")
            print("3. 商談レポートを実行")
        else:
            print("❌ 自動トークン更新に失敗しました")
            print("設定ファイルとトークンファイルを確認してください")
        
        # 状態を表示
        print("\n=== 現在の状態 ===")
        manager.status()
        
    except Exception as e:
        print(f"❌ システムエラー: {e}")
        print("設定ファイルの存在を確認してください")

if __name__ == "__main__":
    main() 