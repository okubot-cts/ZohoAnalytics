#!/usr/bin/env python3
"""
Check VERSANTコーチング Table Script
Verify if VERSANTコーチング table exists and its structure
"""

import os
import json
import time
from datetime import datetime
from zoho_analytics_api_client_final import ZohoAnalyticsAPIFinal

def execute_check_versant_coaching():
    """Check VERSANTコーチング table existence and structure"""
    
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
    
    # Check queries to execute
    check_queries = [
        ("check_versant_coaching_table.sql", "テーブル存在確認"),
        ("check_versant_coaching_structure.sql", "テーブル構造確認")
    ]
    
    for sql_file, description in check_queries:
        try:
            print(f"🔍 {description}...")
            print(f"📁 SQL file: {sql_file}")
            print()
            
            # Execute the query
            result = api.execute_query(sql_file)
            
            if result and result.get('data'):
                # Generate timestamp for filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"check_versant_coaching_{description}_{timestamp}.json"
                
                # Save results to JSON file
                with open(output_filename, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                print(f"✅ {description} completed!")
                print(f"📊 Results saved to: {output_filename}")
                print(f"📈 Total records: {len(result.get('data', []))}")
                
                # Display results
                print("\n📋 Results:")
                print("=" * 60)
                for i, record in enumerate(result['data']):
                    print(f"Record {i+1}:")
                    for key, value in record.items():
                        print(f"  {key}: {value}")
                    print()
                
            else:
                print(f"❌ No results from {description}")
                
        except Exception as e:
            print(f"❌ Error in {description}: {str(e)}")
        
        print("-" * 60)
        print()

def test_versant_coaching_direct():
    """Test direct VERSANTコーチング table access"""
    
    # Get environment variables
    access_token = os.getenv('ZOHO_ANALYTICS_ACCESS_TOKEN')
    workspace_id = os.getenv('ZOHO_ANALYTICS_WORKSPACE_ID')
    org_id = os.getenv('ZOHO_ANALYTICS_ORG_ID')
    
    if not all([access_token, workspace_id, org_id]):
        print("❌ Error: Missing required environment variables")
        return
    
    # Initialize API client
    api = ZohoAnalyticsAPIFinal(access_token, workspace_id, org_id)
    
    # Direct test queries
    test_queries = [
        'SELECT * FROM "VERSANTコーチング" LIMIT 1',
        'SELECT COUNT(*) as "総件数" FROM "VERSANTコーチング"',
        'SELECT * FROM "Versant Coaching" LIMIT 1',
        'SELECT COUNT(*) as "総件数" FROM "Versant Coaching"'
    ]
    
    for i, query in enumerate(test_queries, 1):
        try:
            print(f"🔍 Test Query {i}:")
            print(f"SQL: {query}")
            print()
            
            # Execute direct query
            result = api.execute_query_direct(query)
            
            if result and result.get('data'):
                print(f"✅ Query {i} successful!")
                print(f"📊 Records: {len(result.get('data', []))}")
                
                # Show first record
                if result['data']:
                    print("First record:")
                    for key, value in result['data'][0].items():
                        print(f"  {key}: {value}")
                
            else:
                print(f"❌ Query {i} failed or no data")
                
        except Exception as e:
            print(f"❌ Error in Query {i}: {str(e)}")
        
        print("-" * 40)
        print()

if __name__ == "__main__":
    print("🔍 VERSANTコーチングテーブル確認開始")
    print("=" * 60)
    print()
    
    execute_check_versant_coaching()
    
    print("🔍 直接テストクエリ実行")
    print("=" * 60)
    print()
    
    test_versant_coaching_direct() 