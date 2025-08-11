#!/usr/bin/env python3
"""
N8N MCP Server for Claude Desktop
N8N ワークフロー管理・実行システム
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class N8NClient:
    """N8N APIクライアント"""
    
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        
    async def make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        """API リクエストを実行"""
        url = f"{self.api_url}{endpoint}"
        headers = {
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, params=params, json=data) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    return json.loads(response_text) if response_text else {}
                elif response.status == 201:
                    return json.loads(response_text) if response_text else {}
                elif response.status == 204:
                    return {"success": True}
                else:
                    raise Exception(f"N8N API エラー: {response.status} - {response_text}")
    
    async def get_workflows(self, active: Optional[bool] = None) -> List[Dict]:
        """ワークフロー一覧を取得"""
        params = {}
        if active is not None:
            params["active"] = str(active).lower()
        
        result = await self.make_request("GET", "/api/v1/workflows", params=params)
        return result.get("data", [])
    
    async def get_workflow(self, workflow_id: str) -> Dict:
        """単一ワークフローの詳細を取得"""
        result = await self.make_request("GET", f"/api/v1/workflows/{workflow_id}")
        return result.get("data", {})
    
    async def create_workflow(self, workflow_data: Dict) -> Dict:
        """新規ワークフローを作成"""
        result = await self.make_request("POST", "/api/v1/workflows", data=workflow_data)
        return result.get("data", {})
    
    async def update_workflow(self, workflow_id: str, workflow_data: Dict) -> Dict:
        """ワークフローを更新"""
        result = await self.make_request("PUT", f"/api/v1/workflows/{workflow_id}", data=workflow_data)
        return result.get("data", {})
    
    async def delete_workflow(self, workflow_id: str) -> Dict:
        """ワークフローを削除"""
        result = await self.make_request("DELETE", f"/api/v1/workflows/{workflow_id}")
        return result
    
    async def activate_workflow(self, workflow_id: str) -> Dict:
        """ワークフローをアクティブ化"""
        result = await self.make_request("POST", f"/api/v1/workflows/{workflow_id}/activate")
        return result.get("data", {})
    
    async def deactivate_workflow(self, workflow_id: str) -> Dict:
        """ワークフローを非アクティブ化"""
        result = await self.make_request("POST", f"/api/v1/workflows/{workflow_id}/deactivate")
        return result.get("data", {})
    
    async def execute_workflow(self, workflow_id: str, input_data: Optional[Dict] = None) -> Dict:
        """ワークフローを手動実行"""
        data = input_data or {}
        result = await self.make_request("POST", f"/api/v1/workflows/{workflow_id}/execute", data=data)
        return result.get("data", {})
    
    async def get_executions(self, workflow_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """実行履歴を取得"""
        params = {"limit": limit}
        if workflow_id:
            params["workflowId"] = workflow_id
        
        result = await self.make_request("GET", "/api/v1/executions", params=params)
        return result.get("data", [])
    
    async def get_execution(self, execution_id: str) -> Dict:
        """単一実行の詳細を取得"""
        result = await self.make_request("GET", f"/api/v1/executions/{execution_id}")
        return result.get("data", {})
    
    async def get_credentials(self) -> List[Dict]:
        """認証情報一覧を取得"""
        result = await self.make_request("GET", "/api/v1/credentials")
        return result.get("data", [])
    
    async def get_webhook_url(self, workflow_id: str, webhook_path: str) -> str:
        """WebhookURLを生成"""
        return f"{self.api_url}/webhook/{webhook_path}"


class N8NMCPServer:
    """N8N MCP Server"""
    
    def __init__(self):
        self.server = Server("n8n-mcp")
        self.client = None
        self.setup_handlers()
    
    def load_config(self) -> Dict:
        """設定を読み込み"""
        config = {
            "api_url": os.getenv("N8N_API_URL", "https://cts-automation.onrender.com"),
            "api_key": os.getenv("N8N_API_KEY")
        }
        
        if not config["api_key"]:
            raise Exception("N8N_API_KEY環境変数が設定されていません")
        
        return config
    
    def setup_handlers(self):
        """ハンドラーをセットアップ"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """利用可能なツール一覧を返す"""
            return [
                Tool(
                    name="list_workflows",
                    description="ワークフロー一覧を取得",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "active": {
                                "type": "boolean",
                                "description": "アクティブなワークフローのみを取得するか"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_workflow",
                    description="ワークフローの詳細を取得",
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
                    name="create_workflow",
                    description="新規ワークフローを作成",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "ワークフロー名"
                            },
                            "active": {
                                "type": "boolean",
                                "description": "作成時にアクティブにするか",
                                "default": False
                            },
                            "nodes": {
                                "type": "array",
                                "description": "ノード定義"
                            },
                            "connections": {
                                "type": "object",
                                "description": "ノード間の接続定義"
                            }
                        },
                        "required": ["name"]
                    }
                ),
                Tool(
                    name="update_workflow",
                    description="ワークフローを更新",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow_id": {
                                "type": "string",
                                "description": "ワークフローID"
                            },
                            "name": {
                                "type": "string",
                                "description": "ワークフロー名"
                            },
                            "active": {
                                "type": "boolean",
                                "description": "アクティブ状態"
                            },
                            "nodes": {
                                "type": "array",
                                "description": "ノード定義"
                            },
                            "connections": {
                                "type": "object",
                                "description": "ノード間の接続定義"
                            }
                        },
                        "required": ["workflow_id"]
                    }
                ),
                Tool(
                    name="delete_workflow",
                    description="ワークフローを削除",
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
                    name="deactivate_workflow",
                    description="ワークフローを非アクティブ化",
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
                    name="execute_workflow",
                    description="ワークフローを手動実行",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow_id": {
                                "type": "string",
                                "description": "ワークフローID"
                            },
                            "input_data": {
                                "type": "object",
                                "description": "実行時の入力データ"
                            }
                        },
                        "required": ["workflow_id"]
                    }
                ),
                Tool(
                    name="get_executions",
                    description="実行履歴を取得",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow_id": {
                                "type": "string",
                                "description": "特定ワークフローの実行履歴"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "取得件数（デフォルト: 100）",
                                "default": 100
                            }
                        }
                    }
                ),
                Tool(
                    name="get_execution",
                    description="実行結果の詳細を取得",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "execution_id": {
                                "type": "string",
                                "description": "実行ID"
                            }
                        },
                        "required": ["execution_id"]
                    }
                ),
                Tool(
                    name="get_webhook_url",
                    description="WebhookURLを取得",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow_id": {
                                "type": "string",
                                "description": "ワークフローID"
                            },
                            "webhook_path": {
                                "type": "string",
                                "description": "Webhookパス"
                            }
                        },
                        "required": ["workflow_id", "webhook_path"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> list:
            """ツールを実行"""
            
            if not self.client:
                config = self.load_config()
                self.client = N8NClient(
                    config["api_url"],
                    config["api_key"]
                )
            
            try:
                if name == "list_workflows":
                    workflows = await self.client.get_workflows(arguments.get("active"))
                    return [TextContent(
                        type="text",
                        text=json.dumps(workflows, ensure_ascii=False, indent=2)
                    )]
                
                elif name == "get_workflow":
                    workflow = await self.client.get_workflow(arguments["workflow_id"])
                    return [TextContent(
                        type="text",
                        text=json.dumps(workflow, ensure_ascii=False, indent=2)
                    )]
                
                elif name == "create_workflow":
                    workflow_data = {
                        "name": arguments["name"],
                        "active": arguments.get("active", False),
                        "nodes": arguments.get("nodes", []),
                        "connections": arguments.get("connections", {}),
                        "settings": {"executionOrder": "v1"}
                    }
                    result = await self.client.create_workflow(workflow_data)
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2)
                    )]
                
                elif name == "update_workflow":
                    workflow_data = {}
                    if "name" in arguments:
                        workflow_data["name"] = arguments["name"]
                    if "active" in arguments:
                        workflow_data["active"] = arguments["active"]
                    if "nodes" in arguments:
                        workflow_data["nodes"] = arguments["nodes"]
                    if "connections" in arguments:
                        workflow_data["connections"] = arguments["connections"]
                    
                    result = await self.client.update_workflow(arguments["workflow_id"], workflow_data)
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2)
                    )]
                
                elif name == "delete_workflow":
                    result = await self.client.delete_workflow(arguments["workflow_id"])
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2)
                    )]
                
                elif name == "activate_workflow":
                    result = await self.client.activate_workflow(arguments["workflow_id"])
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2)
                    )]
                
                elif name == "deactivate_workflow":
                    result = await self.client.deactivate_workflow(arguments["workflow_id"])
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2)
                    )]
                
                elif name == "execute_workflow":
                    result = await self.client.execute_workflow(
                        arguments["workflow_id"],
                        arguments.get("input_data")
                    )
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2)
                    )]
                
                elif name == "get_executions":
                    executions = await self.client.get_executions(
                        arguments.get("workflow_id"),
                        arguments.get("limit", 100)
                    )
                    return [TextContent(
                        type="text",
                        text=json.dumps(executions, ensure_ascii=False, indent=2)
                    )]
                
                elif name == "get_execution":
                    execution = await self.client.get_execution(arguments["execution_id"])
                    return [TextContent(
                        type="text",
                        text=json.dumps(execution, ensure_ascii=False, indent=2)
                    )]
                
                elif name == "get_webhook_url":
                    url = await self.client.get_webhook_url(
                        arguments["workflow_id"],
                        arguments["webhook_path"]
                    )
                    return [TextContent(
                        type="text",
                        text=json.dumps({"webhook_url": url}, ensure_ascii=False, indent=2)
                    )]
                
                else:
                    return [TextContent(
                        type="text",
                        text=f"エラー: 不明なツール '{name}'"
                    )]
            
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"エラー: {str(e)}"
                )]
    
    async def run(self):
        """サーバーを実行"""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, 
                write_stream, 
                InitializationOptions(
                    server_name="n8n-mcp",
                    server_version="1.0.0",
                    capabilities={}
                )
            )


async def main():
    """メインエントリーポイント"""
    server = N8NMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())