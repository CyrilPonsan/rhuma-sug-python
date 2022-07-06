from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime
from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str, password: str):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return db.query(models.User)\
        .filter(models.User.email == email and models.User.hashed_password == pwd_context.hash(password)).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_produit(db: Session, produit_id: int):
    return db.query(models.Produit).filter(models.Produit.id == produit_id).first()


def get_produits(db: Session, skip: int = 0, limit = 100):
    return db.query(models.Produit).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    fake_hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password, nom=user.nom, prenom=user.prenom)
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


def create_vente(db: Session, vente: schemas.VenteCreate, user_id: int):
    db_vente = models.Vente(date=datetime.now(), customer_id=user_id)
    db.add(db_vente)
    db.commit()
    db.refresh(db_vente)
    return db_vente


def create_panier_record(db: Session, vente_id: int, produit: schemas.Produit, quantite: int):
    db_panier = models.Panier(produit_id=produit.id, prix_vente=produit.prix, quantite=quantite, vente_id=vente_id)
    db.add(db_panier)
    db.commit()
    db.refresh(db_panier)
    return db_panier
