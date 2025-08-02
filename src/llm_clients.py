"""
Abstract LLM client interfaces for supporting multiple LLM providers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os
import json
from openai import AzureOpenAI
import google.generativeai as genai


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def get_chat_completion(self, prompt: str, temperature: float = 0.3) -> tuple[str, bool, str]:
        """
        Get chat completion from LLM.
        
        Returns:
            tuple: (response_text, is_blocked, block_reason)
        """
        pass
    
    @abstractmethod
    def get_embedding(self, text: str) -> tuple[Optional[List[float]], bool, str]:
        """
        Get text embedding from LLM.
        
        Returns:
            tuple: (embedding_vector, is_blocked, block_reason)
        """
        pass


class AzureOpenAIClient(LLMClient):
    """Azure OpenAI implementation of LLM client."""
    
    def __init__(self):
        self.chat_client = AzureOpenAI(
            api_key=os.getenv('AOAI_API_KEY'),
            api_version=os.getenv('AOAI_API_VERSION'),
            azure_endpoint=os.getenv('AOAI_ENDPOINT')
        )
        
        self.embedding_client = AzureOpenAI(
            api_key=os.getenv('AOAI_EMBEDDING_API_KEY'),
            api_version=os.getenv('AOAI_EMBEDDING_API_VERSION'),
            azure_endpoint=os.getenv('AOAI_EMBEDDING_ENDPOINT')
        )
        
        self.chat_deployment = os.getenv('AOAI_DEPLOYMENT_NAME')
        self.embedding_deployment = os.getenv('AOAI_EMBEDDING_DEPLOYMENT_NAME')
    
    def get_chat_completion(self, prompt: str, temperature: float = 0.3) -> tuple[str, bool, str]:
        """Get chat completion from Azure OpenAI."""
        try:
            response = self.chat_client.chat.completions.create(
                model=self.chat_deployment,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature
            )
            
            content = response.choices[0].message.content.strip()
            return content, False, ""
            
        except Exception as e:
            error_msg = str(e)
            # Check for content filtering or other blocking reasons
            if any(keyword in error_msg.lower() for keyword in ['content_filter', 'blocked', 'prohibited', 'policy']):
                return "", True, error_msg
            else:
                # Re-raise for other errors
                raise e
    
    def get_embedding(self, text: str) -> tuple[Optional[List[float]], bool, str]:
        """Get embedding from Azure OpenAI."""
        try:
            response = self.embedding_client.embeddings.create(
                model=self.embedding_deployment,
                input=text
            )
            
            embedding = response.data[0].embedding
            return embedding, False, ""
            
        except Exception as e:
            error_msg = str(e)
            # Check for content filtering or other blocking reasons
            if any(keyword in error_msg.lower() for keyword in ['content_filter', 'blocked', 'prohibited', 'policy']):
                return None, True, error_msg
            else:
                # Re-raise for other errors
                raise e


class GeminiClient(LLMClient):
    """Google Gemini implementation of LLM client."""
    
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        
        self.chat_model_name = os.getenv('GEMINI_CHAT_MODEL', 'gemini-2.0-flash')
        self.embedding_model_name = os.getenv('GEMINI_EMBEDDING_MODEL', 'gemini-embedding-001')
        
        # Initialize models
        self.chat_model = genai.GenerativeModel(self.chat_model_name)
        
    def get_chat_completion(self, prompt: str, temperature: float = 0.3) -> tuple[str, bool, str]:
        """Get chat completion from Gemini."""
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=2048,
            )
            
            response = self.chat_model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Check if content was blocked
            if response.candidates and response.candidates[0].finish_reason.name in ['SAFETY', 'BLOCKED_REASON_UNSPECIFIED']:
                safety_ratings = response.candidates[0].safety_ratings if response.candidates[0].safety_ratings else []
                block_reason = f"Content blocked by Gemini safety filters: {[rating.category.name for rating in safety_ratings if rating.blocked]}"
                return "", True, block_reason
            
            content = response.text if response.text else ""
            
            # Clean up markdown code blocks that Gemini sometimes adds
            content = self._clean_response(content)
            
            return content, False, ""
            
        except Exception as e:
            error_msg = str(e)
            # Check for content filtering or other blocking reasons
            if any(keyword in error_msg.lower() for keyword in ['safety', 'blocked', 'prohibited', 'policy', 'harmful']):
                return "", True, error_msg
            else:
                # Re-raise for other errors
                raise e
    
    def _clean_response(self, content: str) -> str:
        """Clean up Gemini response by removing markdown code blocks."""
        if not content:
            return content
        
        content = content.strip()
        
        # Remove markdown JSON code blocks
        if content.startswith('```json'):
            content = content[7:]  # Remove ```json
        elif content.startswith('```'):
            content = content[3:]   # Remove ```
        
        if content.endswith('```'):
            content = content[:-3]  # Remove trailing ```
        
        return content.strip()
    
    def get_embedding(self, text: str) -> tuple[Optional[List[float]], bool, str]:
        """Get embedding from Gemini."""
        try:
            response = genai.embed_content(
                model=self.embedding_model_name,
                content=text,
                task_type="retrieval_document"
            )
            
            embedding = response['embedding']
            return embedding, False, ""
            
        except Exception as e:
            error_msg = str(e)
            # Check for content filtering or other blocking reasons
            if any(keyword in error_msg.lower() for keyword in ['safety', 'blocked', 'prohibited', 'policy', 'harmful']):
                return None, True, error_msg
            else:
                # Re-raise for other errors
                raise e


def get_llm_client() -> LLMClient:
    """Factory function to get the appropriate LLM client based on environment configuration."""
    llm_provider = os.getenv('LLM_PROVIDER', 'azure').lower()
    
    if llm_provider == 'azure':
        return AzureOpenAIClient()
    elif llm_provider == 'gemini':
        return GeminiClient()
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")
