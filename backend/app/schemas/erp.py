from pydantic import BaseModel, computed_field
from datetime import datetime


class ErpSnapshotOut(BaseModel):
    id: int
    establishment_id: int
    ref_month: int
    ref_year: int
    months_window: int
    fat_realizado: float | None
    fat_orcado: float | None
    fat_salao_realizado: float | None
    fat_salao_orcado: float | None
    fat_delivery_realizado: float | None
    fat_delivery_orcado: float | None
    cmv_realizado: float | None
    cmv_orcado: float | None
    cmo_realizado: float | None
    cmo_orcado: float | None
    synced_at: datetime

    @computed_field
    @property
    def cmv_pct(self) -> float | None:
        if self.cmv_realizado and self.fat_realizado and self.fat_realizado > 0:
            return round(self.cmv_realizado / self.fat_realizado * 100, 1)
        return None

    @computed_field
    @property
    def cmo_pct(self) -> float | None:
        if self.cmo_realizado and self.fat_realizado and self.fat_realizado > 0:
            return round(self.cmo_realizado / self.fat_realizado * 100, 1)
        return None

    model_config = {"from_attributes": True}
