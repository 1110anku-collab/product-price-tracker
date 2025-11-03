"""
Configuration Manager for Price Tracker Application
Handles environment variables and application settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ----------------------------------------------------------------------
# Load environment variables
# ----------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """Central configuration for the Price Tracker app."""

    # Directories
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    ASSETS_DIR: Path = BASE_DIR / "assets"

    # Database
    DB_PATH: Path = DATA_DIR / "price_tracker.db"

    # Email configuration
    EMAIL_ADDRESS: str = os.getenv("EMAIL_ADDRESS", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))

    # App settings
    DEFAULT_CHECK_FREQUENCY: int = int(os.getenv("DEFAULT_CHECK_FREQUENCY", "30"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # GUI settings
    WINDOW_WIDTH: int = 1000
    WINDOW_HEIGHT: int = 700
    APP_NAME: str = "Price Tracker Pro"

    # Frequency options
    FREQUENCY_OPTIONS: dict[str, int] = {
        "5 minutes": 5,
        "10 minutes": 10,
        "30 minutes": 30,
        "1 hour": 60,
        "12 hours": 720,
    }

    # Misc settings
    ENABLE_SOUND: bool = True
    DEFAULT_CURRENCY: str = "INR"
    TIMEZONE: str = "Asia/Kolkata"
    TIME_FORMAT: str = "%d/%m/%Y %I:%M %p IST"
    DATE_FORMAT: str = "%d/%m/%Y"

    @classmethod
    def create_directories(cls) -> None:
        """Ensure required directories exist."""
        for folder in (cls.DATA_DIR, cls.LOGS_DIR, cls.ASSETS_DIR):
            try:
                folder.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"[Warning] Could not create directory {folder}: {e}")

    @classmethod
    def validate_email_config(cls) -> bool:
        """Return True if email and password are properly set."""
        return bool(
            cls.EMAIL_ADDRESS
            and cls.EMAIL_PASSWORD
            and "@" in cls.EMAIL_ADDRESS
            and len(cls.EMAIL_PASSWORD) > 0
        )


# ----------------------------------------------------------------------
# Create directories immediately
# ----------------------------------------------------------------------
Config.create_directories()


# ----------------------------------------------------------------------
# Scraper Integration (completely clean & warning-free)
# ----------------------------------------------------------------------
try:
    # Try to import get_product_data directly if defined in scraper.py
    from scraper import get_product_data  # type: ignore
except ImportError:
    # Fallback: if scraper only provides a PriceScraper class
    try:
        from scraper import PriceScraper  # type: ignore

        def _get_product_data_with_price_scraper(url: str):  # noqa: E305
            """Fallback: call PriceScraper.scrape_price() if no standalone function exists."""
            scraper = PriceScraper()
            return scraper.scrape_price(url)

        # expose a consistent public name
        get_product_data = _get_product_data_with_price_scraper

    except Exception as e:
        print(f"[Warning] Could not import scraper: {e}")

        def _get_product_data_unavailable(_url: str):  # noqa: E305
            """Final fallback if scraper import completely fails."""
            print("[Error] Scraper unavailable.")
            return None, None, None, None

        # expose a consistent public name
        get_product_data = _get_product_data_unavailable
