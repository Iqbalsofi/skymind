"""
Database configuration and models
SQLAlchemy with async support
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Float, DateTime, JSON, Index
from datetime import datetime
from typing import Optional
import os


# Database URL (will use environment variable)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./skymind.db"  # Default to SQLite for development
)

# For PostgreSQL in production, URL format:
# postgresql+asyncpg://user:password@host:port/dbname

# Create async engine (SQLite compatible - no pooling params)
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class ItineraryModel(Base):
    """
    Cached itinerary model
    Stores search results for faster retrieval
    """
    __tablename__ = "itineraries"

    id: Mapped[int] = mapped_column(primary_key=True)
    itinerary_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    
    # Route information
    origin_code: Mapped[str] = mapped_column(String(3), index=True)
    destination_code: Mapped[str] = mapped_column(String(3), index=True)
    departure_date: Mapped[datetime] = mapped_column(DateTime, index=True)
    
    # Pricing
    price_total: Mapped[float] = mapped_column(Float, index=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    # Flight details
    num_stops: Mapped[int] = mapped_column(Integer, index=True)
    total_duration_minutes: Mapped[int] = mapped_column(Integer)
    is_direct: Mapped[bool] = mapped_column(default=False)
    
    # Scoring
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Full data as JSON
    data: Mapped[dict] = mapped_column(JSON)
    
    # Provider
    provider_name: Mapped[str] = mapped_column(String(50))
    provider_id: Mapped[str] = mapped_column(String(100))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_route_date', 'origin_code', 'destination_code', 'departure_date'),
        Index('idx_price_score', 'price_total', 'score'),
    )


class PriceHistoryModel(Base):
    """
    Price history tracking
    Used for buy-vs-wait logic and alerts
    """
    __tablename__ = "price_history"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Route
    route: Mapped[str] = mapped_column(String(50), index=True)  # e.g., "JFK-LAX"
    date: Mapped[datetime] = mapped_column(DateTime, index=True)
    
    # Price statistics
    min_price: Mapped[float] = mapped_column(Float)
    avg_price: Mapped[float] = mapped_column(Float)
    max_price: Mapped[float] = mapped_column(Float)
    median_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Metadata
    num_results: Mapped[int] = mapped_column(Integer)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_route_date_history', 'route', 'date'),
    )


class SearchLogModel(Base):
    """
    Search query logging for analytics
    """
    __tablename__ = "search_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Search parameters
    origin_code: Mapped[str] = mapped_column(String(3))
    destination_code: Mapped[str] = mapped_column(String(3))
    departure_date: Mapped[datetime] = mapped_column(DateTime)
    priority: Mapped[str] = mapped_column(String(20))
    
    # Results
    num_results: Mapped[int] = mapped_column(Integer)
    search_time_ms: Mapped[float] = mapped_column(Float)
    cache_hit: Mapped[bool] = mapped_column(default=False)
    
    # Metadata
    user_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Get database session"""
    async with async_session_maker() as session:
        yield session
