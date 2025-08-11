#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
n8n MCPサーバー
Model Context Protocolを使用してn8nワークフローを管理
"""

import json
import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

# MCP関連のインポート
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolRequest,
        CallToolResult,
        ListToolsRequest,
        ListToolsResult,
        Tool,
    )
except ImportError:
    print("MCPライブラリがインストールされていません。")
    print("インストール方法: pip install mcp")
    exit(1)

# n8n統合クラスをインポート
from create_workflow_via_api import N8nWorkflowCreator

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class N8nMCPServer:
    def __init__(self, base_url: str, api_key: str):
        """
        n8n MCPサーバーの初期化
        
        Args:
            base_url (str): n8nインスタンスのベースURL
            api_key (str): n8nのAPIキー
        """
        self.base_url = base_url
        self.api_key = api_key
        self.workflow_creator = N8nWorkflowCreator(base_url, api_key)
        
        # MCPサーバーを初期化
        self.server = Server("n8n-workflow-manager")
        
        # ツールを登録
        self.register_tools()
    
    def register_tools(self):
        """MCPツールを登録"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """利用可能なツール一覧を返す"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="list_workflows",
                        description="n8nのワークフロー一覧を取得",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    ),
                    Tool(
                        name="create_workflow",
                        description="新しいn8nワークフローを作成",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "ワークフロー名"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "ワークフローの説明"
                                },
                                "template": {
                                    "type": "string",
                                    "description": "使用するテンプレート（zoho-deals, zoho-products, zoho-create-deal）"
                                }
                            },
                            "required": ["name", "template"]
                        }
                    ),
                    Tool(
                        name="activate_workflow",
                        description="ワークフローをアクティブ化",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "workflow_id": {
                                    "type": "string",
                                    "description": "ワークフローID"
                                }
                            },
                            "required": ["workflow_id"]
                        }
                    ),
                    Tool(
                        name="test_webhook",
                        description="Webhookエンドポイントをテスト",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "webhook_path": {
                                    "type": "string",
                                    "description": "Webhookパス"
                                }
                            },
                            "required": ["webhook_path"]
                        }
                    ),
                    Tool(
                        name="get_workflow_status",
                        description="ワークフローの状態を取得",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "workflow_id": {
                                    "type": "string",
                                    "description": "ワークフローID"
                                }
                            },
                            "required": ["workflow_id"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """ツールを実行"""
            
            try:
                if name == "list_workflows":
                    return await self.list_workflows()
                elif name == "create_workflow":
                    return await self.create_workflow(arguments)
                elif name == "activate_workflow":
                    return await self.activate_workflow(arguments)
                elif name == "test_webhook":
                    return await self.test_webhook(arguments)
                elif name == "get_workflow_status":
                    return await self.get_workflow_status(arguments)
                else:
                    return CallToolResult(
                        content=[
                            {
                                "type": "text",
                                "text": f"未知のツール: {name}"
                            }
                        ]
                    )
            except Exception as e:
                logger.error(f"ツール実行エラー: {e}")
                return CallToolResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"エラーが発生しました: {str(e)}"
                        }
                    ]
                )
    
    async def list_workflows(self) -> CallToolResult:
        """ワークフロー一覧を取得"""
        try:
            workflows_data = self.workflow_creator.get_workflows()
            workflows = workflows_data.get('data', workflows_data) if isinstance(workflows_data, dict) else workflows_data
            
            if isinstance(workflows, list):
                workflow_list = []
                for workflow in workflows:
                    workflow_list.append({
                        "id": workflow.get('id'),
                        "name": workflow.get('name'),
                        "active": workflow.get('active', False),
                        "description": workflow.get('description', '')
                    })
                
                return CallToolResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"ワークフロー一覧 ({len(workflow_list)}件):\n" + 
                                   "\n".join([f"- {w['name']} (ID: {w['id']}, アクティブ: {w['active']})" 
                                            for w in workflow_list])
                        }
                    ]
                )
            else:
                return CallToolResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"ワークフローデータ: {workflows}"
                        }
                    ]
                )
        except Exception as e:
            return CallToolResult(
                content=[
                    {
                        "type": "text",
                        "text": f"ワークフロー一覧取得エラー: {str(e)}"
                    }
                ]
            )
    
    async def create_workflow(self, arguments: Dict[str, Any]) -> CallToolResult:
        """ワークフローを作成"""
        try:
            name = arguments.get('name')
            description = arguments.get('description', '')
            template = arguments.get('template')
            
            # テンプレートに基づいてワークフローデータを生成
            workflow_data = self.generate_workflow_from_template(name, description, template)
            
            if not workflow_data:
                return CallToolResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"無効なテンプレート: {template}"
                        }
                    ]
                )
            
            # 既存のワークフローをチェック
            existing_workflow = self.workflow_creator.get_workflow_by_name(name)
            
            if existing_workflow:
                # 更新
                result = self.workflow_creator.update_workflow(existing_workflow['id'], workflow_data)
                if "error" not in result:
                    # アクティブ化
                    activate_result = self.workflow_creator.activate_workflow(existing_workflow['id'])
                    if "error" not in activate_result:
                        return CallToolResult(
                            content=[
                                {
                                    "type": "text",
                                    "text": f"✅ ワークフロー更新完了: {name} (ID: {existing_workflow['id']})"
                                }
                            ]
                        )
                    else:
                        return CallToolResult(
                            content=[
                                {
                                    "type": "text",
                                    "text": f"❌ アクティブ化エラー: {activate_result['error']}"
                                }
                            ]
                        )
                else:
                    return CallToolResult(
                        content=[
                            {
                                "type": "text",
                                "text": f"❌ 更新エラー: {result['error']}"
                            }
                        ]
                    )
            else:
                # 新規作成
                result = self.workflow_creator.create_workflow(workflow_data)
                if "error" not in result:
                    workflow_id = result.get('id')
                    # アクティブ化
                    activate_result = self.workflow_creator.activate_workflow(workflow_id)
                    if "error" not in activate_result:
                        return CallToolResult(
                            content=[
                                {
                                    "type": "text",
                                    "text": f"✅ ワークフロー作成完了: {name} (ID: {workflow_id})"
                                }
                            ]
                        )
                    else:
                        return CallToolResult(
                            content=[
                                {
                                    "type": "text",
                                    "text": f"❌ アクティブ化エラー: {activate_result['error']}"
                                }
                            ]
                        )
                else:
                    return CallToolResult(
                        content=[
                            {
                                "type": "text",
                                "text": f"❌ 作成エラー: {result['error']}"
                            }
                        ]
                    )
        except Exception as e:
            return CallToolResult(
                content=[
                    {
                        "type": "text",
                        "text": f"ワークフロー作成エラー: {str(e)}"
                    }
                ]
            )
    
    def generate_workflow_from_template(self, name: str, description: str, template: str) -> Optional[Dict]:
        """テンプレートからワークフローデータを生成"""
        
        if template == "zoho-deals":
            return {
                "name": name,
                "description": description,
                "active": True,
                "nodes": [
                    {
                        "id": "webhook-trigger",
                        "name": "Webhook Trigger",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [240, 300],
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "zoho-deals",
                            "responseMode": "responseNode"
                        }
                    },
                    {
                        "id": "respond-success",
                        "name": "Success Response",
                        "type": "n8n-nodes-base.respondToWebhook",
                        "typeVersion": 1,
                        "position": [460, 300],
                        "parameters": {
                            "responseBody": "={{ { 'success': true, 'message': 'ZohoCRM deals workflow', 'timestamp': $now.toISOString() } }}",
                            "responseCode": 200
                        }
                    }
                ],
                "connections": {
                    "Webhook Trigger": {
                        "main": [
                            [
                                {
                                    "node": "Success Response",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                }
            }
        elif template == "zoho-products":
            return {
                "name": name,
                "description": description,
                "active": True,
                "nodes": [
                    {
                        "id": "webhook-trigger",
                        "name": "Webhook Trigger",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [240, 300],
                        "parameters": {
                            "httpMethod": "POST",
                            "path": "zoho-products",
                            "responseMode": "responseNode"
                        }
                    },
                    {
                        "id": "respond-success",
                        "name": "Success Response",
                        "type": "n8n-nodes-base.respondToWebhook",
                        "typeVersion": 1,
                        "position": [460, 300],
                        "parameters": {
                            "responseBody": "={{ { 'success': true, 'message': 'ZohoCRM products workflow', 'timestamp': $now.toISOString() } }}",
                            "responseCode": 200
                        }
                    }
                ],
                "connections": {
                    "Webhook Trigger": {
                        "main": [
                            [
                                {
                                    "node": "Success Response",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                }
            }
        else:
            return None
    
    async def activate_workflow(self, arguments: Dict[str, Any]) -> CallToolResult:
        """ワークフローをアクティブ化"""
        try:
            workflow_id = arguments.get('workflow_id')
            result = self.workflow_creator.activate_workflow(workflow_id)
            
            if "error" not in result:
                return CallToolResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"✅ ワークフローアクティブ化完了: {workflow_id}"
                        }
                    ]
                )
            else:
                return CallToolResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"❌ アクティブ化エラー: {result['error']}"
                        }
                    ]
                )
        except Exception as e:
            return CallToolResult(
                content=[
                    {
                        "type": "text",
                        "text": f"アクティブ化エラー: {str(e)}"
                    }
                ]
            )
    
    async def test_webhook(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Webhookをテスト"""
        try:
            webhook_path = arguments.get('webhook_path')
            url = f"{self.base_url}/webhook/{webhook_path}"
            
            import requests
            response = requests.post(url, json={"test": True}, timeout=10)
            
            return CallToolResult(
                content=[
                    {
                        "type": "text",
                        "text": f"Webhookテスト結果: {webhook_path} - HTTP {response.status_code}"
                    }
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[
                    {
                        "type": "text",
                        "text": f"Webhookテストエラー: {str(e)}"
                    }
                ]
            )
    
    async def get_workflow_status(self, arguments: Dict[str, Any]) -> CallToolResult:
        """ワークフローの状態を取得"""
        try:
            workflow_id = arguments.get('workflow_id')
            workflow = self.workflow_creator.get_workflow_by_name(workflow_id)
            
            if workflow:
                return CallToolResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"ワークフロー状態: {workflow.get('name')} - アクティブ: {workflow.get('active', False)}"
                        }
                    ]
                )
            else:
                return CallToolResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"ワークフローが見つかりません: {workflow_id}"
                        }
                    ]
                )
        except Exception as e:
            return CallToolResult(
                content=[
                    {
                        "type": "text",
                        "text": f"状態取得エラー: {str(e)}"
                    }
                ]
            )

async def main():
    """メイン実行関数"""
    
    # n8n設定
    N8N_BASE_URL = "https://cts-automation.onrender.com"
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDdhZjlkZC0xOTZmLTQ3NTMtOGUzMS1iOTVjMjE0ZDllZDAiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU0Njg4NTIxLCJleHAiOjE3NTcyNTcyMDB9.KmgJp75KaTcrXmnxCb1bNnRmHG3Jex7dgDjLPpRk0EQ"
    
    # MCPサーバーを初期化
    mcp_server = N8nMCPServer(N8N_BASE_URL, N8N_API_KEY)
    
    # MCPサーバーを起動
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="n8n-workflow-manager",
                server_version="1.0.0",
                capabilities=mcp_server.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main()) 