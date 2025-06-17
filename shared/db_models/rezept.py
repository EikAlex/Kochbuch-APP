from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from shared.db_models import Base


class Rezept(Base):
    __tablename__ = "rezepte"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    beschreibung = Column(String)

    rezept_zutaten = relationship(
        "RezeptZutat", back_populates="rezept", cascade="all, delete-orphan"
    )
