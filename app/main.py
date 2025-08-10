from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .config import settings
from .api.v1 import users
from .api.v1 import auth as auth_routes
from .api.v1 import profiles as profiles_routes
from .web import router as web_router


app = FastAPI(title=settings.PROJECT_NAME)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(web_router, tags=["web"])
app.include_router(auth_routes.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["users"])

app.include_router(auth_routes.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(profiles_routes.router, prefix=f"{settings.API_V1_PREFIX}", tags=["profiles"])  # <-- add
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["users"])

@app.get("/healthz")
def healthz():
    return {"ok": True}
