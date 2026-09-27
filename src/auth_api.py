"""
HW4 - Login/logout with password hashing and server-side sessions.

Login flow:
  1. Verify email + password against users table (bcrypt hash check).
  2. Generate a random opaque session token.
  3. Store {token, user_id, expires_at} in the sessions table.
  4. Set the token as an HTTP-only cookie -- the cookie carries ONLY this
     opaque token, never user_id or email directly.

Every protected route depends on get_current_user, which looks the
cookie's token up in the sessions table (not by decoding anything --
the token means nothing on its own without the DB lookup).
"""

import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from passlib.context import CryptContext
from sqlalchemy.orm import Session as DBSession

from src.db import get_db
from src.models import User, Session as SessionModel

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SESSION_COOKIE_NAME = "session_token"
SESSION_LIFETIME_MINUTES = 60


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


@router.post("/api/register")
def register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: DBSession = Depends(get_db),
):
    """Convenience endpoint to create a test user (not in the assignment
    spec, but needed to have someone to log in as)."""
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(name=name, email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "name": user.name, "email": user.email}


@router.post("/api/login")
def login(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: DBSession = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = secrets.token_hex(32)  # opaque, unguessable session token
    expires_at = datetime.utcnow() + timedelta(minutes=SESSION_LIFETIME_MINUTES)

    session_row = SessionModel(id=token, user_id=user.id, expires_at=expires_at)
    db.add(session_row)
    db.commit()

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,  # True in a real HTTPS deployment
        max_age=SESSION_LIFETIME_MINUTES * 60,
    )
    return {"message": "Login successful", "user": {"id": user.id, "name": user.name}}


@router.post("/api/logout")
def logout(
    request: Request,
    response: Response,
    db: DBSession = Depends(get_db),
):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token:
        db.query(SessionModel).filter(SessionModel.id == token).delete()
        db.commit()
    response.delete_cookie(SESSION_COOKIE_NAME)
    return {"message": "Logged out"}


def get_current_user(
    request: Request,
    db: DBSession = Depends(get_db),
) -> User:
    """
    Dependency for protected routes. Looks up the cookie's token in the
    sessions table; the token is meaningless without this DB lookup, and
    an expired session is rejected even if the cookie is still present.
    """
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Login required")

    session_row = db.query(SessionModel).filter(SessionModel.id == token).first()
    if not session_row:
        raise HTTPException(status_code=401, detail="Login required")

    if session_row.expires_at < datetime.utcnow():
        db.delete(session_row)
        db.commit()
        raise HTTPException(status_code=401, detail="Session expired, login required")

    user = db.query(User).filter(User.id == session_row.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Login required")

    return user