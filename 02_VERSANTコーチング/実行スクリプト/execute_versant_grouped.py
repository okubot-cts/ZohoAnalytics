#!/usr/bin/env python3
"""
VERSANT Coaching Report Grouped Execution Script
Executes the grouped VERSANT coaching report to avoid duplicate records per student
"""

import os
import json
import time
from datetime import datetime
from zoho_analytics_api_client_final import ZohoAnalyticsAPIFinal

def execute_versant_grouped():
    """Execute the grouped VERSANT coaching report"""
    
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
    
    # Read the grouped SQL query
    sql_file_path = "versant_coaching_report_complete_grouped.sql"
    
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_query = f.read()
        
        print(f"📋 Executing grouped VERSANT coaching report...")
        print(f"📁 SQL file: {sql_file_path}")
        print(f"🏢 Workspace ID: {workspace_id}")
        print(f"🏢 Organization ID: {org_id}")
        print(f"🎯 Product IDs: 5187347000184182087, 5187347000184182088, 5187347000159927506")
        print(f"📅 Daily counts with actual dates")
        print(f"🏢 Includes: Account name, Product names (concatenated), Learning start date")
        print(f"👥 Grouped by student to avoid duplicates")
        print()
        
        # Execute the query
        result = api.execute_query(sql_file_path)
        
        if result:
            # Generate timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"versant_grouped_result_{timestamp}.json"
            
            # Save results to JSON file
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Grouped VERSANT coaching report executed successfully!")
            print(f"📊 Results saved to: {output_filename}")
            print(f"📈 Total records: {len(result.get('data', []))}")
            
            # Display first few records as preview
            if result.get('data'):
                print("\n📋 Preview of results:")
                print("=" * 100)
                for i, record in enumerate(result['data'][:3]):
                    print(f"Record {i+1}:")
                    for key, value in record.items():
                        print(f"  {key}: {value}")
                    print()
                
                if len(result['data']) > 3:
                    print(f"... and {len(result['data']) - 3} more records")
                
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
                product_counts = {}
                account_counts = {}
                
                for record in result['data']:
                    status = record.get('学習状況', 'Unknown')
                    learning_status_counts[status] = learning_status_counts.get(status, 0) + 1
                    
                    products = record.get('商品名', 'Unknown')
                    if products and products != 'Unknown':
                        # Split multiple products and count each
                        for product in products.split(', '):
                            product_counts[product.strip()] = product_counts.get(product.strip(), 0) + 1
                    
                    account = record.get('会社名', 'Unknown')
                    account_counts[account] = account_counts.get(account, 0) + 1
                
                print(f"\n📊 Summary Statistics:")
                print(f"  Total students: {total_students}")
                
                print(f"\n📈 Learning Status:")
                for status, count in learning_status_counts.items():
                    print(f"  {status}: {count}")
                
                print(f"\n🏢 Companies:")
                for account, count in account_counts.items():
                    print(f"  {account}: {count}")
                
                print(f"\n📦 Products (individual count):")
                for product, count in product_counts.items():
                    print(f"  {product}: {count}")
                
                # Check if naokazu.onishi@lixil.com has the expected count
                target_found = False
                for record in result['data']:
                    if record.get('メールアドレス') == target_email:
                        target_found = True
                        total_count = record.get('全期間合計', 0)
                        three_week_count = record.get('3週間合計', 0)
                        product_names = record.get('商品名', 'Unknown')
                        account_name = record.get('会社名', 'Unknown')
                        learning_start = record.get('学習開始日', 'Unknown')
                        
                        print(f"\n🔍 Target student analysis:")
                        print(f"  Email: {target_email}")
                        print(f"  Company: {account_name}")
                        print(f"  Products: {product_names}")
                        print(f"  Learning Start: {learning_start}")
                        print(f"  Total submissions: {total_count}")
                        print(f"  3-week submissions: {three_week_count}")
                        if total_count >= 165:
                            print(f"  ✅ Expected count (165+) found!")
                        else:
                            print(f"  ⚠️  Count ({total_count}) is less than expected (165+)")
                        break
                
                if not target_found:
                    print(f"\n⚠️  Target student ({target_email}) not found in results")
                
                # Check for duplicate students
                email_counts = {}
                for record in result['data']:
                    email = record.get('メールアドレス')
                    if email:
                        email_counts[email] = email_counts.get(email, 0) + 1
                
                duplicates = {email: count for email, count in email_counts.items() if count > 1}
                if duplicates:
                    print(f"\n⚠️  Found duplicate students:")
                    for email, count in duplicates.items():
                        print(f"  {email}: {count} records")
                else:
                    print(f"\n✅ No duplicate students found - grouping successful!")
            
        else:
            print("❌ No results returned from the query")
            
    except FileNotFoundError:
        print(f"❌ Error: SQL file '{sql_file_path}' not found")
    except Exception as e:
        print(f"❌ Error executing query: {str(e)}")

if __name__ == "__main__":
    execute_versant_grouped() 