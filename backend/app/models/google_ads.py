from sqlalchemy import Integer, Numeric, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
from app.database import Base


class GoogleAdsSnapshot(Base):
    """Cache das métricas do Google Ads por estabelecimento/dia."""
    __tablename__ = "google_ads_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    establishment_id: Mapped[int] = mapped_column(ForeignKey("establishments.id"), nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(String(50), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Métricas
    cost_micros: Mapped[int] = mapped_column(Integer, default=0)  # centavos × 10^6
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    conversions: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    conversion_value: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    synced_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    establishment: Mapped["Establishment"] = relationship(back_populates="google_snapshots")

    @property
    def cost(self) -> float:
        """Retorna o custo em reais (cost_micros / 1_000_000)."""
        return self.cost_micros / 1_000_000
