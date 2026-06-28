from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class AlterIdTracker(Base):
    __tablename__ = "alter_id_tracker"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(30), nullable=False)
    last_alter_id: Mapped[int] = mapped_column(Integer, default=0)
