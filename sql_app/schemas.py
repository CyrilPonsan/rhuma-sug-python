from pydantic import BaseModel
from datetime import datetime


class AdresseBase(BaseModel):
    nom: str
    prenom: str
    adresse: str
    code_postal: str
    ville: str


class AdresseCreate(AdresseBase):
    pass


class Adresse(AdresseBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


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
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class VenteBase(BaseModel):
    id: int


class VenteCreate(VenteBase):
    date: datetime


class Vente(VenteBase):
    customer_id: int
    achats: list[int]

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



