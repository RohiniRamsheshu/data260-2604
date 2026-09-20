from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import time

IDLE_TIMEOUT_SECONDS = 30  # 2 minutes, easy to demo/test

def _session_is_active(request: Request) -> bool:
    user = request.session.get("user")
    last_active = request.session.get("last_active")

    if not user or not last_active:
        return False

    if time.time() - last_active > IDLE_TIMEOUT_SECONDS:
        request.session.clear()   # too old — kill it
        return False

    request.session["last_active"] = time.time()  # still active — refresh
    return True

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.get("/dashboard")
async def dashboard(request: Request):
    if not _session_is_active(request):
        return RedirectResponse(url="/login", status_code=303)
    username = request.session.get("user")
    return templates.TemplateResponse(request, "dashboard.html", {"username": username})
@router.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse(request, "login.html", {"error": None})

VALID_USERS = {
    "admin": "changeme123",
    "analyst": "vulnscan!2604",
}

@router.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    if VALID_USERS.get(username) == password:
        request.session["user"] = username
        request.session["last_active"] = time.time()
        return RedirectResponse(url="/dashboard", status_code=303)

    return templates.TemplateResponse(request, "login.html", {"error": "Invalid username or password."})

@router.get("/")
async def home(request: Request):
    username = request.session.get("user")
    return templates.TemplateResponse(request, "home.html", {"username": username})  # ← fixed, also added username

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)