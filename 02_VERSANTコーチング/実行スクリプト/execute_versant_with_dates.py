#!/usr/bin/env python3
"""
VERSANT Coaching Report with Date Display Execution Script
Executes VERSANT coaching report with actual dates instead of D1, D2, etc.
"""

import os
import json
import time
from datetime import datetime
from zoho_analytics_api_client_final import ZohoAnalyticsAPIFinal

def execute_versant_with_dates():
    """Execute VERSANT coaching report with date display"""
    
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
    
    # SQL files to execute
    sql_files = [
        ("versant_coaching_report_answer_with_dates.sql", "日付表示版（○日前形式）"),
        ("versant_coaching_report_answer_actual_dates.sql", "実際の日付表示版（YYYY-MM-DD形式）")
    ]
    
    for sql_file, description in sql_files:
        try:
            print(f"📋 Executing {description}...")
            print(f"📁 SQL file: {sql_file}")
            print(f"🏢 Workspace ID: {workspace_id}")
            print(f"🏢 Organization ID: {org_id}")
            print(f"🎯 Product IDs: 5187347000184182087, 5187347000184182088, 5187347000159927506")
            print(f"📅 Daily counts with actual dates")
            print()
            
            # Execute the query
            result = api.execute_query(sql_file)
            
            if result:
                # Generate timestamp for filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"versant_with_dates_{description}_{timestamp}.json"
                
                # Save results to JSON file
                with open(output_filename, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                print(f"✅ {description} executed successfully!")
                print(f"📊 Results saved to: {output_filename}")
                print(f"📈 Total records: {len(result.get('data', []))}")
                
                # Display first few records as preview
                if result.get('data'):
                    print("\n📋 Preview of results:")
                    print("=" * 80)
                    for i, record in enumerate(result['data'][:2]):
                        print(f"Record {i+1}:")
                        for key, value in record.items():
                            print(f"  {key}: {value}")
                        print()
                    
                    if len(result['data']) > 2:
                        print(f"... and {len(result['data']) - 2} more records")
                    
                    # Look for the specific student
                    target_email = "naokazu.onishi@lixil.com"
                    for record in result['data']:
                        if record.get('メールアドレス') == target_email:
                            print(f"\n🎯 Found target student (naokazu.onishi@lixil.com):")
                            for key, value in record.items():
                                print(f"  {key}: {value}")
                            break
                    
                    # Summary statistics
                    total_students = len(result['data'])
                    learning_status_counts = {}
                    for record in result['data']:
                        status = record.get('学習状況', 'Unknown')
                        learning_status_counts[status] = learning_status_counts.get(status, 0) + 1
                    
                    print(f"\n📊 Summary Statistics:")
                    print(f"  Total students: {total_students}")
                    for status, count in learning_status_counts.items():
                        print(f"  {status}: {count}")
                
            else:
                print(f"❌ No results from {description}")
                
        except FileNotFoundError:
            print(f"❌ Error: SQL file '{sql_file}' not found")
        except Exception as e:
            print(f"❌ Error executing {description}: {str(e)}")
        
        print("-" * 80)
        print()

if __name__ == "__main__":
    execute_versant_with_dates() 