"""Database connection management."""
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from typing import Optional
from shared.config.settings import settings
from shared.utils.logging import get_logger

logger = get_logger(__name__)

_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def get_database_url() -> str:
    """Get database connection URL based on settings.
    
    Returns:
        Database connection URL string
    """
    if settings.use_postgres:
        # PostgreSQL connection
        if not settings.postgres_host:
            logger.warning("postgres_host_not_set_using_defaults")
            host = "localhost"
            port = settings.postgres_port
            user = settings.postgres_user or "postgres"
            password = settings.postgres_password or "postgres"
            database = settings.postgres_database or "databricks_agent"
        else:
            host = settings.postgres_host
            port = settings.postgres_port
            user = settings.postgres_user
            password = settings.postgres_password
            database = settings.postgres_database or "databricks_agent"
        
        # Build PostgreSQL connection string
        ssl_mode = settings.postgres_ssl_mode
        if ssl_mode == "disable":
            return f"postgresql://{user}:{password}@{host}:{port}/{database}"
        else:
            return f"postgresql://{user}:{password}@{host}:{port}/{database}?sslmode={ssl_mode}"
    else:
        # SQL Server connection (legacy)
        if not settings.azure_sql_server:
            raise ValueError("Azure SQL Server configuration not provided")
        
        # Build SQL Server connection string
        server = settings.azure_sql_server
        database = settings.azure_sql_database
        username = settings.azure_sql_username
        password = settings.azure_sql_password
        
        # Use pyodbc connection string
        return (
            f"mssql+pyodbc://{username}:{password}@{server}/{database}"
            f"?driver=ODBC+Driver+18+for+SQL+Server"
            f"&TrustServerCertificate=yes"
        )


def get_database_engine() -> Engine:
    """Get or create database engine.
    
    Returns:
        SQLAlchemy engine instance
    """
    global _engine
    
    if _engine is None:
        database_url = get_database_url()
        
        # Create engine with appropriate pool settings
        if settings.use_postgres:
            # PostgreSQL connection pool
            _engine = create_engine(
                database_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,  # Verify connections before using
                echo=settings.app_env == "development"
            )
        else:
            # SQL Server connection
            _engine = create_engine(
                database_url,
                poolclass=NullPool,  # SQL Server may need different pooling
                echo=settings.app_env == "development"
            )
        
        logger.info("database_engine_created", database_type="postgresql" if settings.use_postgres else "sqlserver")
    
    return _engine


def get_database_session() -> Session:
    """Get database session.
    
    Returns:
        SQLAlchemy session
    """
    global _SessionLocal
    
    if _SessionLocal is None:
        engine = get_database_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return _SessionLocal()


def init_database():
    """Initialize database tables."""
    from shared.database.models import Base
    
    engine = get_database_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("database_tables_initialized")

