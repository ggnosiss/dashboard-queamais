from sqlalchemy import Integer, Numeric, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
from app.database import Base


class Ga4ChannelSnapshot(Base):
    """Cache de atribuição por canal de marketing (GA4) por estabelecimento/dia."""
    __tablename__ = "ga4_channel_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    establishment_id: Mapped[int] = mapped_column(ForeignKey("establishments.id"), nullable=False, index=True)
    ga4_property_id: Mapped[str] = mapped_column(String(50), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Canal normalizado
    # paid_search | paid_social | organic_search | direct | whatsapp | link_in_bio | email_marketing | other
    channel: Mapped[str] = mapped_column(String(30), nullable=False, index=True)

    # Source/medium original do GA4
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    medium: Mapped[str] = mapped_column(String(100), nullable=False, default="")

    # Métricas
    sessions: Mapped[int] = mapped_column(Integer, default=0)
    users: Mapped[int] = mapped_column(Integer, default=0)
    new_users: Mapped[int] = mapped_column(Integer, default=0)
    reservations: Mapped[int] = mapped_column(Integer, default=0)       # conversão principal
    reservation_value: Mapped[float] = mapped_column(Numeric(12, 2), default=0)  # revenue atribuído

    synced_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    establishment: Mapped["Establishment"] = relationship()
