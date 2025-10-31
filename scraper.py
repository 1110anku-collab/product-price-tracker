"""
scraper.py
-----------
Web scraper module for Price Tracker Pro

- Supports Amazon, Flipkart, and generic e-commerce pages
- Extracts product title, price, image, and availability
- Includes error handling and fallbacks
"""

import re
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
from urllib.parse import urlparse


class PriceScraper:
    """Scraper class for fetching product data"""

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/118.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    # -------------------------------
    # Public Methods
    # -------------------------------
    def fetch_product(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch product details from the given URL."""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            domain = urlparse(url).netloc.lower()

            if "flipkart" in domain:
                return self._parse_flipkart(soup, url)
            elif "amazon" in domain:
                return self._parse_amazon(soup, url)
            else:
                return self._parse_generic(soup, url)
        except Exception as e:
            print(f"[ERROR] Failed to fetch product: {e}")
            return None

    # -------------------------------
    # Parser Implementations
    # -------------------------------
    def _parse_flipkart(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        title = soup.select_one("span.B_NuCI")
        price = soup.select_one("div._30jeq3._16Jk6d")

        name = title.get_text(strip=True) if title else "Unknown Product"
        price_val = self._parse_price(price.get_text()) if price else None

        return {
            "name": name,
            "url": url,
            "price": price_val,
            "image": self._image(soup),
            "site": "Flipkart",
        }

    def _parse_amazon(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        title = soup.select_one("#productTitle")
        price = soup.select_one(".a-price .a-offscreen")

        name = title.get_text(strip=True) if title else "Unknown Product"
        price_val = self._parse_price(price.get_text()) if price else None

        return {
            "name": name,
            "url": url,
            "price": price_val,
            "image": self._image(soup),
            "site": "Amazon",
        }

    def _parse_generic(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        # Fallback generic parser
        title = soup.find("title")
        prices = re.findall(r"₹\s?([\d,]+)", soup.get_text())
        price_val = self._parse_price(prices[0]) if prices else None

        return {
            "name": title.get_text(strip=True) if title else "Unnamed Product",
            "url": url,
            "price": price_val,
            "image": self._image(soup),
            "site": "Generic",
        }

    # -------------------------------
    # Helper Methods
    # -------------------------------
    def _image(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract the most relevant image URL from the page."""
        img = soup.select_one("img[data-src], img[srcset], img[src]")
        if not img:
            return None

        candidates = [
            img.get("data-src"),
            img.get("srcset"),
            img.get("src"),
        ]

        for c in candidates:
            if c and isinstance(c, str) and c.strip():
                return c.strip()
        return None

    @staticmethod
    def _parse_price(raw: str) -> Optional[float]:
        """Convert a string like '₹1,299' to a float 1299.0"""
        try:
            clean = re.sub(r"[^\d.]", "", raw)
            return float(clean)
        except Exception:
            return None


# --------------------------------------------------
# Module-level Helper
# --------------------------------------------------
scraper = PriceScraper()

def get_product_data(url: str) -> Optional[Dict[str, Any]]:
    """Convenience function for other modules."""
    return scraper.fetch_product(url)


if __name__ == "__main__":
    # For quick testing
    test_url = "https://www.flipkart.com/"
    data = get_product_data(test_url)
    print(data)
