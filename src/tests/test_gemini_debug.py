"""
Test script to debug Gemini client configuration and response.
"""

import os
import sys
sys.path.append('.')

from dotenv import load_dotenv
from llm_clients import get_llm_client

# Load environment variables
load_dotenv()

def test_gemini_client():
    """Test Gemini client configuration and simple response."""
    
    print("Testing Gemini Client Configuration")
    print("=" * 40)
    
    # Check environment variables
    provider = os.getenv('LLM_PROVIDER', 'azure')
    gemini_api_key = os.getenv('GEMINI_API_KEY', 'not_set')
    chat_model = os.getenv('GEMINI_CHAT_MODEL', 'gemini-2.0-flash')
    
    print(f"LLM_PROVIDER: {provider}")
    print(f"GEMINI_API_KEY: {'***' + gemini_api_key[-4:] if len(gemini_api_key) > 4 else 'not_set'}")
    print(f"GEMINI_CHAT_MODEL: {chat_model}")
    
    if provider != 'gemini':
        print(f"⚠ Warning: LLM_PROVIDER is set to '{provider}', not 'gemini'")
        return
    
    if gemini_api_key == 'your-gemini-api-key-here' or gemini_api_key == 'not_set':
        print("⚠ Warning: GEMINI_API_KEY appears to be not properly configured")
        return
    
    try:
        # Get the LLM client
        client = get_llm_client()
        print(f"✓ Successfully created Gemini client: {type(client).__name__}")
        
        # Test with a very simple prompt first
        simple_prompt = "Say 'Hello World' as JSON: {\"message\": \"Hello World\"}"
        print(f"\nTesting with simple prompt: '{simple_prompt}'")
        
        response, is_blocked, block_reason = client.get_chat_completion(simple_prompt, temperature=0.1)
        
        if is_blocked:
            print(f"⚠ Chat completion was blocked: {block_reason}")
        else:
            print(f"✓ Chat completion successful")
            print(f"Raw response: '{response}'")
            
            # Try to parse as JSON
            try:
                import json
                parsed = json.loads(response)
                print(f"✓ Successfully parsed as JSON: {parsed}")
            except json.JSONDecodeError as e:
                print(f"⚠ Failed to parse response as JSON: {e}")
        
    except Exception as e:
        print(f"✗ Error testing Gemini client: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini_client()
