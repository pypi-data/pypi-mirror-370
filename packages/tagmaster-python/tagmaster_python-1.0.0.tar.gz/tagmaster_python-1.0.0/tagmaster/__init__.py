"""
Tagmaster Python Client

A comprehensive Python client for the Tagmaster classification API.

This client provides access to all API Key Protected endpoints:
- Project management (CRUD operations)
- Category management (CRUD operations, import/export)
- Text and image classification
- Classification history and analytics
"""

from .classification_client import TagmasterClassificationClient

__version__ = "1.0.0"
__author__ = "Tagmaster"
__email__ = "support@tagmaster.com"

__all__ = ["TagmasterClassificationClient"] 