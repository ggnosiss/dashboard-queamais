from pydantic import BaseModel, computed_field
from datetime import date, datetime


class MetaAdsDailyOut(BaseModel):
    id: int
    establishment_id: int
    date: date
    spend: float
    impressions: int
    reach: int
    clicks: int
    link_clicks: int
    conversions: int
    synced_at: datetime

    @computed_field
    @property
    def ctr(self) -> float | None:
        if self.impressions > 0:
            return round(self.clicks / self.impressions * 100, 2)
        return None

    @computed_field
    @property
    def cpc(self) -> float | None:
        if self.clicks > 0:
            return round(self.spend / self.clicks, 2)
        return None

    @computed_field
    @property
    def cpm(self) -> float | None:
        if self.impressions > 0:
            return round(self.spend / self.impressions * 1000, 2)
        return None

    model_config = {"from_attributes": True}


class GoogleAdsDailyOut(BaseModel):
    id: int
    establishment_id: int
    date: date
    cost: float
    impressions: int
    clicks: int
    conversions: float
    synced_at: datetime

    @computed_field
    @property
    def ctr(self) -> float | None:
        if self.impressions > 0:
            return round(self.clicks / self.impressions * 100, 2)
        return None

    @computed_field
    @property
    def cpc(self) -> float | None:
        if self.clicks > 0:
            return round(self.cost / self.clicks, 2)
        return None

    model_config = {"from_attributes": True}


class AggregatedAdsOut(BaseModel):
    """Métricas de ads agregadas por período para o dashboard."""
    establishment_id: int
    establishment_name: str
    brand: str
    period_start: date
    period_end: date

    # Meta Ads
    meta_spend: float = 0
    meta_impressions: int = 0
    meta_clicks: int = 0
    meta_conversions: int = 0

    # Google Ads
    google_spend: float = 0
    google_impressions: int = 0
    google_clicks: int = 0
    google_conversions: float = 0

    @computed_field
    @property
    def total_spend(self) -> float:
        return round(self.meta_spend + self.google_spend, 2)

    @computed_field
    @property
    def total_impressions(self) -> int:
        return self.meta_impressions + self.google_impressions

    @computed_field
    @property
    def total_clicks(self) -> int:
        return self.meta_clicks + self.google_clicks

    @computed_field
    @property
    def blended_ctr(self) -> float | None:
        if self.total_impressions > 0:
            return round(self.total_clicks / self.total_impressions * 100, 2)
        return None

    @computed_field
    @property
    def blended_cpc(self) -> float | None:
        if self.total_clicks > 0:
            return round(self.total_spend / self.total_clicks, 2)
        return None

    @computed_field
    @property
    def blended_cpm(self) -> float | None:
        if self.total_impressions > 0:
            return round(self.total_spend / self.total_impressions * 1000, 2)
        return None
