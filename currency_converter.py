"""
Currency Converter Module for Price Tracker
Handles currency conversion using forex-python
"""

import logging
from typing import Optional, Dict

# Optional import with graceful fallback
try:
    from forex_python.converter import CurrencyRates, RatesNotAvailableError
    FOREX_AVAILABLE = True
except ImportError:
    FOREX_AVAILABLE = False
    CurrencyRates = None  # type: ignore
    RatesNotAvailableError = Exception

from config import Config

# Setup logging with UTF-8 support
import sys
if sys.version_info >= (3, 9):
    logging.basicConfig(
        filename=Config.LOGS_DIR / "currency.log",
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        encoding='utf-8'
    )
else:
    import codecs
    log_file = codecs.open(str(Config.LOGS_DIR / "currency.log"), 'a', 'utf-8')
    logging.basicConfig(
        stream=log_file,
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)


class CurrencyConverter:
    """Handles currency conversion"""
    
    def __init__(self):
        if FOREX_AVAILABLE:
            self.currency_rates = CurrencyRates()
        else:
            self.currency_rates = None
        self.supported_currencies = [
            'INR', 'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 
            'CNY', 'MXN', 'BRL', 'ZAR'
        ]
        self.cache: Dict[str, float] = {}  # Cache exchange rates
    
    def convert(self, amount: float, from_currency: str, to_currency: str) -> Optional[float]:
        """Convert amount from one currency to another with caching"""
        if not FOREX_AVAILABLE:
            logger.warning("forex-python not installed - currency conversion unavailable")
            return None
        
        try:
            if from_currency == to_currency:
                return amount
            
            if amount <= 0:
                logger.warning(f"Invalid amount for conversion: {amount}")
                return None
            
            # Check cache first for exchange rate
            cache_key = f"{from_currency}_{to_currency}"
            
            if cache_key in self.cache:
                # Use cached rate
                rate = self.cache[cache_key]
                converted = amount * rate
                logger.debug(f"Used cached rate for {cache_key}: {rate}")
            else:
                # Fetch new rate and cache it
                rate = float(self.currency_rates.get_rate(from_currency, to_currency))
                self.cache[cache_key] = rate
                converted = amount * rate
                logger.info(f"Fetched and cached rate for {cache_key}: {rate}")
            
            logger.info(f"Converted {amount} {from_currency} to {converted:.2f} {to_currency}")
            return round(converted, 2)
        
        except RatesNotAvailableError:
            logger.error(f"Exchange rates not available for {from_currency} to {to_currency}")
            return None
        except Exception as e:
            logger.error(f"Error converting currency: {e}")
            return None
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Get exchange rate between two currencies"""
        if not FOREX_AVAILABLE:
            return None
        
        try:
            if from_currency == to_currency:
                return 1.0
            
            rate = float(self.currency_rates.get_rate(from_currency, to_currency))
            logger.info(f"Exchange rate {from_currency}/{to_currency}: {rate}")
            return rate
        
        except RatesNotAvailableError:
            logger.error(f"Exchange rate not available for {from_currency}/{to_currency}")
            return None
        except Exception as e:
            logger.error(f"Error getting exchange rate: {e}")
            return None
    
    def get_all_rates(self, base_currency: str = 'INR') -> Optional[Dict[str, float]]:
        """Get all exchange rates for a base currency"""
        if not FOREX_AVAILABLE:
            return None
        
        try:
            rates = self.currency_rates.get_rates(base_currency)
            return rates
        except Exception as e:
            logger.error(f"Error getting all rates: {e}")
            return None
    
    def is_supported(self, currency: str) -> bool:
        """Check if currency is supported"""
        return currency.upper() in self.supported_currencies
    
    def format_price(self, amount: float, currency: str) -> str:
        """Format price with currency symbol"""
        if amount < 0:
            logger.warning(f"Negative amount for formatting: {amount}")
            amount = 0
        
        symbols = {
            'INR': '₹',
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥',
            'AUD': 'A$',
            'CAD': 'C$',
            'CHF': 'CHF',
            'CNY': '¥',
            'MXN': 'MX$',
            'BRL': 'R$',
            'ZAR': 'R'
        }
        
        symbol = symbols.get(currency.upper(), currency.upper())
        
        if currency.upper() in ['JPY', 'CNY']:
            # No decimal places for yen
            return f"{symbol}{amount:.0f}"
        elif currency.upper() == 'INR':
            # Indian Rupee formatting
            return f"{symbol}{amount:.2f}"
        else:
            return f"{symbol}{amount:.2f}"


# Global converter instance
currency_converter = CurrencyConverter()
