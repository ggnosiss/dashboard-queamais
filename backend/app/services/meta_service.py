"""Integração com a API do Meta Ads (facebook-business SDK)."""
from datetime import date, timedelta, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.config import get_settings
from app.models.establishment import Establishment
from app.models.meta_ads import MetaAdsSnapshot


def _get_api():
    from facebook_business.api import FacebookAdsApi
    settings = get_settings()
    FacebookAdsApi.init(
        app_id=settings.meta_app_id,
        app_secret=settings.meta_app_secret,
        access_token=settings.meta_access_token,
    )


def _fetch_insights(ad_account_id: str, start: date, end: date) -> list[dict]:
    from facebook_business.adobjects.adaccount import AdAccount

    account = AdAccount(f"act_{ad_account_id}")
    params = {
        "time_range": {"since": start.isoformat(), "until": end.isoformat()},
        "time_increment": 1,  # por dia
        "level": "account",
    }
    fields = [
        "date_start",
        "spend",
        "impressions",
        "reach",
        "clicks",
        "inline_link_clicks",
        "actions",
        "action_values",
    ]
    return list(account.get_insights(fields=fields, params=params))


def _extract_conversions(actions: list[dict] | None) -> tuple[int, float]:
    if not actions:
        return 0, 0.0
    count = sum(
        int(a.get("value", 0))
        for a in actions
        if a.get("action_type") in ("offsite_conversion.fb_pixel_purchase", "lead", "omni_purchase")
    )
    return count, 0.0


async def sync_establishment(
    db: AsyncSession,
    establishment: Establishment,
    start_date: date,
    end_date: date,
) -> int:
    """Busca métricas do Meta Ads e salva no banco. Retorna nº de registros inseridos."""
    if not establishment.meta_ad_account_id:
        return 0

    settings = get_settings()
    if not settings.meta_access_token:
        print("[Meta] Access token não configurado, pulando.")
        return 0

    _get_api()

    try:
        insights = _fetch_insights(establishment.meta_ad_account_id, start_date, end_date)
    except Exception as exc:
        print(f"[Meta] Erro ao buscar insights para {establishment.sigla}: {exc}")
        return 0

    # Remover registros existentes no período
    await db.execute(
        delete(MetaAdsSnapshot).where(
            MetaAdsSnapshot.establishment_id == establishment.id,
            MetaAdsSnapshot.date >= start_date,
            MetaAdsSnapshot.date <= end_date,
        )
    )

    records = []
    for row in insights:
        day = date.fromisoformat(row["date_start"])
        conversions, conv_value = _extract_conversions(row.get("actions"))
        records.append(
            MetaAdsSnapshot(
                establishment_id=establishment.id,
                ad_account_id=establishment.meta_ad_account_id,
                date=day,
                spend=float(row.get("spend", 0)),
                impressions=int(row.get("impressions", 0)),
                reach=int(row.get("reach", 0)),
                clicks=int(row.get("clicks", 0)),
                link_clicks=int(row.get("inline_link_clicks", 0)),
                conversions=conversions,
                conversion_value=conv_value,
                synced_at=datetime.utcnow(),
            )
        )

    db.add_all(records)
    await db.commit()
    return len(records)


async def sync_all(
    db: AsyncSession,
    start_date: date | None = None,
    end_date: date | None = None,
) -> int:
    """Sincroniza todos os estabelecimentos com conta Meta configurada."""
    if not end_date:
        end_date = date.today() - timedelta(days=1)
    if not start_date:
        start_date = end_date - timedelta(days=29)

    result = await db.execute(
        select(Establishment).where(Establishment.meta_ad_account_id.isnot(None))
    )
    establishments = result.scalars().all()

    total = 0
    for e in establishments:
        count = await sync_establishment(db, e, start_date, end_date)
        total += count
    return total
