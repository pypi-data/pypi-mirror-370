"""
Basic usage examples for AdsonAI SDK
"""

import os
from adsonai_sdk import AdsonAI, get_ads

def basic_example():
    """Basic SDK usage"""
    # Get API key from environment
    api_key = os.getenv('ADSONAI_API_KEY')
    if not api_key:
        print("Set ADSONAI_API_KEY environment variable")
        return

    # Create client and get ads
    with AdsonAI(api_key=api_key) as client:
        # Test connection
        if not client.test_connection():
            print("Failed to connect to AdsonAI")
            return

        # Get contextual ads
        ads = client.get_contextual_ads("I need running shoes", max_ads=3)
        
        print(f"Found {len(ads)} ads:")
        for ad in ads:
            print(f"• {ad.brand_name}: {ad.ad_text}")

def convenience_example():
    """Using convenience function"""
    api_key = os.getenv('ADSONAI_API_KEY')
    if not api_key:
        return

    # One-liner to get ads
    ads = get_ads(api_key, "best laptop for work", max_ads=2)
    
    for ad in ads:
        print(f"{ad.brand_name} - {ad.product_name}")
        print(f"Bid: ${ad.bid_amount}")

if __name__ == "__main__":
    basic_example()
    convenience_example()