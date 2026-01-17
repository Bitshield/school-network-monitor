"""
Database configuration and session management.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres@localhost:5432/school_network"
)

# Convert to async URL for psycopg3
ASYNC_DATABASE_URL = DATABASE_URL.replace(
    "postgresql://", 
    "postgresql+psycopg://"
)

logger.info(f"Database URL: {ASYNC_DATABASE_URL}")

Base = declarative_base()

def get_async_engine():
    """Create async database engine."""
    return create_async_engine(
        ASYNC_DATABASE_URL,
        echo=False,  # Set to False in production, True for debugging
        future=True,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,  # Recycle connections after 1 hour
    )

async_engine = get_async_engine()

# Create async session maker
async_session = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

async def async_init_db():
    """
    Initialize database tables.
    IMPORTANT: Import all models before calling this function!
    """
    # Import all models to register them with Base
    from models.device import Device
    from models.port import Port
    from models.link import Link
    from models.event import Event # type: ignore
    from models.cable_health import CableHealthMetrics
    
    logger.info("Creating database tables...")
    
    try:
        async with async_engine.begin() as conn:
            # Drop all tables (use with caution!)
            # await conn.run_sync(Base.metadata.drop_all)
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully!")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

async def get_db():
    """
    Dependency for getting async database sessions.
    Use this in FastAPI route dependencies.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()