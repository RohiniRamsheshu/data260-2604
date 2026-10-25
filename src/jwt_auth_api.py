from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.auth_api import verify_password
from src.db import get_db
from src.jwt_auth import create_access_token, get_current_jwt_user
from src.models import User


router = APIRouter(
    prefix="/auth",
    tags=["JWT Authentication"],
)


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()

    if user is None or not verify_password(
        form_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token(user)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
        },
    }


@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_jwt_user),
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
    }
