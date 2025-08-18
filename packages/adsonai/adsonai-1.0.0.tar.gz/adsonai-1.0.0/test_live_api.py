#!/usr/bin/env python3
"""
Optimized AdsonAI Test Script - Rate Limit Aware
FIXED VERSION - Updated for new AI matching algorithm with smart rate limiting
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class AdsonAITestClient:
    """Direct API client for testing with rate limit awareness"""
    
    def __init__(self, api_key: str, base_url: str = "https://adsonai.vercel.app"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key
        }
        self.last_request_time = 0
        self.min_request_interval = 2.0  # 2 seconds between requests to avoid rate limiting
    
    def _wait_if_needed(self):
        """Wait between requests to avoid rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            print(f"   ⏸️  Waiting {wait_time:.1f}s to avoid rate limits...")
            time.sleep(wait_time)
    
    def test_connection(self) -> bool:
        """Test basic API connection"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def get_contextual_ads(self, query: str, max_ads: int = 3, use_ai: bool = True) -> Tuple[List[Dict], float, bool, str]:
        """Get contextual ads and return (ads, response_time, success, error_msg)"""
        self._wait_if_needed()
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/match-ads",
                headers=self.headers,
                json={
                    "query": query,
                    "maxAds": max_ads,
                    "useAI": use_ai,
                    "includeMetadata": True
                },
                timeout=30
            )
            
            response_time = (time.time() - start_time) * 1000
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                return data.get("matches", []), response_time, True, ""
            elif response.status_code == 429:
                # Parse rate limit info
                try:
                    error_data = response.json()
                    reset_time = error_data.get("resetTime", "")
                    return [], response_time, False, f"Rate limit exceeded. Reset at: {reset_time}"
                except:
                    return [], response_time, False, f"Rate limit exceeded (429)"
            else:
                return [], response_time, False, f"API Error {response.status_code}: {response.text[:100]}"
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return [], response_time, False, f"Request failed: {str(e)}"

def print_separator(title="", char="=", width=60):
    """Print a formatted separator"""
    if title:
        title_len = len(title)
        padding = (width - title_len - 2) // 2
        print(f"{char * padding} {title} {char * padding}")
    else:
        print(char * width)

def print_subsection(title):
    """Print a subsection header"""
    print(f"\n📋 {title}")
    print("-" * (len(title) + 5))

def print_ad_details(ad, index=None):
    """Print detailed ad information"""
    prefix = f"   {index}. " if index is not None else "   • "
    
    print(f"{prefix}🏷️  Brand: {ad.get('brandName', 'Unknown')}")
    print(f"     📦 Product: {ad.get('productName', 'Unknown')}")
    print(f"     💬 Ad Text: {ad.get('adText', 'N/A')[:60]}{'...' if len(ad.get('adText', '')) > 60 else ''}")
    print(f"     💰 Bid Amount: ${ad.get('bidAmount', 0)}")
    print(f"     🎯 Keywords: {ad.get('targetKeywords', 'N/A')[:60]}{'...' if len(ad.get('targetKeywords', '')) > 60 else ''}")
    
    if ad.get('description'):
        desc = ad['description']
        print(f"     📝 Description: {desc[:80]}{'...' if len(desc) > 80 else ''}")
    
    if ad.get('id'):
        print(f"     🆔 ID: {ad['id'][:20]}...")
    
    print()

def evaluate_ad_quality(ads: List[Dict]) -> Dict:
    """Evaluate the quality of returned ads"""
    if not ads:
        return {"has_junk": False, "quality_score": 100, "issues": []}
    
    issues = []
    quality_score = 100
    
    for ad in ads:
        brand = ad.get('brandName', '').strip()
        product = ad.get('productName', '').strip()
        ad_text = ad.get('adText', '').strip()
        keywords = ad.get('targetKeywords', '').strip()
        description = ad.get('description', '').strip()
        
        # Check for obvious junk patterns (from your test data)
        junk_patterns = [
            'app;e', 'goog1e', 'micr0soft',  # Common typos
            'q32', 'dfdf', 'dosjpod', 'aple',  # Nonsense from your test
            'asdf', 'qwer', 'zxcv', 'hjkl',   # Keyboard mashing
        ]
        
        all_text = f"{brand} {product} {ad_text} {keywords} {description}".lower()
        
        for pattern in junk_patterns:
            if pattern in all_text:
                issues.append(f"Junk pattern '{pattern}' found in {brand}")
                quality_score -= 30
        
        # Check for very short content
        if len(all_text) < 25:
            issues.append(f"Very short content in {brand} ({len(all_text)} chars)")
            quality_score -= 20
        
        # Check for brand name issues
        if len(brand) < 2:
            issues.append(f"Brand name too short: '{brand}'")
            quality_score -= 25
        
        # Check for repetitive content
        words = all_text.split()
        unique_words = set(words)
        if len(words) > 5 and len(unique_words) / len(words) < 0.5:
            issues.append(f"Too repetitive content in {brand}")
            quality_score -= 15
    
    has_junk = quality_score < 80
    return {"has_junk": has_junk, "quality_score": max(0, quality_score), "issues": issues}

def test_single_query(client, query: str, description: str = "", expected_empty: bool = False):
    """Test a single query and return detailed results"""
    print(f"\n🔍 Testing: '{query}'")
    if description:
        print(f"   📝 {description}")
    
    ads, response_time, success, error_msg = client.get_contextual_ads(query, max_ads=3)
    
    print(f"   ⏱️  Response time: {response_time:.1f}ms")
    
    if not success:
        print(f"   ❌ {error_msg}")
        if "Rate limit" in error_msg:
            print(f"   💡 Wait for rate limit reset or increase limits in dashboard")
        return {"success": False, "error": error_msg, "test_result": "FAILED"}
    
    print(f"   📊 Results: {len(ads)} ads returned")
    
    # Check quality
    quality_check = evaluate_ad_quality(ads)
    
    if quality_check['has_junk']:
        print(f"   🚨 QUALITY ISSUES DETECTED:")
        for issue in quality_check['issues']:
            print(f"      • {issue}")
        print(f"   📊 Quality Score: {quality_check['quality_score']}/100")
        print(f"   💡 Database cleanup needed - junk ads still present!")
        return {
            "success": True,
            "test_result": "QUALITY_ISSUES",
            "ads_count": len(ads),
            "quality_score": quality_check['quality_score'],
            "issues": quality_check['issues']
        }
    
    # Evaluate results
    if expected_empty:
        if len(ads) == 0:
            print(f"   ✅ PASS: Correctly returned no results for nonsense query")
            return {"success": True, "test_result": "PASS", "ads_count": 0}
        else:
            print(f"   ❌ FAIL: Expected no results but got {len(ads)} ads")
            print(f"   💡 Algorithm should filter out irrelevant queries")
            return {"success": True, "test_result": "FAIL", "ads_count": len(ads)}
    else:
        if len(ads) == 0:
            print(f"   ⚠️  No ads returned - could mean:")
            print(f"      • No relevant ads in database for this query")
            print(f"      • Algorithm being too conservative (good)")
            print(f"      • All ads filtered out by quality filter (good)")
            return {"success": True, "test_result": "NO_RESULTS", "ads_count": 0}
        else:
            print(f"   📋 Ad Details:")
            for j, ad in enumerate(ads, 1):
                print_ad_details(ad, j)
            
            # Quick relevance check
            if query and len(ads) > 0:
                query_words = query.lower().split()
                relevance_found = False
                
                for ad in ads:
                    ad_text = f"{ad.get('brandName', '')} {ad.get('productName', '')} {ad.get('targetKeywords', '')}".lower()
                    for word in query_words:
                        if len(word) > 3 and word in ad_text:  # Skip short words like "I", "for", etc.
                            relevance_found = True
                            break
                    if relevance_found:
                        break
                
                if relevance_found:
                    print(f"   ✅ PASS: Found relevant content matching query")
                    return {"success": True, "test_result": "PASS", "ads_count": len(ads)}
                else:
                    print(f"   ⚠️  UNCLEAR: Ads returned but relevance unclear")
                    return {"success": True, "test_result": "UNCLEAR", "ads_count": len(ads)}
            else:
                return {"success": True, "test_result": "PASS", "ads_count": len(ads)}

def run_core_tests(client):
    """Run the most important tests"""
    print_subsection("Core Algorithm Tests")
    
    test_results = []
    
    # Test 1: High-intent query (should return relevant results)
    result1 = test_single_query(
        client, 
        "I need running shoes", 
        "High-intent purchase query"
    )
    test_results.append(("running_shoes", result1))
    
    # If rate limited, stop here
    if not result1["success"] and "Rate limit" in result1.get("error", ""):
        return test_results
    
    # Test 2: Research query (should return relevant results)
    result2 = test_single_query(
        client,
        "best coffee maker",
        "Research/comparison query"
    )
    test_results.append(("coffee_maker", result2))
    
    if not result2["success"] and "Rate limit" in result2.get("error", ""):
        return test_results
    
    # Test 3: Nonsense query (should return empty)
    result3 = test_single_query(
        client,
        "random nonsense qwerty zxcvbn",
        "Nonsense query - should return empty",
        expected_empty=True
    )
    test_results.append(("nonsense", result3))
    
    return test_results

def run_extended_tests(client):
    """Run additional tests if rate limits allow"""
    print_subsection("Extended Tests")
    
    test_results = []
    
    tests = [
        ("laptop programming", "Technology query"),
        ("gaming headset", "Gaming peripheral query"),
        ("asdf qwer zxcv", "Keyboard mashing - should return empty", True),
    ]
    
    for query, desc, *empty in tests:
        expected_empty = empty[0] if empty else False
        result = test_single_query(client, query, desc, expected_empty)
        test_results.append((query.replace(" ", "_"), result))
        
        # Stop if rate limited
        if not result["success"] and "Rate limit" in result.get("error", ""):
            break
    
    return test_results

def generate_smart_report(core_results, extended_results, api_key):
    """Generate an intelligent test report"""
    print_separator("📄 SMART TEST REPORT", "=", 60)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"🕒 Test completed at: {timestamp}")
    print(f"🔑 API Key: {api_key[:15]}...")
    print(f"🌐 Endpoint: https://adsonai.vercel.app")
    
    all_results = core_results + extended_results
    total_tests = len(all_results)
    
    # Analyze results
    rate_limited = any("Rate limit" in r[1].get("error", "") for r in all_results if not r[1]["success"])
    quality_issues = any(r[1].get("test_result") == "QUALITY_ISSUES" for r in all_results)
    passes = sum(1 for r in all_results if r[1].get("test_result") == "PASS")
    fails = sum(1 for r in all_results if r[1].get("test_result") == "FAIL")
    
    print(f"\n📊 Test Results Summary:")
    print(f"   Total tests run: {total_tests}")
    print(f"   Passed: {passes}")
    print(f"   Failed: {fails}")
    
    if rate_limited:
        print(f"   ⚠️  Rate limited - some tests not completed")
    
    if quality_issues:
        print(f"   🚨 CRITICAL: Quality issues detected!")
        print(f"   💡 Database still contains junk ads - cleanup needed")
        
        print(f"\n🔧 IMMEDIATE ACTION REQUIRED:")
        print(f"   1. Run database cleanup script to remove junk ads")
        print(f"   2. Verify fixed utils.js is deployed to production")
        print(f"   3. Check quality filter is working properly")
        
        return "NEEDS_CLEANUP"
    
    # Determine overall status
    if passes >= 2 and fails == 0:
        print(f"   🎉 Overall: EXCELLENT - Algorithm working well!")
        status = "EXCELLENT"
    elif passes >= 1 and fails <= 1:
        print(f"   ✅ Overall: GOOD - Algorithm mostly working")
        status = "GOOD"
    elif fails > passes:
        print(f"   ❌ Overall: POOR - Algorithm needs work")
        status = "POOR"
    else:
        print(f"   ⚠️  Overall: UNCLEAR - Need more testing")
        status = "UNCLEAR"
    
    # Specific recommendations
    print(f"\n💡 Recommendations:")
    
    if rate_limited:
        print(f"   • Increase API key rate limits for testing")
        print(f"   • Wait for rate limit reset to complete testing")
    
    if status == "EXCELLENT":
        print(f"   • Algorithm is working correctly!")
        print(f"   • Monitor performance in production")
        print(f"   • Add more diverse test cases")
    elif status == "GOOD":
        print(f"   • Fine-tune relevance scoring if needed")
        print(f"   • Add more quality ads to database")
    elif status == "POOR":
        print(f"   • Check OpenAI API key configuration")
        print(f"   • Verify algorithm fixes are deployed")
        print(f"   • Review database content quality")
    
    return status

def main():
    """Main test function - optimized for rate limiting"""
    print_separator("🧪 ADSONAI OPTIMIZED TEST SUITE")
    
    # Get API key
    api_key ="adsonai_6a7ry1cf3mxrctohbywrijjpxeljlwqo9"
    if not api_key and len(sys.argv) > 1:
        api_key = sys.argv[1]
    
    if not api_key:
        print("❌ API key not provided")
        print("💡 Usage:")
        print("   export ADSONAI_API_KEY='your_key' && python script.py")
        print("   python script.py 'your_key'")
        return False
    
    print(f"🔑 Using API key: {api_key[:15]}...")
    print(f"🌐 Testing endpoint: https://adsonai.vercel.app")
    print(f"⚡ Rate limit aware - 2s delays between requests")
    
    try:
        # Initialize client
        client = AdsonAITestClient(api_key=api_key)
        print(f"✅ Test client initialized successfully")
        
        # Test connection
        print_subsection("Connection Test")
        if client.test_connection():
            print("   ✅ API endpoint accessible")
        else:
            print("   ❌ Cannot connect to API endpoint")
            return False
        
        # Run core tests
        core_results = run_core_tests(client)
        
        # Run extended tests if no rate limiting
        extended_results = []
        if core_results and all(r[1]["success"] for r in core_results):
            extended_results = run_extended_tests(client)
        
        # Generate report
        status = generate_smart_report(core_results, extended_results, api_key)
        
        print(f"\n🎉 Testing completed!")
        
        if status == "NEEDS_CLEANUP":
            print(f"\n🚨 NEXT STEP: Run database cleanup script immediately!")
            print(f"   node scripts/cleanup-database.js")
        
        return status in ["EXCELLENT", "GOOD"]
        
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)