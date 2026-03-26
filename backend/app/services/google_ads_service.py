"""Integração com a API do Google Ads."""
from datetime import date, timedelta, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.config import get_settings
from app.models.establishment import Establishment
from app.models.google_ads import GoogleAdsSnapshot


def _get_client():
    from google.ads.googleads.client import GoogleAdsClient
    settings = get_settings()
    credentials = {
        "developer_token": settings.google_ads_developer_token,
        "client_id": settings.google_ads_client_id,
        "client_secret": settings.google_ads_client_secret,
        "refresh_token": settings.google_ads_refresh_token,
        "login_customer_id": settings.google_ads_login_customer_id,
        "use_proto_plus": True,
    }
    return GoogleAdsClient.load_from_dict(credentials)


def _fetch_daily_metrics(customer_id: str, start: date, end: date) -> list[dict]:
    client = _get_client()
    service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT
            segments.date,
            metrics.cost_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.conversions_value
        FROM campaign
        WHERE segments.date BETWEEN '{start.isoformat()}' AND '{end.isoformat()}'
        ORDER BY segments.date
    """
    response = service.search_stream(customer_id=customer_id, query=query)

    daily: dict[str, dict] = {}
    for batch in response:
        for row in batch.results:
            day = row.segments.date
            if day not in daily:
                daily[day] = {
                    "cost_micros": 0,
                    "impressions": 0,
                    "clicks": 0,
                    "conversions": 0.0,
                    "conversion_value": 0.0,
                }
            daily[day]["cost_micros"] += row.metrics.cost_micros
            daily[day]["impressions"] += row.metrics.impressions
            daily[day]["clicks"] += row.metrics.clicks
            daily[day]["conversions"] += row.metrics.conversions
            daily[day]["conversion_value"] += row.metrics.conversions_value

    return [{"date": d, **v} for d, v in daily.items()]


async def sync_establishment(
    db: AsyncSession,
    establishment: Establishment,
    start_date: date,
    end_date: date,
) -> int:
    if not establishment.google_ads_customer_id:
        return 0

    settings = get_settings()
    if not settings.google_ads_developer_token:
        print("[GoogleAds] Developer token não configurado, pulando.")
        return 0

    try:
        rows = _fetch_daily_metrics(establishment.google_ads_customer_id, start_date, end_date)
    except Exception as exc:
        print(f"[GoogleAds] Erro para {establishment.sigla}: {exc}")
        return 0

    await db.execute(
        delete(GoogleAdsSnapshot).where(
            GoogleAdsSnapshot.establishment_id == establishment.id,
            GoogleAdsSnapshot.date >= start_date,
            GoogleAdsSnapshot.date <= end_date,
        )
    )

    records = [
        GoogleAdsSnapshot(
            establishment_id=establishment.id,
            customer_id=establishment.google_ads_customer_id,
            date=date.fromisoformat(row["date"]),
            cost_micros=row["cost_micros"],
            impressions=row["impressions"],
            clicks=row["clicks"],
            conversions=row["conversions"],
            conversion_value=row["conversion_value"],
            synced_at=datetime.utcnow(),
        )
        for row in rows
    ]

    db.add_all(records)
    await db.commit()
    return len(records)


async def sync_all(
    db: AsyncSession,
    start_date: date | None = None,
    end_date: date | None = None,
) -> int:
    if not end_date:
        end_date = date.today() - timedelta(days=1)
    if not start_date:
        start_date = end_date - timedelta(days=29)

    result = await db.execute(
        select(Establishment).where(Establishment.google_ads_customer_id.isnot(None))
    )
    establishments = result.scalars().all()

    total = 0
    for e in establishments:
        count = await sync_establishment(db, e, start_date, end_date)
        total += count
    return total
