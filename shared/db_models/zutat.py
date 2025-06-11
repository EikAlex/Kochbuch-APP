from sqlalchemy import Column, Integer, String
from shared.db_models.base import Base
from sqlalchemy.orm import relationship


class Zutat(Base):
    __tablename__ = "zutaten"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    einheit = Column(String, nullable=False)

    vorrat = relationship("Vorrat", back_populates="zutat")
    rezept_zutaten = relationship("RezeptZutat", back_populates="zutat")
    # TODO: Icon nach Zutat(Kategorie) hinzufügen, sowie Hinweis TK, Frisch, Gewürze etc.
