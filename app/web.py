from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/machines")
def machines_page(request: Request):
    return templates.TemplateResponse("machines.html", {"request": request})

@router.get("/listings")
def listings_page(request: Request):
    return templates.TemplateResponse("listings.html", {"request": request})

@router.get("/fields")
def fields_page(request: Request):
    return templates.TemplateResponse("fields.html", {"request": request})

@router.get("/inbox")
def provider_inbox(request: Request):
    return templates.TemplateResponse("provider_inbox.html", {"request": request})
