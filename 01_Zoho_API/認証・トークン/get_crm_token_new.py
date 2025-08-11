#!/usr/bin/env python3
"""
Zoho CRM トークン取得スクリプト
認証コードからアクセストークンを取得して保存します
"""
import requests
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

def get_crm_token(auth_code):
    """認証コードからCRMトークンを取得"""
    
    # 既存の認証情報を使用
    CLIENT_ID = "1000.YN0LA88XQRCDTARO3FO5PWCOEY2IFZ"
    CLIENT_SECRET = "25549573ace167da7319c6b561a8ea477ca235e0ef"
    REDIRECT_URI = "http://localhost:8080/callback"
    
    print("Zoho CRMトークンを取得中...")
    
    # トークン取得リクエスト
    token_url = "https://accounts.zoho.com/oauth/v2/token"
    
    data = {
        'code': auth_code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    
    try:
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            
            # 有効期限とスコープを追加
            token_data['expires_at'] = (datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))).isoformat()
            token_data['updated_at'] = datetime.now().isoformat()
            token_data['scope'] = 'ZohoCRM.modules.ALL ZohoCRM.settings.modules.READ ZohoCRM.settings.fields.READ'
            token_data['api_domain'] = 'https://www.zohoapis.com'
            
            # トークンをファイルに保存
            tokens_file = Path(__file__).parent / "zoho_crm_tokens.json"
            with open(tokens_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            print(f"\n✅ Zoho CRMトークンを正常に取得・保存しました！")
            print(f"   保存先: {tokens_file}")
            
            # 取得したトークン情報を表示
            print("\n📋 取得したトークン情報:")
            print(f"   アクセストークン: {token_data['access_token'][:20]}...")
            print(f"   リフレッシュトークン: {token_data.get('refresh_token', 'N/A')[:20]}...")
            print(f"   有効期限: {token_data.get('expires_in', 'N/A')}秒")
            print(f"   スコープ: {token_data.get('scope', 'N/A')}")
            
            # 接続テスト
            test_connection(token_data['access_token'])
            
            return True
            
        else:
            print(f"\n❌ トークン取得エラー: {response.status_code}")
            print(f"   詳細: {response.text}")
            
            # よくあるエラーの解説
            if response.status_code == 400:
                error_data = response.json() if response.text else {}
                error_code = error_data.get('error', '')
                
                if error_code == 'invalid_code':
                    print("\n⚠️  認証コードが無効です。以下を確認してください:")
                    print("   1. 認証コードは一度しか使用できません")
                    print("   2. 認証コードの有効期限は短いです（通常1-2分）")
                    print("   3. 新しい認証コードを取得するには、setup_zoho_crm.pyを再実行してください")
                elif error_code == 'invalid_client':
                    print("\n⚠️  クライアント認証エラーです。CLIENT_IDとCLIENT_SECRETを確認してください")
            
            return False
            
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {str(e)}")
        return False

def test_connection(access_token):
    """CRMへの接続をテスト"""
    print("\n🔍 Zoho CRM接続テスト中...")
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    # 商談データを取得
    api_url = "https://www.zohoapis.com/crm/v2/Deals"
    params = {
        'fields': 'Deal_Name,Stage,Amount,Closing_Date',
        'per_page': 5,
        'sort_by': 'Modified_Time',
        'sort_order': 'desc'
    }
    
    try:
        response = requests.get(api_url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Zoho CRM接続成功！")
            
            if 'data' in data and data['data']:
                print(f"\n📊 最新の商談 (最大5件):")
                for i, deal in enumerate(data['data'][:5], 1):
                    print(f"   {i}. {deal.get('Deal_Name', 'N/A')}")
                    print(f"      ステージ: {deal.get('Stage', 'N/A')}")
                    print(f"      金額: ¥{deal.get('Amount', 0):,.0f}")
                    print(f"      完了予定日: {deal.get('Closing_Date', 'N/A')}")
            else:
                print("  商談データが見つかりません")
        elif response.status_code == 204:
            print("✅ Zoho CRM接続成功！（データなし）")
        else:
            print(f"❌ CRM APIエラー: {response.status_code}")
            print(f"   詳細: {response.text}")
            
    except Exception as e:
        print(f"❌ 接続テストエラー: {str(e)}")

def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("使用方法: python3 get_crm_token_new.py [認証コード]")
        print("\n例: python3 get_crm_token_new.py 1000.a1b2c3d4e5f6...")
        print("\n認証コードを取得するには、setup_zoho_crm.pyを実行してください")
        sys.exit(1)
    
    auth_code = sys.argv[1].strip()
    
    if not auth_code.startswith('1000.'):
        print("⚠️  認証コードの形式が正しくありません")
        print("   正しい形式: 1000.xxxxx...")
        sys.exit(1)
    
    success = get_crm_token(auth_code)
    
    if success:
        print("\n✨ セットアップ完了！")
        print("   invoice_checker.pyを実行して請求書チェックができます")
    else:
        print("\n❌ セットアップ失敗")
        print("   setup_zoho_crm.pyを再実行して新しい認証コードを取得してください")

if __name__ == "__main__":
    main()