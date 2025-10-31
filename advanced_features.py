"""Advanced Features for Price Tracker Pro
Includes: Clipboard monitoring, Bulk CSV import, Price predictions
"""

import re
import logging
import csv
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path

# Optional imports with graceful fallback
try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

from database import db
from config import Config

logger = logging.getLogger(__name__)


class ClipboardMonitor:
    """Monitor clipboard for product URLs"""
    
    def __init__(self):
        self.last_clipboard = ""
        self.supported_domains = [
            'amazon', 'flipkart', 'snapdeal', 'shopclues', 'ajio',
            'pepperfry', 'croma', 'blinkit', 'firstcry', 'ebay', 
            'walmart', 'target'
        ]
    
    def check_clipboard(self) -> Optional[str]:
        """Check if clipboard contains a valid product URL"""
        if not PYPERCLIP_AVAILABLE:
            return None
        
        try:
            current_clipboard = pyperclip.paste()
            
            # Check if clipboard changed and contains URL
            if current_clipboard != self.last_clipboard:
                self.last_clipboard = current_clipboard
                
                # Check if it's a URL
                if current_clipboard.startswith(('http://', 'https://')):
                    # Check if it's from supported website
                    url_lower = current_clipboard.lower()
                    for domain in self.supported_domains:
                        if domain in url_lower:
                            return current_clipboard
            
            return None
        except Exception as e:
            logger.error(f"Clipboard check error: {e}")
            return None


class BulkImporter:
    """Import products from CSV file"""
    
    @staticmethod
    def import_from_csv(file_path: str, user_id: int) -> Tuple[int, List[str]]:
        """
        Import products from CSV file
        CSV Format: product_name, product_url, target_price, notification_email, frequency
        Returns: (success_count, error_list)
        """
        success_count = 0
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        product_name = row.get('product_name', '').strip()
                        product_url = row.get('product_url', '').strip()
                        target_price = float(row.get('target_price', 0))
                        notification_email = row.get('notification_email', '').strip()
                        frequency_str = row.get('frequency', '30 minutes').strip()
                        
                        if not product_name or not product_url or target_price <= 0:
                            errors.append(f"Row {row_num}: Missing required fields")
                            continue
                        
                        # Convert frequency string to integer (in minutes)
                        frequency = BulkImporter._parse_frequency(frequency_str)
                        if frequency is None:
                            errors.append(f"Row {row_num}: Invalid frequency '{frequency_str}'")
                            continue
                        
                        # Add product to database
                        product_id = db.add_product(
                            user_id=user_id,
                            product_name=product_name,
                            product_url=product_url,
                            target_price=target_price,
                            notification_email=notification_email,
                            check_frequency=frequency
                        )
                        
                        if product_id:
                            success_count += 1
                        else:
                            errors.append(f"Row {row_num}: Failed to add product")
                    
                    except ValueError as e:
                        errors.append(f"Row {row_num}: Invalid price value")
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
            
            return success_count, errors
        
        except FileNotFoundError:
            return 0, [f"File not found: {file_path}"]
        except Exception as e:
            return 0, [f"Import error: {str(e)}"]
    
    @staticmethod
    def export_template(file_path: str) -> bool:
        """Export a CSV template file"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['product_name', 'product_url', 'target_price', 'notification_email', 'frequency'])
                writer.writerow([
                    'iPhone 15 Pro Max',
                    'https://www.amazon.in/...',
                    '120000',
                    'your@email.com',
                    '30 minutes'
                ])
            return True
        except Exception as e:
            logger.error(f"Template export error: {e}")
            return False
    
    @staticmethod
    def _parse_frequency(frequency_str: str) -> Optional[int]:
        """
        Convert frequency string to integer minutes
        Accepts: "5 minutes", "30 minutes", "1 hour", "12 hours", or just "30"
        Returns: Integer minutes or None if invalid
        """
        try:
            frequency_str = frequency_str.lower().strip()
            
            # Direct number (assume minutes)
            if frequency_str.isdigit():
                return int(frequency_str)
            
            # Parse "X minutes" or "X minute"
            if 'minute' in frequency_str:
                num = int(frequency_str.split()[0])
                return num
            
            # Parse "X hours" or "X hour"
            if 'hour' in frequency_str:
                num = int(frequency_str.split()[0])
                return num * 60
            
            # Try to extract just the number
            match = re.search(r'(\d+)', frequency_str)
            if match:
                return int(match.group(1))
            
            return None
        
        except:
            return None


class PricePredictor:
    """Predict future prices based on historical data"""
    
    @staticmethod
    def predict_price_trend(product_id: int, days_ahead: int = 7) -> Optional[Dict]:
        """
        Predict price trend for next N days
        Returns: {
            'current_price': float,
            'predicted_price': float,
            'trend': 'up'|'down'|'stable',
            'confidence': float (0-1)
        }
        """
        if not NUMPY_AVAILABLE:
            return None
        
        try:
            # Get price history
            history = db.get_price_history(product_id, limit=30)
            
            if len(history) < 3:
                return None
            
            # Extract prices and timestamps
            prices = [h['price'] for h in history if h['price']]
            timestamps = [datetime.fromisoformat(h['checked_at']) for h in history]
            
            if len(prices) < 3:
                return None
            
            # Simple linear regression for trend
            x = np.arange(len(prices))
            z = np.polyfit(x, prices, 1)
            trend_line = np.poly1d(z)
            
            # Predict future price
            future_x = len(prices) + days_ahead
            predicted_price = trend_line(future_x)
            
            # Determine trend
            slope = z[0]
            if slope < -10:  # Decreasing by more than ₹10/check
                trend = 'down'
            elif slope > 10:  # Increasing by more than ₹10/check
                trend = 'up'
            else:
                trend = 'stable'
            
            # Calculate confidence (based on variance)
            variance = np.var(prices)
            confidence = min(1.0, max(0.3, 1.0 - (variance / (np.mean(prices) * 10))))
            
            return {
                'current_price': prices[-1],
                'predicted_price': max(0, predicted_price),
                'trend': trend,
                'confidence': confidence,
                'slope': slope
            }
        
        except Exception as e:
            logger.error(f"Price prediction error: {e}")
            return None
    
    @staticmethod
    def get_best_time_to_buy(product_id: int) -> Optional[str]:
        """Suggest best time to buy based on price history"""
        if not NUMPY_AVAILABLE:
            return "NumPy not installed - prediction unavailable"
        
        try:
            history = db.get_price_history(product_id, limit=50)
            
            if len(history) < 10:
                return "Not enough data for analysis"
            
            prices = [h['price'] for h in history if h['price']]
            avg_price = np.mean(prices)
            current_price = prices[-1]
            lowest_price = min(prices)
            
            if current_price <= lowest_price * 1.05:  # Within 5% of lowest
                return "🟢 Great time to buy! Price is near historical low"
            elif current_price <= avg_price:
                return "🟡 Good time to buy! Price is below average"
            else:
                return "🔴 Wait for better price! Current price is above average"
        
        except Exception as e:
            logger.error(f"Best time calculation error: {e}")
            return "Unable to calculate"


class PriceDropCalculator:
    """Calculate price drop percentages and savings"""
    
    @staticmethod
    def calculate_drop_percentage(original_price: float, current_price: float) -> float:
        """Calculate percentage drop"""
        if original_price <= 0:
            return 0.0
        return ((original_price - current_price) / original_price) * 100
    
    @staticmethod
    def get_drop_badge_color(percentage: float) -> str:
        """Get color for price drop badge"""
        if percentage >= 30:
            return "#e74c3c"  # Red - Amazing deal
        elif percentage >= 20:
            return "#f39c12"  # Orange - Great deal
        elif percentage >= 10:
            return "#3498db"  # Blue - Good deal
        elif percentage > 0:
            return "#2ecc71"  # Green - Small drop
        else:
            return "#95a5a6"  # Gray - No drop
    
    @staticmethod
    def get_drop_badge_text(percentage: float) -> str:
        """Get text for price drop badge"""
        if percentage >= 30:
            return f"🔥 {percentage:.1f}% OFF - AMAZING!"
        elif percentage >= 20:
            return f"⚡ {percentage:.1f}% OFF - GREAT!"
        elif percentage >= 10:
            return f"✨ {percentage:.1f}% OFF - GOOD"
        elif percentage > 0:
            return f"↓ {percentage:.1f}% OFF"
        else:
            return "No discount"


# Global instances
clipboard_monitor = ClipboardMonitor()
bulk_importer = BulkImporter()
price_predictor = PricePredictor()
price_calculator = PriceDropCalculator()
