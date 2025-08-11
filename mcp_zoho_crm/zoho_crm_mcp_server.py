#!/usr/bin/env python3
"""
Zoho CRM MCP Server for Claude Desktop
全てのZoho CRMテーブルへのアクセスを提供
"""

import asyncio
import json
import os
import sys
import webbrowser
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode, parse_qs
import http.server
import socketserver
import threading
import time

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


class CallbackServer:
    """OAuth認証コールバック受信用サーバー"""
    
    def __init__(self, port=8080):
        self.port = port
        self.auth_code = None
        self.error = None
        self.server = None
        self.server_thread = None
    
    def start_server(self):
        """コールバックサーバーを開始"""
        handler = self.create_handler()
        self.server = socketserver.TCPServer(("", self.port), handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        print(f"コールバックサーバーを開始しました: http://localhost:{self.port}")
    
    def stop_server(self):
        """コールバックサーバーを停止"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.server_thread:
            self.server_thread.join()
    
    def create_handler(self):
        """リクエストハンドラーを作成"""
        callback_server = self
        
        class CallbackHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path.startswith('/callback'):
                    # クエリパラメータを解析
                    query_params = parse_qs(self.path.split('?', 1)[1] if '?' in self.path else '')
                    
                    if 'code' in query_params:
                        callback_server.auth_code = query_params['code'][0]
                        response = "✅ 認証が完了しました。このウィンドウを閉じてください。"
                        print("✅ 認証コードを受信しました")
                    elif 'error' in query_params:
                        callback_server.error = query_params['error'][0]
                        response = f"❌ 認証エラー: {callback_server.error}"
                        print(f"❌ 認証エラー: {callback_server.error}")
                    else:
                        response = "❌ 無効なコールバックです"
                    
                    # レスポンスを返す
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(f"""
                    <html>
                    <head><title>Zoho CRM認証</title></head>
                    <body>
                        <h2>Zoho CRM認証</h2>
                        <p>{response}</p>
                        <script>setTimeout(() => window.close(), 3000);</script>
                    </body>
                    </html>
                    """.encode('utf-8'))
                else:
                    self.send_error(404)
            
            def log_message(self, format, *args):
                # ログ出力を抑制
                pass
        
        return CallbackHandler


class ZohoCRMClient:
    """Zoho CRM APIクライアント"""
    
    def __init__(self, client_id: str, client_secret: str, refresh_token: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = None
        self.token_expires_at = None
        self.api_domain = "https://www.zohoapis.com"
        self.redirect_uri = "http://localhost:8080/callback"
        self.token_file_path = project_root / "01_Zoho_API" / "認証・トークン" / "zoho_crm_tokens.json"
        
    async def refresh_access_token(self):
        """アクセストークンをリフレッシュ（失敗時は自動再認証）"""
        if not self.refresh_token:
            print("リフレッシュトークンがありません。新規認証を開始します...")
            await self.perform_full_authentication()
            return True
            
        token_url = "https://accounts.zoho.com/oauth/v2/token"
        
        data = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.access_token = result.get("access_token")
                    # リフレッシュトークンが更新される場合があります
                    if result.get("refresh_token"):
                        self.refresh_token = result.get("refresh_token")
                    expires_in = result.get("expires_in", 3600)
                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                    
                    # 新しいトークンを保存
                    await self.save_tokens()
                    return True
                else:
                    error_text = await response.text()
                    print(f"リフレッシュトークンが無効になりました: {response.status} - {error_text}")
                    print("自動再認証を開始します...")
                    await self.perform_full_authentication()
                    return True
    
    async def perform_full_authentication(self):
        """完全な認証フローを実行（ブラウザを使用）"""
        print("\n=== Zoho CRM 自動再認証 ===")
        print("ブラウザが開きます。Zohoアカウントでログインして認証を完了してください。")
        
        # コールバックサーバーを開始
        callback_server = CallbackServer()
        callback_server.start_server()
        
        try:
            # 認証URLを生成
            auth_url = self.generate_auth_url()
            print(f"認証URL: {auth_url}")
            
            # ブラウザで認証URLを開く
            webbrowser.open(auth_url)
            
            # 認証コードの受信を待機
            print("認証完了を待機中...")
            max_wait_time = 300  # 5分間待機
            start_time = time.time()
            
            while callback_server.auth_code is None and callback_server.error is None:
                if time.time() - start_time > max_wait_time:
                    raise Exception("認証がタイムアウトしました")
                await asyncio.sleep(1)
            
            if callback_server.error:
                raise Exception(f"認証エラー: {callback_server.error}")
            
            if not callback_server.auth_code:
                raise Exception("認証コードを取得できませんでした")
            
            # 認証コードでトークンを取得
            await self.exchange_code_for_tokens(callback_server.auth_code)
            print("✅ 自動再認証が完了しました！")
            
        finally:
            callback_server.stop_server()
    
    def generate_auth_url(self):
        """認証URL生成"""
        scope = "ZohoCRM.modules.ALL,ZohoCRM.settings.modules.READ,ZohoCRM.settings.fields.READ"
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'scope': scope,
            'redirect_uri': self.redirect_uri,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        return f"https://accounts.zoho.com/oauth/v2/auth?{urlencode(params)}"
    
    async def exchange_code_for_tokens(self, auth_code: str):
        """認証コードをトークンに交換"""
        token_url = "https://accounts.zoho.com/oauth/v2/token"
        
        data = {
            'code': auth_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.access_token = result.get('access_token')
                    self.refresh_token = result.get('refresh_token')
                    expires_in = result.get('expires_in', 3600)
                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                    
                    # トークンを保存
                    await self.save_tokens()
                    return True
                else:
                    error_text = await response.text()
                    raise Exception(f"トークン取得エラー: {response.status} - {error_text}")
    
    async def save_tokens(self):
        """トークンをファイルに保存"""
        token_data = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_at': self.token_expires_at.isoformat() if self.token_expires_at else None,
            'scope': 'ZohoCRM.modules.ALL ZohoCRM.settings.modules.READ ZohoCRM.settings.fields.READ',
            'api_domain': self.api_domain,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'updated_at': datetime.now().isoformat()
        }
        
        # ディレクトリが存在しない場合は作成
        self.token_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # バックアップを作成
        if self.token_file_path.exists():
            backup_path = self.token_file_path.with_suffix('.json.backup')
            import shutil
            shutil.copy2(self.token_file_path, backup_path)
        
        # 新しいトークンを保存
        with open(self.token_file_path, 'w', encoding='utf-8') as f:
            json.dump(token_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ トークンを保存しました: {self.token_file_path}")
    
    def load_tokens_from_file(self):
        """ファイルからトークンを読み込み"""
        if not self.token_file_path.exists():
            return
        
        try:
            with open(self.token_file_path, 'r', encoding='utf-8') as f:
                token_data = json.load(f)
            
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            
            if token_data.get('expires_at'):
                self.token_expires_at = datetime.fromisoformat(token_data['expires_at'])
            
            print(f"✅ トークンを読み込みました: {self.token_file_path}")
            
        except Exception as e:
            print(f"⚠️ トークン読み込みエラー: {e}")
            # エラーの場合は既存の値を使用
    
    async def ensure_valid_token(self):
        """有効なトークンを確保"""
        if not self.access_token or not self.token_expires_at or datetime.now() >= self.token_expires_at:
            await self.refresh_access_token()
    
    async def make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        """API リクエストを実行"""
        await self.ensure_valid_token()
        
        url = f"{self.api_domain}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, params=params, json=data) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    return json.loads(response_text) if response_text else {}
                elif response.status == 204:
                    return {"success": True}
                else:
                    raise Exception(f"API エラー: {response.status} - {response_text}")
    
    async def get_modules(self) -> List[Dict]:
        """利用可能なモジュール一覧を取得"""
        result = await self.make_request("GET", "/crm/v6/settings/modules")
        return result.get("modules", [])
    
    async def get_fields(self, module_name: str) -> List[Dict]:
        """モジュールのフィールド情報を取得"""
        result = await self.make_request("GET", f"/crm/v6/settings/fields", params={"module": module_name})
        return result.get("fields", [])
    
    async def get_records(self, module_name: str, params: Optional[Dict] = None) -> Dict:
        """レコードを取得"""
        default_params = {
            "per_page": 200,
            "page": 1,
            "fields": "id"  # APIv6では必須パラメータ
        }
        if params:
            default_params.update(params)
        
        result = await self.make_request("GET", f"/crm/v6/{module_name}", params=default_params)
        return result
    
    async def search_records(self, module_name: str, criteria: str, params: Optional[Dict] = None) -> Dict:
        """レコードを検索"""
        search_params = {
            "criteria": criteria,
            "per_page": 200,
            "page": 1
        }
        if params:
            search_params.update(params)
        
        result = await self.make_request("GET", f"/crm/v6/{module_name}/search", params=search_params)
        return result
    
    async def get_record(self, module_name: str, record_id: str) -> Dict:
        """単一レコードを取得"""
        result = await self.make_request("GET", f"/crm/v6/{module_name}/{record_id}")
        return result.get("data", [{}])[0] if result.get("data") else {}
    
    async def create_record(self, module_name: str, data: Dict) -> Dict:
        """レコードを作成"""
        payload = {"data": [data]}
        result = await self.make_request("POST", f"/crm/v6/{module_name}", data=payload)
        return result
    
    async def update_record(self, module_name: str, record_id: str, data: Dict) -> Dict:
        """レコードを更新"""
        payload = {"data": [data]}
        result = await self.make_request("PUT", f"/crm/v6/{module_name}/{record_id}", data=payload)
        return result
    
    async def delete_record(self, module_name: str, record_id: str) -> Dict:
        """レコードを削除"""
        result = await self.make_request("DELETE", f"/crm/v6/{module_name}/{record_id}")
        return result
    
    async def get_related_records(self, module_name: str, record_id: str, related_module: str, params: Optional[Dict] = None) -> Dict:
        """関連レコードを取得"""
        result = await self.make_request("GET", f"/crm/v6/{module_name}/{record_id}/{related_module}", params=params)
        return result


class ZohoCRMMCPServer:
    """Zoho CRM MCP Server"""
    
    def __init__(self):
        self.server = Server("zoho-crm-mcp")
        self.client = None
        self.setup_handlers()
    
    def load_config(self) -> Dict:
        """設定ファイルを読み込み"""
        config_path = project_root / "01_Zoho_API" / "認証・トークン" / "zoho_crm_tokens.json"
        
        config = {}
        
        # ファイルが存在する場合は読み込み
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception as e:
                print(f"⚠️ 設定ファイル読み込みエラー: {e}")
        
        # 環境変数から認証情報を取得（優先）
        if os.getenv("ZOHO_CLIENT_ID"):
            config["client_id"] = os.getenv("ZOHO_CLIENT_ID")
        elif "client_id" not in config:
            config["client_id"] = "1000.YN0LA88XQRCDTARO3FO5PWCOEY2IFZ"
        
        if os.getenv("ZOHO_CLIENT_SECRET"):
            config["client_secret"] = os.getenv("ZOHO_CLIENT_SECRET")
        elif "client_secret" not in config:
            config["client_secret"] = "25549573ace167da7319c6b561a8ea477ca235e0ef"
        
        if os.getenv("ZOHO_REFRESH_TOKEN"):
            config["refresh_token"] = os.getenv("ZOHO_REFRESH_TOKEN")
        # refresh_tokenが無い場合でも、自動認証で取得するため例外を発生させない
        
        return config
    
    def setup_handlers(self):
        """ハンドラーをセットアップ"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """利用可能なツール一覧を返す"""
            return [
                Tool(
                    name="list_modules",
                    description="利用可能なZoho CRMモジュール一覧を取得",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_module_fields",
                    description="指定モジュールのフィールド情報を取得",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "module_name": {
                                "type": "string",
                                "description": "モジュール名（例: Leads, Contacts, Deals）"
                            }
                        },
                        "required": ["module_name"]
                    }
                ),
                Tool(
                    name="get_records",
                    description="指定モジュールのレコードを取得",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "module_name": {
                                "type": "string",
                                "description": "モジュール名"
                            },
                            "page": {
                                "type": "integer",
                                "description": "ページ番号（デフォルト: 1）",
                                "default": 1
                            },
                            "per_page": {
                                "type": "integer",
                                "description": "1ページあたりのレコード数（最大200）",
                                "default": 200
                            },
                            "fields": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "取得するフィールド名のリスト"
                            },
                            "sort_by": {
                                "type": "string",
                                "description": "ソートフィールド"
                            },
                            "sort_order": {
                                "type": "string",
                                "enum": ["asc", "desc"],
                                "description": "ソート順"
                            }
                        },
                        "required": ["module_name"]
                    }
                ),
                Tool(
                    name="search_records",
                    description="条件を指定してレコードを検索",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "module_name": {
                                "type": "string",
                                "description": "モジュール名"
                            },
                            "criteria": {
                                "type": "string",
                                "description": "検索条件（Zoho CRM検索構文）"
                            },
                            "page": {
                                "type": "integer",
                                "description": "ページ番号",
                                "default": 1
                            },
                            "per_page": {
                                "type": "integer",
                                "description": "1ページあたりのレコード数",
                                "default": 200
                            }
                        },
                        "required": ["module_name", "criteria"]
                    }
                ),
                Tool(
                    name="get_record",
                    description="単一レコードの詳細を取得",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "module_name": {
                                "type": "string",
                                "description": "モジュール名"
                            },
                            "record_id": {
                                "type": "string",
                                "description": "レコードID"
                            }
                        },
                        "required": ["module_name", "record_id"]
                    }
                ),
                Tool(
                    name="create_record",
                    description="新規レコードを作成",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "module_name": {
                                "type": "string",
                                "description": "モジュール名"
                            },
                            "data": {
                                "type": "object",
                                "description": "レコードデータ"
                            }
                        },
                        "required": ["module_name", "data"]
                    }
                ),
                Tool(
                    name="update_record",
                    description="既存レコードを更新",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "module_name": {
                                "type": "string",
                                "description": "モジュール名"
                            },
                            "record_id": {
                                "type": "string",
                                "description": "レコードID"
                            },
                            "data": {
                                "type": "object",
                                "description": "更新データ"
                            }
                        },
                        "required": ["module_name", "record_id", "data"]
                    }
                ),
                Tool(
                    name="delete_record",
                    description="レコードを削除",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "module_name": {
                                "type": "string",
                                "description": "モジュール名"
                            },
                            "record_id": {
                                "type": "string",
                                "description": "レコードID"
                            }
                        },
                        "required": ["module_name", "record_id"]
                    }
                ),
                Tool(
                    name="get_related_records",
                    description="関連レコードを取得",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "module_name": {
                                "type": "string",
                                "description": "親モジュール名"
                            },
                            "record_id": {
                                "type": "string",
                                "description": "親レコードID"
                            },
                            "related_module": {
                                "type": "string",
                                "description": "関連モジュール名"
                            },
                            "page": {
                                "type": "integer",
                                "description": "ページ番号",
                                "default": 1
                            },
                            "per_page": {
                                "type": "integer",
                                "description": "1ページあたりのレコード数",
                                "default": 200
                            }
                        },
                        "required": ["module_name", "record_id", "related_module"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> list:
            """ツールを実行"""
            
            if not self.client:
                config = self.load_config()
                self.client = ZohoCRMClient(
                    config["client_id"],
                    config["client_secret"],
                    config.get("refresh_token")
                )
                # 既存のトークンファイルを読み込み
                self.client.load_tokens_from_file()
            
            try:
                if name == "list_modules":
                    modules = await self.client.get_modules()
                    return [TextContent(
                        type="text",
                        text=json.dumps(modules, ensure_ascii=False, indent=2)
                    )]
                
                elif name == "get_module_fields":
                    fields = await self.client.get_fields(arguments["module_name"])
                    return [TextContent(
                        type="text",
                        text=json.dumps(fields, ensure_ascii=False, indent=2)
                    )]
                
                elif name == "get_records":
                    params = {}
                    if "page" in arguments:
                        params["page"] = arguments["page"]
                    if "per_page" in arguments:
                        params["per_page"] = arguments["per_page"]
                    if "fields" in arguments:
                        params["fields"] = ",".join(arguments["fields"])
                    if "sort_by" in arguments:
                        params["sort_by"] = arguments["sort_by"]
                    if "sort_order" in arguments:
                        params["sort_order"] = arguments["sort_order"]
                    
                    result = await self.client.get_records(arguments["module_name"], params)
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2)
                    )]
                
                elif name == "search_records":
                    params = {
                        "page": arguments.get("page", 1),
                        "per_page": arguments.get("per_page", 200)
                    }
                    result = await self.client.search_records(
                        arguments["module_name"],
                        arguments["criteria"],
                        params
                    )
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2)
                    )]
                
                elif name == "get_record":
                    result = await self.client.get_record(
                        arguments["module_name"],
                        arguments["record_id"]
                    )
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2)
                    )]
                
                elif name == "create_record":
                    result = await self.client.create_record(
                        arguments["module_name"],
                        arguments["data"]
                    )
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2)
                    )]
                
                elif name == "update_record":
                    result = await self.client.update_record(
                        arguments["module_name"],
                        arguments["record_id"],
                        arguments["data"]
                    )
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2)
                    )]
                
                elif name == "delete_record":
                    result = await self.client.delete_record(
                        arguments["module_name"],
                        arguments["record_id"]
                    )
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2)
                    )]
                
                elif name == "get_related_records":
                    params = {
                        "page": arguments.get("page", 1),
                        "per_page": arguments.get("per_page", 200)
                    }
                    result = await self.client.get_related_records(
                        arguments["module_name"],
                        arguments["record_id"],
                        arguments["related_module"],
                        params
                    )
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2)
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
                    server_name="zoho-crm-mcp",
                    server_version="1.0.0",
                    capabilities={}
                )
            )


async def main():
    """メインエントリーポイント"""
    server = ZohoCRMMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())