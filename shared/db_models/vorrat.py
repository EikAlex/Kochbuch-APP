from sqlalchemy import Column, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from shared.db_models import Base


class Vorrat(Base):
    __tablename__ = "vorrat"

    id = Column(Integer, primary_key=True)
    zutat_id = Column(Integer, ForeignKey("zutaten.id"), nullable=False)
    menge = Column(Integer, nullable=False)
    haltbar_bis = Column(Date)
    mindestbestand = Column(Integer, nullable=True)

    zutat = relationship("Zutat", back_populates="vorrat")
