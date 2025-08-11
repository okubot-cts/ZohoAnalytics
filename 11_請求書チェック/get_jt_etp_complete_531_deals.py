#!/usr/bin/env python3
"""
JT ETP 531件完全取得と「後期」なし商談の金額集計
新しいCRMトークンを使用して全データを取得
"""
import requests
import json
from pathlib import Path
from datetime import datetime

def load_crm_token():
    """CRMトークンを読み込み"""
    token_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン" / "zoho_crm_tokens.json"
    with open(token_path, 'r') as f:
        tokens = json.load(f)
    return tokens['access_token']

def get_all_jt_etp_children(access_token, parent_id):
    """JT ETP親商談に紐づく全子商談を取得"""
    print(f"📊 JT ETP子商談取得開始 (親ID: {parent_id})")
    
    url = "https://www.zohoapis.com/crm/v2/Deals/search"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    all_children = []
    page = 1
    
    while page <= 50:  # 最大50ページまで
        params = {
            'criteria': f'(field78:equals:{parent_id})',
            'page': page,
            'per_page': 200,
            'fields': 'id,Deal_Name,Amount,Stage,Closing_Date,field78'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                deals = data.get('data', [])
                
                if deals:
                    all_children.extend(deals)
                    print(f"  ページ{page}: {len(deals)}件取得 (累計: {len(all_children)}件)")
                    
                    # より多くのレコードがあるかチェック
                    if not data.get('info', {}).get('more_records', False):
                        break
                    page += 1
                else:
                    print(f"  ページ{page}: データなし")
                    break
                    
            elif response.status_code == 204:
                print(f"  ページ{page}: データなし (204)")
                break
            else:
                print(f"  ❌ ページ{page}エラー: {response.status_code}")
                print(f"     レスポンス: {response.text}")
                break
                
        except Exception as e:
            print(f"  ❌ ページ{page}例外: {str(e)}")
            break
    
    print(f"✅ JT ETP子商談取得完了: {len(all_children)}件")
    return all_children

def analyze_kouki_deals(children):
    """「後期」商談を分析（ステージ「受注」のみ）"""
    print(f"\n🔍 「後期」商談分析開始（ステージ「受注」フィルタあり）")
    
    # まずステージ「受注」でフィルタ
    jucyu_deals = [deal for deal in children if deal.get('Stage') == '受注']
    print(f"  ステージ「受注」: {len(jucyu_deals)}件 (全体: {len(children)}件)")
    
    kouki_deals = []
    non_kouki_deals = []
    
    for deal in jucyu_deals:
        deal_name = deal.get('Deal_Name', '')
        if '後期' in deal_name:
            kouki_deals.append(deal)
        else:
            non_kouki_deals.append(deal)
    
    print(f"  「受注」かつ「後期」商談: {len(kouki_deals)}件")
    print(f"  「受注」かつ「後期」なし商談: {len(non_kouki_deals)}件")
    
    return kouki_deals, non_kouki_deals, jucyu_deals

def calculate_amounts(deals, category_name):
    """商談金額を集計"""
    print(f"\n💰 {category_name}金額集計")
    
    total_amount_excluding_tax = 0
    deal_count = len(deals)
    
    for deal in deals:
        amount = deal.get('Amount', 0) or 0
        total_amount_excluding_tax += amount
    
    total_amount_including_tax = total_amount_excluding_tax * 1.10
    
    print(f"  件数: {deal_count}件")
    print(f"  総額（税抜き）: ¥{total_amount_excluding_tax:,.0f}")
    print(f"  総額（税込み）: ¥{total_amount_including_tax:,.0f}")
    
    if deal_count > 0:
        avg_amount = total_amount_excluding_tax / deal_count
        print(f"  平均単価（税抜き）: ¥{avg_amount:,.0f}")
    
    return {
        'count': deal_count,
        'total_excluding_tax': total_amount_excluding_tax,
        'total_including_tax': total_amount_including_tax,
        'average_amount': total_amount_excluding_tax / deal_count if deal_count > 0 else 0
    }

def save_results(all_children, kouki_deals, non_kouki_deals, jucyu_deals, kouki_summary, non_kouki_summary):
    """結果を保存"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent / "JT_ETP_完全分析結果"
    output_dir.mkdir(exist_ok=True)
    
    # 1. 全件データ保存
    all_data = {
        'parent_id': '5187347000129692086',
        'parent_name': '【2025】JT ETP _事務局',
        'timestamp': timestamp,
        'total_children_count': len(all_children),
        'jucyu_count': len(jucyu_deals),
        'kouki_summary': kouki_summary,
        'non_kouki_summary': non_kouki_summary,
        'all_children': all_children,
        'jucyu_deals': jucyu_deals
    }
    
    with open(output_dir / f"JT_ETP_全件データ_{timestamp}.json", 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    # 2. 「後期」商談データ
    with open(output_dir / f"JT_ETP_後期商談_{timestamp}.json", 'w', encoding='utf-8') as f:
        json.dump(kouki_deals, f, ensure_ascii=False, indent=2)
    
    # 3. 「後期」なし商談データ
    with open(output_dir / f"JT_ETP_後期なし商談_{timestamp}.json", 'w', encoding='utf-8') as f:
        json.dump(non_kouki_deals, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 結果保存完了:")
    print(f"  出力ディレクトリ: {output_dir}")
    print(f"  全件データ: JT_ETP_全件データ_{timestamp}.json")
    print(f"  後期商談: JT_ETP_後期商談_{timestamp}.json")
    print(f"  後期なし商談: JT_ETP_後期なし商談_{timestamp}.json")

def main():
    """メイン処理"""
    print("="*80)
    print("📊 JT ETP 531件完全取得・「後期」なし商談金額集計")
    print("="*80)
    
    # 1. CRMトークン読み込み
    try:
        access_token = load_crm_token()
        print("✅ CRMトークン読み込み完了")
    except Exception as e:
        print(f"❌ CRMトークン読み込みエラー: {e}")
        return
    
    # 2. JT ETP全子商談取得
    parent_id = '5187347000129692086'
    all_children = get_all_jt_etp_children(access_token, parent_id)
    
    if not all_children:
        print("❌ 子商談が取得できませんでした")
        return
    
    # 3. 「後期」分析（受注ステージのみ）
    kouki_deals, non_kouki_deals, jucyu_deals = analyze_kouki_deals(all_children)
    
    # 4. 金額集計
    kouki_summary = calculate_amounts(kouki_deals, "「後期」商談")
    non_kouki_summary = calculate_amounts(non_kouki_deals, "「後期」なし商談")
    
    # 5. 比較分析
    print(f"\n📊 比較分析")
    print("="*50)
    payment_until_june = 91079160
    print(f"6月まで入金額: ¥{payment_until_june:,.0f}")
    print(f"「後期」なし総額（税込み）: ¥{non_kouki_summary['total_including_tax']:,.0f}")
    
    diff_with_payment = payment_until_june - non_kouki_summary['total_including_tax']
    print(f"入金との差額: ¥{diff_with_payment:,.0f}")
    
    if abs(diff_with_payment) < 1000:
        print("✅ ほぼ完全一致！「後期」なし商談が上期入金対象")
    elif diff_with_payment > 0:
        print("⚠️ 入金の方が多い（他の収入源または前払い？）")
    else:
        print("⚠️ 商談の方が多い（未入金あり？）")
    
    # 6. 結果保存
    save_results(all_children, kouki_deals, non_kouki_deals, jucyu_deals, kouki_summary, non_kouki_summary)
    
    # 7. 最終回答
    print(f"\n" + "="*80)
    print("🎯 最終回答")
    print("="*80)
    print(f"JT ETP 531件の構成:")
    print(f"  全子商談数: {len(all_children)}件")
    print(f"  ステージ「受注」: {len(jucyu_deals)}件")
    print(f"  「受注」かつ「後期」商談: {kouki_summary['count']}件")
    print(f"  「受注」かつ「後期」なし商談: {non_kouki_summary['count']}件")
    print()
    print(f"「受注」かつ「後期」なし商談の金額:")
    print(f"  総額（税抜き）: ¥{non_kouki_summary['total_excluding_tax']:,.0f}")
    print(f"  総額（税込み）: ¥{non_kouki_summary['total_including_tax']:,.0f}")
    print()
    print(f"6月まで入金額との比較:")
    print(f"  入金額: ¥{payment_until_june:,.0f}")
    print(f"  差額: ¥{diff_with_payment:,.0f}")
    print("="*80)

if __name__ == "__main__":
    main()