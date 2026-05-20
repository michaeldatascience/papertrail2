#!/usr/bin/env python3
"""Test OpenRouter integration"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
load_dotenv()

# Check for API key
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key or api_key == "YOUR_OPENROUTER_API_KEY_HERE":
    print("ERROR: Please set OPENROUTER_API_KEY in your .env file")
    print("Get your API key from: https://openrouter.ai/keys")
    sys.exit(1)

print("Testing OpenRouter integration...")
print(f"API Key present: {'Yes' if api_key else 'No'}")

try:
    from src.client.lm_client import LMStudioClient, VisionRequest
    from src.config import get_settings
    
    # Initialize client
    client = LMStudioClient()
    print(f"Base URL: {client.base_url}")
    print(f"Model: {client.model}")
    
    # Test health check
    print("\nTesting connection...")
    is_healthy = client.is_healthy()
    print(f"Health check: {'PASSED' if is_healthy else 'FAILED'}")
    
    # Test with a simple text-only request
    print("\nTesting text-only request...")
    test_request = VisionRequest(
        image_data="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",  # 1x1 transparent pixel
        prompt="Return JSON: {\"test\": \"success\", \"provider\": \"openrouter\"}",
        max_tokens=100,
        temperature=0.0
    )
    
    response = client.send_vision_request(test_request)
    print(f"Response received: {response.content[:100]}...")
    if response.has_json:
        print(f"JSON parsed: {response.parsed_json}")
    
    print("\nOpenRouter integration test completed successfully!")
    
except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)