from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date, timedelta

from app.database import get_db
from app.auth import require_api_key
from app.models.establishment import Establishment
from app.models.meta_ads import MetaAdsSnapshot
from app.models.google_ads import GoogleAdsSnapshot
from app.schemas.ads import AggregatedAdsOut
from app.services import meta_service, google_ads_service

router = APIRouter(prefix="/api/ads", tags=["ads"])


def _default_dates() -> tuple[date, date]:
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=29)
    return start, end


@router.get("/summary", response_model=list[AggregatedAdsOut])
async def get_ads_summary(
    establishment_ids: list[int] = Query(default=[]),
    brands: list[str] = Query(default=[]),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_api_key),
):
    """Métricas de ads agregadas por estabelecimento no período."""
    if not end_date:
        end_date = date.today() - timedelta(days=1)
    if not start_date:
        start_date = end_date - timedelta(days=29)

    # Busca estabelecimentos com filtros
    stmt = select(Establishment)
    if establishment_ids:
        stmt = stmt.where(Establishment.id.in_(establishment_ids))
    if brands:
        stmt = stmt.where(Establishment.brand.in_(brands))
    result = await db.execute(stmt)
    establishments = {e.id: e for e in result.scalars().all()}

    if not establishments:
        return []

    ids = list(establishments.keys())

    # Meta Ads agregado
    meta_stmt = (
        select(
            MetaAdsSnapshot.establishment_id,
            func.sum(MetaAdsSnapshot.spend).label("spend"),
            func.sum(MetaAdsSnapshot.impressions).label("impressions"),
            func.sum(MetaAdsSnapshot.clicks).label("clicks"),
            func.sum(MetaAdsSnapshot.conversions).label("conversions"),
        )
        .where(
            MetaAdsSnapshot.establishment_id.in_(ids),
            MetaAdsSnapshot.date >= start_date,
            MetaAdsSnapshot.date <= end_date,
        )
        .group_by(MetaAdsSnapshot.establishment_id)
    )
    meta_result = await db.execute(meta_stmt)
    meta_by_est = {row.establishment_id: row for row in meta_result.all()}

    # Google Ads agregado
    google_stmt = (
        select(
            GoogleAdsSnapshot.establishment_id,
            func.sum(GoogleAdsSnapshot.cost_micros).label("cost_micros"),
            func.sum(GoogleAdsSnapshot.impressions).label("impressions"),
            func.sum(GoogleAdsSnapshot.clicks).label("clicks"),
            func.sum(GoogleAdsSnapshot.conversions).label("conversions"),
        )
        .where(
            GoogleAdsSnapshot.establishment_id.in_(ids),
            GoogleAdsSnapshot.date >= start_date,
            GoogleAdsSnapshot.date <= end_date,
        )
        .group_by(GoogleAdsSnapshot.establishment_id)
    )
    google_result = await db.execute(google_stmt)
    google_by_est = {row.establishment_id: row for row in google_result.all()}

    out = []
    for eid, est in establishments.items():
        meta = meta_by_est.get(eid)
        google = google_by_est.get(eid)
        out.append(
            AggregatedAdsOut(
                establishment_id=eid,
                establishment_name=est.name,
                brand=est.brand,
                period_start=start_date,
                period_end=end_date,
                meta_spend=float(meta.spend or 0) if meta else 0,
                meta_impressions=int(meta.impressions or 0) if meta else 0,
                meta_clicks=int(meta.clicks or 0) if meta else 0,
                meta_conversions=int(meta.conversions or 0) if meta else 0,
                google_spend=round((google.cost_micros or 0) / 1_000_000, 2) if google else 0,
                google_impressions=int(google.impressions or 0) if google else 0,
                google_clicks=int(google.clicks or 0) if google else 0,
                google_conversions=float(google.conversions or 0) if google else 0,
            )
        )
    return out


@router.post("/sync")
async def trigger_ads_sync(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_api_key),
):
    """Dispara sincronização manual de Meta Ads + Google Ads."""
    if not end_date:
        end_date = date.today() - timedelta(days=1)
    if not start_date:
        start_date = end_date - timedelta(days=29)

    meta_count = await meta_service.sync_all(db, start_date, end_date)
    google_count = await google_ads_service.sync_all(db, start_date, end_date)
    return {"meta_records": meta_count, "google_records": google_count}
