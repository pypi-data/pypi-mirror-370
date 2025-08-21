#!/usr/bin/env python
"""
Test raw REST API calls to mindzie API without using the SDK.
This helps debug authentication issues.
"""

import os
import requests
import json
from pathlib import Path

# Try to load .env file
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f"Loaded credentials from {env_file}")
except ImportError:
    pass

def test_unauthenticated_ping():
    """Test the unauthenticated ping endpoint - should always work."""
    print("\n" + "=" * 60)
    print("TEST 1: Unauthenticated Ping (No credentials needed)")
    print("=" * 60)
    
    # This endpoint doesn't require authentication
    url = "https://dev.mindziestudio.com/api/hello-world-test/hello-world-test/ping/unauthorizedping"
    
    print(f"URL: {url}")
    print("Headers: None (no authentication)")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("\n[SUCCESS] Unauthenticated endpoint works!")
        else:
            print(f"\n[FAILED] Got status {response.status_code}")
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
    
    return response.status_code == 200

def test_authenticated_ping_apikey():
    """Test authenticated ping with API Key in header."""
    print("\n" + "=" * 60)
    print("TEST 2: Authenticated Ping with API Key Header")
    print("=" * 60)
    
    tenant_id = os.getenv("MINDZIE_TENANT_ID")
    api_key = os.getenv("MINDZIE_API_KEY")
    
    if not tenant_id or not api_key:
        print("[X] Missing credentials in environment")
        return False
    
    print(f"Tenant ID: {tenant_id[:8]}...{tenant_id[-4:]}")
    print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
    
    # Try authenticated endpoint
    url = f"https://dev.mindziestudio.com/api/{tenant_id}/{tenant_id}/ping/ping"
    
    # Try different header formats (Bearer should work based on C# code)
    header_formats = [
        {"Authorization": f"Bearer {api_key}"},  # This is the correct format
        {"X-API-Key": api_key},  # Legacy format (won't work)
        {"Authorization": f"ApiKey {api_key}"},  # Old format (won't work)
    ]
    
    for i, headers in enumerate(header_formats, 1):
        print(f"\nAttempt {i}: Headers = {list(headers.keys())[0]}")
        print(f"URL: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"Response: {response.text}")
                print(f"\n[OK] SUCCESS with header: {list(headers.keys())[0]}")
                return True
            elif response.status_code == 401:
                print(f"[X] 401 Unauthorized")
                # Try to get error details
                try:
                    error_data = response.json()
                    print(f"Error details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Error text: {response.text}")
            else:
                print(f"[X] Status {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"[X] ERROR: {e}")
    
    print("\n[X] FAILED: No header format worked")
    return False

def test_project_endpoint():
    """Test the projects endpoint with authentication."""
    print("\n" + "=" * 60)
    print("TEST 3: Projects Endpoint")
    print("=" * 60)
    
    tenant_id = os.getenv("MINDZIE_TENANT_ID")
    api_key = os.getenv("MINDZIE_API_KEY")
    
    if not tenant_id or not api_key:
        print("[X] Missing credentials")
        return False
    
    # Try the projects endpoint
    url = f"https://dev.mindziestudio.com/api/{tenant_id}/project"
    headers = {"Authorization": f"Bearer {api_key}"}  # Use the correct Bearer format
    
    print(f"URL: {url}")
    print(f"Headers: Authorization: Bearer...")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] SUCCESS: Got {len(data.get('projects', []))} projects")
        else:
            print(f"[X] Status {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"[X] ERROR: {e}")
    
    return response.status_code == 200

def test_swagger_endpoints():
    """Check what the Swagger spec says about authentication."""
    print("\n" + "=" * 60)
    print("TEST 4: Check Swagger Documentation")
    print("=" * 60)
    
    url = "https://dev.mindziestudio.com/swagger/v1/swagger.json"
    print(f"Fetching: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            swagger = response.json()
            
            # Check security definitions
            if "securityDefinitions" in swagger:
                print("\nSecurity Definitions:")
                for name, definition in swagger["securityDefinitions"].items():
                    print(f"  - {name}: {definition}")
            
            if "security" in swagger:
                print("\nGlobal Security:")
                print(f"  {swagger['security']}")
                
            # Check a specific endpoint
            if "paths" in swagger:
                # Look for ping endpoint
                for path, methods in swagger["paths"].items():
                    if "ping" in path.lower() and "get" in methods:
                        endpoint = methods["get"]
                        if "security" in endpoint:
                            print(f"\nSecurity for {path}:")
                            print(f"  {endpoint['security']}")
                        break
            
            print("\n[OK] Swagger spec retrieved successfully")
            return True
    except Exception as e:
        print(f"[X] ERROR: {e}")
    
    return False

def main():
    print("Raw API Testing Script")
    print("=" * 60)
    
    # Check credentials
    tenant_id = os.getenv("MINDZIE_TENANT_ID")
    api_key = os.getenv("MINDZIE_API_KEY")
    
    if tenant_id and api_key:
        print(f"Tenant ID found: {tenant_id}")
        print(f"API Key found: {api_key[:20]}..." if len(api_key) > 20 else f"API Key found: {api_key}")
    else:
        print("WARNING: Credentials not found in environment")
        print("Some tests will be skipped")
    
    # Run tests
    results = []
    
    # Test 1: Unauthenticated should always work
    results.append(("Unauthenticated Ping", test_unauthenticated_ping()))
    
    # Test 2: Try different auth header formats
    if tenant_id and api_key:
        results.append(("Authenticated Ping", test_authenticated_ping_apikey()))
        results.append(("Projects Endpoint", test_project_endpoint()))
    
    # Test 3: Check Swagger
    results.append(("Swagger Check", test_swagger_endpoints()))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for test_name, passed in results:
        status = "[OK] PASS" if passed else "[X] FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "=" * 60)
    print("DEBUGGING TIPS")
    print("=" * 60)
    print("1. If unauthenticated works but authenticated fails: Check API key format")
    print("2. Common API key issues:")
    print("   - Wrong environment (dev vs prod)")
    print("   - Expired key")
    print("   - Wrong tenant ID")
    print("   - Key not activated")
    print("3. Try creating a new API key in mindzieStudio")
    print("4. Check if the API key needs a specific prefix (mz_, etc.)")

if __name__ == "__main__":
    main()