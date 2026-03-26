from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class UserEstablishment(Base):
    """Permissões: quais casas cada gerente pode visualizar."""
    __tablename__ = "user_establishments"
    __table_args__ = (UniqueConstraint("user_id", "establishment_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    establishment_id: Mapped[int] = mapped_column(ForeignKey("establishments.id", ondelete="CASCADE"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="establishments")
    establishment: Mapped["Establishment"] = relationship()
