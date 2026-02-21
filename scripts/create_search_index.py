#!/usr/bin/env python3
"""Create the recommendations-index in Azure AI Search.

Run this script after creating an Azure AI Search service and configuring
AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_API_KEY in .env.

Usage:
    python scripts/create_search_index.py
"""
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        SearchIndex,
        SearchField,
        SearchFieldDataType,
        SimpleField,
        SearchableField,
        VectorSearch,
        HnswAlgorithmConfiguration,
        VectorSearchProfile,
    )
    from shared.config.settings import settings
except ImportError as e:
    print(f"Import error: {e}")
    print("Ensure you have run: pip install -r requirements.txt")
    sys.exit(1)


INDEX_NAME = "recommendations-index"
VECTOR_DIMENSIONS = 1536  # text-embedding-3-small
VECTOR_CONFIG_NAME = "hnsw-config"


def create_index():
    """Create or update the recommendations-index."""
    if not settings.azure_search_endpoint or not settings.azure_search_api_key:
        print("Error: Set AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_API_KEY in .env")
        sys.exit(1)

    client = SearchIndexClient(
        endpoint=settings.azure_search_endpoint,
        credential=AzureKeyCredential(settings.azure_search_api_key),
    )

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="job_id", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="job_run_id", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="workspace_id", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="workload_type", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchField(
            name="embedding",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=VECTOR_DIMENSIONS,
            vector_search_profile_name="default-vector-profile",
        ),
        SimpleField(name="document_type", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="is_recommendation", type=SearchFieldDataType.Boolean, filterable=True),
        SimpleField(name="config_quality", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="recommendation", type=SearchFieldDataType.String),
        SimpleField(name="metrics", type=SearchFieldDataType.String),
        SimpleField(name="current_config", type=SearchFieldDataType.String),
    ]

    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name=VECTOR_CONFIG_NAME,
                kind="hnsw",
                parameters={
                    "m": 4,
                    "efConstruction": 400,
                    "efSearch": 500,
                    "metric": "cosine",
                },
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="default-vector-profile",
                algorithm_configuration_name=VECTOR_CONFIG_NAME,
            )
        ],
    )

    index = SearchIndex(
        name=INDEX_NAME,
        fields=fields,
        vector_search=vector_search,
    )

    result = client.create_or_update_index(index)
    print(f"Index '{result.name}' created/updated successfully.")
    return True


if __name__ == "__main__":
    try:
        create_index()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
