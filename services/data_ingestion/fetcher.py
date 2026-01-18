"""
Stock Data Fetcher with Rate Limiting and Exponential Backoff

Uses Alpha Vantage API to fetch stock data.
- Rate limiting: Prevents API blocks
- Exponential backoff: Smart retries on failures
"""

import time
import requests
from typing import Optional, Dict, Any
from rate_limiter import TokenBucketRateLimiter


class StockFetcher:
    """
    Fetches stock data from Alpha Vantage API with:
    - Rate limiting (5 requests/minute for free tier)
    - Exponential backoff retry logic
    """

    # Alpha Vantage base URL
    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str):
        """
        Initialize the fetcher.

        Args:
            api_key: Your Alpha Vantage API key
        """
        self.api_key = api_key

        # Alpha Vantage free tier: 5 requests per minute
        # 5 requests / 60 seconds = 0.083 requests per second
        self.rate_limiter = TokenBucketRateLimiter(
            max_tokens=5,
            refill_rate=5/60  # 0.083 tokens per second
        )

    def _make_request(self, params: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Make HTTP request with rate limiting and exponential backoff.

        Args:
            params: Query parameters for the API

        Returns:
            JSON response or None if all retries failed
        """
        # Add API key to params
        params["apikey"] = self.api_key

        # Exponential backoff settings
        max_retries = 5
        base_delay = 1  # Start with 1 second

        for attempt in range(max_retries):
            # Wait for rate limiter
            while not self.rate_limiter.acquire():
                time.sleep(0.5)  # Wait and retry

            try:
                response = requests.get(self.BASE_URL, params=params, timeout=10)

                # Check for HTTP errors
                if response.status_code == 200:
                    data = response.json()

                    # Alpha Vantage returns error messages in JSON
                    if "Error Message" in data:
                        print(f"API Error: {data['Error Message']}")
                        return None

                    if "Note" in data:  # Rate limit warning
                        print(f"Rate limit warning: {data['Note']}")
                        # Wait longer before retry
                        time.sleep(60)
                        continue

                    return data

                elif response.status_code == 429:  # Too Many Requests
                    print(f"Rate limited by API (429)")
                    # Fall through to exponential backoff

                else:
                    print(f"HTTP Error: {response.status_code}")

            except requests.exceptions.Timeout:
                print(f"Request timeout (attempt {attempt + 1})")

            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")

            # EXPONENTIAL BACKOFF
            # Attempt 0: wait 1 sec  (1 * 2^0 = 1)
            # Attempt 1: wait 2 sec  (1 * 2^1 = 2)
            # Attempt 2: wait 4 sec  (1 * 2^2 = 4)
            # Attempt 3: wait 8 sec  (1 * 2^3 = 8)
            # Attempt 4: wait 16 sec (1 * 2^4 = 16)
            delay = base_delay * (2 ** attempt)
            print(f"Retrying in {delay} seconds... (attempt {attempt + 1}/{max_retries})")
            time.sleep(delay)

        print("All retries failed")
        return None

    def get_stock_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get current stock price (Global Quote).

        Args:
            symbol: Stock ticker (e.g., "AAPL")

        Returns:
            Dict with price data or None
        """
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol
        }
        return self._make_request(params)

    def get_daily_prices(self, symbol: str, outputsize: str = "compact") -> Optional[Dict[str, Any]]:
        """
        Get daily historical prices.

        Args:
            symbol: Stock ticker (e.g., "AAPL")
            outputsize: "compact" (100 days) or "full" (20+ years)

        Returns:
            Dict with daily price data or None
        """
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": outputsize
        }
        return self._make_request(params)

    def get_company_overview(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get company fundamentals (P/E ratio, market cap, etc).

        Args:
            symbol: Stock ticker (e.g., "AAPL")

        Returns:
            Dict with company data or None
        """
        params = {
            "function": "OVERVIEW",
            "symbol": symbol
        }
        return self._make_request(params)


# Test the fetcher
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    from config import Settings

    settings = Settings()

    # Check if API key exists
    if not hasattr(settings, 'alpha_vantage_api_key') or not settings.alpha_vantage_api_key:
        print("ERROR: ALPHA_VANTAGE_API_KEY not found in .env")
        print("Add this line to your .env file:")
        print("ALPHA_VANTAGE_API_KEY=your_key_here")
        sys.exit(1)

    print("Testing Stock Fetcher with Alpha Vantage API")
    print("=" * 50)

    fetcher = StockFetcher(api_key=settings.alpha_vantage_api_key)

    # Test 1: Get stock price
    print("\nTest 1: Get AAPL current price")
    data = fetcher.get_stock_price("AAPL")
    if data and "Global Quote" in data:
        quote = data["Global Quote"]
        print(f"  Symbol: {quote.get('01. symbol')}")
        print(f"  Price: ${quote.get('05. price')}")
        print(f"  Change: {quote.get('10. change percent')}")
    else:
        print("  Failed to get price data")

    print("\n" + "=" * 50)
    print("Test complete!")
