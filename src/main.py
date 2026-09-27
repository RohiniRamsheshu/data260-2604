from fastapi import FastAPI, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from src.auth import router as auth_router
from src.auth_api import router as auth_api_router

app = FastAPI()   # <-- must be created before any app.xxx() call

app.add_middleware(
    SessionMiddleware,
    secret_key="dev-secret-2604",
    https_only=False,
    same_site="lax",
)
app.include_router(auth_router)
app.include_router(auth_api_router)   # <-- moved here, after app exists

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)