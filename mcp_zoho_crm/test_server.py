#!/usr/bin/env python3
"""
Zoho CRM MCPサーバーの簡単なテストスクリプト
"""

import asyncio
import json
import sys
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from zoho_crm_mcp_server import ZohoCRMClient


async def test_connection():
    """接続テスト"""
    print("=== Zoho CRM MCP サーバー接続テスト ===\n")
    
    # 設定ファイルを読み込み
    config_path = project_root / "01_Zoho_API" / "認証・トークン" / "zoho_crm_tokens.json"
    
    if not config_path.exists():
        print(f"❌ 設定ファイルが見つかりません: {config_path}")
        return
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # クライアントの初期化
    client = ZohoCRMClient(
        client_id="1000.YN0LA88XQRCDTARO3FO5PWCOEY2IFZ",
        client_secret="25549573ace167da7319c6b561a8ea477ca235e0ef",
        refresh_token=config.get("refresh_token")
    )
    
    try:
        # トークンリフレッシュテスト
        print("1. トークンのリフレッシュ...")
        await client.refresh_access_token()
        print("✅ トークンリフレッシュ成功")
        print(f"   アクセストークン: {client.access_token[:30]}...")
        print()
        
        # モジュール一覧取得テスト
        print("2. 利用可能なモジュール一覧を取得...")
        modules = await client.get_modules()
        print(f"✅ {len(modules)}個のモジュールを取得")
        
        # 最初の5つのモジュール名を表示
        for i, module in enumerate(modules[:5]):
            print(f"   - {module.get('module_name', 'N/A')} ({module.get('api_name', 'N/A')})")
        if len(modules) > 5:
            print(f"   ... 他 {len(modules) - 5}個")
        print()
        
        # 商談（Deals）モジュールのテスト
        print("3. 商談（Deals）モジュールからレコードを取得...")
        deals_result = await client.get_records("Deals", {"per_page": 5, "fields": "Deal_Name,Amount,Stage,id"})
        deals = deals_result.get("data", [])
        print(f"✅ {len(deals)}件の商談を取得")
        
        for deal in deals[:3]:
            print(f"   - {deal.get('Deal_Name', 'N/A')} (金額: {deal.get('Amount', 'N/A')}, ステージ: {deal.get('Stage', 'N/A')})")
        print()
        
        print("✅ すべてのテストが成功しました！")
        print("MCPサーバーは正常に動作しています。")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_connection())