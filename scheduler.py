"""
Scheduler Module for Price Tracker Pro
Handles periodic price checking with threading and notification support.
"""

import time
import logging
import threading
from typing import Dict, Optional, Any
from datetime import datetime
import schedule

from database import db
from scraper import scraper
from notifications import notifier
from config import Config

# ==============================
# Logging Setup
# ==============================
logging.basicConfig(
    filename=Config.LOGS_DIR / "scheduler.log",
    level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class PriceScheduler:
    """Background scheduler for automated price checking."""

    def __init__(self, user: Dict[str, Any]):
        self.user = user
        self.user_id: int = int(user.get("id", 1))
        self.running: bool = False
        self.thread: Optional[threading.Thread] = None
        self.jobs: Dict[int, schedule.Job] = {}
        self.check_counts: Dict[int, int] = {}
        self.frequency_minutes: int = 30  # Default check frequency
        logger.info(f"Scheduler initialized for user: {self.user_id}")

    # ==============================
    # CONTROL METHODS
    # ==============================
    def start(self) -> None:
        """Start the scheduler loop in a background thread."""
        if self.running:
            logger.warning("Scheduler already running.")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("Scheduler thread started successfully.")

    def stop(self) -> None:
        """Stop the scheduler safely."""
        if not self.running:
            logger.info("Scheduler already stopped.")
            return

        self.running = False
        schedule.clear()
        self.jobs.clear()
        logger.info("Scheduler stopped and cleared all jobs.")

    def set_frequency(self, freq_text: str) -> None:
        """Set how often prices are checked."""
        freq_map = {"5m": 5, "10m": 10, "30m": 30, "1h": 60, "12h": 720}
        self.frequency_minutes = freq_map.get(freq_text, 30)
        logger.info(f"Price check frequency set to {self.frequency_minutes} minutes.")

    # ==============================
    # INTERNAL LOOP
    # ==============================
    def _run_loop(self) -> None:
        """Run the schedule loop continuously in a background thread."""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.exception(f"Scheduler loop error: {e}")

    # ==============================
    # PRODUCT SCHEDULING
    # ==============================
    def schedule_all_products(self) -> None:
        """Schedule all active products for regular checks."""
        try:
            products = db.get_user_products(self.user_id, active_only=True)
            if not products:
                logger.info("No active products found for scheduling.")
                return

            for product in products:
                self.schedule_product(int(product["id"]), self.frequency_minutes)

            logger.info(f"Scheduled {len(products)} products for user {self.user_id}.")
        except Exception as e:
            logger.exception(f"Error scheduling products for user {self.user_id}: {e}")

    def schedule_product(self, product_id: int, freq_minutes: int) -> None:
        """Schedule a single product for periodic price checks."""
        try:
            if product_id in self.jobs:
                schedule.cancel_job(self.jobs[product_id])
                logger.debug(f"Existing job for product {product_id} cancelled.")

            # Use a safe lambda with default args to avoid late binding warnings
            job = schedule.every(freq_minutes).minutes.do(
                lambda pid=product_id: self.check_product(pid)
            )
            self.jobs[product_id] = job
            self.check_counts[product_id] = 0

            # Run an immediate check
            self.check_product(product_id)
            logger.info(f"Product {product_id} scheduled every {freq_minutes} minutes.")
        except Exception as e:
            logger.exception(f"Error scheduling product {product_id}: {e}")

    def unschedule_product(self, product_id: int) -> None:
        """Cancel the scheduled job for a given product."""
        try:
            if product_id in self.jobs:
                schedule.cancel_job(self.jobs[product_id])
                del self.jobs[product_id]
                self.check_counts.pop(product_id, None)
                logger.info(f"Product {product_id} unscheduled successfully.")
            else:
                logger.warning(f"Attempted to unschedule non-existent product {product_id}.")
        except Exception as e:
            logger.exception(f"Error unscheduling product {product_id}: {e}")

    # ==============================
    # PRICE CHECKING
    # ==============================
    def check_product(self, product_id: int) -> None:
        """Scrape and update price data for a single product."""
        try:
            product: Optional[Dict[str, Any]] = db.get_product(product_id)
            if not product:
                logger.warning(f"Product {product_id} not found in database.")
                return

            product_name: str = product.get("product_name", f"Product_{product_id}")
            url: str = product.get("product_url", "")
            target_price: float = float(product.get("target_price", 0) or 0.0)

            if not url:
                logger.warning(f"Product {product_id} has no valid URL.")
                db.update_product_status(product_id, "Error: No URL")
                return

            current_price, name, currency, image_url = scraper.scrape_price(url) # type: ignore

            if current_price is None:
                db.update_product_status(product_id, "Error: Price unavailable")
                notifier.send_error_notification(product_name, "Price unavailable.")
                return

            db.update_product_price(product_id, current_price, image_url or "")

            # Update name if changed
            if name and name != product_name:
                db.update_product_name(product_id, name)

            # Check for target price reached
            if target_price > 0 and current_price <= target_price:
                db.update_product_status(product_id, "Target Reached!")
                notifier.send_price_alert(
                    product_name=name or product_name,
                    current_price=current_price,
                    target_price=target_price,
                    product_url=url,
                    email_address=product.get("notification_email", ""),
                    enable_sound=True,
                    enable_desktop=True,
                )
                db.log_notification(
                    product_id,
                    "price_drop",
                    f"Price dropped to {current_price} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                )
            else:
                db.update_product_status(product_id, "Tracking")

            # Increment check counter
            self.check_counts[product_id] = self.check_counts.get(product_id, 0) + 1

        except Exception as e:
            db.update_product_status(product_id, f"Error: {str(e)[:60]}")
            logger.exception(f"Error checking product {product_id}: {e}")

    # ==============================
    # STATUS REPORT
    # ==============================
    def get_status(self) -> Dict[str, Any]:
        """Return current scheduler status."""
        return {
            "running": self.running,
            "total_jobs": len(self.jobs),
            "total_checks": sum(self.check_counts.values()),
            "frequency_minutes": self.frequency_minutes,
            "user_id": self.user_id,
        }


# Alias for GUI integration
Scheduler = PriceScheduler
