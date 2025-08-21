#!/usr/bin/env python
"""
Hello World with .env file support for mindzie-api package.

This version automatically loads credentials from a .env file,
making it easier to manage credentials during development.
"""

import os
import sys
from pathlib import Path

# Try to import python-dotenv (for .env file support)
try:
    from dotenv import load_dotenv
    # Load .env file if it exists
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f"Loaded credentials from {env_file}")
except ImportError:
    print("Note: python-dotenv not installed. Using system environment variables only.")
    print("To use .env files, run: pip install python-dotenv\n")

from mindzie_api import MindzieAPIClient

def main():
    print("mindzie-api Hello World - With .env Support")
    print("=" * 50)
    
    # Get credentials from environment (now includes .env file)
    tenant_id = os.getenv("MINDZIE_TENANT_ID")
    api_key = os.getenv("MINDZIE_API_KEY")
    
    # Check if credentials are set
    if not tenant_id or not api_key:
        print("\n[ERROR] Missing required credentials!")
        print("\nQuick Setup:")
        print("1. Copy .env.template to .env")
        print("2. Edit .env and add your credentials")
        print("3. Run this script again")
        print("\nAlternatively, set environment variables:")
        print('  set MINDZIE_TENANT_ID="your-tenant-id"')
        print('  set MINDZIE_API_KEY="your-api-key"')
        return 1
    
    # Show what we're using (masked)
    print(f"\nUsing credentials:")
    print(f"  Tenant ID: {tenant_id[:8]}...{tenant_id[-4:]}")
    print(f"  API Key: {api_key[:10]}...{api_key[-4:]}")
    
    # Create client
    print("\nConnecting to API...")
    client = MindzieAPIClient(
        base_url="https://dev.mindziestudio.com",
        tenant_id=tenant_id,
        api_key=api_key
    )
    
    try:
        # Test authentication
        response = client.ping.ping()
        print(f"\n[SUCCESS] Authenticated!")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"\n[ERROR] Authentication failed: {e}")
        return 1
    
    finally:
        client.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())