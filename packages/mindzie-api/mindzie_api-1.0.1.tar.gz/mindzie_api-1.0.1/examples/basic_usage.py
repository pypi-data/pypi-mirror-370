"""
Basic usage example for Mindzie API Python Client.

This script demonstrates the fundamental operations you can perform
with the Mindzie API client library.
"""

import os
from dotenv import load_dotenv
from mindzie_api import MindzieAPIClient
from mindzie_api.exceptions import MindzieAPIException

# Load environment variables
load_dotenv()


def main():
    """Main example function."""
    
    # Initialize the client
    print("Initializing Mindzie API client...")
    client = MindzieAPIClient(
        base_url=os.getenv("MINDZIE_API_URL", "https://dev.mindziestudio.com"),
        tenant_id=os.getenv("MINDZIE_TENANT_ID"),
        api_key=os.getenv("MINDZIE_API_KEY")
    )
    
    try:
        # Test connectivity
        print("\n1. Testing connectivity...")
        ping_result = client.projects.ping()
        print(f"   ✓ {ping_result}")
        
        # Get all projects
        print("\n2. Fetching projects...")
        projects_response = client.projects.get_all(page=1, page_size=10)
        print(f"   Found {projects_response.total_count} projects")
        
        if projects_response.projects:
            # Display first few projects
            for i, project in enumerate(projects_response.projects[:3], 1):
                print(f"   {i}. {project.project_name}")
                print(f"      - ID: {project.project_id}")
                print(f"      - Datasets: {project.dataset_count}")
                print(f"      - Dashboards: {project.dashboard_count}")
            
            # Get details of the first project
            first_project = projects_response.projects[0]
            print(f"\n3. Getting details for project: {first_project.project_name}")
            
            # Get project summary
            summary = client.projects.get_summary(first_project.project_id)
            print(f"   - Total Datasets: {summary.total_datasets}")
            print(f"   - Total Investigations: {summary.total_investigations}")
            print(f"   - Total Dashboards: {summary.total_dashboards}")
            print(f"   - Storage Used: {summary.storage_used_mb:.2f} MB")
            
            # Get datasets for the project
            print(f"\n4. Fetching datasets for project...")
            datasets = client.datasets.get_all(first_project.project_id)
            
            if datasets.get("Items"):
                print(f"   Found {len(datasets['Items'])} datasets")
                for dataset in datasets["Items"][:3]:
                    print(f"   - {dataset['DatasetName']}")
            else:
                print("   No datasets found")
            
            # Get investigations
            print(f"\n5. Fetching investigations...")
            investigations = client.investigations.get_all(
                first_project.project_id,
                page=1,
                page_size=5
            )
            
            if investigations.get("Investigations"):
                print(f"   Found {investigations['TotalCount']} investigations")
                for inv in investigations["Investigations"][:3]:
                    print(f"   - {inv['InvestigationName']}")
            else:
                print("   No investigations found")
            
            # Get dashboards
            print(f"\n6. Fetching dashboards...")
            dashboards = client.dashboards.get_all(
                first_project.project_id,
                page=1,
                page_size=5
            )
            
            if dashboards.get("Dashboards"):
                print(f"   Found {dashboards['TotalCount']} dashboards")
                for dash in dashboards["Dashboards"][:3]:
                    print(f"   - {dash['Name']}")
                    if dash.get("Url"):
                        print(f"     URL: {dash['Url']}")
            else:
                print("   No dashboards found")
        
        else:
            print("   No projects found. Please create a project first.")
        
        print("\n✅ Basic usage example completed successfully!")
        
    except MindzieAPIException as e:
        print(f"\n❌ API Error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        # Clean up
        client.close()
        print("\nClient connection closed.")


if __name__ == "__main__":
    main()