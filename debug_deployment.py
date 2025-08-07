#!/usr/bin/env python3
"""
Debug current RunPod deployment issues
"""

import requests
import json

API_KEY = "pa_LECM6N2DFP080KTOWB5311INUPHT36EZ2QMRB9P6wyat4e"

def list_templates():
    """List all your templates"""
    print("📋 Listing your templates...")
    
    response = requests.get(
        "https://api.runpod.io/v2/template",
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=30
    )
    
    if response.status_code == 200:
        templates = response.json()
        print(f"Found {len(templates)} templates:")
        
        for template in templates:
            print(f"\n  Template: {template.get('name', 'Unknown')}")
            print(f"    ID: {template.get('id')}")
            print(f"    Status: {template.get('status', 'Unknown')}")
            print(f"    Created: {template.get('createdAt', 'Unknown')}")
            
            # Check for build errors
            if 'buildLogs' in template and 'error' in template['buildLogs'].lower():
                print("    ⚠️ Build errors detected!")
                error_lines = [l for l in template['buildLogs'].split('\n') if 'error' in l.lower()][:5]
                for line in error_lines:
                    print(f"      {line}")
        
        return templates
    else:
        print(f"❌ Failed to list templates: {response.status_code}")
        return []

def list_endpoints():
    """List all your endpoints"""
    print("\n📋 Listing your endpoints...")
    
    response = requests.get(
        "https://api.runpod.io/v2/serverless/endpoint",
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=30
    )
    
    if response.status_code == 200:
        endpoints = response.json()
        print(f"Found {len(endpoints)} endpoints:")
        
        for endpoint in endpoints:
            print(f"\n  Endpoint: {endpoint.get('name', 'Unknown')}")
            print(f"    ID: {endpoint.get('id')}")
            print(f"    Status: {endpoint.get('status', 'Unknown')}")
            print(f"    Template: {endpoint.get('templateId')}")
            print(f"    Workers: {endpoint.get('workersMin', 0)}-{endpoint.get('workersMax', 0)}")
            print(f"    GPU: {endpoint.get('gpuIds', 'Unknown')}")
        
        return endpoints
    else:
        print(f"❌ Failed to list endpoints: {response.status_code}")
        return []

def get_endpoint_logs(endpoint_id):
    """Get logs for a specific endpoint"""
    print(f"\n📝 Getting logs for endpoint {endpoint_id}...")
    
    response = requests.get(
        f"https://api.runpod.io/v2/serverless/endpoint/{endpoint_id}/logs",
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=30
    )
    
    if response.status_code == 200:
        logs = response.json()
        if logs:
            print("Recent logs:")
            for log in logs[-20:]:  # Last 20 log entries
                print(f"  {log}")
        else:
            print("No logs available")
    else:
        print(f"❌ Failed to get logs: {response.status_code}")

def check_account_info():
    """Check account information"""
    print("👤 Checking account info...")
    
    response = requests.get(
        "https://api.runpod.io/v2/user",
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=30
    )
    
    if response.status_code == 200:
        user = response.json()
        print(f"  User: {user.get('email', 'Unknown')}")
        print(f"  Credits: ${user.get('currentSpendRate', 0):.2f}/hr")
        print(f"  Balance: ${user.get('balance', 0):.2f}")
    else:
        print(f"⚠️ Could not get account info: {response.status_code}")

def diagnose_common_issues():
    """Diagnose common deployment issues"""
    print("\n🔍 Diagnosing common issues...")
    
    issues = []
    
    # Check if API key works
    response = requests.get(
        "https://api.runpod.io/v2/user",
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=30
    )
    
    if response.status_code != 200:
        issues.append("❌ API key may be invalid or expired")
    else:
        print("✅ API key is valid")
    
    # Check for templates
    templates = list_templates()
    if not templates:
        issues.append("❌ No templates found - need to create one first")
    else:
        # Check for failed builds
        failed = [t for t in templates if t.get('status') in ['FAILED', 'ERROR']]
        if failed:
            issues.append(f"⚠️ {len(failed)} template(s) have build failures")
    
    # Check for endpoints
    endpoints = list_endpoints()
    if not endpoints:
        issues.append("❌ No endpoints found - need to create one from a template")
    
    if issues:
        print("\n⚠️ Issues found:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ No obvious issues detected")
    
    print("\n💡 Common fixes:")
    print("1. Dockerfile syntax errors - check the Dockerfile is valid")
    print("2. Package conflicts - try installing packages separately")
    print("3. CUDA version mismatch - ensure CUDA versions match across base image and packages")
    print("4. Build timeout - large images may timeout, try reducing packages")
    print("5. Insufficient disk space - 350GB may not be enough for all models")

def main():
    print("🔍 RunPod Deployment Debugger")
    print("=" * 50)
    
    # Check account
    check_account_info()
    
    # List resources
    templates = list_templates()
    endpoints = list_endpoints()
    
    # Get logs if endpoints exist
    if endpoints and len(endpoints) > 0:
        # Get logs for the first endpoint
        endpoint_id = endpoints[0].get('id')
        if endpoint_id:
            get_endpoint_logs(endpoint_id)
    
    # Diagnose issues
    diagnose_common_issues()
    
    print("\n📋 Next steps:")
    print("1. Fix any Dockerfile issues using the provided fixed version")
    print("2. Create a new template with the fixed Dockerfile")
    print("3. Wait for the build to complete (check logs)")
    print("4. Create an endpoint from the successful template")
    print("5. Test the endpoint with a health check")

if __name__ == "__main__":
    main()
