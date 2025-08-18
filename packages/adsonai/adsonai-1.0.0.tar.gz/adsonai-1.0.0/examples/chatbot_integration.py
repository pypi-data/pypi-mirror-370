"""
Example: Integrating AdsonAI into a chatbot
"""

import os
from adsonai_sdk import get_ads

API_KEY = os.getenv('ADSONAI_API_KEY')

def get_sponsored_response(user_message):
    """Get sponsored ad for user message"""
    if not API_KEY:
        return None
    
    try:
        ads = get_ads(API_KEY, user_message, max_ads=1)
        if ads:
            ad = ads[0]
            return f"💡 {ad.brand_name}: {ad.ad_text}"
    except:
        pass
    return None

def chatbot_loop():
    """Simple chatbot with sponsored suggestions"""
    print("🤖 Chatbot with AdsonAI integration")
    print("Type 'quit' to exit")
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == 'quit':
            break
        
        # Your normal chatbot response logic here
        print("Bot: I understand you're interested in that topic.")
        
        # Add sponsored suggestion
        sponsored = get_sponsored_response(user_input)
        if sponsored:
            print(f"Sponsored: {sponsored}")

if __name__ == "__main__":
    chatbot_loop()
