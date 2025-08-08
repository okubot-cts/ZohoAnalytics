#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テーブル構造確認スクリプト
"""

import requests
import json
import os

def check_table_structure(workspace_id, org_id, access_token, table_name):
    """
    テーブルの構造を確認
    """
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'ZANALYTICS-ORGID': org_id,
        'Content-Type': 'application/json'
    }
    
    # テーブル情報を取得
    url = f"https://analyticsapi.zoho.com/restapi/v2/workspaces/{workspace_id}/views"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        tables = data.get('data', {}).get('views', [])
        
        # 指定されたテーブルを探す
        target_table = None
        for table in tables:
            if table.get('viewName') == table_name:
                target_table = table
                break
        
        if target_table:
            print(f"📋 テーブル情報: {table_name}")
            print(f"   ID: {target_table.get('viewId')}")
            print(f"   名前: {target_table.get('viewName')}")
            print(f"   説明: {target_table.get('viewDesc', 'なし')}")
            
            # 列情報を取得
            columns_url = f"https://analyticsapi.zoho.com/restapi/v2/workspaces/{workspace_id}/views/{target_table.get('viewId')}/columns"
            columns_response = requests.get(columns_url, headers=headers)
            
            if columns_response.status_code == 200:
                columns_data = columns_response.json()
                columns = columns_data.get('data', {}).get('columns', [])
                
                print(f"   📊 列情報 ({len(columns)}件):")
                for col in columns:
                    print(f"      - {col.get('columnName')} ({col.get('dataType', 'unknown')})")
            else:
                print(f"   ❌ 列情報取得失敗: {columns_response.status_code}")
        else:
            print(f"❌ テーブル '{table_name}' が見つかりません")
    else:
        print(f"❌ テーブル一覧取得失敗: {response.status_code}")

def main():
    """
    メイン実行関数
    """
    access_token = "1000.8621860282e81be6562d037429111add.01bf659cc6c8f0751ac1cf3915ce2178"
    workspace_id = "2527115000001040002"
    org_id = "772044231"
    
    # 確認したいテーブル
    tables_to_check = [
        "Versant",
        "連絡先",
        "手配"
    ]
    
    for table_name in tables_to_check:
        print(f"\n{'='*50}")
        check_table_structure(workspace_id, org_id, access_token, table_name)

if __name__ == "__main__":
    main() 