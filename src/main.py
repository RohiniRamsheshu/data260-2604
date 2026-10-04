from fastapi import FastAPI, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from src.auth import router as auth_router
from src.auth_api import router as auth_api_router
from src.crud_api import router as crud_api_router
from src.hw5_api import router as hw5_router
app = FastAPI()   # <-- must be created before any app.xxx() call

# Explicit CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,  # Mandatory for HTTP-only session cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key="dev-secret-2604",
    https_only=False,
    same_site="lax",
)

app.include_router(auth_router)
app.include_router(auth_api_router)   # <-- moved here, after app exists
app.include_router(crud_api_router)
app.include_router(hw5_router)

