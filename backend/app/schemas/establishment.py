from pydantic import BaseModel


class EstablishmentOut(BaseModel):
    id: int
    sigla: str
    name: str
    brand: str
    meta_ad_account_id: str | None
    google_ads_customer_id: str | None
    ga4_property_id: str | None

    model_config = {"from_attributes": True}


class EstablishmentUpdate(BaseModel):
    meta_ad_account_id: str | None = None
    google_ads_customer_id: str | None = None
    ga4_property_id: str | None = None
