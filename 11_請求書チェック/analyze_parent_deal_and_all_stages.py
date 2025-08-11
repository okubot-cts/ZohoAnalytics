#!/usr/bin/env python3
"""
JT ETP親商談の金額と全ステージの商談を確認
差額の原因を商談側から分析
"""
import requests
import json
from pathlib import Path

def load_crm_token():
    """CRMトークンを読み込み"""
    token_path = Path(__file__).parent.parent / "01_Zoho_API" / "認証・トークン" / "zoho_crm_tokens.json"
    with open(token_path, 'r') as f:
        tokens = json.load(f)
    return tokens['access_token']

def get_parent_deal_details(access_token, parent_id):
    """親商談の詳細を取得"""
    print(f"📊 親商談詳細取得 (ID: {parent_id})")
    
    url = f"https://www.zohoapis.com/crm/v2/Deals/{parent_id}"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            parent_deal = data.get('data', [{}])[0]
            
            print(f"  親商談名: {parent_deal.get('Deal_Name', 'N/A')}")
            print(f"  金額: ¥{parent_deal.get('Amount', 0):,.0f}")
            print(f"  ステージ: {parent_deal.get('Stage', 'N/A')}")
            print(f"  成約予定日: {parent_deal.get('Closing_Date', 'N/A')}")
            print(f"  顧客名: {parent_deal.get('Account_Name', 'N/A')}")
            
            return parent_deal
        else:
            print(f"  ❌ 親商談取得エラー: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"  ❌ 親商談取得例外: {str(e)}")
        return None

def analyze_all_children_by_stage(access_token, parent_id):
    """全子商談をステージ別に分析"""
    print(f"\n📊 全子商談のステージ別分析")
    
    url = "https://www.zohoapis.com/crm/v2/Deals/search"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    all_children = []
    page = 1
    
    # 全子商談を取得
    while page <= 50:
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
                    
                    if not data.get('info', {}).get('more_records', False):
                        break
                    page += 1
                else:
                    break
                    
            else:
                print(f"  ❌ ページ{page}エラー: {response.status_code}")
                break
                
        except Exception as e:
            print(f"  ❌ ページ{page}例外: {str(e)}")
            break
    
    print(f"  全子商談取得: {len(all_children)}件")
    
    # ステージ別集計
    stage_analysis = {}
    kouki_analysis = {'kouki': [], 'non_kouki': []}
    
    for deal in all_children:
        stage = deal.get('Stage', '不明')
        amount = deal.get('Amount', 0) or 0
        deal_name = deal.get('Deal_Name', '')
        
        # ステージ別集計
        if stage not in stage_analysis:
            stage_analysis[stage] = {'count': 0, 'amount': 0, 'deals': []}
        
        stage_analysis[stage]['count'] += 1
        stage_analysis[stage]['amount'] += amount
        stage_analysis[stage]['deals'].append(deal)
        
        # 後期分析
        if '後期' in deal_name:
            kouki_analysis['kouki'].append(deal)
        else:
            kouki_analysis['non_kouki'].append(deal)
    
    # ステージ別結果表示
    print(f"\n📋 ステージ別分析結果:")
    print("="*60)
    
    total_amount = 0
    for stage, data in sorted(stage_analysis.items()):
        count = data['count']
        amount = data['amount']
        amount_with_tax = amount * 1.10
        total_amount += amount
        
        print(f"【{stage}】")
        print(f"  件数: {count}件")
        print(f"  金額（税抜き）: ¥{amount:,.0f}")
        print(f"  金額（税込み）: ¥{amount_with_tax:,.0f}")
        print(f"  平均単価: ¥{amount/count if count > 0 else 0:,.0f}")
        
        # 後期・非後期の内訳
        stage_kouki = [d for d in data['deals'] if '後期' in d.get('Deal_Name', '')]
        stage_non_kouki = [d for d in data['deals'] if '後期' not in d.get('Deal_Name', '')]
        
        if stage_kouki:
            kouki_amount = sum(d.get('Amount', 0) or 0 for d in stage_kouki)
            print(f"    └ 後期: {len(stage_kouki)}件 ¥{kouki_amount:,.0f}")
        
        if stage_non_kouki:
            non_kouki_amount = sum(d.get('Amount', 0) or 0 for d in stage_non_kouki)
            print(f"    └ 後期なし: {len(stage_non_kouki)}件 ¥{non_kouki_amount:,.0f}")
        
        print()
    
    print(f"全商談合計（税抜き）: ¥{total_amount:,.0f}")
    print(f"全商談合計（税込み）: ¥{total_amount * 1.10:,.0f}")
    
    return stage_analysis, kouki_analysis

def calculate_total_with_parent(parent_deal, stage_analysis):
    """親商談込みの合計を計算"""
    print(f"\n💰 親商談込み合計計算")
    print("="*40)
    
    parent_amount = parent_deal.get('Amount', 0) or 0 if parent_deal else 0
    children_total = sum(data['amount'] for data in stage_analysis.values())
    
    print(f"親商談金額: ¥{parent_amount:,.0f}")
    print(f"子商談合計: ¥{children_total:,.0f}")
    print(f"総合計（税抜き）: ¥{parent_amount + children_total:,.0f}")
    print(f"総合計（税込み）: ¥{(parent_amount + children_total) * 1.10:,.0f}")
    
    # 6月まで入金との比較
    june_payment = 91079160
    total_with_tax = (parent_amount + children_total) * 1.10
    diff = total_with_tax - june_payment
    
    print(f"\n📊 6月まで入金との比較:")
    print(f"商談総額（親子込み・税込み）: ¥{total_with_tax:,.0f}")
    print(f"6月まで入金: ¥{june_payment:,.0f}")
    print(f"差額: ¥{diff:,.0f}")
    
    return parent_amount + children_total, total_with_tax, diff

def find_potential_missing_deals(stage_analysis, target_diff):
    """差額に相当する可能性のある商談を特定"""
    print(f"\n🔍 差額¥{target_diff:,.0f}に相当する可能性のある商談")
    print("="*50)
    
    # 受注以外のステージで金額が大きいもの
    non_jucyu_stages = {k: v for k, v in stage_analysis.items() if k != '受注'}
    
    for stage, data in sorted(non_jucyu_stages.items(), key=lambda x: x[1]['amount'], reverse=True):
        amount = data['amount']
        amount_with_tax = amount * 1.10
        count = data['count']
        
        if amount > 0:
            print(f"【{stage}】 {count}件 - ¥{amount:,.0f}（税抜き）¥{amount_with_tax:,.0f}（税込み）")
            
            # 大口商談を表示
            large_deals = sorted([d for d in data['deals'] if (d.get('Amount', 0) or 0) > 100000], 
                                key=lambda x: x.get('Amount', 0) or 0, reverse=True)
            
            for deal in large_deals[:5]:  # 上位5件
                deal_amount = deal.get('Amount', 0) or 0
                deal_name = deal.get('Deal_Name', 'N/A')[:50]
                print(f"    ¥{deal_amount:,.0f} - {deal_name}")

def main():
    """メイン処理"""
    print("="*80)
    print("📊 JT ETP 親商談・全ステージ分析（差額原因調査）")
    print("="*80)
    
    # 1. CRMトークン読み込み
    try:
        access_token = load_crm_token()
        print("✅ CRMトークン読み込み完了")
    except Exception as e:
        print(f"❌ CRMトークン読み込みエラー: {e}")
        return
    
    parent_id = '5187347000129692086'
    
    # 2. 親商談詳細取得
    parent_deal = get_parent_deal_details(access_token, parent_id)
    
    # 3. 全子商談のステージ別分析
    stage_analysis, kouki_analysis = analyze_all_children_by_stage(access_token, parent_id)
    
    # 4. 親商談込み合計
    total_amount, total_with_tax, diff = calculate_total_with_parent(parent_deal, stage_analysis)
    
    # 5. 差額原因の候補特定
    find_potential_missing_deals(stage_analysis, abs(diff))
    
    # 6. 最終結論
    print(f"\n" + "="*80)
    print("🎯 差額原因の結論")
    print("="*80)
    
    if parent_deal and parent_deal.get('Amount', 0) > 0:
        print(f"✅ 親商談に金額あり: ¥{parent_deal.get('Amount', 0):,.0f}")
    else:
        print(f"❌ 親商談に金額なし")
    
    print(f"\n📊 主要ステージ:")
    for stage, data in sorted(stage_analysis.items(), key=lambda x: x[1]['amount'], reverse=True):
        if data['amount'] > 0:
            print(f"  {stage}: {data['count']}件 ¥{data['amount']:,.0f}")
    
    print(f"\n💰 最終差額: ¥{diff:,.0f}")
    
    if abs(diff) < 100000:
        print("✅ 差額は許容範囲内")
    else:
        print("⚠️ 大きな差額があります - 要調査")

if __name__ == "__main__":
    main()