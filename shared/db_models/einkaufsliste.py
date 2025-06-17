from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from shared.db_models import Base


class Einkaufsliste(Base):
    __tablename__ = "einkaufsliste"

    id = Column(Integer, primary_key=True)
    zutat_id = Column(Integer, ForeignKey("zutaten.id"))
    menge = Column(Integer)

    zutat = relationship("Zutat")


