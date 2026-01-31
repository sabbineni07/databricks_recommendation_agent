"""Azure AI Search service integration."""
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from shared.config.settings import settings
from shared.utils.logging import get_logger
from typing import List, Dict, Optional
from AI.src.services.azure_openai_service import AzureOpenAIService

logger = get_logger(__name__)


class AzureSearchService:
    """Service for Azure AI Search integration."""
    
    def __init__(self):
        """Initialize Azure AI Search service."""
        self.client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index_name,
            credential=AzureKeyCredential(settings.azure_search_api_key)
        )
        self.openai_service = AzureOpenAIService()
        logger.info("azure_search_service_initialized")
    
    def index_recommendation(self, recommendation: dict) -> bool:
        """Index a recommendation for semantic search.
        
        Args:
            recommendation: Recommendation dictionary to index
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate embedding
            text = f"{recommendation.get('rationale', '')} {recommendation.get('detailed_explanation', '')}"
            embedding = self.openai_service.get_embeddings().embed_query(text)
            
            document = {
                "id": recommendation["recommendation_id"],
                "job_id": recommendation.get("job_id", ""),
                "workload_type": recommendation.get("workload_type", ""),
                "content": text,
                "embedding": embedding,
                "recommendation": recommendation
            }
            
            self.client.upload_documents(documents=[document])
            logger.info("indexed_recommendation", recommendation_id=recommendation["recommendation_id"])
            return True
        except Exception as e:
            logger.error("index_recommendation_error", error=str(e))
            return False
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for similar recommendations.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            
        Returns:
            List of similar recommendations
        """
        try:
            # Generate query embedding
            query_embedding = self.openai_service.get_embeddings().embed_query(query)
            
            # Vector search
            results = self.client.search(
                search_text="",
                vector_queries=[{
                    "vector": query_embedding,
                    "k_nearest_neighbors": top_k,
                    "fields": "embedding"
                }]
            )
            
            recommendations = [result for result in results]
            logger.info("search_similar_complete", query=query, results_count=len(recommendations))
            return recommendations
        except Exception as e:
            logger.error("search_similar_error", error=str(e))
            return []

