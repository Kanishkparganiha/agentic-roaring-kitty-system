"""
ETL Pipeline for Stock Data

ETL = Extract, Transform, Load
1. Extract: Fetch data from Alpha Vantage API
2. Transform: Clean and format data
3. Load: Save to PostgreSQL database
"""

import sys
import os
from datetime import datetime
from typing import List, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Stock, Price, Fundamental
from config import Settings
from services.data_ingestion.fetcher import StockFetcher


class StockDataPipeline:
    """
    ETL Pipeline for stock data ingestion.

    Usage:
        pipeline = StockDataPipeline()
        pipeline.run(["AAPL", "GOOGL", "MSFT"])
    """

    def __init__(self):
        """Initialize pipeline with database connection and API fetcher."""
        self.settings = Settings()
        self.engine = create_engine(self.settings.database_url)
        self.fetcher = StockFetcher(api_key=self.settings.alpha_vantage_api_key)

    # ==================== EXTRACT ====================

    def extract_stock_quote(self, symbol: str) -> Optional[dict]:
        """
        Extract current stock price from API.

        Args:
            symbol: Stock ticker (e.g., "AAPL")

        Returns:
            Raw API response or None
        """
        print(f"  [EXTRACT] Fetching quote for {symbol}...")
        return self.fetcher.get_stock_price(symbol)

    def extract_company_info(self, symbol: str) -> Optional[dict]:
        """
        Extract company overview/fundamentals from API.

        Args:
            symbol: Stock ticker

        Returns:
            Raw API response or None
        """
        print(f"  [EXTRACT] Fetching company info for {symbol}...")
        return self.fetcher.get_company_overview(symbol)

    # ==================== TRANSFORM ====================

    def transform_stock(self, symbol: str, company_data: dict) -> Optional[Stock]:
        """
        Transform raw API data into Stock model.

        Args:
            symbol: Stock ticker
            company_data: Raw API response from company overview

        Returns:
            Stock object or None
        """
        print(f"  [TRANSFORM] Processing stock data for {symbol}...")

        if not company_data:
            return None

        try:
            # Extract and clean data
            market_cap_str = company_data.get("MarketCapitalization", "0")
            market_cap = int(market_cap_str) if market_cap_str else None

            return Stock(
                ticker=symbol,
                name=company_data.get("Name", symbol),
                sector=company_data.get("Sector"),
                market_cap=market_cap
            )
        except Exception as e:
            print(f"  [ERROR] Transform failed for {symbol}: {e}")
            return None

    def transform_price(self, stock_id: int, quote_data: dict) -> Optional[Price]:
        """
        Transform raw quote data into Price model.

        Args:
            stock_id: Database ID of the stock
            quote_data: Raw API response from global quote

        Returns:
            Price object or None
        """
        if not quote_data or "Global Quote" not in quote_data:
            return None

        try:
            quote = quote_data["Global Quote"]

            return Price(
                stock_id=stock_id,
                date=datetime.now().date(),
                open=float(quote.get("02. open", 0)),
                high=float(quote.get("03. high", 0)),
                low=float(quote.get("04. low", 0)),
                close=float(quote.get("05. price", 0)),
                volume=int(quote.get("06. volume", 0))
            )
        except Exception as e:
            print(f"  [ERROR] Transform price failed: {e}")
            return None

    def transform_fundamental(self, stock_id: int, company_data: dict) -> Optional[Fundamental]:
        """
        Transform company data into Fundamental model.

        Args:
            stock_id: Database ID of the stock
            company_data: Raw API response

        Returns:
            Fundamental object or None
        """
        if not company_data:
            return None

        try:
            # Helper to safely convert to float
            def safe_float(value, default=None):
                try:
                    return float(value) if value and value != "None" else default
                except:
                    return default

            return Fundamental(
                stock_id=stock_id,
                quarter=f"{datetime.now().year}-Q{(datetime.now().month - 1) // 3 + 1}",
                revenue=int(company_data.get("RevenueTTM", 0) or 0),
                net_income=int(company_data.get("GrossProfitTTM", 0) or 0),
                eps=safe_float(company_data.get("EPS")),
                pe_ratio=safe_float(company_data.get("PERatio")),
                debt_to_equity=safe_float(company_data.get("DebtToEquityRatio")),
                reported_at=datetime.now()
            )
        except Exception as e:
            print(f"  [ERROR] Transform fundamental failed: {e}")
            return None

    # ==================== LOAD ====================

    def load_stock(self, session: Session, stock: Stock) -> Optional[int]:
        """
        Load stock into database (insert or update).

        Args:
            session: Database session
            stock: Stock object to save

        Returns:
            Stock ID or None
        """
        print(f"  [LOAD] Saving stock {stock.ticker}...")

        try:
            # Check if stock already exists
            existing = session.query(Stock).filter_by(ticker=stock.ticker).first()

            if existing:
                # Update existing
                existing.name = stock.name
                existing.sector = stock.sector
                existing.market_cap = stock.market_cap
                session.commit()
                return existing.id
            else:
                # Insert new
                session.add(stock)
                session.commit()
                return stock.id

        except Exception as e:
            print(f"  [ERROR] Load stock failed: {e}")
            session.rollback()
            return None

    def load_price(self, session: Session, price: Price) -> bool:
        """
        Load price into database.

        Args:
            session: Database session
            price: Price object to save

        Returns:
            True if successful
        """
        print(f"  [LOAD] Saving price data...")

        try:
            session.add(price)
            session.commit()
            return True
        except Exception as e:
            print(f"  [ERROR] Load price failed: {e}")
            session.rollback()
            return False

    def load_fundamental(self, session: Session, fundamental: Fundamental) -> bool:
        """
        Load fundamental into database.

        Args:
            session: Database session
            fundamental: Fundamental object to save

        Returns:
            True if successful
        """
        print(f"  [LOAD] Saving fundamental data...")

        try:
            session.add(fundamental)
            session.commit()
            return True
        except Exception as e:
            print(f"  [ERROR] Load fundamental failed: {e}")
            session.rollback()
            return False

    # ==================== RUN PIPELINE ====================

    def process_single_stock(self, symbol: str) -> bool:
        """
        Run full ETL pipeline for a single stock.

        Args:
            symbol: Stock ticker

        Returns:
            True if successful
        """
        print(f"\nProcessing {symbol}...")
        print("-" * 40)

        with Session(self.engine) as session:
            # 1. EXTRACT
            company_data = self.extract_company_info(symbol)
            quote_data = self.extract_stock_quote(symbol)

            # 2. TRANSFORM
            stock = self.transform_stock(symbol, company_data)
            if not stock:
                print(f"  [SKIP] Could not transform stock data for {symbol}")
                return False

            # 3. LOAD stock first (need ID for related records)
            stock_id = self.load_stock(session, stock)
            if not stock_id:
                return False

            # 4. TRANSFORM & LOAD price
            price = self.transform_price(stock_id, quote_data)
            if price:
                self.load_price(session, price)

            # 5. TRANSFORM & LOAD fundamentals
            fundamental = self.transform_fundamental(stock_id, company_data)
            if fundamental:
                self.load_fundamental(session, fundamental)

            print(f"  [DONE] {symbol} processed successfully!")
            return True

    def run(self, symbols: List[str]) -> dict:
        """
        Run ETL pipeline for multiple stocks.

        Args:
            symbols: List of stock tickers

        Returns:
            Summary of results
        """
        print("=" * 50)
        print("STOCK DATA PIPELINE - Starting")
        print("=" * 50)

        results = {"success": [], "failed": []}

        for symbol in symbols:
            try:
                if self.process_single_stock(symbol.upper()):
                    results["success"].append(symbol)
                else:
                    results["failed"].append(symbol)
            except Exception as e:
                print(f"  [ERROR] Pipeline failed for {symbol}: {e}")
                results["failed"].append(symbol)

        print("\n" + "=" * 50)
        print("PIPELINE COMPLETE")
        print(f"  Success: {len(results['success'])} stocks")
        print(f"  Failed: {len(results['failed'])} stocks")
        print("=" * 50)

        return results


# Test the pipeline
if __name__ == "__main__":
    print("Testing Stock Data Pipeline")
    print("=" * 50)

    # Check API key
    settings = Settings()
    if not settings.alpha_vantage_api_key:
        print("ERROR: ALPHA_VANTAGE_API_KEY not found in .env")
        sys.exit(1)

    # Create pipeline
    pipeline = StockDataPipeline()

    # Test with one stock (to conserve API calls)
    results = pipeline.run(["AAPL"])

    print("\nResults:", results)
