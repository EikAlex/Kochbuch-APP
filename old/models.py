from sqlalchemy import Column, Integer, ForeignKey, String, Date
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Vorrat(Base):
    __tablename__ = "vorrat"
    id = Column(Integer, primary_key=True, index=True)
    zutat_id = Column(Integer, ForeignKey("zutaten.id"), nullable=False)
    menge_vorhanden = Column(Integer, nullable=False)
    haltbar_bis = Column(Date)
    mindestbestand = Column(Integer, nullable=True)
    zutat = relationship("Zutat", back_populates="vorrat")


class Rezept(Base):
    __tablename__ = "rezepte"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    beschreibung = Column(String)

    rezept_zutaten = relationship(
        "RezeptZutat", back_populates="rezept", cascade="all, delete-orphan"
    )


class RezeptZutat(Base):
    __tablename__ = "rezept_zutaten"
    rezept_id = Column(Integer, ForeignKey("rezepte.id"), primary_key=True)
    zutat_id = Column(Integer, ForeignKey("zutaten.id"), primary_key=True)
    menge = Column(Integer, nullable=False)

    rezept = relationship("Rezept", back_populates="rezept_zutaten")
    zutat = relationship("Zutat", back_populates="rezept_zutaten")


class Zutat(Base):
    __tablename__ = "zutaten"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    einheit = Column(String, nullable=False)

    vorrat = relationship("Vorrat", back_populates="zutat")
    rezept_zutaten = relationship("RezeptZutat", back_populates="zutat")
    # TODO: Icon nach Zutat(Kategorie) hinzufügen, sowie Hinweis TK, Frisch, Gewürze etc.


class Einkaufsliste(Base):
    __tablename__ = "einkaufsliste"
    id = Column(Integer, primary_key=True)
    zutat_id = Column(Integer, ForeignKey("zutaten.id"))
    menge = Column(Integer)

    zutat = relationship("Zutat")
