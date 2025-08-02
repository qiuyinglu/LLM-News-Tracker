"""
Test script for the LLM client abstraction.
"""

import os
import sys
sys.path.append('.')

from dotenv import load_dotenv
from llm_clients import get_llm_client

# Load environment variables
load_dotenv()

def test_llm_clients():
    """Test the LLM client abstraction."""
    
    print("Testing LLM Client Abstraction")
    print("=" * 40)
    
    current_provider = os.getenv('LLM_PROVIDER', 'azure').lower()
    print(f"Current LLM Provider: {current_provider}")
    
    try:
        # Get the LLM client
        client = get_llm_client()
        print(f"✓ Successfully created {current_provider} client: {type(client).__name__}")
        
        # Test chat completion with a simple prompt
        test_prompt = "Briefly explain what artificial intelligence is in one sentence."
        print(f"\nTesting chat completion with prompt: '{test_prompt}'")
        
        response, is_blocked, block_reason = client.get_chat_completion(test_prompt, temperature=0.3)
        
        if is_blocked:
            print(f"⚠ Chat completion was blocked: {block_reason}")
        else:
            print(f"✓ Chat completion successful")
            print(f"Response: {response[:100]}..." if len(response) > 100 else response)
        
        # Test embedding
        test_text = "This is a test text for embedding generation."
        print(f"\nTesting embedding with text: '{test_text}'")
        
        embedding, is_blocked, block_reason = client.get_embedding(test_text)
        
        if is_blocked:
            print(f"⚠ Embedding was blocked: {block_reason}")
        else:
            print(f"✓ Embedding successful")
            print(f"Embedding dimension: {len(embedding) if embedding else 'None'}")
            if embedding:
                print(f"First 5 values: {embedding[:5]}")
        
    except Exception as e:
        print(f"✗ Error testing LLM client: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm_clients()
