"""Integração com Google Analytics 4 — atribuição por canal de marketing."""
import os
from datetime import date, timedelta, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.config import get_settings
from app.models.establishment import Establishment
from app.models.ga4_attribution import Ga4ChannelSnapshot

# Mapeamento source/medium → canal normalizado
CHANNEL_RULES = [
    # Pago — Meta Ads
    (lambda s, m: s in ("facebook", "instagram") and m in ("cpc", "paid", "paidsocial"), "paid_social"),
    # Pago — Google Ads
    (lambda s, m: s == "google" and m in ("cpc", "ppc", "paid"), "paid_search"),
    # WhatsApp
    (lambda s, m: "whatsapp" in s, "whatsapp"),
    # Email marketing
    (lambda s, m: m in ("email", "newsletter") or s in ("email", "mailchimp", "sendgrid"), "email_marketing"),
    # Link na bio (Instagram orgânico)
    (lambda s, m: s == "instagram" and m in ("social", "referral", "link_in_bio"), "link_in_bio"),
    # Busca orgânica
    (lambda s, m: m == "organic" or (s == "google" and m == "organic"), "organic_search"),
    # Direct
    (lambda s, m: s in ("(direct)", "direct") and m in ("(none)", "none", ""), "direct"),
]


def normalize_channel(source: str, medium: str) -> str:
    s = source.lower().strip()
    m = medium.lower().strip()
    for rule, channel in CHANNEL_RULES:
        try:
            if rule(s, m):
                return channel
        except Exception:
            pass
    return "other"


CHANNEL_LABELS = {
    "paid_search":    "Google Ads",
    "paid_social":    "Meta Ads (Pago)",
    "organic_search": "Busca Orgânica",
    "direct":         "Direto",
    "whatsapp":       "WhatsApp",
    "link_in_bio":    "Link na Bio",
    "email_marketing":"Email Marketing",
    "other":          "Outros",
}

CHANNEL_COLORS = {
    "paid_search":    "#EA4335",
    "paid_social":    "#1877F2",
    "organic_search": "#22c55e",
    "direct":         "#94a3b8",
    "whatsapp":       "#25D366",
    "link_in_bio":    "#E1306C",
    "email_marketing":"#f59e0b",
    "other":          "#475569",
}


def _get_ga4_client(service_account_file: str):
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.oauth2 import service_account
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"],
    )
    return BetaAnalyticsDataClient(credentials=credentials)


def _fetch_attribution(property_id: str, start: date, end: date, service_account_file: str) -> list[dict]:
    from google.analytics.data_v1beta.types import (
        RunReportRequest, DateRange, Dimension, Metric, OrderBy,
    )
    client = _get_ga4_client(service_account_file)
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start.isoformat(), end_date=end.isoformat())],
        dimensions=[
            Dimension(name="date"),
            Dimension(name="sessionSource"),
            Dimension(name="sessionMedium"),
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="newUsers"),
            Metric(name="conversions"),          # total de conversões
            Metric(name="totalRevenue"),         # revenue atribuído
        ],
        order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="date"))],
    )
    response = client.run_report(request)
    rows = []
    for row in response.rows:
        rows.append({
            "date":     row.dimension_values[0].value,
            "source":   row.dimension_values[1].value,
            "medium":   row.dimension_values[2].value,
            "sessions": int(row.metric_values[0].value),
            "users":    int(row.metric_values[1].value),
            "new_users": int(row.metric_values[2].value),
            "reservations": int(float(row.metric_values[3].value)),
            "reservation_value": float(row.metric_values[4].value),
        })
    return rows


async def sync_establishment(
    db: AsyncSession,
    establishment: Establishment,
    start_date: date,
    end_date: date,
) -> int:
    settings = get_settings()
    property_id = establishment.ga4_property_id
    if not property_id:
        return 0

    sa_file = settings.google_service_account_file
    if not os.path.exists(sa_file):
        print(f"[GA4] Service account não encontrado: {sa_file}")
        return 0

    try:
        rows = _fetch_attribution(property_id, start_date, end_date, sa_file)
    except Exception as exc:
        print(f"[GA4] Erro para {establishment.sigla}: {exc}")
        return 0

    await db.execute(
        delete(Ga4ChannelSnapshot).where(
            Ga4ChannelSnapshot.establishment_id == establishment.id,
            Ga4ChannelSnapshot.date >= start_date,
            Ga4ChannelSnapshot.date <= end_date,
        )
    )

    records = []
    for row in rows:
        channel = normalize_channel(row["source"], row["medium"])
        records.append(Ga4ChannelSnapshot(
            establishment_id=establishment.id,
            ga4_property_id=property_id,
            date=date.fromisoformat(row["date"]),
            channel=channel,
            source=row["source"],
            medium=row["medium"],
            sessions=row["sessions"],
            users=row["users"],
            new_users=row["new_users"],
            reservations=row["reservations"],
            reservation_value=row["reservation_value"],
            synced_at=datetime.utcnow(),
        ))

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
        select(Establishment).where(Establishment.ga4_property_id.isnot(None))
    )
    establishments = result.scalars().all()

    total = 0
    for e in establishments:
        count = await sync_establishment(db, e, start_date, end_date)
        total += count
    return total
