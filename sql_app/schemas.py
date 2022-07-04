from pydantic import BaseModel
from datetime import datetime

from sql_app.models import Vente


class ProduitBase(BaseModel):
    nom: str
    prix: float
    description: str | None = None


class ProduitCreate(ProduitBase):
    pass


class Produit(ProduitBase):
    id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str
    nom: str
    prenom: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    ventes: list[int] = []

    class Config:
        orm_mode = True


class VenteBase(BaseModel):
    id: int


class VenteCreate(VenteBase):
    date: datetime


class Vente(VenteBase):
    customer_id: int

    class Config:
        orm_mode = True


class PanierBase(BaseModel):
    id: int


class PanierCreate(PanierBase):
    prix_vente: float
    quantite: int


class Panier(PanierBase):
    produit_id: int
    vente_id: int

    class Config:
        orm_mode = True



