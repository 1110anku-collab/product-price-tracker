import time
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PriceScraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = uc.Chrome(options=chrome_options, version_main=142)
        self.wait = WebDriverWait(self.driver, 15)

    def scrape_price(self, url: str):
        """Main dispatcher — detects site and calls respective scraper."""
        try:
            print(f"[INFO] Scraping started for: {url}")
            if "amazon." in url:
                return self._scrape_amazon(url)
            elif "flipkart." in url:
                return self._scrape_flipkart(url)
            else:
                raise ValueError("Unsupported website")
        except Exception as e:
            print(f"[ERROR] {e}")
            return None, None, None, None
        finally:
            self.driver.quit()

    # ---------------------------------------------------------------------
    # Amazon scraper
    # ---------------------------------------------------------------------
    def _scrape_amazon(self, url: str):
        self.driver.get(url)

        # Product title
        try:
            name_el = self.wait.until(
                EC.presence_of_element_located((By.ID, "productTitle"))
            )
            name = name_el.text.strip()
        except:
            name = None

        # Price
        price_selectors = [
            "#priceblock_ourprice",
            "#priceblock_dealprice",
            "span.a-price-whole",
        ]
        price = None
        for sel in price_selectors:
            try:
                elem = self.driver.find_element(By.CSS_SELECTOR, sel)
                if elem and elem.text.strip():
                    price = elem.text.strip()
                    break
            except:
                continue

        # Image
        try:
            image_el = self.driver.find_element(By.ID, "landingImage")
            image = image_el.get_attribute("src")
        except:
            image = None

        currency = "INR"
        print(f"[RESULT][Amazon] {name} - {price}")
        return price, name, currency, image

    # ---------------------------------------------------------------------
    # Flipkart scraper
    # ---------------------------------------------------------------------
    def _scrape_flipkart(self, url: str):
        self.driver.get(url)

        # Close login popup if present
        try:
            time.sleep(2)
            self.driver.find_element(By.CSS_SELECTOR, "button._2KpZ6l._2doB4z").click()
        except:
            pass

        # Title
        title_selectors = [
            "span.B_NuCI",  # old layout
            "span.VU-ZEz",  # new layout
            "h1.yhB1nd",    # alternate layout
        ]
        name = None
        for sel in title_selectors:
            try:
                elem = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
                if elem and elem.text.strip():
                    name = elem.text.strip()
                    break
            except:
                continue

        # Price
        price_selectors = [
            "div._30jeq3._16Jk6d",  # standard layout
            "div.Nx9bqj.CxhGGd",    # new layout
            "div.UOCQB5",           # fallback
        ]
        price = None
        for sel in price_selectors:
            try:
                elem = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
                if elem and elem.text.strip():
                    price = elem.text.strip()
                    break
            except:
                continue

        # Image
        try:
            img_el = self.driver.find_element(By.CSS_SELECTOR, "img._396cs4._2amPTt._3qGmMb")
            image = img_el.get_attribute("src")
        except:
            image = None

        currency = "INR"
        print(f"[RESULT][Flipkart] {name} - {price}")
        return price, name, currency, image


# ---------------------------------------------------------------------
# Standalone test (manual run)
# ---------------------------------------------------------------------
if __name__ == "__main__":
    scraper = PriceScraper()

    test_url = "https://www.flipkart.com/samsung-galaxy-s23-ultra-5g-green-256-gb/p/itm0f3946a5d0a7a"
    result = scraper.scrape_price(test_url)
    print("[FINAL RESULT]", result)
