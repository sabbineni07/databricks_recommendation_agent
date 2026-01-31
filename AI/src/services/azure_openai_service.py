"""Azure OpenAI service integration."""
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from shared.config.settings import settings
from shared.utils.logging import get_logger

logger = get_logger(__name__)


class AzureOpenAIService:
    """Service for Azure OpenAI integration."""
    
    def __init__(self):
        """Initialize Azure OpenAI service."""
        # Check if we have credentials, otherwise use mock service
        if not settings.azure_openai_endpoint or not settings.azure_openai_api_key:
            logger.warning("azure_openai_credentials_missing_using_mock")
            from AI.src.services.mock_llm_service import MockLLMService
            mock_service = MockLLMService()
            self.llm = mock_service.get_llm()
            self.embeddings = mock_service.get_embeddings()
            return
        
        try:
            self.llm = AzureChatOpenAI(
                azure_endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
                azure_deployment=settings.azure_openai_deployment_name,
                temperature=0.7,
            )
            
            self.embeddings = AzureOpenAIEmbeddings(
                azure_endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
                azure_deployment=settings.azure_openai_embedding_deployment,
            )
            
            logger.info("azure_openai_service_initialized")
        except Exception as e:
            logger.warning(f"azure_openai_init_failed_using_mock: {e}")
            from AI.src.services.mock_llm_service import MockLLMService
            mock_service = MockLLMService()
            self.llm = mock_service.get_llm()
            self.embeddings = mock_service.get_embeddings()
    
    def get_llm(self) -> AzureChatOpenAI:
        """Get the LLM instance."""
        return self.llm
    
    def get_embeddings(self) -> AzureOpenAIEmbeddings:
        """Get the embeddings model."""
        return self.embeddings

