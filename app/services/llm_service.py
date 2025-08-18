import asyncio
from typing import List, Dict, Optional, Any

# LangChain components for different providers
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_groq import ChatGroq
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

# Utility imports for config and secrets
from app.utils.env_loader import settings
from app.utils.config_loader import load_config

class LLMService:
    """
    A centralized service to get configured LLM and Embedding models
    from various providers based on the config.yml file.
    """
    def __init__(self):
        self.config = load_config()
        print("✅ LLMService initialized with config.")

    def get_llm(self, provider: Optional[str] = None) -> Any:
        """
        Gets a configured LangChain Chat Model instance for a specific provider.
        If no provider is specified, it uses the default from config.yml.
        """
        if provider is None:
            provider = self.config['llm']['default_provider']
        
        model_name = self.config['llm']['providers'][provider]['model_name']
        print(f"   ↳ Getting LLM for provider: '{provider}', model: '{model_name}'")

        if provider == "openai":
            return ChatOpenAI(model=model_name, api_key=settings.OPENAI_API_KEY)
        elif provider == "groq":
            return ChatGroq(model=model_name, api_key=settings.GROQ_API_KEY)
        elif provider == "google":
            return ChatGoogleGenerativeAI(model=model_name, google_api_key=settings.GOOGLE_API_KEY)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def get_embedding_model(self, provider: Optional[str] = None) -> Any:
        """
        Gets a configured LangChain Embedding Model instance.
        If no provider is specified, it uses the default from config.yml.
        """
        if provider is None:
            provider = self.config['embedding_model']['default_provider']

        model_name = self.config['embedding_model']['providers'][provider]['model_name']
        print(f"   ↳ Getting Embedding Model for provider: '{provider}', model: '{model_name}'")

        if provider == "openai":
            return OpenAIEmbeddings(model=model_name, api_key=settings.OPENAI_API_KEY)
        elif provider == "google":
            return GoogleGenerativeAIEmbeddings(model=model_name, google_api_key=settings.GOOGLE_API_KEY)
        else:
            raise ValueError(f"Unsupported Embedding provider: {provider}")
            
    async def agenerate(self, messages: List[Dict], provider: Optional[str] = None) -> str:
        """
        Convenience method to generate a response using the default or specified LLM provider.
        """
        llm = self.get_llm(provider)
        response = await llm.ainvoke([{"role": "user", "content": messages[0]['content']}])
        return response.content

    async def aget_embedding(self, text: str, provider: Optional[str] = None) -> List[float]:
        """
        Convenience method to get embeddings using the default or specified provider.
        """
        embedding_model = self.get_embedding_model(provider)
        return await embedding_model.aembed_query(text)

# ==============================================================================
# ✅ TEST BLOCK
# To test this file, run `python -m app.services.llm_service` from the root directory.
# ==============================================================================
async def main():
    """Main function to test the refactored LLMService."""
    print("\n--- Running LLMService Refactor Test ---")

    try:
        service = LLMService()

        # --- 1. Test Getter Methods ---
        print("\n[1. Testing Getter Methods...]")
        default_llm = service.get_llm()
        print(f"   Default LLM loaded: {type(default_llm).__name__}")
        
        default_embedding = service.get_embedding_model()
        print(f"   Default Embedding Model loaded: {type(default_embedding).__name__}")

        groq_llm = service.get_llm(provider="groq")
        print(f"   Specific LLM (Groq) loaded: {type(groq_llm).__name__}")
        print("✅ Getter methods test passed!")


        # --- 2. Test Default Chat Model ---
        print("\n[2. Testing agenerate with default provider...]")
        test_messages = [{"role": "user", "content": "Say 'Hello, World!'"}]
        response = await service.agenerate(test_messages)
        print(f"   Default Chat Model Response: {response}")
        assert "hello" in response.lower()
        print("✅ Default chat model test passed!")

        # --- 3. Test Default Embedding Model ---
        print("\n[3. Testing aget_embedding with default provider...]")
        embedding_text = "This is a test sentence for the embedding model."
        embedding = await service.aget_embedding(embedding_text)
        
        if embedding:
            print(f"   Successfully generated an embedding vector of dimension: {len(embedding)}")
            print(f"   First 5 dimensions: {embedding[:5]}")
            print("✅ Default embedding model test passed!")
        else:
            print("❌ Default embedding model test failed.")

    except Exception as e:
        print(f"\n❌ A critical error occurred during the test: {e}")

if __name__ == "__main__":
    asyncio.run(main())