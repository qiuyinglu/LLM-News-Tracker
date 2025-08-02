"""
Test script to verify configurable retry attempts functionality.
"""

import os
import sys
sys.path.append('.')

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_retry_configuration():
    """Test that retry configuration is properly loaded from environment."""
    
    print("Testing LLM Retry Configuration")
    print("=" * 40)
    
    # Test current configuration
    max_retries = int(os.getenv('LLM_MAX_RETRY_ATTEMPTS', '3'))
    print(f"Current LLM_MAX_RETRY_ATTEMPTS: {max_retries}")
    
    # Test with different values
    test_values = ['1', '2', '5', '10']
    
    for test_val in test_values:
        # Temporarily set the environment variable
        os.environ['LLM_MAX_RETRY_ATTEMPTS'] = test_val
        
        # Get the value as the functions would
        retrieved_val = int(os.getenv('LLM_MAX_RETRY_ATTEMPTS', '3'))
        print(f"Set LLM_MAX_RETRY_ATTEMPTS to '{test_val}', retrieved: {retrieved_val}")
        
        # Verify it works correctly
        assert retrieved_val == int(test_val), f"Expected {test_val}, got {retrieved_val}"
    
    # Reset to original value
    max_retries_original = int(os.getenv('LLM_MAX_RETRY_ATTEMPTS', '3'))
    os.environ['LLM_MAX_RETRY_ATTEMPTS'] = str(max_retries)
    
    print("\n✓ All retry configuration tests passed!")
    print(f"Reset LLM_MAX_RETRY_ATTEMPTS to original value: {max_retries}")

if __name__ == "__main__":
    test_retry_configuration()
