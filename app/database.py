from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# normalize DSN for psycopg v3
dsn = settings.DATABASE_URL
if dsn.startswith("postgres://"):
    dsn = dsn.replace("postgres://", "postgresql://", 1)
# force psycopg v3 driver
if dsn.startswith("postgresql://") and "+psycopg" not in dsn:
    dsn = dsn.replace("postgresql://", "postgresql+psycopg://", 1)

connect_args = {}
if dsn.startswith(("postgresql+psycopg://")):
    connect_args = {"sslmode": "require"}

engine = create_engine(dsn, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
