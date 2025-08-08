#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
実際のZoho Analytics APIを使用してデータ取得をテストするスクリプト（修正版）
"""

import os
import sys
from datetime import datetime
import json

# APIクライアントをインポート
try:
    from zoho_analytics_api_client import ZohoAnalyticsAPI, load_versant_query
except ImportError:
    print("❌ zoho_analytics_api_client.py が見つかりません")
    sys.exit(1)

def test_api_connection():
    """
    API接続テスト
    """
    print("=== API接続テスト ===")
    
    # 環境変数の確認
    access_token = os.getenv('ZOHO_ANALYTICS_ACCESS_TOKEN')
    workspace_id = os.getenv('ZOHO_ANALYTICS_WORKSPACE_ID')
    
    if not access_token:
        print("❌ ZOHO_ANALYTICS_ACCESS_TOKEN が設定されていません")
        return False
    
    if not workspace_id:
        print("❌ ZOHO_ANALYTICS_WORKSPACE_ID が設定されていません")
        return False
    
    print("✅ 環境変数が設定されています")
    print(f"   アクセストークン: {access_token[:10]}...")
    print(f"   ワークスペースID: {workspace_id}")
    
    # APIクライアントの初期化
    try:
        client = ZohoAnalyticsAPI()
        print("✅ APIクライアント初期化成功")
        return client
    except Exception as e:
        print(f"❌ APIクライアント初期化失敗: {e}")
        return False

def test_workspace_access(client):
    """
    ワークスペースアクセステスト
    """
    print("\n=== ワークスペースアクセステスト ===")
    
    try:
        workspaces = client.get_workspaces()
        if workspaces and 'data' in workspaces:
            # 正しいレスポンス構造に対応
            owned_workspaces = workspaces['data'].get('ownedWorkspaces', [])
            shared_workspaces = workspaces['data'].get('sharedWorkspaces', [])
            total_workspaces = len(owned_workspaces) + len(shared_workspaces)
            
            print(f"✅ ワークスペース取得成功: {total_workspaces}件")
            print(f"   所有ワークスペース: {len(owned_workspaces)}件")
            print(f"   共有ワークスペース: {len(shared_workspaces)}件")
            
            # 現在のワークスペースを確認
            current_workspace = None
            all_workspaces = owned_workspaces + shared_workspaces
            
            for ws in all_workspaces:
                if ws.get('workspaceId') == os.getenv('ZOHO_ANALYTICS_WORKSPACE_ID'):
                    current_workspace = ws
                    break
            
            if current_workspace:
                print(f"✅ 対象ワークスペース確認: {current_workspace.get('workspaceName', 'Unknown')}")
                print(f"   ワークスペースID: {current_workspace.get('workspaceId')}")
                print(f"   組織ID: {current_workspace.get('orgId')}")
            else:
                print("⚠️ 対象ワークスペースが見つかりません")
                print("利用可能なワークスペース:")
                for ws in all_workspaces:
                    print(f"   - {ws.get('workspaceName')} (ID: {ws.get('workspaceId')})")
            
            return True
        else:
            print("❌ ワークスペース取得失敗")
            return False
    except Exception as e:
        print(f"❌ ワークスペースアクセスエラー: {e}")
        return False

def test_table_access(client):
    """
    テーブルアクセステスト
    """
    print("\n=== テーブルアクセステスト ===")
    
    try:
        tables = client.get_tables()
        if tables and 'data' in tables and 'views' in tables['data']:
            views = tables['data']['views']
            view_count = len(views)
            print(f"✅ ビュー取得成功: {view_count}件")
            
            # ビューの種類別カウント
            view_types = {}
            for view in views:
                view_type = view.get('viewType', 'Unknown')
                view_types[view_type] = view_types.get(view_type, 0) + 1
            
            print("ビューの種類:")
            for view_type, count in view_types.items():
                print(f"   - {view_type}: {count}件")
            
            # 最初の5件を表示
            print("\n最初の5件のビュー:")
            for i, view in enumerate(views[:5]):
                print(f"   {i+1}. {view.get('viewName')} ({view.get('viewType')})")
            
            return True
        else:
            print("❌ テーブル取得失敗")
            if tables:
                print(f"レスポンス構造: {list(tables.keys()) if isinstance(tables, dict) else 'Not a dict'}")
            return False
    except Exception as e:
        print(f"❌ テーブルアクセスエラー: {e}")
        return False

def test_simple_query(client):
    """
    簡単なクエリテスト
    """
    print("\n=== 簡単なクエリテスト ===")
    
    # 簡単なクエリを実行
    simple_query = "SELECT COUNT(*) as total_count FROM 連絡先 LIMIT 1"
    
    try:
        print(f"🔄 クエリ実行中: {simple_query}")
        result = client.execute_query(simple_query)
        
        if result:
            print("✅ クエリ実行成功")
            print(f"結果: {result}")
            return True
        else:
            print("❌ クエリ実行失敗")
            return False
    except Exception as e:
        print(f"❌ クエリ実行エラー: {e}")
        return False

def test_versant_query(client):
    """
    VERSANTコーチングレポートクエリテスト
    """
    print("\n=== VERSANTコーチングレポートクエリテスト ===")
    
    # VERSANTコーチングレポートのSQLファイルを読み込み
    sql_file = "versant_coaching_report_basic.sql"
    
    try:
        query = load_versant_query(sql_file)
        if not query:
            print(f"❌ SQLファイルの読み込みに失敗: {sql_file}")
            return False
        
        print(f"🔄 VERSANTクエリ実行中: {sql_file}")
        result = client.execute_query(query)
        
        if result:
            print("✅ VERSANTクエリ実行成功")
            
            # 結果をファイルに保存
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"versant_test_result_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"結果を保存しました: {filename}")
            return True
        else:
            print("❌ VERSANTクエリ実行失敗")
            return False
    except Exception as e:
        print(f"❌ VERSANTクエリ実行エラー: {e}")
        return False

def generate_test_summary():
    """
    テスト結果のサマリーを生成
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary = {
        "test_timestamp": timestamp,
        "access_token": os.getenv('ZOHO_ANALYTICS_ACCESS_TOKEN', '')[:10] + "...",
        "workspace_id": os.getenv('ZOHO_ANALYTICS_WORKSPACE_ID', ''),
        "test_results": {}
    }
    
    return summary

def main():
    """
    メイン実行関数
    """
    print("=== 実際のAPIテスト実行（修正版） ===")
    
    # API接続テスト
    client = test_api_connection()
    if not client:
        print("❌ API接続に失敗しました。環境変数を確認してください。")
        return
    
    # ワークスペースアクセステスト
    workspace_success = test_workspace_access(client)
    
    # テーブルアクセステスト
    table_success = test_table_access(client)
    
    # 簡単なクエリテスト
    query_success = test_simple_query(client)
    
    # VERSANTクエリテスト
    versant_success = test_versant_query(client)
    
    # 結果サマリー
    print("\n=== テスト結果サマリー ===")
    print(f"✅ API接続: 成功")
    print(f"{'✅' if workspace_success else '❌'} ワークスペースアクセス: {'成功' if workspace_success else '失敗'}")
    print(f"{'✅' if table_success else '❌'} テーブルアクセス: {'成功' if table_success else '失敗'}")
    print(f"{'✅' if query_success else '❌'} 簡単なクエリ: {'成功' if query_success else '失敗'}")
    print(f"{'✅' if versant_success else '❌'} VERSANTクエリ: {'成功' if versant_success else '失敗'}")
    
    # サマリーをファイルに保存
    summary = generate_test_summary()
    summary["test_results"] = {
        "workspace_access": workspace_success,
        "table_access": table_success,
        "simple_query": query_success,
        "versant_query": versant_success
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_filename = f"api_test_summary_{timestamp}.json"
    
    with open(summary_filename, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\nテストサマリーを保存しました: {summary_filename}")

if __name__ == "__main__":
    main() 