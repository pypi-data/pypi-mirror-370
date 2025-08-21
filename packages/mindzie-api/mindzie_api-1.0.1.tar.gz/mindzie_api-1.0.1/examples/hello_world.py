#!/usr/bin/env python
"""
Hello World example for mindzie-api package.

This is the simplest possible example - it connects to the dev server
and calls an unauthenticated endpoint to verify the package is working.

No API credentials required!
"""

from mindzie_api import MindzieAPIClient

def main():
    print("mindzie-api Hello World Example")
    print("=" * 40)
    
    # Create client - using dummy tenant ID since we're only calling unauthenticated endpoints
    # Note: A real tenant ID would be needed for authenticated endpoints
    client = MindzieAPIClient(
        base_url="https://dev.mindziestudio.com",
        tenant_id="hello-world-test",  # Dummy tenant ID for unauthenticated test
        api_key="not-required-for-ping"  # Dummy API key for unauthenticated test
    )
    
    try:
        # Call the unauthenticated ping endpoint
        # This doesn't require valid credentials
        print("\nCalling unauthenticated ping endpoint...")
        response = client.ping.unauthorized_ping()
        
        print("Success! The API responded:")
        print(f"Response: {response}")
        print("\nThe mindzie-api package is working correctly!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify https://dev.mindziestudio.com is accessible")
        print("3. Ensure the package is installed: pip install mindzie-api")
    
    finally:
        client.close()

if __name__ == "__main__":
    main()