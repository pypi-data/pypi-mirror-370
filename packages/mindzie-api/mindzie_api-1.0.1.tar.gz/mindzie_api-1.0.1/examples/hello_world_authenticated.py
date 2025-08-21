#!/usr/bin/env python
"""
Hello World AUTHENTICATED example for mindzie-api package.

This example shows the simplest authenticated API call.
It requires real credentials to work.

REQUIRED SETUP:
1. You need a valid Tenant ID and API Key from mindzieStudio
2. Set them as environment variables (see instructions below)
"""

import os
import sys
from pathlib import Path

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

from mindzie_api import MindzieAPIClient

def main():
    print("mindzie-api Hello World - Authenticated Example")
    print("=" * 50)
    
    # Get credentials from environment variables
    tenant_id = os.getenv("MINDZIE_TENANT_ID")
    api_key = os.getenv("MINDZIE_API_KEY")
    
    # Check if credentials are set
    if not tenant_id or not api_key:
        print("\n[ERROR] Missing required credentials!")
        print("\n" + "=" * 50)
        print("SETUP INSTRUCTIONS:")
        print("=" * 50)
        print("\nYou need to set two environment variables:")
        print("\n1. MINDZIE_TENANT_ID - Your tenant identifier")
        print("2. MINDZIE_API_KEY - Your API authentication key")
        print("\n" + "-" * 50)
        print("HOW TO GET THESE VALUES:")
        print("-" * 50)
        print("\n1. Log into mindzieStudio (https://dev.mindziestudio.com)")
        print("2. Go to Settings or API Configuration")
        print("3. Find your Tenant ID (usually a GUID like: 12345678-1234-1234-1234-123456789012)")
        print("4. Generate or copy your API Key")
        print("\n" + "-" * 50)
        print("HOW TO SET THE VARIABLES:")
        print("-" * 50)
        print("\nOption 1 - Temporary (current session only):")
        print('  set MINDZIE_TENANT_ID="your-tenant-id-here"')
        print('  set MINDZIE_API_KEY="your-api-key-here"')
        print("\nOption 2 - Permanent (Windows):")
        print("  1. Open System Properties -> Environment Variables")
        print("  2. Add new User variables for both")
        print("\nOption 3 - Use a .env file:")
        print("  1. Create a .env file in this directory")
        print("  2. Add:")
        print('     MINDZIE_TENANT_ID="your-tenant-id-here"')
        print('     MINDZIE_API_KEY="your-api-key-here"')
        print("\n" + "=" * 50)
        print("\nExample with dummy values:")
        print('  set MINDZIE_TENANT_ID="a1b2c3d4-e5f6-7890-abcd-ef1234567890"')
        print('  set MINDZIE_API_KEY="mz_prod_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890"')
        print("\n" + "=" * 50)
        return 1
    
    # Show what we're using (masked for security)
    print(f"\nUsing credentials:")
    print(f"  Tenant ID: {tenant_id[:8]}...{tenant_id[-4:]}")
    print(f"  API Key: {api_key[:10]}...{api_key[-4:]}")
    
    # Create client with real credentials
    print("\nCreating authenticated client...")
    client = MindzieAPIClient(
        base_url="https://dev.mindziestudio.com",
        tenant_id=tenant_id,
        api_key=api_key
    )
    
    try:
        # Call the authenticated ping endpoint
        print("Calling authenticated ping endpoint...")
        response = client.ping.ping()
        
        print("\n[SUCCESS] Authenticated connection established")
        print(f"Response: {response}")
        
        # Try to get projects (another authenticated call)
        print("\nTrying to list projects...")
        try:
            projects = client.projects.get_all(page_size=1)
            if hasattr(projects, 'projects') and projects.projects:
                print(f"[OK] Found {len(projects.projects)} project(s)")
                print(f"  First project: {projects.projects[0].project_name}")
            else:
                print("[OK] Connected successfully (no projects found)")
        except Exception as e:
            print(f"[OK] Connected (projects list not available: {e})")
        
        print("\n" + "=" * 50)
        print("Authentication successful! You're ready to use the API")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n[ERROR] Authentication failed: {e}")
        print("\nTroubleshooting:")
        print("1. Verify your Tenant ID is correct")
        print("2. Check your API Key is valid and not expired")
        print("3. Ensure you have access to the dev server")
        print("4. Check network connectivity to https://dev.mindziestudio.com")
        return 1
    
    finally:
        client.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())