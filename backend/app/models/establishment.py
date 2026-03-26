from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Establishment(Base):
    __tablename__ = "establishments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # ID do SIG (ex: 102)
    sigla: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    brand: Mapped[str] = mapped_column(String(50), nullable=False)

    # Contas de ads (uma por canal, pode ser nulo até configurar)
    meta_ad_account_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    google_ads_customer_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ga4_property_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    erp_snapshots: Mapped[list["ErpSnapshot"]] = relationship(back_populates="establishment")
    meta_snapshots: Mapped[list["MetaAdsSnapshot"]] = relationship(back_populates="establishment")
    google_snapshots: Mapped[list["GoogleAdsSnapshot"]] = relationship(back_populates="establishment")

    def __repr__(self) -> str:
        return f"<Establishment {self.sigla} - {self.name}>"
