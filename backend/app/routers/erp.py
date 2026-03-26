from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.auth import require_api_key
from app.models.erp_snapshot import ErpSnapshot
from app.models.establishment import Establishment
from app.schemas.erp import ErpSnapshotOut
from app.services import erp_service

router = APIRouter(prefix="/api/erp", tags=["erp"])


@router.get("/summary", response_model=list[ErpSnapshotOut])
async def get_erp_summary(
    establishment_ids: list[int] = Query(default=[]),
    months: int = Query(default=3, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_api_key),
):
    """Retorna os snapshots ERP mais recentes por estabelecimento."""
    stmt = (
        select(ErpSnapshot)
        .where(ErpSnapshot.months_window == months)
        .order_by(ErpSnapshot.establishment_id, ErpSnapshot.synced_at.desc())
    )
    if establishment_ids:
        stmt = stmt.where(ErpSnapshot.establishment_id.in_(establishment_ids))

    result = await db.execute(stmt)
    all_snapshots = result.scalars().all()

    # Retornar apenas o mais recente por estabelecimento
    seen: set[int] = set()
    latest: list[ErpSnapshot] = []
    for s in all_snapshots:
        if s.establishment_id not in seen:
            seen.add(s.establishment_id)
            latest.append(s)
    return latest


@router.post("/sync")
async def trigger_erp_sync(
    months: int = Query(default=3, ge=1, le=24),
    establishment_id: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_api_key),
):
    """Dispara sincronização manual do ERP."""
    if establishment_id:
        result = await db.execute(
            select(Establishment).where(Establishment.id == establishment_id)
        )
        establishment = result.scalar_one_or_none()
        if not establishment:
            return {"error": f"Estabelecimento {establishment_id} não encontrado."}
        snapshot = await erp_service.sync_establishment(db, establishment, months)
        return {"synced": 1, "snapshot_id": snapshot.id}

    snapshots = await erp_service.sync_all(db, months)
    return {"synced": len(snapshots)}
