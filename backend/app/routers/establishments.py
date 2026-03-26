from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.database import get_db
from app.auth import require_api_key
from app.models.establishment import Establishment
from app.schemas.establishment import EstablishmentOut, EstablishmentUpdate

router = APIRouter(prefix="/api/establishments", tags=["establishments"])


@router.get("/", response_model=list[EstablishmentOut])
async def list_establishments(
    brand: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_api_key),
):
    stmt = select(Establishment).order_by(Establishment.brand, Establishment.name)
    if brand:
        stmt = stmt.where(Establishment.brand == brand)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/brands", response_model=list[str])
async def list_brands(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_api_key),
):
    result = await db.execute(select(Establishment.brand).distinct().order_by(Establishment.brand))
    return [r[0] for r in result.all()]


@router.patch("/{establishment_id}", response_model=EstablishmentOut)
async def update_establishment(
    establishment_id: int,
    data: EstablishmentUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_api_key),
):
    """Vincula IDs de contas de ads a um estabelecimento."""
    values = {k: v for k, v in data.model_dump().items() if v is not None}
    if values:
        await db.execute(
            update(Establishment).where(Establishment.id == establishment_id).values(**values)
        )
        await db.commit()
    result = await db.execute(select(Establishment).where(Establishment.id == establishment_id))
    return result.scalar_one()
