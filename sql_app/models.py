from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    ventes = relationship("Vente", back_populates="user")
    adresses = relationship("Adresse", back_populates="user")


class Adresse(Base):
    __tablename__ = "adresse"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255))
    prenom = Column(String(255))
    adresse = Column(String(255))
    code_postal = Column(String(10))
    ville = Column(String(255))
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="adresses")


class Produit(Base):
    __tablename__ = "produit"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255), index=True)
    prix = Column(Float)
    description = Column(String(255))
    achats = relationship("Panier", back_populates="produits")


class Vente(Base):
    __tablename__ = "vente"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    customer_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="ventes")
    achats = relationship("Panier", back_populates="ventes")


class Panier(Base):
    __tablename__ = "panier"
    id = Column(Integer, primary_key=True, index=True)
    produit_id = Column(Integer, ForeignKey("produit.id"))
    prix_vente = Column(Float)
    quantite = Column(Integer)
    vente_id = Column(Integer, ForeignKey("vente.id"))
    ventes = relationship("Vente", back_populates="achats")
    produits = relationship("Produit", back_populates="achats")
