#!/usr/bin/env python3
"""
Check Specific Student Data Script
Checks the data for naokazu.onishi@lixil.com
"""

import os
import json
from zoho_analytics_api_client_final import ZohoAnalyticsAPIFinal

def check_specific_student():
    """Check the data for the specific student"""
    
    # Get environment variables
    access_token = os.getenv('ZOHO_ANALYTICS_ACCESS_TOKEN')
    workspace_id = os.getenv('ZOHO_ANALYTICS_WORKSPACE_ID')
    org_id = os.getenv('ZOHO_ANALYTICS_ORG_ID')
    
    if not all([access_token, workspace_id, org_id]):
        print("❌ Error: Missing required environment variables")
        return
    
    # Initialize API client
    api = ZohoAnalyticsAPIFinal(access_token, workspace_id, org_id)
    
    # Execute the query
    result = api.execute_query("check_specific_student.sql")
    
    if result and result.get('data'):
        print("✅ Specific student data found:")
        print(f"📊 Total records: {len(result['data'])}")
        print()
        
        # Show all records
        for i, record in enumerate(result['data']):
            print(f"Record {i+1}:")
            for key, value in record.items():
                print(f"  {key}: {value}")
            print()
            
        # Count records in last 21 days
        from datetime import datetime, timedelta
        today = datetime.now()
        cutoff_date = today - timedelta(days=21)
        
        recent_count = 0
        for record in result['data']:
            completion_date_str = record.get('完了日', '')
            if completion_date_str:
                try:
                    completion_date = datetime.strptime(completion_date_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
                    if completion_date >= cutoff_date:
                        recent_count += 1
                except:
                    pass
        
        print(f"📅 Records in last 21 days: {recent_count}")
        print(f"📅 Total records: {len(result['data'])}")
        
    else:
        print("❌ No data found for this student")

if __name__ == "__main__":
    check_specific_student() 