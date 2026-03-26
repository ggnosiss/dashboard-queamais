from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date, timedelta

from app.database import get_db
from app.auth import require_api_key
from app.models.establishment import Establishment
from app.models.erp_snapshot import ErpSnapshot
from app.models.meta_ads import MetaAdsSnapshot
from app.models.google_ads import GoogleAdsSnapshot
from app.schemas.dashboard import EstablishmentDashboard, DashboardSummary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/combined", response_model=DashboardSummary)
async def get_combined_dashboard(
    establishment_ids: list[int] = Query(default=[]),
    brands: list[str] = Query(default=[]),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    erp_months: int = Query(default=1, ge=1, le=24),
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
        return DashboardSummary(
            period_start=start_date, period_end=end_date,
            total_spend=0, total_impressions=0, total_clicks=0,
            total_fat_salao=None, blended_roas=None, establishments=[],
        )

    # Meta Ads
    meta_r = await db.execute(
        select(
            MetaAdsSnapshot.establishment_id,
            func.sum(MetaAdsSnapshot.spend).label("spend"),
            func.sum(MetaAdsSnapshot.impressions).label("impressions"),
            func.sum(MetaAdsSnapshot.clicks).label("clicks"),
        )
        .where(
            MetaAdsSnapshot.establishment_id.in_(ids),
            MetaAdsSnapshot.date >= start_date,
            MetaAdsSnapshot.date <= end_date,
        )
        .group_by(MetaAdsSnapshot.establishment_id)
    )
    meta_by_est = {r.establishment_id: r for r in meta_r.all()}

    # Google Ads
    google_r = await db.execute(
        select(
            GoogleAdsSnapshot.establishment_id,
            func.sum(GoogleAdsSnapshot.cost_micros).label("cost_micros"),
            func.sum(GoogleAdsSnapshot.impressions).label("impressions"),
            func.sum(GoogleAdsSnapshot.clicks).label("clicks"),
        )
        .where(
            GoogleAdsSnapshot.establishment_id.in_(ids),
            GoogleAdsSnapshot.date >= start_date,
            GoogleAdsSnapshot.date <= end_date,
        )
        .group_by(GoogleAdsSnapshot.establishment_id)
    )
    google_by_est = {r.establishment_id: r for r in google_r.all()}

    # ERP — snapshot mais recente por estabelecimento
    erp_r = await db.execute(
        select(ErpSnapshot)
        .where(
            ErpSnapshot.establishment_id.in_(ids),
            ErpSnapshot.months_window == erp_months,
        )
        .order_by(ErpSnapshot.establishment_id, ErpSnapshot.synced_at.desc())
    )
    erp_raw = erp_r.scalars().all()
    erp_by_est: dict[int, ErpSnapshot] = {}
    for s in erp_raw:
        if s.establishment_id not in erp_by_est:
            erp_by_est[s.establishment_id] = s

    items: list[EstablishmentDashboard] = []
    for eid, est in establishments.items():
        meta = meta_by_est.get(eid)
        google = google_by_est.get(eid)
        erp = erp_by_est.get(eid)

        meta_spend = float(meta.spend or 0) if meta else 0.0
        meta_imp = int(meta.impressions or 0) if meta else 0
        meta_clk = int(meta.clicks or 0) if meta else 0

        google_spend = round((google.cost_micros or 0) / 1_000_000, 2) if google else 0.0
        google_imp = int(google.impressions or 0) if google else 0
        google_clk = int(google.clicks or 0) if google else 0

        total_spend = round(meta_spend + google_spend, 2)
        total_imp = meta_imp + google_imp
        total_clk = meta_clk + google_clk

        fat_salao = float(erp.fat_salao_realizado) if erp and erp.fat_salao_realizado else None
        fat_total = float(erp.fat_realizado) if erp and erp.fat_realizado else None
        fat_delivery = float(erp.fat_delivery_realizado) if erp and erp.fat_delivery_realizado else None
        cmv_pct = (
            round(erp.cmv_realizado / erp.fat_realizado * 100, 1)
            if erp and erp.cmv_realizado and erp.fat_realizado
            else None
        )
        cmo_pct = (
            round(erp.cmo_realizado / erp.fat_realizado * 100, 1)
            if erp and erp.cmo_realizado and erp.fat_realizado
            else None
        )

        items.append(
            EstablishmentDashboard(
                establishment_id=eid,
                establishment_name=est.name,
                sigla=est.sigla,
                brand=est.brand,
                period_start=start_date,
                period_end=end_date,
                total_spend=total_spend,
                meta_spend=meta_spend,
                google_spend=google_spend,
                total_impressions=total_imp,
                total_clicks=total_clk,
                ctr=round(total_clk / total_imp * 100, 2) if total_imp > 0 else None,
                cpc=round(total_spend / total_clk, 2) if total_clk > 0 else None,
                cpm=round(total_spend / total_imp * 1000, 2) if total_imp > 0 else None,
                fat_salao=fat_salao,
                fat_total=fat_total,
                fat_delivery=fat_delivery,
                cmv_pct=cmv_pct,
                cmo_pct=cmo_pct,
            )
        )

    total_spend = sum(i.total_spend for i in items)
    total_imp = sum(i.total_impressions for i in items)
    total_clk = sum(i.total_clicks for i in items)
    total_fat = sum(i.fat_salao for i in items if i.fat_salao) or None
    blended_roas = round(total_fat / total_spend, 2) if total_fat and total_spend > 0 else None

    return DashboardSummary(
        period_start=start_date,
        period_end=end_date,
        total_spend=total_spend,
        total_impressions=total_imp,
        total_clicks=total_clk,
        total_fat_salao=total_fat,
        blended_roas=blended_roas,
        establishments=items,
    )
