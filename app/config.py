import os

class Settings:
    PROJECT_NAME: str = "FastFarmer v0.1"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://koyeb-adm:npg_PND1qt8ckuvM@ep-bitter-bush-a2xswfkn.eu-central-1.pg.koyeb.app/koyebdb")

settings = Settings()
