#!/usr/bin/env python3
"""
VERSANT Coaching Report Direct Execution Script
Executes the VERSANT coaching report SQL query directly without file reading
"""

import os
import json
import time
from datetime import datetime
from zoho_analytics_api_client_final import ZohoAnalyticsAPIFinal

def execute_versant_coaching_report():
    """Execute the VERSANT coaching report with daily submission counts for last 3 weeks"""
    
    # Get environment variables
    access_token = os.getenv('ZOHO_ANALYTICS_ACCESS_TOKEN')
    workspace_id = os.getenv('ZOHO_ANALYTICS_WORKSPACE_ID')
    org_id = os.getenv('ZOHO_ANALYTICS_ORG_ID')
    
    if not all([access_token, workspace_id, org_id]):
        print("❌ Error: Missing required environment variables")
        print("Please set: ZOHO_ANALYTICS_ACCESS_TOKEN, ZOHO_ANALYTICS_WORKSPACE_ID, ZOHO_ANALYTICS_ORG_ID")
        return
    
    # Initialize API client
    api = ZohoAnalyticsAPIFinal(access_token, workspace_id, org_id)
    
    # SQL query directly embedded
    sql_query = """
-- VERSANTコーチング 簡略版レポート
-- 直近3週間の提出回数を受講生別にカウント

SELECT 
    c."Id" as "受講生ID",
    CONCAT(c."Last Name", ' ', c."First Name") as "受講生名",
    c."メール" as "メールアドレス",
    c."所属会社" as "会社名",
    
    -- 直近3週間の日別件数（短縮版）
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 20 DAY) THEN 1 ELSE 0 END) as "D20",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 19 DAY) THEN 1 ELSE 0 END) as "D19",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 18 DAY) THEN 1 ELSE 0 END) as "D18",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 17 DAY) THEN 1 ELSE 0 END) as "D17",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 16 DAY) THEN 1 ELSE 0 END) as "D16",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 15 DAY) THEN 1 ELSE 0 END) as "D15",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 14 DAY) THEN 1 ELSE 0 END) as "D14",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 13 DAY) THEN 1 ELSE 0 END) as "D13",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 12 DAY) THEN 1 ELSE 0 END) as "D12",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 11 DAY) THEN 1 ELSE 0 END) as "D11",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 10 DAY) THEN 1 ELSE 0 END) as "D10",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 9 DAY) THEN 1 ELSE 0 END) as "D9",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 8 DAY) THEN 1 ELSE 0 END) as "D8",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 7 DAY) THEN 1 ELSE 0 END) as "D7",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 6 DAY) THEN 1 ELSE 0 END) as "D6",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 5 DAY) THEN 1 ELSE 0 END) as "D5",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 4 DAY) THEN 1 ELSE 0 END) as "D4",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 3 DAY) THEN 1 ELSE 0 END) as "D3",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 2 DAY) THEN 1 ELSE 0 END) as "D2",
    SUM(CASE WHEN DATE(v."Completion Date") = DATE_SUB(CURDATE(), INTERVAL 1 DAY) THEN 1 ELSE 0 END) as "D1",
    SUM(CASE WHEN DATE(v."Completion Date") = CURDATE() THEN 1 ELSE 0 END) as "今日",
    
    -- 合計と平均
    SUM(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) as "3週間合計",
    ROUND(SUM(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) / 21.0, 1) as "1日平均",
    
    -- 学習状況の判定
    CASE 
        WHEN SUM(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) = 0 THEN '未学習'
        WHEN SUM(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) < 10 THEN '学習不足'
        WHEN SUM(CASE WHEN DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY) THEN 1 ELSE 0 END) < 30 THEN '学習中'
        ELSE '積極的'
    END as "学習状況"
    
FROM "連絡先" c
INNER JOIN "手配" ar ON c."Id" = ar."連絡先"
LEFT JOIN "Versant" v ON c."Id" = v."連絡先名" 
    AND DATE(v."Completion Date") >= DATE_SUB(CURDATE(), INTERVAL 21 DAY)
WHERE ar."商品" IN (
    '5187347000184182087',
    '5187347000184182088', 
    '5187347000159927506'
)
GROUP BY 
    c."Id", c."Last Name", c."First Name", c."メール", c."所属会社"
ORDER BY 
    "学習状況" DESC, "3週間合計" DESC, c."Last Name", c."First Name"
"""
    
    try:
        print(f"📋 Executing VERSANT coaching report query...")
        print(f"🏢 Workspace ID: {workspace_id}")
        print(f"🏢 Organization ID: {org_id}")
        print()
        
        # Execute the query directly using the API client's internal method
        # We need to modify the approach to pass SQL directly
        import urllib.parse
        import requests
        
        # Create config for the API call
        config = {
            "responseFormat": "json",
            "sqlQuery": sql_query.strip()
        }
        
        config_encoded = urllib.parse.quote(json.dumps(config))
        url = f"{api.base_url}/bulk/workspaces/{workspace_id}/data?CONFIG={config_encoded}"
        
        print(f"🔄 クエリ実行中: {url[:100]}...")
        print(f"   クエリ長: {len(sql_query)}文字")
        
        try:
            response = requests.get(url, headers=api.get_headers(), timeout=60)
            print(f"   ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'jobId' in data['data']:
                    job_id = data['data']['jobId']
                    print(f"   ✅ ジョブ開始成功 (ID: {job_id})")
                    
                    # Wait for job completion
                    result = api.wait_for_job_completion(job_id)
                    
                    if result:
                        # Generate timestamp for filename
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        output_filename = f"versant_coaching_report_result_{timestamp}.json"
                        
                        # Save results to JSON file
                        with open(output_filename, 'w', encoding='utf-8') as f:
                            json.dump(result, f, ensure_ascii=False, indent=2)
                        
                        print(f"✅ VERSANT coaching report executed successfully!")
                        print(f"📊 Results saved to: {output_filename}")
                        print(f"📈 Total records: {len(result.get('data', []))}")
                        
                        # Display first few records as preview
                        if result.get('data'):
                            print("\n📋 Preview of results:")
                            print("=" * 80)
                            for i, record in enumerate(result['data'][:3]):
                                print(f"Record {i+1}:")
                                for key, value in record.items():
                                    print(f"  {key}: {value}")
                                print()
                            
                            if len(result['data']) > 3:
                                print(f"... and {len(result['data']) - 3} more records")
                        
                    else:
                        print("❌ No results returned from the query")
                else:
                    print(f"   ❌ 予期しないレスポンス形式")
                    print(f"   レスポンス: {json.dumps(data, indent=2, ensure_ascii=False)}")
            else:
                print(f"   ❌ クエリ実行失敗: {response.status_code}")
                print(f"   レスポンス: {response.text[:500]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ リクエストエラー: {e}")
            
    except Exception as e:
        print(f"❌ Error executing query: {str(e)}")

if __name__ == "__main__":
    execute_versant_coaching_report() 