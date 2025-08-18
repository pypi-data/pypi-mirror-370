"""
Main client for AdsonAI SDK
"""

import requests
import json
import logging
from typing import List, Optional
from .models import Ad
from .exceptions import AdsonAIError, AuthenticationError, APIError, ValidationError, NetworkError

# Configure logging
logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://adsonai.vercel.app"
DEFAULT_TIMEOUT = 30

class AdsonAI:
    """
    AdsonAI Python SDK Client
    
    Simple interface for getting contextual ads using AI matching.
    
    Example:
        client = AdsonAI(api_key="your_api_key")
        ads = client.get_contextual_ads("I need running shoes")
        
        for ad in ads:
            print(f"{ad.brand_name}: {ad.ad_text}")
    """
    
    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize AdsonAI client
        
        Args:
            api_key: Your AdsonAI API key (get from https://adsonai.vercel.app/api-keys)
            base_url: API base URL (optional)
            timeout: Request timeout in seconds (default: 30)
        
        Raises:
            ValueError: If api_key is empty or invalid format
        """
        if not api_key:
            raise ValueError("API key is required")
        
        if not api_key.startswith('adsonai_'):
            raise ValueError("Invalid API key format. Key should start with 'adsonai_'")
            
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        # Set up session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json',
            'User-Agent': f'AdsonAI-Python-SDK/1.0.0'
        })
        
        logger.info(f"AdsonAI SDK initialized with base URL: {self.base_url}")
    
    def test_connection(self) -> bool:
        """
        Test connection to AdsonAI API
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/health", 
                timeout=self.timeout
            )
            return response.status_code == 200 and "healthy" in response.text.lower()
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_contextual_ads(self, query: str, max_ads: int = 3, context: dict = None) -> List[Ad]:
        """
        Get contextual ads for a user query using AI matching
        
        Args:
            query: User query or conversation context
            max_ads: Maximum number of ads to return (default: 3, max: 10)
            context: Optional additional context for better matching
            
        Returns:
            List of Ad objects matched to the query
            
        Raises:
            ValueError: If query is empty or max_ads is invalid
            AuthenticationError: If API key is invalid
            APIError: If API request fails
            NetworkError: If network connection fails
            
        Example:
            ads = client.get_contextual_ads("I need a new laptop for work", max_ads=5)
            for ad in ads:
                print(f"💡 {ad.brand_name}: {ad.ad_text}")
                if ad.landing_url:
                    print(f"   🔗 {ad.landing_url}")
        """
        # Validate inputs
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if not isinstance(max_ads, int) or max_ads < 1 or max_ads > 10:
            raise ValueError("max_ads must be an integer between 1 and 10")
        
        # Prepare request data
        data = {
            'query': query.strip(),
            'maxAds': max_ads,
            'context': context or {}
        }
        
        try:
            # Make API request
            response = self.session.post(
                f"{self.base_url}/api/v1/match-ads",
                json=data,
                timeout=self.timeout
            )
            
            # Handle response codes
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key or authentication failed")
            elif response.status_code == 429:
                raise APIError("Rate limit exceeded. Please try again later.", status_code=429)
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Bad request')
                except:
                    error_msg = 'Bad request'
                raise ValidationError(f"Validation error: {error_msg}")
            elif response.status_code != 200:
                error_msg = f"API request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg = error_data['error']
                except:
                    pass
                raise APIError(error_msg, status_code=response.status_code)
            
            # Parse successful response
            try:
                result = response.json()
            except json.JSONDecodeError:
                raise APIError("Invalid JSON response from API")
            
            if not result.get('success'):
                error_msg = result.get('error', 'API returned unsuccessful response')
                raise APIError(error_msg)
            
            # Extract and convert ads
            response_data = result.get('data', {})
            ads_data = response_data.get('matches', [])
            ads = [Ad(ad_data) for ad_data in ads_data]
            
            logger.info(f"Found {len(ads)} ads for query: '{query}'")
            return ads
            
        except requests.exceptions.Timeout:
            raise NetworkError(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise NetworkError("Failed to connect to AdsonAI API")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {e}")
    
    def close(self):
        """Close the session and clean up resources"""
        if self.session:
            self.session.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def __del__(self):
        """Destructor to ensure session is closed"""
        self.close()