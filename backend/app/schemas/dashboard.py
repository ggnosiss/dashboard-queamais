"""Schema combinado para o endpoint /api/dashboard/combined."""
from pydantic import BaseModel, computed_field
from datetime import date


class FunnelStep(BaseModel):
    label: str
    value: float | int | None
    source: str  # "meta_ads" | "google_ads" | "erp" | "ga4" | "calculated"
    available: bool = True  # False = placeholder (GA4 ainda não integrado)


class EstablishmentDashboard(BaseModel):
    establishment_id: int
    establishment_name: str
    sigla: str
    brand: str
    period_start: date
    period_end: date

    # Ads
    total_spend: float = 0
    meta_spend: float = 0
    google_spend: float = 0
    total_impressions: int = 0
    total_clicks: int = 0
    ctr: float | None = None
    cpc: float | None = None
    cpm: float | None = None

    # GA4 (placeholder até fase 7)
    sessions: int | None = None          # GA4
    reservations: int | None = None      # GA4

    # ERP
    fat_salao: float | None = None
    fat_total: float | None = None
    fat_delivery: float | None = None
    cmv_pct: float | None = None
    cmo_pct: float | None = None

    @computed_field
    @property
    def roas(self) -> float | None:
        if self.fat_salao and self.total_spend and self.total_spend > 0:
            return round(self.fat_salao / self.total_spend, 2)
        return None

    @computed_field
    @property
    def funnel(self) -> list[FunnelStep]:
        return [
            FunnelStep(label="Investimento (R$)", value=self.total_spend, source="calculated"),
            FunnelStep(label="Impressões", value=self.total_impressions, source="meta_ads+google_ads"),
            FunnelStep(label="Cliques", value=self.total_clicks, source="meta_ads+google_ads"),
            FunnelStep(label="Sessões", value=self.sessions, source="ga4", available=False),
            FunnelStep(label="Reservas", value=self.reservations, source="ga4", available=False),
            FunnelStep(label="Fat. Salão (R$)", value=self.fat_salao, source="erp"),
        ]


class DashboardSummary(BaseModel):
    period_start: date
    period_end: date
    total_spend: float
    total_impressions: int
    total_clicks: int
    total_fat_salao: float | None
    blended_roas: float | None
    establishments: list[EstablishmentDashboard]
