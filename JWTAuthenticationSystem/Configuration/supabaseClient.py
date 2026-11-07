# Configuration/supabaseClient.py
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from Configuration.config import settings

Base = declarative_base()

_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None

def getDatabaseEngine() -> AsyncEngine:
    global _engine
    if _engine is not None:
        return _engine

    _engine = create_async_engine(
        settings.database_url, 
        echo=settings.db_echo,
        connect_args={"statement_cache_size": 0} 
    )
    return _engine

def getSessionFactory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is not None:
        return _session_factory

    engine = getDatabaseEngine()
    _session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    return _session_factory

async def getDbSession():
    sessionFactory = getSessionFactory()
    async with sessionFactory() as session:
        yield session

async def closeDatabaseConnections() -> None:
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None