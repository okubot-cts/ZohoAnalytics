#!/usr/bin/env python3
"""
Debug Script for naokazu.onishi@lixil.com
Detailed analysis of contact, arrangement, and VERSANT data
"""

import os
import json
import time
from datetime import datetime
from zoho_analytics_api_client_final import ZohoAnalyticsAPIFinal

def execute_debug_naokazu():
    """Execute debug query for naokazu.onishi@lixil.com"""
    
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
    
    # Read the debug SQL query
    sql_file_path = "debug_naokazu_detailed.sql"
    
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_query = f.read()
        
        print(f"🔍 Executing detailed debug query for naokazu.onishi@lixil.com...")
        print(f"📁 SQL file: {sql_file_path}")
        print()
        
        # Execute the query
        result = api.execute_query(sql_file_path)
        
        if result and result.get('data'):
            # Generate timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"debug_naokazu_result_{timestamp}.json"
            
            # Save results to JSON file
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Debug query executed successfully!")
            print(f"📊 Results saved to: {output_filename}")
            print(f"📈 Total records: {len(result.get('data', []))}")
            
            # Analyze results by data type
            data_by_type = {}
            for record in result['data']:
                data_type = record.get('データ種別', 'Unknown')
                if data_type not in data_by_type:
                    data_by_type[data_type] = []
                data_by_type[data_type].append(record)
            
            print("\n📋 Analysis by Data Type:")
            print("=" * 80)
            
            for data_type, records in data_by_type.items():
                print(f"\n🔍 {data_type}:")
                print(f"   📊 Count: {len(records)}")
                
                for i, record in enumerate(records):
                    print(f"   Record {i+1}:")
                    for key, value in record.items():
                        if key != 'データ種別':
                            print(f"     {key}: {value}")
                    print()
                
                # Special analysis for VERSANT data
                if 'VERSANT' in data_type:
                    print(f"   📅 Date range analysis:")
                    dates = [record.get('回答日') for record in records if record.get('回答日')]
                    if dates:
                        print(f"     Earliest: {min(dates)}")
                        print(f"     Latest: {max(dates)}")
                        print(f"     Total unique dates: {len(set(dates))}")
                        
                        # Count by date
                        date_counts = {}
                        for record in records:
                            date = record.get('回答日')
                            if date:
                                date_counts[date] = date_counts.get(date, 0) + 1
                        
                        print(f"     Daily counts:")
                        for date, count in sorted(date_counts.items()):
                            print(f"       {date}: {count} submissions")
            
            # Summary
            print(f"\n📊 Summary:")
            for data_type, records in data_by_type.items():
                print(f"  {data_type}: {len(records)} records")
            
        else:
            print("❌ No results returned from the debug query")
            
    except FileNotFoundError:
        print(f"❌ Error: SQL file '{sql_file_path}' not found")
    except Exception as e:
        print(f"❌ Error executing debug query: {str(e)}")

if __name__ == "__main__":
    execute_debug_naokazu() 