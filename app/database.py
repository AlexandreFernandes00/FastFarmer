from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# Normalize DSN for psycopg v3 or psycopg2
dsn = settings.DATABASE_URL
if dsn.startswith("postgres://"):
    dsn = dsn.replace("postgres://", "postgresql://", 1)
# If using psycopg v3
if "+psycopg" not in dsn and dsn.startswith("postgresql://"):
    dsn = dsn.replace("postgresql://", "postgresql+psycopg://", 1)

connect_args = {}
if dsn.startswith("postgresql+psycopg://"):
    connect_args = {"sslmode": "require"}

engine = create_engine(dsn, connect_args=connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
