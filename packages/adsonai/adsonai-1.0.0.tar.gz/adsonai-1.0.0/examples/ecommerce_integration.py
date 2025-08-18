"""
Example: E-commerce website integration
"""

import os
from adsonai_sdk import AdsonAI

API_KEY = os.getenv('ADSONAI_API_KEY')

def show_sponsored_products(search_query, max_results=3):
    """Show sponsored products for search query"""
    if not API_KEY:
        print("No API key configured")
        return
    
    try:
        with AdsonAI(api_key=API_KEY) as client:
            ads = client.get_contextual_ads(search_query, max_ads=max_results)
        
        if ads:
            print(f"\n🎯 Sponsored Products for '{search_query}':")
            print("-" * 50)
            
            for i, ad in enumerate(ads, 1):
                print(f"{i}. {ad.brand_name} - {ad.product_name}")
                print(f"   💬 {ad.ad_text}")
                print(f"   💰 ${ad.bid_amount}")
                if ad.landing_url:
                    print(f"   🔗 {ad.landing_url}")
                print()
        else:
            print(f"No sponsored products found for '{search_query}'")
    
    except Exception as e:
        print(f"Error getting sponsored products: {e}")

def simulate_ecommerce_search():
    """Simulate e-commerce search with sponsored results"""
    search_queries = [
        "wireless headphones",
        "coffee maker",
        "running shoes",
        "laptop bag",
        "smartphone case"
    ]
    
    print("🛒 E-commerce Search Simulation")
    print("=" * 40)
    
    for query in search_queries:
        show_sponsored_products(query, max_results=2)
        input("Press Enter for next search...")

if __name__ == "__main__":
    simulate_ecommerce_search()
