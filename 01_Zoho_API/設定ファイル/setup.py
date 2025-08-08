#!/usr/bin/env python3
"""
Zoho Analytics セットアップスクリプト
初期設定とトークン管理のためのユーティリティ
"""

import json
from pathlib import Path
from token_manager import ZohoTokenManager

def create_initial_config():
    """初期設定ファイルを作成"""
    config = {
        "client_id": "1000.YN0LA88XQRCDTARO3FO5PWCOEY2IFZ",
        "client_secret": "25549573ace167da7319c6b561a8ea477ca235e0ef",
        "org_id": "772043921",
        "redirect_uri": "http://localhost:8080/callback"
    }
    
    config_file = Path("zoho_config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"設定ファイル {config_file} を作成しました。")
    return config

def setup_tokens():
    """リフレッシュトークンを使用してトークンを設定"""
    # 既存のリフレッシュトークンがある場合は使用
    refresh_token = "1000.8177ba2f0705562d6bb22b12175cf327.7d32cf158319da563ce34b11099ab13b"
    
    token_data = {
        "access_token": "1000.f968cb6cf8df9cd3d4a7a313f21614d7.457e07fbee4330d7b112223db005541e",
        "refresh_token": refresh_token,
        "api_domain": "https://www.zohoapis.com",
        "token_type": "Bearer",
        "expires_in": 3600,
        "expires_at": "2025-07-26T01:16:51.000000",
        "created_at": "2025-07-26T00:16:51.000000"
    }
    
    token_file = Path("zoho_tokens.json")
    with open(token_file, 'w', encoding='utf-8') as f:
        json.dump(token_data, f, indent=2, ensure_ascii=False)
    
    print(f"トークンファイル {token_file} を作成しました。")
    return token_data

def main():
    """メイン関数"""
    print("=== Zoho Analytics セットアップ ===\n")
    
    # 設定ファイル作成
    print("1. 設定ファイルを作成中...")
    create_initial_config()
    
    # トークンファイル作成
    print("2. トークンファイルを作成中...")
    setup_tokens()
    
    # トークンマネージャーのテスト
    print("3. トークンマネージャーをテスト中...")
    try:
        token_manager = ZohoTokenManager()
        status = token_manager.get_token_status()
        print(f"トークン状態: {status['status']}")
        
        if status['status'] == 'valid' or status['status'] == 'expired':
            # リフレッシュトークンでアクセストークンを更新
            print("4. アクセストークンを更新中...")
            token_manager.refresh_access_token()
            print("アクセストークンが正常に更新されました。")
        
    except Exception as e:
        print(f"エラー: {e}")
        return
    
    print("\n=== セットアップ完了 ===")
    print("以下のコマンドでSQL Helperを実行できます:")
    print("python zoho_analytics_helper.py")
    print("\nトークン管理コマンド:")
    print("python token_manager.py status  # トークン状態確認")
    print("python token_manager.py refresh # 手動更新")

if __name__ == "__main__":
    main()