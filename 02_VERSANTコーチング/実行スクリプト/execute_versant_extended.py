#!/usr/bin/env python3
"""
VERSANT Coaching Report Extended Execution Script
Executes the extended VERSANT coaching report with longer date range
"""

import os
import json
import time
from datetime import datetime
from zoho_analytics_api_client_final import ZohoAnalyticsAPIFinal

def execute_versant_extended():
    """Execute the extended VERSANT coaching report"""
    
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
    
    # Read the extended SQL query
    sql_file_path = "versant_coaching_report_extended.sql"
    
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_query = f.read()
        
        print(f"📋 Executing extended VERSANT coaching report query...")
        print(f"📁 SQL file: {sql_file_path}")
        print(f"🏢 Workspace ID: {workspace_id}")
        print(f"🏢 Organization ID: {org_id}")
        print(f"📅 Extended date range (no product filtering)")
        print()
        
        # Execute the query
        result = api.execute_query(sql_file_path)
        
        if result:
            # Generate timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"versant_extended_result_{timestamp}.json"
            
            # Save results to JSON file
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Extended VERSANT coaching report executed successfully!")
            print(f"📊 Results saved to: {output_filename}")
            print(f"📈 Total records: {len(result.get('data', []))}")
            
            # Display first few records as preview
            if result.get('data'):
                print("\n📋 Preview of results:")
                print("=" * 80)
                for i, record in enumerate(result['data'][:10]):
                    print(f"Record {i+1}:")
                    for key, value in record.items():
                        print(f"  {key}: {value}")
                    print()
                
                if len(result['data']) > 10:
                    print(f"... and {len(result['data']) - 10} more records")
                
                # Look for the specific student
                target_email = "naokazu.onishi@lixil.com"
                for record in result['data']:
                    if record.get('メールアドレス') == target_email:
                        print(f"\n🎯 Found target student:")
                        for key, value in record.items():
                            print(f"  {key}: {value}")
                        break
            
        else:
            print("❌ No results returned from the query")
            
    except FileNotFoundError:
        print(f"❌ Error: SQL file '{sql_file_path}' not found")
    except Exception as e:
        print(f"❌ Error executing query: {str(e)}")

if __name__ == "__main__":
    execute_versant_extended() 