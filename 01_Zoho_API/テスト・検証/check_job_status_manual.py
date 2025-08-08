#!/usr/bin/env python3
"""
Manual Job Status Check Script
Checks the status of a specific job ID
"""

import os
import json
import time
import requests
from zoho_analytics_api_client_final import ZohoAnalyticsAPIFinal

def check_job_status_manual(job_id):
    """Manually check job status"""
    
    # Get environment variables
    access_token = os.getenv('ZOHO_ANALYTICS_ACCESS_TOKEN')
    workspace_id = os.getenv('ZOHO_ANALYTICS_WORKSPACE_ID')
    org_id = os.getenv('ZOHO_ANALYTICS_ORG_ID')
    
    if not all([access_token, workspace_id, org_id]):
        print("❌ Error: Missing required environment variables")
        return
    
    # Initialize API client
    api = ZohoAnalyticsAPIFinal(access_token, workspace_id, org_id)
    
    # Check job status
    status_url = f"{api.base_url}/bulk/workspaces/{workspace_id}/exportjobs/{job_id}"
    
    try:
        response = requests.get(status_url, headers=api.get_headers(), timeout=30)
        if response.status_code == 200:
            status_data = response.json()
            print(f"Job Status: {status_data}")
            
            if status_data.get('status') == 'success':
                download_url = status_data['data'].get('downloadUrl')
                if download_url:
                    print(f"✅ Download URL found: {download_url}")
                    return api.download_data(download_url)
                else:
                    print(f"❌ Download URL not found")
            else:
                print(f"Job is still {status_data.get('status', 'unknown')}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking job status: {e}")

if __name__ == "__main__":
    # Use the job ID from the previous run
    job_id = "2527115000016770005"
    check_job_status_manual(job_id) 