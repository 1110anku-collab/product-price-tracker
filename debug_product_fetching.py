import sys
import os
import logging

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def debug_product_fetching():
    """Debug product fetching to see what's happening"""
    print("Debugging product fetching...")
    
    try:
        from scraper import PriceScraper
        
        # Create scraper
        scraper = PriceScraper()
        
        # Test with a simple URL to see what happens
        # We'll test with a URL that we know will fail to get real data
        # but will help us see the flow
        
        print("1. Testing scraper initialization...")
        print(f"   Scraper session: {scraper.session}")
        print(f"   Scraper headers: {dict(scraper.session.headers)}")
        
        # Test the _extract_price method
        print("\n2. Testing price extraction...")
        test_prices = [
            "₹1,299",
            "Rs. 2,499", 
            "Price: ₹599.50",
            "$29.99",
            "€19.95"
        ]
        
        for price_text in test_prices:
            price, currency = scraper._extract_price(price_text)
            print(f"   '{price_text}' -> {price} {currency}")
        
        print("\n3. Testing URL detection...")
        test_urls = [
            "https://www.snapdeal.com/test-product/p/12345",
            "https://www.shopclues.com/test-product/p/67890",
            "https://www.amazon.in/test-product/dp/B012345678",
            "https://www.flipkart.com/test-product/p/ITM1234567890"
        ]
        
        for url in test_urls:
            url_lower = url.lower()
            if "amazon" in url_lower:
                platform = "Amazon"
            elif "flipkart" in url_lower:
                platform = "Flipkart"
            elif "snapdeal" in url_lower:
                platform = "Snapdeal"
            elif "shopclues" in url_lower:
                platform = "ShopClues"
            else:
                platform = "Unknown"
            print(f"   {url} -> {platform}")
        
        print("\nDebug test completed.")
        
    except Exception as e:
        print(f"Error in debug test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_product_fetching()