from app.database import Base, engine
from app.models import user  # ensure models are imported

if __name__ == "__main__":
    print("📦 Creating tables in Postgres...")
    Base.metadata.create_all(bind=engine)
    print("✅ Done. Tables are ready.")
