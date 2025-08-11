#!/usr/bin/env python3
"""
N8N MCP サーバーのテストスクリプト
"""

import asyncio
import json
import sys
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from n8n_mcp_server import N8NClient


async def test_n8n_connection():
    """N8N API接続テスト"""
    print("=== N8N MCP Server接続テスト ===\n")
    
    # N8Nクライアントを初期化
    client = N8NClient(
        api_url="https://cts-automation.onrender.com",
        api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    )
    
    try:
        # 1. ワークフロー一覧を取得
        print("1. ワークフロー一覧を取得...")
        workflows = await client.get_workflows()
        print(f"✅ {len(workflows)}個のワークフローを取得")
        
        # アクティブなワークフローを表示
        active_workflows = [w for w in workflows if w.get('active')]
        print(f"   アクティブ: {len(active_workflows)}個")
        
        for i, workflow in enumerate(workflows[:3]):
            status = "🟢" if workflow.get('active') else "🔴"
            print(f"   {status} {workflow.get('name')} (ID: {workflow.get('id')})")
        
        if len(workflows) > 3:
            print(f"   ... 他 {len(workflows) - 3}個")
        print()
        
        # 2. 特定のワークフロー詳細を取得
        if workflows:
            first_workflow_id = workflows[0]['id']
            print(f"2. ワークフロー詳細を取得... (ID: {first_workflow_id})")
            workflow_detail = await client.get_workflow(first_workflow_id)
            print(f"✅ ワークフロー詳細取得成功")
            print(f"   名前: {workflow_detail.get('name')}")
            print(f"   ノード数: {len(workflow_detail.get('nodes', []))}")
            print(f"   アクティブ: {workflow_detail.get('active')}")
            print()
        
        # 3. 実行履歴を取得
        print("3. 実行履歴を取得...")
        executions = await client.get_executions(limit=5)
        print(f"✅ {len(executions)}件の実行履歴を取得")
        
        for execution in executions[:3]:
            status_emoji = "✅" if execution.get('finished') else "⏳"
            workflow_name = execution.get('workflowData', {}).get('name', 'Unknown')
            print(f"   {status_emoji} {workflow_name} ({execution.get('id')})")
        print()
        
        # 4. WebhookURL生成テスト
        if workflows:
            workflow_id = workflows[0]['id']
            webhook_path = "test-webhook"
            print("4. WebhookURL生成...")
            webhook_url = await client.get_webhook_url(workflow_id, webhook_path)
            print(f"✅ WebhookURL: {webhook_url}")
            print()
        
        print("✅ すべてのテストが成功しました！")
        print("N8N MCPサーバーは正常に動作しています。")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_n8n_connection())