from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.db import get_db
from src.models import User


JWT_SECRET = "hw7-development-secret-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(user: User) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)

    payload = {
        "sub": user.username,
        "user_id": user.id,
        "role": user.role,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def get_current_jwt_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired JWT token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )

        username = payload.get("sub")

        if not username:
            raise credentials_error

    except jwt.PyJWTError:
        raise credentials_error

    user = db.query(User).filter(User.username == username).first()

    if user is None:
        raise credentials_error

    return user


def require_roles(*allowed_roles: str):
    def role_checker(
        current_user: User = Depends(get_current_jwt_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role permissions",
            )

        return current_user

    return role_checker
