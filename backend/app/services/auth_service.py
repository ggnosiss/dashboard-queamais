"""Serviço de autenticação: hash de senha, JWT, validação de token."""
from datetime import datetime, timedelta
import bcrypt
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import get_settings
from app.models.user import User
from app.models.user_establishment import UserEstablishment

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: int, role: str, name: str) -> str:
    settings = get_settings()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {"sub": str(user_id), "role": role, "name": name, "exp": expire}
    return jwt.encode(payload, settings.api_key, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.api_key, algorithms=[ALGORITHM])
    except JWTError:
        return None


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


async def get_allowed_establishment_ids(db: AsyncSession, user: User) -> list[int]:
    """Admin vê tudo (retorna []). Gerente vê só as casas atribuídas."""
    if user.role == "admin":
        return []
    result = await db.execute(
        select(UserEstablishment.establishment_id).where(UserEstablishment.user_id == user.id)
    )
    return list(result.scalars().all())
