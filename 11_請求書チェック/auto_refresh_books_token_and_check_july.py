#!/usr/bin/env python3
"""
ZohoBooks トークン自動再取得 & 7月入金確認
リフレッシュトークンを使って自動的にトークンを更新し、7月入金データを取得
"""
import requests
import json
from pathlib import Path
from datetime import datetime

def load_config():
    """設定ファイルを読み込み"""
    config_path = Path(__file__).parent.parent / "01_Zoho_API" / "設定ファイル" / "zoho_config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def load_books_tokens():
    """既存のBooksトークンを読み込み"""
    token_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン" / "zoho_books_tokens.json"
    with open(token_path, 'r') as f:
        return json.load(f)

def refresh_books_token(refresh_token, client_id, client_secret):
    """Booksトークンを更新"""
    print("🔄 ZohoBooksトークンを更新中...")
    
    url = "https://accounts.zoho.com/oauth/v2/token"
    
    payload = {
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'refresh_token'
    }
    
    try:
        response = requests.post(url, data=payload, timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            
            # タイムスタンプを追加
            token_data['expires_at'] = (datetime.now()).strftime('%Y-%m-%dT%H:%M:%S.%f')
            token_data['updated_at'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
            
            # リフレッシュトークンを保持（新しいトークンに含まれていない場合）
            if 'refresh_token' not in token_data:
                token_data['refresh_token'] = refresh_token
            
            print("✅ Booksトークン更新成功")
            return token_data
        else:
            print(f"❌ トークン更新エラー: {response.status_code}")
            print(f"   レスポンス: {response.text}")
            return None
    
    except Exception as e:
        print(f"❌ トークン更新例外: {str(e)}")
        return None

def save_books_tokens(tokens):
    """Booksトークンを保存"""
    token_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン" / "zoho_books_tokens.json"
    
    # バックアップを作成
    if token_path.exists():
        backup_path = token_path.with_suffix('.json.backup')
        with open(token_path, 'r') as f:
            backup_data = f.read()
        with open(backup_path, 'w') as f:
            f.write(backup_data)
        print(f"📁 トークンバックアップ作成: {backup_path}")
    
    # 新しいトークンを保存
    with open(token_path, 'w', encoding='utf-8') as f:
        json.dump(tokens, f, ensure_ascii=False, indent=2)
    
    print(f"💾 新しいBooksトークン保存: {token_path}")
    return True

def get_org_id(headers):
    """Books組織IDを取得"""
    try:
        response = requests.get("https://www.zohoapis.com/books/v3/organizations", headers=headers)
        if response.status_code == 200:
            orgs = response.json()['organizations']
            for org in orgs:
                if '株式会社シー・ティー・エス' in org.get('name', ''):
                    return org['organization_id']
            return orgs[0]['organization_id'] if orgs else None
        return None
    except:
        return "772044231"  # フォールバック

def get_july_payments(headers, org_id):
    """7月の入金データを取得"""
    print("📊 7月の入金データを取得中...")
    
    url = "https://www.zohoapis.com/books/v3/customerpayments"
    all_payments = []
    page = 1
    
    while page <= 10:
        params = {
            'organization_id': org_id,
            'per_page': 200,
            'page': page,
            'sort_column': 'date',
            'sort_order': 'D',
            'date_start': '2025-07-01',
            'date_end': '2025-07-31'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                payments = data.get('customerpayments', [])
                
                if payments:
                    all_payments.extend(payments)
                    print(f"  ページ{page}: {len(payments)}件取得 (累計: {len(all_payments)}件)")
                    
                    page_context = data.get('page_context', {})
                    if not page_context.get('has_more_page', False):
                        break
                    page += 1
                else:
                    print(f"  ページ{page}: データなし")
                    break
            else:
                print(f"  ❌ ページ{page}エラー: {response.status_code}")
                if page == 1:  # 最初のページでエラーの場合は詳細出力
                    print(f"     レスポンス: {response.text}")
                break
                
        except Exception as e:
            print(f"  ❌ ページ{page}例外: {str(e)}")
            break
    
    print(f"✅ 7月入金データ取得完了: {len(all_payments)}件")
    return all_payments

def analyze_july_payments_for_jt_etp(payments):
    """7月入金データをJT ETP視点で分析"""
    print(f"\n💰 7月入金分析（JT ETP差額解明）")
    print("="*50)
    
    if not payments:
        print("  7月の入金データはありません")
        return
    
    total_amount = 0
    jt_etp_payments = []
    potential_jt_etp = []
    
    target_diff = 1534114  # 探している差額
    
    for payment in payments:
        amount = payment.get('amount', 0)
        total_amount += amount
        
        # 顧客名やメモでJT ETP関連を判定
        customer_name = payment.get('customer_name', '').upper()
        description = payment.get('description', '').upper()
        reference_number = payment.get('reference_number', '').upper()
        
        search_text = customer_name + ' ' + description + ' ' + reference_number
        
        # JT ETP関連キーワード
        jt_keywords = ['JT', 'ジェイティ', 'JAPAN TOBACCO', 'ETP']
        
        is_jt_etp = any(keyword in search_text for keyword in jt_keywords)
        
        if is_jt_etp:
            jt_etp_payments.append(payment)
        
        # 金額が差額に近い場合も要チェック
        if abs(amount - target_diff) < 100000:  # 10万円以内
            potential_jt_etp.append(payment)
    
    print(f"  7月総入金額: ¥{total_amount:,.0f}")
    print(f"  7月入金件数: {len(payments)}件")
    
    # JT ETP確実
    if jt_etp_payments:
        jt_etp_amount = sum(p.get('amount', 0) for p in jt_etp_payments)
        print(f"\n🎯 JT ETP確実:")
        print(f"  件数: {len(jt_etp_payments)}件")
        print(f"  金額: ¥{jt_etp_amount:,.0f}")
        
        for payment in jt_etp_payments:
            date = payment.get('date', '')
            amount = payment.get('amount', 0)
            customer = payment.get('customer_name', 'N/A')
            print(f"    {date}: ¥{amount:,.0f} - {customer}")
    
    # 金額的に可能性あり
    if potential_jt_etp:
        print(f"\n🤔 金額的にJT ETP可能性:")
        for payment in potential_jt_etp:
            if payment not in jt_etp_payments:  # 重複除外
                date = payment.get('date', '')
                amount = payment.get('amount', 0)
                customer = payment.get('customer_name', 'N/A')
                description = payment.get('description', '')
                print(f"    {date}: ¥{amount:,.0f} - {customer}")
                if description:
                    print(f"      メモ: {description}")
    
    # 差額との比較
    print(f"\n📊 差額¥{target_diff:,.0f}との比較:")
    
    if jt_etp_payments:
        jt_etp_amount = sum(p.get('amount', 0) for p in jt_etp_payments)
        remaining_diff = target_diff - jt_etp_amount
        print(f"  JT ETP確実入金: ¥{jt_etp_amount:,.0f}")
        print(f"  差額との差: ¥{remaining_diff:,.0f}")
        
        if abs(remaining_diff) < 50000:
            print("  ✅ 差額がほぼ一致！JT ETP 7月入金で説明可能")
        elif remaining_diff > 0:
            print("  ⚠️ まだ説明できない差額があります")
        else:
            print("  ⚠️ 7月JT ETP入金の方が多いです")
    else:
        print(f"  JT ETP確実入金: ¥0")
        print(f"  差額¥{target_diff:,.0f}は7月JT ETP入金では説明できません")
    
    # トップ入金を表示（参考）
    if payments:
        print(f"\n📈 7月の大口入金 (TOP 10):")
        sorted_payments = sorted(payments, key=lambda x: x.get('amount', 0), reverse=True)
        for i, payment in enumerate(sorted_payments[:10], 1):
            date = payment.get('date', '')
            amount = payment.get('amount', 0)
            customer = payment.get('customer_name', 'N/A')[:20]
            print(f"    {i:2}. {date}: ¥{amount:,.0f} - {customer}")

def main():
    """メイン処理"""
    print("="*80)
    print("📊 ZohoBooks自動トークン更新 & 7月入金確認")
    print("="*80)
    
    # 1. 設定とトークン読み込み
    try:
        config = load_config()
        old_tokens = load_books_tokens()
        print("✅ 設定・トークン読み込み完了")
    except Exception as e:
        print(f"❌ 読み込みエラー: {e}")
        return
    
    # 2. トークン更新
    new_tokens = refresh_books_token(
        old_tokens['refresh_token'],
        config['client_id'],
        config['client_secret']
    )
    
    if not new_tokens:
        print("❌ トークン更新に失敗しました")
        return
    
    # 3. 新しいトークンを保存
    save_books_tokens(new_tokens)
    
    # 4. 新しいトークンで組織ID取得
    headers = {'Authorization': f"Bearer {new_tokens['access_token']}"}
    org_id = get_org_id(headers)
    print(f"✅ 組織ID: {org_id}")
    
    # 5. 7月入金データ取得
    july_payments = get_july_payments(headers, org_id)
    
    # 6. JT ETP視点での分析
    analyze_july_payments_for_jt_etp(july_payments)
    
    print("\n" + "="*80)
    print("🎯 結論: 7月入金データでJT ETP差額¥1,534,114の説明を試行")
    print("="*80)

if __name__ == "__main__":
    main()