from app.database import Base, engine
from app.models import user  # ensure models are imported
from app.models import profile as profile_model     # noqa
from app.models import catalog as catalog_model     # <-- ADD
from app.models import inventory as inventory_model # noqa

Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    print("📦 Creating tables in Postgres...")
    Base.metadata.create_all(bind=engine)
    print("✅ Done. Tables are ready.")
