#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zoho CRM & Books 接続テスト
請求書チェックプロジェクト用
"""

import json
import os
from zoho_auth_manager import ZohoAuthManager, ZohoCRMAPI, ZohoBooksAPI

def test_crm_connection(access_token, org_id):
    """Zoho CRMへの接続をテスト"""
    print("=== Zoho CRM 接続テスト ===")
    
    try:
        crm_api = ZohoCRMAPI(access_token, org_id)
        
        # モジュール一覧を取得
        print("1. モジュール一覧を取得中...")
        modules = crm_api.get_modules()
        print(f"✓ モジュール数: {len(modules.get('modules', []))}")
        
        # 主要モジュールのフィールドを取得
        main_modules = ['Deals', 'Contacts', 'Accounts']
        for module in main_modules:
            try:
                print(f"2. {module}モジュールのフィールドを取得中...")
                fields = crm_api.get_module_fields(module)
                field_count = len(fields.get('fields', []))
                print(f"✓ {module}: {field_count}個のフィールド")
            except Exception as e:
                print(f"✗ {module}: エラー - {str(e)}")
        
        # 商談レコードを取得（サンプル）
        try:
            print("3. 商談レコードを取得中...")
            deals = crm_api.get_records('Deals', {'per_page': 5})
            deal_count = len(deals.get('data', []))
            print(f"✓ 商談レコード: {deal_count}件")
        except Exception as e:
            print(f"✗ 商談レコード取得エラー: {str(e)}")
        
        print("✓ Zoho CRM接続テスト完了\n")
        return True
        
    except Exception as e:
        print(f"✗ Zoho CRM接続エラー: {str(e)}\n")
        return False

def test_books_connection(access_token, org_id):
    """Zoho Booksへの接続をテスト"""
    print("=== Zoho Books 接続テスト ===")
    
    try:
        books_api = ZohoBooksAPI(access_token, org_id)
        
        # 組織一覧を取得
        print("1. 組織一覧を取得中...")
        organizations = books_api.get_organizations()
        org_count = len(organizations.get('organizations', []))
        print(f"✓ 組織数: {org_count}")
        
        # 請求書一覧を取得（サンプル）
        try:
            print("2. 請求書一覧を取得中...")
            invoices = books_api.get_invoices({'per_page': 5})
            invoice_count = len(invoices.get('invoices', []))
            print(f"✓ 請求書: {invoice_count}件")
        except Exception as e:
            print(f"✗ 請求書取得エラー: {str(e)}")
        
        # 顧客一覧を取得（サンプル）
        try:
            print("3. 顧客一覧を取得中...")
            customers = books_api.get_customers({'per_page': 5})
            customer_count = len(customers.get('contacts', []))
            print(f"✓ 顧客: {customer_count}件")
        except Exception as e:
            print(f"✗ 顧客取得エラー: {str(e)}")
        
        print("✓ Zoho Books接続テスト完了\n")
        return True
        
    except Exception as e:
        print(f"✗ Zoho Books接続エラー: {str(e)}\n")
        return False

def main():
    print("=== Zoho CRM & Books 接続テスト ===")
    print("請求書チェックプロジェクト用の接続テストを実行します\n")
    
    # トークンファイルを確認
    token_file = 'zoho_tokens.json'
    
    if not os.path.exists(token_file):
        print("❌ トークンファイルが見つかりません")
        print("先に zoho_auth_manager.py を実行して認証を行ってください")
        return
    
    # トークンを読み込み
    try:
        with open(token_file, 'r', encoding='utf-8') as f:
            tokens = json.load(f)
        
        access_token = tokens.get('access_token')
        org_id = tokens.get('org_id')
        
        if not access_token:
            print("❌ アクセストークンが見つかりません")
            return
        
        print(f"✓ トークンを読み込みました (保存日時: {tokens.get('saved_at', '不明')})")
        
    except Exception as e:
        print(f"❌ トークンファイル読み込みエラー: {str(e)}")
        return
    
    # 接続テスト実行
    crm_success = test_crm_connection(access_token, org_id)
    books_success = test_books_connection(access_token, org_id)
    
    # 結果サマリー
    print("=== 接続テスト結果 ===")
    print(f"Zoho CRM: {'✓ 成功' if crm_success else '✗ 失敗'}")
    print(f"Zoho Books: {'✓ 成功' if books_success else '✗ 失敗'}")
    
    if crm_success and books_success:
        print("\n🎉 両方のサービスへの接続が成功しました！")
        print("請求書チェックプロジェクトを開始できます。")
    else:
        print("\n⚠️  一部のサービスで接続に失敗しました。")
        print("認証情報を確認して再度実行してください。")

if __name__ == "__main__":
    main()

