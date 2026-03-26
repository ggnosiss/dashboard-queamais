from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date, timedelta

from app.database import get_db
from app.auth import require_api_key
from app.models.establishment import Establishment
from app.models.ga4_attribution import Ga4ChannelSnapshot
from app.models.meta_ads import MetaAdsSnapshot
from app.models.google_ads import GoogleAdsSnapshot
from app.models.erp_snapshot import ErpSnapshot
from app.schemas.ga4 import ChannelMetrics, AttributionSummary
from app.services.ga4_service import sync_all, sync_establishment, CHANNEL_LABELS, CHANNEL_COLORS

router = APIRouter(prefix="/api/ga4", tags=["ga4"])

ALL_CHANNELS = list(CHANNEL_LABELS.keys())


@router.get("/attribution", response_model=list[AttributionSummary])
async def get_attribution(
    establishment_ids: list[int] = Query(default=[]),
    brands: list[str] = Query(default=[]),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_api_key),
):
    if not end_date:
        end_date = date.today() - timedelta(days=1)
    if not start_date:
        start_date = end_date - timedelta(days=29)

    # Estabelecimentos
    stmt = select(Establishment)
    if establishment_ids:
        stmt = stmt.where(Establishment.id.in_(establishment_ids))
    if brands:
        stmt = stmt.where(Establishment.brand.in_(brands))
    result = await db.execute(stmt)
    establishments = {e.id: e for e in result.scalars().all()}
    ids = list(establishments.keys())
    if not ids:
        return []

    # GA4 por canal
    ga4_r = await db.execute(
        select(
            Ga4ChannelSnapshot.establishment_id,
            Ga4ChannelSnapshot.channel,
            func.sum(Ga4ChannelSnapshot.sessions).label("sessions"),
            func.sum(Ga4ChannelSnapshot.users).label("users"),
            func.sum(Ga4ChannelSnapshot.reservations).label("reservations"),
            func.sum(Ga4ChannelSnapshot.reservation_value).label("reservation_value"),
        )
        .where(
            Ga4ChannelSnapshot.establishment_id.in_(ids),
            Ga4ChannelSnapshot.date >= start_date,
            Ga4ChannelSnapshot.date <= end_date,
        )
        .group_by(Ga4ChannelSnapshot.establishment_id, Ga4ChannelSnapshot.channel)
    )
    # {est_id: {channel: row}}
    ga4_by_est: dict[int, dict] = {}
    for row in ga4_r.all():
        ga4_by_est.setdefault(row.establishment_id, {})[row.channel] = row

    # Meta Ads spend
    meta_r = await db.execute(
        select(MetaAdsSnapshot.establishment_id, func.sum(MetaAdsSnapshot.spend).label("spend"))
        .where(MetaAdsSnapshot.establishment_id.in_(ids),
               MetaAdsSnapshot.date >= start_date, MetaAdsSnapshot.date <= end_date)
        .group_by(MetaAdsSnapshot.establishment_id)
    )
    meta_spend = {r.establishment_id: float(r.spend or 0) for r in meta_r.all()}

    # Google Ads spend
    google_r = await db.execute(
        select(GoogleAdsSnapshot.establishment_id, func.sum(GoogleAdsSnapshot.cost_micros).label("cost_micros"))
        .where(GoogleAdsSnapshot.establishment_id.in_(ids),
               GoogleAdsSnapshot.date >= start_date, GoogleAdsSnapshot.date <= end_date)
        .group_by(GoogleAdsSnapshot.establishment_id)
    )
    google_spend = {r.establishment_id: round((r.cost_micros or 0) / 1_000_000, 2) for r in google_r.all()}

    # ERP faturamento total
    erp_r = await db.execute(
        select(ErpSnapshot)
        .where(ErpSnapshot.establishment_id.in_(ids), ErpSnapshot.months_window == 1)
        .order_by(ErpSnapshot.establishment_id, ErpSnapshot.synced_at.desc())
    )
    erp_by_est: dict[int, ErpSnapshot] = {}
    for s in erp_r.scalars().all():
        if s.establishment_id not in erp_by_est:
            erp_by_est[s.establishment_id] = s

    summaries = []
    for eid, est in establishments.items():
        channels_data = ga4_by_est.get(eid, {})
        m_spend = meta_spend.get(eid, 0)
        g_spend = google_spend.get(eid, 0)
        total_ads = round(m_spend + g_spend, 2)
        erp = erp_by_est.get(eid)
        fat_total = float(erp.fat_realizado) if erp and erp.fat_realizado else None

        channel_list = []
        for ch in ALL_CHANNELS:
            row = channels_data.get(ch)
            # Atribuir spend aos canais pagos
            ch_spend = 0.0
            if ch == "paid_social":
                ch_spend = m_spend
            elif ch == "paid_search":
                ch_spend = g_spend

            channel_list.append(ChannelMetrics(
                channel=ch,
                label=CHANNEL_LABELS[ch],
                color=CHANNEL_COLORS[ch],
                sessions=int(row.sessions or 0) if row else 0,
                users=int(row.users or 0) if row else 0,
                reservations=int(row.reservations or 0) if row else 0,
                reservation_value=float(row.reservation_value or 0) if row else 0.0,
                ads_spend=ch_spend,
            ))

        total_sessions = sum(c.sessions for c in channel_list)
        total_reservations = sum(c.reservations for c in channel_list)
        total_rv = sum(c.reservation_value for c in channel_list)

        summaries.append(AttributionSummary(
            establishment_id=eid,
            establishment_name=est.name,
            sigla=est.sigla,
            brand=est.brand,
            period_start=start_date,
            period_end=end_date,
            total_sessions=total_sessions,
            total_reservations=total_reservations,
            total_reservation_value=total_rv,
            total_ads_spend=total_ads,
            fat_total=fat_total,
            channels=channel_list,
        ))

    return summaries


@router.post("/sync")
async def trigger_ga4_sync(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    establishment_id: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_api_key),
):
    if not end_date:
        end_date = date.today() - timedelta(days=1)
    if not start_date:
        start_date = end_date - timedelta(days=29)

    if establishment_id:
        r = await db.execute(select(Establishment).where(Establishment.id == establishment_id))
        est = r.scalar_one_or_none()
        if not est:
            return {"error": "Estabelecimento não encontrado"}
        count = await sync_establishment(db, est, start_date, end_date)
        return {"synced": count}

    count = await sync_all(db, start_date, end_date)
    return {"synced": count}
