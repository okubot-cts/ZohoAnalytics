#!/usr/bin/env python3
"""
Test Contact Columns Script
Tests the column names in the 連絡先 table
"""

import os
import json
from zoho_analytics_api_client_final import ZohoAnalyticsAPIFinal

def test_contact_columns():
    """Test the column names in the 連絡先 table"""
    
    # Get environment variables
    access_token = os.getenv('ZOHO_ANALYTICS_ACCESS_TOKEN')
    workspace_id = os.getenv('ZOHO_ANALYTICS_WORKSPACE_ID')
    org_id = os.getenv('ZOHO_ANALYTICS_ORG_ID')
    
    if not all([access_token, workspace_id, org_id]):
        print("❌ Error: Missing required environment variables")
        return
    
    # Initialize API client
    api = ZohoAnalyticsAPIFinal(access_token, workspace_id, org_id)
    
    # Execute the test query
    result = api.execute_query("test_contact_columns.sql")
    
    if result and result.get('data'):
        print("✅ Contact table columns:")
        for key, value in result['data'][0].items():
            print(f"  {key}: {value}")
    else:
        print("❌ No results returned")

if __name__ == "__main__":
    test_contact_columns() 