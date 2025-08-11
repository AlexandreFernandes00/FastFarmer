from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .config import settings
from .api.v1 import users
from .api.v1 import auth as auth_routes
from .api.v1 import profiles as profiles_routes
from .api.v1 import machines as machines_routes
from .api.v1 import listings as listings_routes
from .api.v1 import pricing as pricing_routes
from .api.v1 import categories as categories_routes
from .api.v1 import fields as fields_routes
from .api.v1 import requests as requests_routes
from .api.v1 import quotes as quotes_routes
from .web import router as web_router




app = FastAPI(title=settings.PROJECT_NAME)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(web_router, tags=["web"])
app.include_router(auth_routes.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["users"])

app.include_router(profiles_routes.router, prefix=f"{settings.API_V1_PREFIX}", tags=["profiles"])  # <-- add
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["users"])

app.include_router(machines_routes.router, prefix=f"{settings.API_V1_PREFIX}/machines", tags=["machines"])
app.include_router(listings_routes.router, prefix=f"{settings.API_V1_PREFIX}/listings", tags=["listings"])
app.include_router(pricing_routes.router, prefix=f"{settings.API_V1_PREFIX}/pricing", tags=["pricing"])
app.include_router(categories_routes.router, prefix=f"{settings.API_V1_PREFIX}/categories", tags=["categories"])

app.include_router(fields_routes.router,   prefix=f"{settings.API_V1_PREFIX}/fields",   tags=["fields"])
app.include_router(requests_routes.router, prefix=f"{settings.API_V1_PREFIX}/requests", tags=["requests"])
app.include_router(quotes_routes.router,   prefix=f"{settings.API_V1_PREFIX}/quotes",   tags=["quotes"])

@app.get("/healthz")
def healthz():
    return {"ok": True}
