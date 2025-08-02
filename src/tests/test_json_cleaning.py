"""
Test script to verify JSON cleaning and parsing functionality.
"""

import os
import sys
sys.path.append('.')

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the functions we just created
from main import clean_json_response, parse_llm_json_response

def test_json_cleaning():
    """Test the JSON cleaning functionality with problematic examples."""
    
    print("Testing JSON Cleaning and Parsing")
    print("=" * 40)
    
    # Test case 1: The problematic JSON from the user
    problematic_json = '''{
    "llm_similarity_justification": "The news article discusses the GENIUS Act, a piece of legislation in the US aimed at regulating stablecoins, and its potential impact on the cryptocurrency and DeFi landscape. It mentions key entities like Circle, the Treasury Department, and DeFi platforms. The existing thread, on the other hand, focuses on Tesla's entry into the Indian market and the lukewarm reception it's receiving from early adopters. It mentions Tesla, Elon Musk, and Indian companies like Tata Motors and Paytm.

There is virtually no overlap in topic, entities, or geographic location. The news article is about US cryptocurrency regulation, while the thread is about Tesla's market entry in India. The only very tenuous connection is that both relate to technology and business, but that's a very broad connection. There is no event connection. Therefore, the similarity is extremely low.",
    "llm_similarity_score": 2
}'''
    
    print("Test Case 1: Problematic JSON with embedded newlines")
    print("Original JSON (first 200 chars):")
    print(repr(problematic_json[:200]))
    
    try:
        # Test cleaning
        cleaned = clean_json_response(problematic_json)
        print(f"\n✓ Cleaning successful")
        
        # Test parsing
        required_fields = ['llm_similarity_score', 'llm_similarity_justification']
        result = parse_llm_json_response(problematic_json, required_fields)
        print(f"✓ Parsing successful")
        print(f"Parsed score: {result['llm_similarity_score']}")
        print(f"Justification length: {len(result['llm_similarity_justification'])} characters")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test case 2: JSON with markdown code blocks
    markdown_json = '''```json
{
    "llm_title": "Test Title",
    "llm_summary": "Test summary with
multiple lines",
    "status": "evolving"
}
```'''
    
    print("\n" + "="*40)
    print("Test Case 2: JSON wrapped in markdown")
    print("Original:")
    print(repr(markdown_json))
    
    try:
        required_fields = ['llm_title', 'llm_summary', 'status']
        result = parse_llm_json_response(markdown_json, required_fields)
        print(f"✓ Parsing successful")
        print(f"Parsed: {result}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test case 3: Valid JSON (should work without changes)
    valid_json = '''{"llm_similarity_score": 85, "llm_similarity_justification": "High similarity"}'''
    
    print("\n" + "="*40)
    print("Test Case 3: Valid JSON (should work as-is)")
    
    try:
        required_fields = ['llm_similarity_score', 'llm_similarity_justification']
        result = parse_llm_json_response(valid_json, required_fields)
        print(f"✓ Parsing successful: {result}")
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_json_cleaning()
