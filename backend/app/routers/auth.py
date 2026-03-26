from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.database import get_db
from app.auth import get_current_user, require_admin
from app.models.user import User
from app.models.user_establishment import UserEstablishment
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserOut, UserEstablishmentsUpdate
from app.services.auth_service import authenticate_user, create_access_token, hash_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha incorretos.")
    token = create_access_token(user.id, user.role, user.name)
    return TokenResponse(access_token=token, user_id=user.id, name=user.name, role=user.role)


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserEstablishment.establishment_id).where(UserEstablishment.user_id == current_user.id)
    )
    est_ids = list(result.scalars().all())
    out = UserOut.model_validate(current_user)
    out.establishment_ids = est_ids
    return out


# ---- Admin endpoints ----------------------------------------

@router.get("/users", response_model=list[UserOut])
async def list_users(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).order_by(User.name))
    users = result.scalars().all()
    out = []
    for u in users:
        est_r = await db.execute(
            select(UserEstablishment.establishment_id).where(UserEstablishment.user_id == u.id)
        )
        uo = UserOut.model_validate(u)
        uo.establishment_ids = list(est_r.scalars().all())
        out.append(uo)
    return out


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")
    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    uo = UserOut.model_validate(user)
    uo.establishment_ids = []
    return uo


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Você não pode desativar sua própria conta.")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    user.is_active = False
    await db.commit()


@router.put("/users/{user_id}/establishments", response_model=UserOut)
async def set_user_establishments(
    user_id: int,
    data: UserEstablishmentsUpdate,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin define quais casas um gerente pode ver."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    await db.execute(delete(UserEstablishment).where(UserEstablishment.user_id == user_id))
    for eid in data.establishment_ids:
        db.add(UserEstablishment(user_id=user_id, establishment_id=eid))
    await db.commit()

    uo = UserOut.model_validate(user)
    uo.establishment_ids = data.establishment_ids
    return uo
