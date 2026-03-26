from sqlalchemy import Integer, Numeric, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base


class ErpSnapshot(Base):
    """Cache dos dados do ERP SIG por estabelecimento/mês/indicador."""
    __tablename__ = "erp_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    establishment_id: Mapped[int] = mapped_column(ForeignKey("establishments.id"), nullable=False, index=True)

    # Período de referência (mês/ano)
    ref_month: Mapped[int] = mapped_column(Integer, nullable=False)   # 1-12
    ref_year: Mapped[int] = mapped_column(Integer, nullable=False)
    months_window: Mapped[int] = mapped_column(Integer, nullable=False)  # ultimosMeses usado

    # Indicadores — valores médios acumulados
    fat_realizado: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    fat_orcado: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    fat_salao_realizado: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    fat_salao_orcado: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    fat_delivery_realizado: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    fat_delivery_orcado: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    cmv_realizado: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    cmv_orcado: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    cmo_realizado: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    cmo_orcado: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)

    synced_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    establishment: Mapped["Establishment"] = relationship(back_populates="erp_snapshots")
