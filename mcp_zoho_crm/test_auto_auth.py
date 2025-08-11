#!/usr/bin/env python3
"""
自動再認証機能のテストスクリプト
"""

import asyncio
import sys
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from zoho_crm_mcp_server import ZohoCRMClient


async def test_auto_authentication():
    """自動認証機能のテスト"""
    print("=== Zoho CRM 自動認証機能テスト ===\n")
    
    # 無効なリフレッシュトークンでクライアントを初期化
    client = ZohoCRMClient(
        client_id="1000.YN0LA88XQRCDTARO3FO5PWCOEY2IFZ",
        client_secret="25549573ace167da7319c6b561a8ea477ca235e0ef",
        refresh_token="invalid_token_for_test"  # 無効なトークン
    )
    
    try:
        print("1. 既存のトークンファイルを読み込み...")
        client.load_tokens_from_file()
        print(f"   リフレッシュトークン: {client.refresh_token[:20] if client.refresh_token else 'なし'}...")
        print()
        
        print("2. APIへのアクセスを試行...")
        modules = await client.get_modules()
        print(f"✅ {len(modules)}個のモジュールを取得成功")
        
        # 最初の5つのモジュール名を表示
        for i, module in enumerate(modules[:5]):
            print(f"   - {module.get('module_name', 'N/A')} ({module.get('api_name', 'N/A')})")
        if len(modules) > 5:
            print(f"   ... 他 {len(modules) - 5}個")
        print()
        
        print("3. トークン情報の確認...")
        print(f"   アクセストークン: {client.access_token[:30] if client.access_token else 'なし'}...")
        print(f"   リフレッシュトークン: {client.refresh_token[:30] if client.refresh_token else 'なし'}...")
        print(f"   有効期限: {client.token_expires_at}")
        print()
        
        print("✅ 自動認証機能が正常に動作しています！")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        print("\n⚠️ 注意: 初回実行時や、リフレッシュトークンが期限切れの場合は")
        print("   ブラウザが開いて手動認証が必要です。")
        import traceback
        traceback.print_exc()


async def test_token_refresh():
    """トークンリフレッシュのテスト"""
    print("\n=== トークンリフレッシュテスト ===")
    
    client = ZohoCRMClient(
        client_id="1000.YN0LA88XQRCDTARO3FO5PWCOEY2IFZ",
        client_secret="25549573ace167da7319c6b561a8ea477ca235e0ef"
    )
    
    # 既存のトークンを読み込み
    client.load_tokens_from_file()
    
    if client.refresh_token:
        try:
            print("リフレッシュトークンを使用してアクセストークンを更新...")
            await client.refresh_access_token()
            print("✅ トークンリフレッシュ成功")
            print(f"   新しいアクセストークン: {client.access_token[:30]}...")
        except Exception as e:
            print(f"❌ トークンリフレッシュ失敗: {e}")
    else:
        print("⚠️ リフレッシュトークンがありません")


if __name__ == "__main__":
    # 基本テスト
    asyncio.run(test_auto_authentication())
    
    # トークンリフレッシュテスト
    asyncio.run(test_token_refresh())