from sqlalchemy import Integer, Numeric, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
from app.database import Base


class MetaAdsSnapshot(Base):
    """Cache das métricas do Meta Ads por estabelecimento/dia."""
    __tablename__ = "meta_ads_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    establishment_id: Mapped[int] = mapped_column(ForeignKey("establishments.id"), nullable=False, index=True)
    ad_account_id: Mapped[str] = mapped_column(String(50), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Métricas
    spend: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    reach: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    link_clicks: Mapped[int] = mapped_column(Integer, default=0)
    conversions: Mapped[int] = mapped_column(Integer, default=0)
    conversion_value: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    synced_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    establishment: Mapped["Establishment"] = relationship(back_populates="meta_snapshots")
