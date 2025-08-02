"""
Test script to verify DEBUG_MODE functionality.
"""

import os
import sys
sys.path.append('.')

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the functions we created
from main import is_debug_mode, debug_print, get_similarity_score

def test_debug_mode():
    """Test the DEBUG_MODE functionality."""
    
    print("Testing DEBUG_MODE Functionality")
    print("=" * 40)
    
    # Test current debug mode setting
    current_debug = is_debug_mode()
    print(f"Current DEBUG_MODE setting: {os.getenv('DEBUG_MODE', 'not set')}")
    print(f"is_debug_mode() returns: {current_debug}")
    
    # Test debug_print function
    print("\nTesting debug_print with current setting:")
    debug_print("This message should only appear if DEBUG_MODE is true")
    
    # Test with different values
    print("\nTesting different DEBUG_MODE values:")
    
    test_values = [
        ('true', True),
        ('false', False),
        ('1', True),
        ('0', False),
        ('yes', True),
        ('no', False),
        ('on', True),
        ('off', False),
        ('TRUE', True),
        ('FALSE', False),
        ('random', False)
    ]
    
    original_value = os.getenv('DEBUG_MODE', 'false')
    
    for test_val, expected in test_values:
        os.environ['DEBUG_MODE'] = test_val
        result = is_debug_mode()
        status = "✓" if result == expected else "✗"
        print(f"{status} DEBUG_MODE='{test_val}' -> is_debug_mode()={result} (expected {expected})")
    
    # Reset to original value
    os.environ['DEBUG_MODE'] = original_value
    
    print(f"\nReset DEBUG_MODE to original value: '{original_value}'")

def test_debug_with_llm():
    """Test debug mode with actual LLM functions."""
    
    print("\n" + "=" * 40)
    print("Testing DEBUG_MODE with LLM Functions")
    print("=" * 40)
    
    # Sample data
    news_item = {
        'title': 'Test News for Debug Mode',
        'description': 'Testing debug output control.',
        'content': 'This is a test to see if debug output is controlled properly.'
    }
    
    thread_item = {
        'llm_title': 'Test Thread',
        'llm_summary': 'Test thread for debugging purposes.'
    }
    
    # Test with debug mode ON
    print("Setting DEBUG_MODE=true and testing...")
    os.environ['DEBUG_MODE'] = 'true'
    
    try:
        result, is_blocked, block_reason = get_similarity_score(news_item, thread_item)
        if not is_blocked:
            print("✓ LLM call succeeded with debug output visible above")
        else:
            print(f"⚠ LLM call was blocked: {block_reason}")
    except Exception as e:
        print(f"✗ LLM call failed: {e}")
    
    # Test with debug mode OFF
    print("\nSetting DEBUG_MODE=false and testing...")
    os.environ['DEBUG_MODE'] = 'false'
    
    try:
        result, is_blocked, block_reason = get_similarity_score(news_item, thread_item)
        if not is_blocked:
            print("✓ LLM call succeeded with debug output hidden")
        else:
            print(f"⚠ LLM call was blocked: {block_reason}")
    except Exception as e:
        print(f"✗ LLM call failed: {e}")

if __name__ == "__main__":
    test_debug_mode()
    test_debug_with_llm()
