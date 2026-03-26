from pydantic import BaseModel, computed_field
from datetime import date


class ChannelMetrics(BaseModel):
    channel: str
    label: str
    color: str
    sessions: int = 0
    users: int = 0
    reservations: int = 0
    reservation_value: float = 0.0
    ads_spend: float = 0.0          # injetado do Meta/Google para canais pagos

    @computed_field
    @property
    def conversion_rate(self) -> float | None:
        if self.sessions > 0:
            return round(self.reservations / self.sessions * 100, 2)
        return None

    @computed_field
    @property
    def cpa(self) -> float | None:
        """Custo por reserva (apenas canais com spend)."""
        if self.ads_spend > 0 and self.reservations > 0:
            return round(self.ads_spend / self.reservations, 2)
        return None

    @computed_field
    @property
    def roas(self) -> float | None:
        if self.ads_spend > 0 and self.reservation_value > 0:
            return round(self.reservation_value / self.ads_spend, 2)
        return None


class AttributionSummary(BaseModel):
    establishment_id: int
    establishment_name: str
    sigla: str
    brand: str
    period_start: date
    period_end: date

    # Agregados
    total_sessions: int = 0
    total_reservations: int = 0
    total_reservation_value: float = 0.0
    total_ads_spend: float = 0.0
    fat_total: float | None = None   # ERP — faturamento total

    channels: list[ChannelMetrics] = []

    @computed_field
    @property
    def overall_conversion_rate(self) -> float | None:
        if self.total_sessions > 0:
            return round(self.total_reservations / self.total_sessions * 100, 2)
        return None

    @computed_field
    @property
    def overall_roas(self) -> float | None:
        if self.total_ads_spend > 0 and self.fat_total:
            return round(self.fat_total / self.total_ads_spend, 2)
        return None

    @computed_field
    @property
    def overall_cpa(self) -> float | None:
        if self.total_ads_spend > 0 and self.total_reservations > 0:
            return round(self.total_ads_spend / self.total_reservations, 2)
        return None
