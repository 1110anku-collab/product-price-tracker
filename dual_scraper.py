"""
Dual Site Scraper - Scrapes product data from 2 websites simultaneously
Supports Flipkart, Amazon, and other major e-commerce sites
"""

import time
import threading
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict, Optional, Tuple, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DualSiteScraper:
    """Scrapes product data from two websites simultaneously"""

    def __init__(self):
        self.timeout = 15

    def _detect_site(self, url: str) -> str:
        """Detect which e-commerce site the URL belongs to - Only Amazon and Flipkart supported"""
        if not url:
            return "generic"
        
        url_lower = url.lower().strip()
        
        # Flipkart detection - more flexible
        if "flipkart.com" in url_lower or ("flipkart" in url_lower and ("http" in url_lower or "www" in url_lower)):
            return "flipkart"
        
        # Amazon detection - more flexible
        if "amazon.in" in url_lower or "amazon.com" in url_lower:
            return "amazon"
        if "amazon" in url_lower and ("/dp/" in url_lower or "/gp/" in url_lower or "/product/" in url_lower):
            return "amazon"
        
        return "generic"

    def _scrape_flipkart(self, driver, wait) -> Dict[str, Optional[str]]:
        """Scrape Flipkart product page with enhanced selectors"""
        data = {"name": None, "price": None, "image": None}

        # Wait for page to load - longer wait for Flipkart
        time.sleep(3)
        
        # Scroll down a bit to trigger lazy loading
        try:
            driver.execute_script("window.scrollTo(0, 300);")
            time.sleep(1)
        except:
            pass

        # Title selectors - More comprehensive
        title_selectors = [
            "span.B_NuCI",           # Main title
            "span.VU-ZEz",           # Alternative title
            "h1.yhB1nd",             # Header title
            "h1._2I9KP_",            # Another header variant
            "span[class*='B_NuCI']",  # Class contains B_NuCI
            "h1[class*='yhB1nd']",   # Class contains yhB1nd
            "._2i1QSc",              # Alternative selector
            "span._35KyD6"          # Another alternative
        ]

        # Price selectors - Enhanced
        price_selectors = [
            "div._30jeq3._16Jk6d",   # Main price
            "div.Nx9bqj.CxhGGd",      # New layout price
            "div.UOCQB5",             # Alternative price
            "div._25b18c",            # Price container
            "span._16Jk6d",           # Price span
            "div[class*='_30jeq3']",  # Class contains _30jeq3
            "._1vC4OE._2rQ-NK",       # Price with classes
            "div[class*='Nx9bqj']"    # Class contains Nx9bqj
        ]

        # Image selectors - Enhanced
        image_selectors = [
            "img._396cs4._2amPTt._3iP0cB",  # Main product image
            "img._2r_T1I",                   # Image variant
            "img.q6DClP",                    # Another variant
            "img[class*='_396cs4']",         # Class contains _396cs4
            "img[class*='_2r_T1I']",        # Class contains _2r_T1I
            "._2r_T1I img",                  # Image inside container
            "#container img"                  # Fallback
        ]

        # Extract title
        for sel in title_selectors:
            try:
                elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
                if elem and elem.text.strip():
                    data["name"] = elem.text.strip()
                    logger.info(f"Flipkart title found: {data['name'][:50]}...")
                    break
            except:
                continue

        # Extract price
        for sel in price_selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, sel)
                if elem and elem.text.strip():
                    price_text = elem.text.strip()
                    # Clean price text (remove extra spaces, newlines)
                    price_text = " ".join(price_text.split())
                    data["price"] = price_text
                    logger.info(f"Flipkart price found: {price_text}")
                    break
            except:
                continue

        # Extract image
        for sel in image_selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, sel)
                if elem:
                    img_url = elem.get_attribute("src") or elem.get_attribute("data-src")
                    if img_url and ("http" in img_url or "//" in img_url):
                        data["image"] = img_url
                        logger.info(f"Flipkart image found: {img_url[:50]}...")
                        break
            except:
                continue

        return data

    def _scrape_amazon(self, driver, wait) -> Dict[str, Optional[str]]:
        """Scrape Amazon product page with enhanced selectors"""
        data = {"name": None, "price": None, "image": None}

        # Wait for page to load
        time.sleep(2)

        # Title selectors - More comprehensive
        title_selectors = [
            "span#productTitle",           # Main product title (ID)
            "h1.a-size-large",              # Large heading
            "h1.a-size-base-plus",          # Base plus heading
            "h1[data-automation-id='title']", # Automation ID
            "#title_feature_div h1",        # Title in feature div
            "span[id*='productTitle']",      # ID contains productTitle
            "h1.a-size-large.product-title-word-break", # Full class path
        ]

        # Price selectors - Enhanced (Amazon has multiple price formats)
        price_selectors = [
            "span.a-price-whole",              # Whole price (with decimal)
            "span.a-offscreen",                 # Hidden price (most reliable)
            "span#priceblock_dealprice",        # Deal price
            "span#priceblock_ourprice",         # Our price
            "span#priceblock_saleprice",        # Sale price
            "span.a-price .a-offscreen",        # Price in price container
            ".a-price-range",                   # Price range
            "span[class*='a-price']",           # Any price class
            ".a-price.a-text-price",            # Text price
            "span[data-a-color='price']"        # Data attribute price
        ]

        # Image selectors - Enhanced
        image_selectors = [
            "img#landingImage",                  # Main landing image
            "img#main-image",                    # Main image
            "img#imgBlkFront",                   # Front image
            "img#main-image-feature",            # Feature image
            "#landingImage",                     # ID selector
            "#imgTagWrapperId img",              # Image in wrapper
            "img[data-a-dynamic-image]",         # Dynamic image
            "#productDescription_feature_div img" # Description image
        ]

        # Extract title - try multiple approaches
        for sel in title_selectors:
            try:
                elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
                if elem and elem.text.strip():
                    data["name"] = elem.text.strip()
                    logger.info(f"Amazon title found: {data['name'][:50]}...")
                    break
            except Exception as e:
                logger.debug(f"Amazon title selector {sel} failed: {e}")
                continue
        
        # Fallback: try by ID directly
        if not data["name"]:
            try:
                elem = driver.find_element(By.ID, "productTitle")
                if elem and elem.text.strip():
                    data["name"] = elem.text.strip()
                    logger.info(f"Amazon title found (fallback): {data['name'][:50]}...")
            except:
                pass

        # Extract price - Try multiple methods
        price_found = False
        for sel in price_selectors:
            try:
                elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
                if elem:
                    price_text = elem.text.strip() or elem.get_attribute("textContent") or elem.get_attribute("aria-label")
                    if price_text and any(char.isdigit() for char in price_text):
                        # Clean price text
                        price_text = " ".join(price_text.split())
                        data["price"] = price_text
                        logger.info(f"Amazon price found: {price_text}")
                        price_found = True
                        break
            except Exception as e:
                logger.debug(f"Amazon price selector {sel} failed: {e}")
                continue

        # If price not found, try getting from multiple price elements and combine
        if not price_found:
            try:
                # Try .a-price-whole first
                price_elements = driver.find_elements(By.CSS_SELECTOR, ".a-price")
                if price_elements:
                    for price_elem in price_elements:
                        try:
                            whole = price_elem.find_element(By.CSS_SELECTOR, ".a-price-whole")
                            fraction_elem = price_elem.find_elements(By.CSS_SELECTOR, ".a-price-fraction")
                            if whole:
                                if fraction_elem:
                                    data["price"] = f"{whole.text}.{fraction_elem[0].text}"
                                else:
                                    data["price"] = whole.text
                                logger.info(f"Amazon price found (combined): {data['price']}")
                                price_found = True
                                break
                        except:
                            continue
                
                # Try a-offscreen as last resort
                if not price_found:
                    try:
                        offscreen = driver.find_element(By.CSS_SELECTOR, "span.a-offscreen")
                        if offscreen:
                            price_text = offscreen.text or offscreen.get_attribute("textContent")
                            if price_text and any(char.isdigit() for char in price_text):
                                data["price"] = price_text.strip()
                                logger.info(f"Amazon price found (offscreen): {data['price']}")
                    except:
                        pass
            except Exception as e:
                logger.debug(f"Amazon price fallback failed: {e}")

        # Extract image
        for sel in image_selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, sel)
                if elem:
                    img_url = elem.get_attribute("src") or elem.get_attribute("data-src") or elem.get_attribute("data-old-src")
                    if img_url and ("http" in img_url or "//" in img_url):
                        data["image"] = img_url
                        logger.info(f"Amazon image found: {img_url[:50]}...")
                        break
            except:
                continue

        return data

    def _scrape_generic(self, driver, wait) -> Dict[str, Optional[str]]:
        """Generic scraper for unknown sites"""
        data = {"name": None, "price": None, "image": None}

        # Try common selectors
        try:
            # Title - try h1, meta tags
            try:
                elem = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
                if elem and elem.text.strip():
                    data["name"] = elem.text.strip()
            except:
                pass

            # Price - try common price patterns
            price_patterns = ["price", "cost", "amount"]
            for pattern in price_patterns:
                try:
                    elem = driver.find_element(By.CSS_SELECTOR, f"[class*='{pattern}']")
                    if elem and elem.text.strip():
                        data["price"] = elem.text.strip()
                        break
                except:
                    continue

            # Image - try img tags
            try:
                img = driver.find_element(By.CSS_SELECTOR, "img")
                if img and img.get_attribute("src"):
                    data["image"] = img.get_attribute("src")
            except:
                pass

        except Exception as e:
            logger.error(f"Generic scrape error: {e}")

        return data

    def _extract_price_value(self, price_text: str) -> float:
        """Extract numeric price from text string - Enhanced for Amazon and Flipkart"""
        if not price_text:
            return 0.0

        import re
        # Remove currency symbols (₹, Rs, $, etc.) and commas
        # Handle cases like "₹1,299", "Rs. 2,499.50", "1,299.00", etc.
        price_clean = price_text.replace(',', '').replace('₹', '').replace('Rs.', '').replace('Rs', '').replace('$', '').replace('€', '')
        
        # Extract numbers and decimal points (handle formats like "1299.50" or "1299")
        # Match pattern: digits with optional decimal point and more digits
        price_match = re.search(r'(\d+\.?\d*)', price_clean)
        if price_match:
            try:
                return float(price_match.group(1))
            except:
                pass
        
        # Fallback: extract all digits
        digits = re.sub(r'[^\d.]', '', price_clean)
        try:
            return float(digits) if digits else 0.0
        except:
            return 0.0

    def _scrape_single_url(self, url: str) -> Dict[str, Any]:
        """Scrape a single URL and return product data"""
        site_type = self._detect_site(url)
        result = {
            "url": url,
            "site": site_type,
            "name": None,
            "price": None,
            "price_value": 0.0,
            "image": None,
            "error": None
        }

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--window-size=1920,1080")
        
        # Fix for undetected_chromedriver - simpler experimental options
        try:
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.managed_default_content_settings.images": 2
            }
            options.add_experimental_option("prefs", prefs)
        except:
            pass

        driver = None
        try:
            # Use undetected_chromedriver - let it auto-detect Chrome version
            # use_subprocess=False helps avoid parsing errors
            driver = uc.Chrome(options=options, use_subprocess=False, version_main=None)
            driver.get(url)
            wait = WebDriverWait(driver, self.timeout)

            # Scrape based on site type
            if site_type == "flipkart":
                data = self._scrape_flipkart(driver, wait)
            elif site_type == "amazon":
                data = self._scrape_amazon(driver, wait)
            else:
                data = self._scrape_generic(driver, wait)

            result["name"] = data.get("name")
            result["price"] = data.get("price")
            result["price_value"] = self._extract_price_value(data.get("price", ""))
            result["image"] = data.get("image")

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error scraping {url}: {e}")

        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

        return result

    def scrape_dual_urls(self, url1: str, url2: str) -> Tuple[Dict, Dict]:
        """
        Scrape two URLs simultaneously using threading
        Specifically designed for Amazon and Flipkart
        Returns tuple of (result1, result2)
        """
        # Validate URLs are Amazon or Flipkart
        site1_type = self._detect_site(url1)
        site2_type = self._detect_site(url2)
        
        if site1_type not in ["amazon", "flipkart"]:
            logger.warning(f"URL1 is not Amazon or Flipkart: {site1_type}")
        
        if site2_type not in ["amazon", "flipkart"]:
            logger.warning(f"URL2 is not Amazon or Flipkart: {site2_type}")
        
        results = {}

        # Use ThreadPoolExecutor for parallel scraping
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(self._scrape_single_url, url1): 0,
                executor.submit(self._scrape_single_url, url2): 1
            }

            for future in as_completed(futures):
                index = futures[future]
                try:
                    result = future.result()
                    results[index] = result
                    logger.info(f"Scraping completed for URL {index + 1}: {result.get('site', 'unknown')}")
                except Exception as e:
                    logger.error(f"Error scraping URL {index + 1}: {e}")
                    results[index] = {
                        "url": url1 if index == 0 else url2,
                        "site": site1_type if index == 0 else site2_type,
                        "name": None,
                        "price": None,
                        "price_value": 0.0,
                        "image": None,
                        "error": str(e)
                    }

        return results.get(0, {}), results.get(1, {})


# Global instance
dual_scraper = DualSiteScraper()

