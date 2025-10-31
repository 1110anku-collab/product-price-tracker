"""
Configuration Manager for Price Tracker Application
Handles environment variables and application settings
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    """Application configuration settings"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    ASSETS_DIR = BASE_DIR / "assets"
    
    # Database
    DB_PATH = DATA_DIR / "price_tracker.db"
    
    # Email settings
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    
    # Application settings
    DEFAULT_CHECK_FREQUENCY = int(os.getenv("DEFAULT_CHECK_FREQUENCY", "30"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # GUI settings
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 700
    APP_NAME = "Price Tracker Pro"
    
    # Frequency options (in minutes)
    FREQUENCY_OPTIONS = {
        "5 minutes": 5,
        "10 minutes": 10,
        "30 minutes": 30,
        "1 hour": 60,
        "12 hours": 720
    }
    
    # Sound alert settings
    ENABLE_SOUND = True
    
    # Currency settings
    DEFAULT_CURRENCY = "INR"
    TIMEZONE = "Asia/Kolkata"
    TIME_FORMAT = "%d/%m/%Y %I:%M %p IST"
    DATE_FORMAT = "%d/%m/%Y"
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        try:
            cls.DATA_DIR.mkdir(exist_ok=True, parents=True)
            cls.LOGS_DIR.mkdir(exist_ok=True, parents=True)
            cls.ASSETS_DIR.mkdir(exist_ok=True, parents=True)
        except Exception as e:
            print(f"Warning: Could not create directories: {e}")
    
    @classmethod
    def validate_email_config(cls) -> bool:
        """Check if email configuration is valid"""
        email = cls.EMAIL_ADDRESS
        password = cls.EMAIL_PASSWORD
        return bool(email and password and '@' in email and len(password) > 0)


# Create directories on import
Config.create_directories()