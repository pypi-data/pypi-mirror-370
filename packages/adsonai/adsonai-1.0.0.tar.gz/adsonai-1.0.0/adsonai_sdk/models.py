"""
Data models for AdsonAI SDK
"""

class Ad:
    """Ad data structure"""
    
    def __init__(self, data: dict):
        """
        Initialize Ad from API response data
        
        Args:
            data: Dictionary containing ad data from API
        """
        self.id = data.get('id')
        self.brand_name = data.get('brandName', '')
        self.product_name = data.get('productName', '')
        self.description = data.get('description', '')
        self.ad_text = data.get('adText', '')
        self.bid_amount = float(data.get('bidAmount', 0))
        self.landing_url = data.get('landingUrl')
        self.target_keywords = data.get('targetKeywords', '')
        self.status = data.get('status', 'unknown')
        self.relevance_score = data.get('relevanceScore')
    
    def to_dict(self) -> dict:
        """Convert ad to dictionary"""
        return {
            'id': self.id,
            'brand_name': self.brand_name,
            'product_name': self.product_name,
            'description': self.description,
            'ad_text': self.ad_text,
            'bid_amount': self.bid_amount,
            'landing_url': self.landing_url,
            'target_keywords': self.target_keywords,
            'status': self.status,
            'relevance_score': self.relevance_score
        }
    
    def __str__(self):
        return f"{self.brand_name} - {self.product_name}: {self.ad_text}"
    
    def __repr__(self):
        return f"Ad(id='{self.id}', brand='{self.brand_name}', product='{self.product_name}')"
