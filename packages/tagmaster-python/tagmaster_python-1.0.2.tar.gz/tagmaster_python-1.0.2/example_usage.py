#!/usr/bin/env python3
"""
Comprehensive Example Usage of Tagmaster Python Client

This example demonstrates all the available methods in the TagmasterClassificationClient
for managing projects, categories, and performing classifications.
"""

import json
import requests
from datetime import datetime, date
from tagmaster import TagmasterClassificationClient


def main():
    """Main example function demonstrating all client capabilities."""
    
    # Replace with your actual API key
    API_KEY = "your-api-key-here"
    
    print("🚀 Tagmaster Python Client - Comprehensive Example")
    print("=" * 60)
    
    try:
        # Initialize the client
        print("📡 Initializing client...")
        client = TagmasterClassificationClient(api_key=API_KEY)
        print("✅ Client initialized successfully!")
        
        # Test health check
        print("\n🏥 Testing health check...")
        health = client.get_health_status()
        print(f"✅ Health status: {health.get('status', 'Unknown')}")
        print(f"   Message: {health.get('message', 'N/A')}")
        print(f"   Uptime: {health.get('uptime', 'N/A')}")
        
        # ========================================================================
        # PROJECT MANAGEMENT EXAMPLES
        # ========================================================================
        print("\n📁 PROJECT MANAGEMENT EXAMPLES")
        print("-" * 40)
        
        # Get existing projects
        print("📋 Getting existing projects...")
        projects = client.get_projects()
        print(f"✅ Found {len(projects)} existing projects")
        
        if projects:
            # Use the first project for examples
            project = projects[0]
            project_uuid = project['uuid']
            print(f"   Using project: {project['name']} (UUID: {project_uuid})")
        else:
            # Create a new project if none exist
            print("📝 Creating new project...")
            project = client.create_project(
                name="Example Project",
                description="A project created for demonstration purposes"
            )
            project_uuid = project['uuid']
            print(f"✅ Created project: {project['name']} (UUID: {project_uuid})")
        
        # Update project
        print("✏️  Updating project...")
        updated_project = client.update_project(
            project_uuid=project_uuid,
            description="Updated description for demonstration"
        )
        print(f"✅ Updated project: {updated_project['name']}")
        
        # ========================================================================
        # CATEGORY MANAGEMENT EXAMPLES
        # ========================================================================
        print("\n🏷️  CATEGORY MANAGEMENT EXAMPLES")
        print("-" * 40)
        
        # Get existing categories
        print("📋 Getting existing categories...")
        categories = client.get_categories(project_uuid)
        print(f"✅ Found {len(categories)} existing categories")
        
        # Create new categories if none exist
        if not categories:
            print("📝 Creating sample categories...")
            
            # Create customer support categories
            support_categories = [
                ("Login Issues", "Problems with user authentication and login"),
                ("Password Reset", "Password recovery and reset requests"),
                ("Account Access", "General account access problems"),
                ("Technical Support", "Technical issues and troubleshooting"),
                ("Billing Questions", "Payment and billing inquiries")
            ]
            
            for name, description in support_categories:
                category = client.create_category(
                    project_uuid=project_uuid,
                    name=name,
                    description=description
                )
                print(f"   ✅ Created category: {category['name']}")
            
            # Refresh categories list
            categories = client.get_categories(project_uuid)
            print(f"✅ Total categories: {len(categories)}")
        
        # Get a specific category
        if categories:
            first_category = categories[0]
            category_uuid = first_category['uuid']
            print(f"📖 Getting details for category: {first_category['name']}")
            category_details = client.get_category(project_uuid, category_uuid)
            print(f"   Description: {category_details.get('description', 'N/A')}")
        
        # ========================================================================
        # CLASSIFICATION EXAMPLES
        # ========================================================================
        print("\n🤖 CLASSIFICATION EXAMPLES")
        print("-" * 40)
        
        # Text classification examples
        text_examples = [
            "Customer is having trouble logging into their account and needs password reset",
            "User reports that their payment was charged twice this month",
            "Technical issue with the mobile app crashing on startup",
            "Question about upgrading to premium subscription plan"
        ]
        
        print("📝 Performing text classifications...")
        for i, text in enumerate(text_examples, 1):
            print(f"   Example {i}: {text[:50]}...")
            try:
                result = client.classify_text(text)
                if result.get('success'):
                    classifications = result.get('classifications', [])
                    if classifications:
                        top_match = classifications[0]
                        print(f"      ✅ Top match: {top_match.get('category', 'N/A')} "
                              f"(Confidence: {top_match.get('confidence', 'N/A')}%)")
                    else:
                        print("      ⚠️  No classifications returned")
                else:
                    print(f"      ❌ Classification failed: {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"      ❌ Error: {str(e)}")
        
        # Image classification example
        print("\n🖼️  Testing image classification...")
        try:
            image_result = client.classify_image("https://example.com/sample-image.jpg")
            if image_result.get('success'):
                print("✅ Image classification successful!")
                print(f"   Provider: {image_result.get('provider', 'N/A')}")
                print(f"   Model: {image_result.get('model', 'N/A')}")
            else:
                print(f"❌ Image classification failed: {image_result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Image classification error: {str(e)}")
        
        # ========================================================================
        # CLASSIFICATION HISTORY EXAMPLES
        # ========================================================================
        print("\n📊 CLASSIFICATION HISTORY EXAMPLES")
        print("-" * 40)
        
        # Get classification history
        print("📋 Getting classification history...")
        try:
            history = client.get_classification_history(
                limit=10,
                offset=0,
                classification_type='text'
            )
            
            if history.get('success'):
                requests = history.get('requests', [])
                print(f"✅ Retrieved {len(requests)} classification requests")
                
                if requests:
                    # Show details of the most recent request
                    latest = requests[0]
                    print(f"   Latest request:")
                    print(f"     Type: {latest.get('type', 'N/A')}")
                    print(f"     Success: {latest.get('success', 'N/A')}")
                    print(f"     Created: {latest.get('createdAt', 'N/A')}")
                    print(f"     Response time: {latest.get('responseTime', 'N/A')}ms")
            else:
                print(f"❌ Failed to get history: {history.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ History retrieval error: {str(e)}")
        
        # Get classification statistics
        print("\n📈 Getting classification statistics...")
        try:
            stats = client.get_classification_stats()
            if stats.get('success'):
                statistics = stats.get('statistics', {})
                print("✅ Classification statistics:")
                print(f"   Total requests: {statistics.get('totalRequests', 'N/A')}")
                print(f"   Successful: {statistics.get('successfulRequests', 'N/A')}")
                print(f"   Failed: {statistics.get('failedRequests', 'N/A')}")
                print(f"   Average response time: {statistics.get('averageResponseTime', 'N/A')}ms")
            else:
                print(f"❌ Failed to get stats: {stats.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Statistics retrieval error: {str(e)}")
        
        # ========================================================================
        # CSV IMPORT/EXPORT EXAMPLES
        # ========================================================================
        print("\n📁 CSV IMPORT/EXPORT EXAMPLES")
        print("-" * 40)
        
        # Export categories to CSV
        print("📤 Exporting categories to CSV...")
        try:
            csv_file = client.export_categories_csv(project_uuid)
            print(f"✅ Categories exported to: {csv_file}")
        except Exception as e:
            print(f"❌ Export error: {str(e)}")
        
        # Export classification history to CSV
        print("📤 Exporting classification history to CSV...")
        try:
            history_csv = client.export_classification_history_csv(
                start_date=date.today().replace(day=1),  # First day of current month
                end_date=date.today()
            )
            print(f"✅ History exported to: {history_csv}")
        except Exception as e:
            print(f"❌ History export error: {str(e)}")
        
        # ========================================================================
        # UTILITY EXAMPLES
        # ========================================================================
        print("\n🔧 UTILITY EXAMPLES")
        print("-" * 40)
        
        # Check remaining requests
        print("🔍 Checking remaining requests...")
        remaining = client.get_remaining_requests()
        print(f"   Remaining requests: {remaining}")
        
        # Change base URL (if needed)
        print("🌐 Base URL configuration...")
        print(f"   Current base URL: {client.base_url}")
        
        # You can change the base URL if needed:
        # client.set_base_url("https://api.tagmaster.com")
        
        print("\n🎉 All examples completed successfully!")
        
    except ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print("   Please check if the API server is running and accessible.")
    except requests.RequestException as e:
        print(f"❌ API Error: {e}")
        print("   Please check your API key and server configuration.")
    except ValueError as e:
        print(f"❌ Data Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print(f"   Error type: {type(e).__name__}")


def quick_start_example():
    """Quick start example for basic usage."""
    print("\n🚀 QUICK START EXAMPLE")
    print("=" * 40)
    
    # Initialize client
    client = TagmasterClassificationClient(api_key="your-api-key-here")
    
    # Simple text classification
    text = "Customer needs help with password reset"
    result = client.classify_text(text)
    
    print(f"Input: {text}")
    print(f"Result: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    main()
    
    # Uncomment to run quick start example
    # quick_start_example() 