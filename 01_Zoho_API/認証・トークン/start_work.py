#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
作業開始時の自動トークン更新・API接続確認スクリプト
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """コマンドを実行して結果を表示"""
    print(f"\n🔄 {description}")
    print(f"実行コマンド: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print(f"✅ {description} - 成功")
            if result.stdout:
                print(f"出力: {result.stdout[:500]}...")
        else:
            print(f"❌ {description} - 失敗")
            if result.stderr:
                print(f"エラー: {result.stderr}")
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} - エラー: {e}")
        return False

def check_environment():
    """環境設定を確認"""
    print("=== 環境設定確認 ===")
    
    # 必要なディレクトリの存在確認
    required_dirs = [
        "01_Zoho_API/設定ファイル",
        "01_Zoho_API/認証・トークン",
        "01_Zoho_API/テスト・検証"
    ]
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path} - 存在")
        else:
            print(f"❌ {dir_path} - 存在しない")
            return False
    
    # 設定ファイルの存在確認
    config_file = Path("01_Zoho_API/設定ファイル/zoho_config.json")
    if config_file.exists():
        print(f"✅ 設定ファイル - 存在")
    else:
        print(f"❌ 設定ファイル - 存在しない")
        return False
    
    return True

def auto_refresh_tokens():
    """自動トークン更新を実行"""
    print("\n=== 自動トークン更新 ===")
    
    # 自動トークン管理システムを実行
    success = run_command(
        "python3 01_Zoho_API/認証・トークン/auto_token_manager.py",
        "自動トークン更新"
    )
    
    return success

def test_api_connection():
    """API接続テストを実行"""
    print("\n=== API接続テスト ===")
    
    # 環境変数を設定
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            env_content = f.read()
        
        for line in env_content.strip().split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
        
        print("✅ 環境変数を設定しました")
    else:
        print("❌ .envファイルが見つかりません")
        return False
    
    # API接続テストを実行
    success = run_command(
        "python3 01_Zoho_API/テスト・検証/test_actual_api_fixed.py",
        "API接続テスト"
    )
    
    return success

def show_next_steps():
    """次のステップを表示"""
    print("\n=== 次のステップ ===")
    print("✅ 自動トークン更新が完了しました")
    print("\n📋 利用可能なコマンド:")
    print("1. VERSANTレポート実行:")
    print("   cd 02_VERSANTコーチング/実行スクリプト/")
    print("   python3 execute_versant_basic.py")
    print("\n2. 商談レポート生成:")
    print("   cd 03_商談・粗利率/実行スクリプト/")
    print("   python3 generate_2025_report.py")
    print("\n3. API接続テスト:")
    print("   cd 01_Zoho_API/テスト・検証/")
    print("   python3 test_actual_api_fixed.py")
    print("\n4. トークン状態確認:")
    print("   cd 01_Zoho_API/認証・トークン/")
    print("   python3 auto_token_manager.py")

def main():
    """メイン実行関数"""
    print("=== Zoho Analytics 作業開始スクリプト ===")
    print("自動トークン更新とAPI接続確認を実行します")
    
    # 環境設定確認
    if not check_environment():
        print("\n❌ 環境設定に問題があります")
        print("必要なファイルとディレクトリを確認してください")
        return False
    
    # 自動トークン更新
    if not auto_refresh_tokens():
        print("\n❌ 自動トークン更新に失敗しました")
        print("設定ファイルとトークンファイルを確認してください")
        return False
    
    # API接続テスト
    if not test_api_connection():
        print("\n⚠️ API接続テストに失敗しました")
        print("ネットワーク接続とAPI設定を確認してください")
        # 警告として続行
    else:
        print("\n✅ API接続テストが成功しました")
    
    # 次のステップを表示
    show_next_steps()
    
    print("\n🎯 作業開始準備が完了しました！")
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ 作業開始スクリプトが正常に完了しました")
        else:
            print("\n❌ 作業開始スクリプトでエラーが発生しました")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによって中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 予期しないエラーが発生しました: {e}")
        sys.exit(1) 