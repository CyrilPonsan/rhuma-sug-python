from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime
from . import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_produit(db: Session, produit_id: int):
    return db.query(models.Produit).filter(models.Produit.id == produit_id).first()


def get_produits(db: Session, skip: int = 0, limit = 100):
    return db.query(models.Produit).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_produit(db: Session, produit: schemas.ProduitCreate):
    db_produit = models.Produit(nom=produit.nom, prix=produit.prix, description=produit.description)
    db.add(db_produit)
    db.commit()
    db.refresh(db_produit)
    return db_produit


def create_vente(db: Session, user_id: int):
    db_vente = models.Vente(date=datetime.now(), customer_id=user_id)
    db.add(db_vente)
    db.commit()
    db.refresh(db_vente)
    return db_vente.id


def create_panier_record(db: Session, vente_id: int, produit: schemas.Produit, quantite: int):
    db_panier = models.Panier(produit_id=produit.id, prix_vente=produit.prix, quantite=quantite, vente_id=vente_id)
    db.add(db_panier)
    db.commit()
    db.refresh(db_panier)
    return db_panier


def create_fixtures(db: Session, liste_produits: list[schemas.ProduitCreate]):
    for produit in liste_produits:
        db_fixtures = models.Produit(nom=produit.nom, prix=produit.prix, description=produit.description)
        db.add(db_fixtures)
        db.commit()
        db.refresh(db_fixtures)
    return True