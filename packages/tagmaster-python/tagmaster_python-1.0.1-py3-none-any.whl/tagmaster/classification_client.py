import requests
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
import csv
import io


class TagmasterClassificationClient:
    """
    A comprehensive Python client for the Tagmaster classification API.
    
    This class provides methods to interact with all API Key Protected endpoints:
    - Project management (CRUD operations)
    - Category management (CRUD operations, import/export)
    - Text and image classification
    - Classification history and analytics
    """
    
    # Constant base URL for the API
    BASE_URL = "https://tagmaster.ai"
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Initialize the TagmasterClassificationClient.
        
        Args:
            api_key: The API key for authentication
            base_url: Optional custom base URL (defaults to https://tagmaster.ai)
            
        Raises:
            ConnectionError: If the API server is not accessible
        """
        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-API-Key': api_key
        })
        
        # Test connection during initialization
        if not self._test_connection():
            raise ConnectionError(f"Failed to connect to API server at {self.base_url}. Please check if the server is running and accessible.")
    
    def set_api_key(self, api_key: str) -> None:
        """Set or update the API key."""
        self.api_key = api_key
        self.session.headers.update({
            'X-API-Key': api_key
        })
    
    def set_base_url(self, base_url: str) -> None:
        """Set or update the base URL."""
        self.base_url = base_url
        if not self._test_connection():
            raise ConnectionError(f"Failed to connect to API server at {self.base_url}")
    
    # ============================================================================
    # PROJECT MANAGEMENT METHODS
    # ============================================================================
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """
        Get all projects for the authenticated API key.
        
        Returns:
            List of project dictionaries
            
        Raises:
            requests.RequestException: If the API request fails
        """
        url = f"{self.base_url}/api/sdk/projects"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_project(self, project_uuid: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific project by UUID.
        
        Args:
            project_uuid: The UUID of the project
            
        Returns:
            Project dictionary or None if not found
            
        Raises:
            requests.RequestException: If the API request fails
        """
        projects = self.get_projects()
        for project in projects:
            if project.get('uuid') == project_uuid:
                return project
        return None
    
    def create_project(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new project.
        
        Args:
            name: Project name (required)
            description: Project description (optional)
            
        Returns:
            Created project dictionary
            
        Raises:
            requests.RequestException: If the API request fails
            ValueError: If name is empty or invalid
        """
        if not name or not name.strip():
            raise ValueError("Project name is required and cannot be empty")
        
        url = f"{self.base_url}/api/sdk/projects"
        payload = {"name": name.strip()}
        if description:
            payload["description"] = description.strip()
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def update_project(self, project_uuid: str, name: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing project.
        
        Args:
            project_uuid: The UUID of the project to update
            name: New project name (optional)
            description: New project description (optional)
            
        Returns:
            Updated project dictionary
            
        Raises:
            requests.RequestException: If the API request fails
            ValueError: If no update fields provided
        """
        if not name and not description:
            raise ValueError("At least one field (name or description) must be provided for update")
        
        url = f"{self.base_url}/api/sdk/projects/{project_uuid}"
        payload = {}
        if name:
            payload["name"] = name.strip()
        if description:
            payload["description"] = description.strip()
        
        response = self.session.put(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def delete_project(self, project_uuid: str) -> bool:
        """
        Delete a project.
        
        Args:
            project_uuid: The UUID of the project to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            requests.RequestException: If the API request fails
        """
        url = f"{self.base_url}/api/sdk/projects/{project_uuid}"
        response = self.session.delete(url)
        response.raise_for_status()
        return True
    
    # ============================================================================
    # CATEGORY MANAGEMENT METHODS
    # ============================================================================
    
    def get_categories(self, project_uuid: str) -> List[Dict[str, Any]]:
        """
        Get all categories for a specific project.
        
        Args:
            project_uuid: The UUID of the project
            
        Returns:
            List of category dictionaries
            
        Raises:
            requests.RequestException: If the API request fails
        """
        url = f"{self.base_url}/api/sdk/categories/project/{project_uuid}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_category(self, project_uuid: str, category_uuid: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific category by UUID.
        
        Args:
            project_uuid: The UUID of the project
            category_uuid: The UUID of the category
            
        Returns:
            Category dictionary or None if not found
            
        Raises:
            requests.RequestException: If the API request fails
        """
        categories = self.get_categories(project_uuid)
        for category in categories:
            if category.get('uuid') == category_uuid:
                return category
        return None
    
    def create_category(self, project_uuid: str, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new category in a project.
        
        Args:
            project_uuid: The UUID of the project
            name: Category name (required)
            description: Category description (optional)
            
        Returns:
            Created category dictionary
            
        Raises:
            requests.RequestException: If the API request fails
            ValueError: If name is empty or invalid
        """
        if not name or not name.strip():
            raise ValueError("Category name is required and cannot be empty")
        
        url = f"{self.base_url}/api/sdk/categories/project/{project_uuid}"
        payload = {"name": name.strip()}
        if description:
            payload["description"] = description.strip()
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def update_category(self, project_uuid: str, category_uuid: str, name: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing category.
        
        Args:
            project_uuid: The UUID of the project
            category_uuid: The UUID of the category to update
            name: New category name (optional)
            description: New category description (optional)
            
        Returns:
            Updated category dictionary
            
        Raises:
            requests.RequestException: If the API request fails
            ValueError: If no update fields provided
        """
        if not name and not description:
            raise ValueError("At least one field (name or description) must be provided for update")
        
        url = f"{self.base_url}/api/sdk/categories/{category_uuid}"
        payload = {}
        if name:
            payload["name"] = name.strip()
        if description:
            payload["description"] = description.strip()
        
        response = self.session.put(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def delete_category(self, category_uuid: str) -> bool:
        """
        Delete a category.
        
        Args:
            category_uuid: The UUID of the category to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            requests.RequestException: If the API request fails
        """
        url = f"{self.base_url}/api/sdk/categories/{category_uuid}"
        response = self.session.delete(url)
        response.raise_for_status()
        return True
    
    def bulk_delete_categories(self, category_uuids: List[str]) -> Dict[str, Any]:
        """
        Delete multiple categories at once.
        
        Args:
            category_uuids: List of category UUIDs to delete
            
        Returns:
            Response dictionary with deletion results
            
        Raises:
            requests.RequestException: If the API request fails
            ValueError: If no UUIDs provided
        """
        if not category_uuids:
            raise ValueError("At least one category UUID must be provided")
        
        url = f"{self.base_url}/api/sdk/categories/bulk-delete"
        payload = {"categoryIds": category_uuids}
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def import_categories_csv(self, project_uuid: str, csv_file_path: str) -> Dict[str, Any]:
        """
        Import categories from a CSV file.
        
        Args:
            project_uuid: The UUID of the project
            csv_file_path: Path to the CSV file
            
        Returns:
            Response dictionary with import results
            
        Raises:
            requests.RequestException: If the API request fails
            FileNotFoundError: If CSV file doesn't exist
        """
        url = f"{self.base_url}/api/sdk/categories/project/{project_uuid}/import"
        
        with open(csv_file_path, 'rb') as file:
            files = {'file': (csv_file_path, file, 'text/csv')}
            response = self.session.post(url, files=files)
        
        response.raise_for_status()
        return response.json()
    
    def export_categories_csv(self, project_uuid: str, output_file_path: Optional[str] = None) -> str:
        """
        Export categories to a CSV file.
        
        Args:
            project_uuid: The UUID of the project
            output_file_path: Optional output file path (defaults to auto-generated name)
            
        Returns:
            Path to the exported CSV file
            
        Raises:
            requests.RequestException: If the API request fails
        """
        url = f"{self.base_url}/api/sdk/categories/project/{project_uuid}/export"
        response = self.session.get(url)
        response.raise_for_status()
        
        if not output_file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file_path = f"categories_export_{project_uuid}_{timestamp}.csv"
        
        with open(output_file_path, 'w', newline='', encoding='utf-8') as file:
            file.write(response.text)
        
        return output_file_path
    
    # ============================================================================
    # CLASSIFICATION METHODS
    # ============================================================================
    
    def classify_text(self, text: str) -> Dict[str, Any]:
        """
        Classify the given text using the API.
        
        Args:
            text: The text to classify
            
        Returns:
            Dictionary containing the classification results
            
        Raises:
            requests.RequestException: If the API request fails
            ValueError: If the response format is invalid
        """
        url = f"{self.base_url}/api/sdk/classify"
        payload = {"data": text}
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            raise requests.RequestException(f"API request failed: {str(e)}")
        except (KeyError, TypeError) as e:
            raise ValueError(f"Invalid response format: {str(e)}")
    
    def classify_image(self, image_url: str) -> Dict[str, Any]:
        """
        Classify an image using the API.
        
        Args:
            image_url: URL of the image to classify
            
        Returns:
            Dictionary containing the classification results
            
        Raises:
            requests.RequestException: If the API request fails
            ValueError: If the response format is invalid
        """
        url = f"{self.base_url}/api/sdk/classify/image"
        payload = {"fileUrl": image_url}
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            raise requests.RequestException(f"API request failed: {str(e)}")
        except (KeyError, TypeError) as e:
            raise ValueError(f"Invalid response format: {str(e)}")
    
    # ============================================================================
    # CLASSIFICATION HISTORY METHODS
    # ============================================================================
    
    def get_classification_history(self, 
                                 limit: int = 50, 
                                 offset: int = 0,
                                 classification_type: Optional[str] = None,
                                 success: Optional[bool] = None,
                                 start_date: Optional[Union[str, date, datetime]] = None,
                                 end_date: Optional[Union[str, date, datetime]] = None) -> Dict[str, Any]:
        """
        Get classification history with optional filtering.
        
        Args:
            limit: Number of records to return (max 100, default 50)
            offset: Number of records to skip (default 0)
            classification_type: Filter by type ('text' or 'image')
            success: Filter by success status (True/False)
            start_date: Filter by start date (string in YYYY-MM-DD format, or date/datetime object)
            end_date: Filter by end date (string in YYYY-MM-DD format, or date/datetime object)
            
        Returns:
            Dictionary containing classification history and pagination info
            
        Raises:
            requests.RequestException: If the API request fails
            ValueError: If date format is invalid
        """
        url = f"{self.base_url}/api/sdk/classification-history"
        params = {
            'limit': min(max(limit, 1), 100),
            'offset': max(offset, 0)
        }
        
        if classification_type:
            params['type'] = classification_type
        if success is not None:
            params['success'] = success
        
        # Handle date formatting
        if start_date:
            if isinstance(start_date, (date, datetime)):
                params['startDate'] = start_date.strftime('%Y-%m-%d')
            else:
                params['startDate'] = start_date
        
        if end_date:
            if isinstance(end_date, (date, datetime)):
                params['endDate'] = end_date.strftime('%Y-%m-%d')
            else:
                params['endDate'] = end_date
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_classification_request(self, request_uuid: str) -> Dict[str, Any]:
        """
        Get details of a specific classification request.
        
        Args:
            request_uuid: The UUID of the classification request
            
        Returns:
            Dictionary containing the classification request details
            
        Raises:
            requests.RequestException: If the API request fails
        """
        url = f"{self.base_url}/api/sdk/classification-history/{request_uuid}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_classification_stats(self, 
                               start_date: Optional[Union[str, date, datetime]] = None,
                               end_date: Optional[Union[str, date, datetime]] = None) -> Dict[str, Any]:
        """
        Get classification statistics and analytics.
        
        Args:
            start_date: Filter by start date (string in YYYY-MM-DD format, or date/datetime object)
            end_date: Filter by end date (string in YYYY-MM-DD format, or date/datetime object)
            
        Returns:
            Dictionary containing classification statistics
            
        Raises:
            requests.RequestException: If the API request fails
        """
        url = f"{self.base_url}/api/sdk/classification-history/stats"
        params = {}
        
        # Handle date formatting
        if start_date:
            if isinstance(start_date, (date, datetime)):
                params['startDate'] = start_date.strftime('%Y-%m-%d')
            else:
                params['startDate'] = start_date
        
        if end_date:
            if isinstance(end_date, (date, datetime)):
                params['endDate'] = end_date.strftime('%Y-%m-%d')
            else:
                params['endDate'] = end_date
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def export_classification_history_csv(self, 
                                        output_file_path: Optional[str] = None,
                                        start_date: Optional[Union[str, date, datetime]] = None,
                                        end_date: Optional[Union[str, date, datetime]] = None) -> str:
        """
        Export classification history to a CSV file.
        
        Args:
            output_file_path: Optional output file path (defaults to auto-generated name)
            start_date: Filter by start date (string in YYYY-MM-DD format, or date/datetime object)
            end_date: Filter by end date (string in YYYY-MM-DD format, or date/datetime object)
            
        Returns:
            Path to the exported CSV file
            
        Raises:
            requests.RequestException: If the API request fails
        """
        url = f"{self.base_url}/api/sdk/classification-history/export"
        params = {}
        
        # Handle date formatting
        if start_date:
            if isinstance(start_date, (date, datetime)):
                params['startDate'] = start_date.strftime('%Y-%m-%d')
            else:
                params['startDate'] = start_date
        
        if end_date:
            if isinstance(end_date, (date, datetime)):
                params['endDate'] = end_date.strftime('%Y-%m-%d')
            else:
                params['endDate'] = end_date
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        if not output_file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file_path = f"classification_history_export_{timestamp}.csv"
        
        with open(output_file_path, 'w', newline='', encoding='utf-8') as file:
            file.write(response.text)
        
        return output_file_path
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _test_connection(self) -> bool:
        """
        Test the connection to the API server.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get the health status of the API server.
        
        Returns:
            Dictionary containing health status information
            
        Raises:
            requests.RequestException: If the API request fails
        """
        url = f"{self.base_url}/health"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_remaining_requests(self) -> Optional[int]:
        """
        Get the number of remaining requests in the current subscription.
        
        Returns:
            Number of remaining requests or None if not available
            
        Raises:
            requests.RequestException: If the API request fails
        """
        try:
            # Try to get projects to check subscription status
            projects = self.get_projects()
            if projects:
                # The API key middleware should have validated the subscription
                # We can't directly get remaining requests, but we can infer from successful calls
                return "Unlimited"  # This is a placeholder - actual implementation depends on API response
        except requests.RequestException:
            pass
        return None


def main():
    """Example usage of the TagmasterClassificationClient."""
    # Test text
    test_text = "Customer is having trouble logging into their account and needs password reset"
    
    print("Testing Tagmaster Classification API...")
    print(f"Input data: {test_text}")
    print("---")
    
    try:
        # Initialize the client (connection test happens automatically)
        client = TagmasterClassificationClient(api_key="your-api-key-here")  # Replace with your actual API key
        
        # Test health check
        health = client.get_health_status()
        print(f"✅ Health check: {health.get('status', 'Unknown')}")
        
        # Perform classification
        result = client.classify_text(test_text)
        print("✅ Classification successful!")
        print("Raw JSON response:")
        print(json.dumps(result, indent=2))
        
        # Get projects
        projects = client.get_projects()
        print(f"✅ Retrieved {len(projects)} projects")
        
    except ConnectionError as e:
        print(f"❌ Connection Error: {e}")
    except requests.RequestException as e:
        print(f"❌ API Error: {e}")
    except ValueError as e:
        print(f"❌ Data Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")


if __name__ == "__main__":
    main() 