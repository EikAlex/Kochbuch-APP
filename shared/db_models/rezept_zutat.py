from sqlalchemy import Column, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from shared.db_models.base import Base


class RezeptZutat(Base):
    __tablename__ = "rezept_zutaten"

    rezept_id = Column(Integer, ForeignKey("rezepte.id"), primary_key=True)
    zutat_id = Column(Integer, ForeignKey("zutaten.id"), primary_key=True)
    menge = Column(Integer, nullable=False)

    rezept = relationship("Rezept", back_populates="rezept_zutaten")
    zutat = relationship("Zutat", back_populates="rezept_zutaten")
