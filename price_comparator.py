"""
Price Comparator - Compares prices from two sites and triggers notifications
"""

import logging
from typing import Dict, Optional, Tuple, Any
from notifications import notifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PriceComparator:
    """Compares prices from two sites and handles notifications"""

    def __init__(self):
        self.price_drop_threshold = 0.01  # 1% drop triggers notification

    def compare_prices(
        self,
        product_id: int,
        product_name: str,
        site1_price: float,
        site2_price: float,
        site1_url: str,
        site2_url: str,
        previous_site1_price: Optional[float] = None,
        previous_site2_price: Optional[float] = None,
        email: str = "",
    ) -> Dict[str, Any]:
        """
        Compare prices from Amazon (site1) and Flipkart (site2)
        Returns dict with comparison results and notification status
        """
        result = {
            "cheaper_site": None,
            "cheaper_price": 0.0,
            "price_difference": 0.0,
            "notification_sent": False,
            "message": "",
            "amazon_price": site1_price,
            "flipkart_price": site2_price
        }

        # Validate prices
        if site1_price <= 0 and site2_price <= 0:
            result["message"] = "Both prices invalid"
            return result

        if site1_price <= 0:
            result["cheaper_site"] = "site2"
            result["cheaper_price"] = site2_price
            result["price_difference"] = site2_price
            return result

        if site2_price <= 0:
            result["cheaper_site"] = "site1"
            result["cheaper_price"] = site1_price
            result["price_difference"] = site1_price
            return result

        # Compare prices (Amazon vs Flipkart)
        if site1_price < site2_price:
            result["cheaper_site"] = "Amazon"
            result["cheaper_price"] = site1_price
            result["price_difference"] = site2_price - site1_price
        elif site2_price < site1_price:
            result["cheaper_site"] = "Flipkart"
            result["cheaper_price"] = site2_price
            result["price_difference"] = site1_price - site2_price
        else:
            result["cheaper_site"] = "Equal"
            result["cheaper_price"] = site1_price
            result["price_difference"] = 0.0

        # Check for price drops and send notification
        price_dropped = False
        dropped_site = None
        dropped_price = 0.0
        previous_price = 0.0

        # Check Amazon price drop
        if previous_site1_price and previous_site1_price > 0:
            if site1_price < previous_site1_price:
                drop_percent = ((previous_site1_price - site1_price) / previous_site1_price) * 100
                if drop_percent >= (self.price_drop_threshold * 100):
                    price_dropped = True
                    dropped_site = "Amazon"
                    dropped_price = site1_price
                    previous_price = previous_site1_price

        # Check Flipkart price drop
        if previous_site2_price and previous_site2_price > 0:
            if site2_price < previous_site2_price:
                drop_percent = ((previous_site2_price - site2_price) / previous_site2_price) * 100
                if drop_percent >= (self.price_drop_threshold * 100):
                    # If both dropped, notify for the bigger drop
                    if not price_dropped or (site2_price < site1_price):
                        price_dropped = True
                        dropped_site = "Flipkart"
                        dropped_price = site2_price
                        previous_price = previous_site2_price

        # Send notification if price dropped
        if price_dropped and email:
            try:
                product_url = site1_url if dropped_site == "Amazon" else site2_url
                
                notifier.send_price_alert(
                    product_name=product_name,
                    current_price=dropped_price,
                    target_price=previous_price,
                    product_url=product_url,
                    email_address=email,
                    enable_sound=True,
                    enable_desktop=True,
                )
                
                result["notification_sent"] = True
                result["message"] = f"Price dropped on {dropped_site}! Now ₹{dropped_price:.2f} (was ₹{previous_price:.2f}). Notification sent."
                logger.info(f"Price drop notification sent for {product_name} on {dropped_site}: ₹{dropped_price:.2f}")
                
            except Exception as e:
                logger.error(f"Error sending notification: {e}")
                result["message"] = f"Price dropped but notification failed: {e}"

        return result

    def get_best_deal(
        self,
        site1_price: float,
        site2_price: float,
        site1_name: str = "Amazon",
        site2_name: str = "Flipkart",
    ) -> Tuple[str, float]:
        """Return the best deal (site name and price)"""
        if site1_price <= 0:
            return (site2_name, site2_price)
        if site2_price <= 0:
            return (site1_name, site1_price)
        
        if site1_price < site2_price:
            return (site1_name, site1_price)
        elif site2_price < site1_price:
            return (site2_name, site2_price)
        else:
            return ("Both sites", site1_price)


# Global instance
price_comparator = PriceComparator()

