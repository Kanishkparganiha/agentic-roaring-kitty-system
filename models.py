from sqlalchemy import create_engine, Column, Integer, BigInteger, Float,String, DateTime,ForeignKey, Index,CheckConstraint
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from sqlalchemy import Date  

Base = declarative_base()

class Stock(Base):
    __tablename__ = 'stocks'

    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    sector = Column(String(100))
    market_cap = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    prices = relationship("Price", back_populates="stock")
    fundamentals = relationship("Fundamental", back_populates="stock")
    scores = relationship("Score", back_populates="stock")
    alerts = relationship("Alert", back_populates="stock")


class Price(Base):
    __tablename__ = 'prices'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(Date, nullable=False)

    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)

    # Relationship back to Stock
    stock = relationship("Stock", back_populates="prices")


class Fundamental(Base):
    __tablename__ = 'fundamentals'

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    quarter = Column(String(10), nullable=False)  # e.g., "2024-Q1"
    revenue = Column(BigInteger)
    net_income = Column(BigInteger)
    eps = Column(Float)  # Earnings per share
    pe_ratio = Column(Float)  # Price to earnings
    debt_to_equity = Column(Float)
    reported_at = Column(DateTime)

    # Relationship back to Stock
    stock = relationship("Stock", back_populates="fundamentals")


class Score(Base):
    __tablename__ = 'scores'

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(Date, nullable=False)
    overall_score = Column(Float)  # Combined score 0-100
    fundamental_score = Column(Float)  # Based on financials
    momentum_score = Column(Float)  # Based on price trends
    sentiment_score = Column(Float)  # Based on news/social
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship back to Stock
    stock = relationship("Stock", back_populates="scores")


class Alert(Base):
    __tablename__ = 'alerts'

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    alert_type = Column(String(50), nullable=False)  # e.g., "price_drop", "score_change"
    message = Column(String(500))
    is_read = Column(Integer, default=0)  # 0 = unread, 1 = read
    triggered_at = Column(DateTime, default=datetime.utcnow)

    # Relationship back to Stock
    stock = relationship("Stock", back_populates="alerts")