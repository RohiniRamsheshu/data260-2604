from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.get("/dashboard")
async def dashboard(request: Request):
    username = request.session.get("user")
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "username": username}
    )
@router.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": None}
    )
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
        return RedirectResponse(url="/dashboard", status_code=303)

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Invalid username or password."}
    )
@router.get("/")
async def home(request: Request):
    username = request.session.get("user")
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "username": username}
    )
@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)