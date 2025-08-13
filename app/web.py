from fastapi import APIRouter, Request, Depends
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

@router.get("/marketplace")
def marketplace_page(request: Request):
    return templates.TemplateResponse("marketplace.html", {"request": request})

@router.get("/request")
def request_page(request: Request):
    return templates.TemplateResponse("request.html", {"request": request})

@router.get("/requests")  # list my requests
def my_requests_page(request: Request):
    return templates.TemplateResponse("requests.html", {"request": request})

# app/pages.py
@router.get("/provider/requests")
def provider_requests_page(request: Request):
    return templates.TemplateResponse("provider_requests.html", {"request": request})
