from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Annotated

from pydantic import BaseModel, EmailStr
from jose import jwt
from passlib.context import CryptContext

from app.db.session import get_db
from app.models.user import User
from app.config.config import getAppConfig


router = APIRouter(tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
config = getAppConfig()


# Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"



# Utils

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=config.access_token_expire_minutes
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        config.secret_key,
        algorithm=config.algorithm
    )

    return encoded_jwt



# Routes
@router.post("/register", response_model=UserResponse)
def register(
    user_data: UserRegister,
    db: Annotated[Session, Depends(get_db)]
):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=TokenResponse)
def login(
    user_data: UserLogin,
    db: Annotated[Session, Depends(get_db)]
):
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    payload = {
        "sub": str(user.id),
        "email": user.email
    }

    token = create_access_token(payload)

    return {
        "access_token": token,
        "token_type": "bearer"
    }



# Protected Dependency


from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
):
    try:
        payload = jwt.decode(
            token,
            config.secret_key,
            algorithms=[config.algorithm]
        )

        user_id: str | None = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user