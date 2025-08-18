# AdsonAI Python SDK

[![PyPI version](https://badge.fury.io/py/adsonai-sdk.svg)](https://badge.fury.io/py/adsonai-sdk)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Python SDK for AdsonAI - AI-powered contextual advertising platform.

## 🚀 Quick Start

### Installation

```bash
pip install adsonai-sdk
```

### Get API Key

1. Visit [AdsonAI Dashboard](https://adsonai.vercel.app/api-keys)
2. Create a new API key
3. Copy your key (starts with `adsonai_`)

### Basic Usage

```python
from adsonai_sdk import AdsonAI

# Initialize client
client = AdsonAI(api_key="your_adsonai_api_key")

# Get contextual ads
ads = client.get_contextual_ads("I need running shoes", max_ads=3)

# Display results
for ad in ads:
    print(f"🏷️  {ad.brand_name} - {ad.product_name}")
    print(f"💬 {ad.ad_text}")
    print(f"💰 Bid: ${ad.bid_amount}")
    if ad.landing_url:
        print(f"🔗 {ad.landing_url}")
    print()

client.close()
```

## 📖 Documentation

### AdsonAI Class

#### `AdsonAI(api_key, base_url=None, timeout=30)`

Initialize the AdsonAI client.

**Parameters:**
- `api_key` (str): Your AdsonAI API key
- `base_url` (str, optional): Custom API base URL
- `timeout` (int, optional): Request timeout in seconds

#### `test_connection()`

Test connection to the AdsonAI API.

**Returns:** `bool` - True if successful

#### `get_contextual_ads(query, max_ads=3, context=None)`

Get contextual ads using AI matching.

**Parameters:**
- `query` (str): User query or conversation context
- `max_ads` (int): Maximum ads to return (1-10)
- `context` (dict, optional): Additional context for matching

**Returns:** `List[Ad]` - List of matched ads

### Ad Object

**Properties:**
- `id`: Unique ad identifier
- `brand_name`: Brand or company name
- `product_name`: Product or service name
- `description`: Ad description
- `ad_text`: Display text for the ad
- `bid_amount`: Bid amount in USD
- `landing_url`: Landing page URL (optional)
- `target_keywords`: Target keywords
- `status`: Ad status

### Exception Handling

```python
from adsonai_sdk import AdsonAI, AuthenticationError, APIError, ValidationError

try:
    client = AdsonAI(api_key="your_key")
    ads = client.get_contextual_ads("search query")
except AuthenticationError:
    print("Invalid API key")
except APIError as e:
    print(f"API error: {e}")
except ValidationError as e:
    print(f"Validation error: {e}")
```

## 💡 Examples

### Context Manager

```python
with AdsonAI(api_key="your_key") as client:
    ads = client.get_contextual_ads("smart home devices")
    for ad in ads:
        print(f"{ad.brand_name}: {ad.ad_text}")
```

### Convenience Function

```python
from adsonai_sdk import get_ads

# Quick one-liner
ads = get_ads("your_key", "gaming laptop", max_ads=5)
```

### Chatbot Integration

```python
def get_sponsored_suggestion(user_message):
    try:
        ads = get_ads(API_KEY, user_message, max_ads=1)
        if ads:
            ad = ads[0]
            return f"💡 {ad.brand_name}: {ad.ad_text}"
    except Exception:
        pass
    return None

# In your chatbot
user_input = "I need a new coffee maker"
suggestion = get_sponsored_suggestion(user_input)
if suggestion:
    print(suggestion)
```

### E-commerce Integration

```python
def show_sponsored_products(search_query):
    with AdsonAI(api_key=API_KEY) as client:
        ads = client.get_contextual_ads(search_query, max_ads=3)
    
    print("🎯 Sponsored Products:")
    for ad in ads:
        print(f"• {ad.brand_name} - {ad.product_name}")
        print(f"  {ad.ad_text}")
        print(f"  ${ad.bid_amount} | {ad.landing_url}")
```

## 🔧 Advanced Usage

### With Additional Context

```python
context = {
    'user_location': 'San Francisco',
    'user_age': '25-34',
    'interests': ['fitness', 'technology'],
    'budget': 'mid-range'
}

ads = client.get_contextual_ads(
    "workout equipment", 
    max_ads=5, 
    context=context
)
```

### Error Handling with Retries

```python
import time
from adsonai_sdk import AdsonAI, APIError

def get_ads_with_retry(query, max_retries=3):
    for attempt in range(max_retries):
        try:
            with AdsonAI(api_key=API_KEY) as client:
                return client.get_contextual_ads(query)
        except APIError as e:
            if e.status_code == 429:  # Rate limit
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
    return []
```

## 🧪 Testing

```bash
# Set your API key
export ADSONAI_API_KEY="your_actual_api_key"

# Run tests
python -m pytest tests/

# Run integration test
python test_live_api.py
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Support

- 📚 Documentation: [https://docs.adsonai.com](https://docs.adsonai.com)
- 🎛️ Dashboard: [https://adsonai.vercel.app](https://adsonai.vercel.app)
- 🐛 Issues: [GitHub Issues](https://github.com/adsonai/python-sdk/issues)
- 📧 Email: developers@adsonai.com

## 🛣️ Roadmap

- [ ] Async support with `aiohttp`
- [ ] Batch ad matching
- [ ] Advanced analytics
- [ ] Webhook support
- [ ] Ad performance tracking

