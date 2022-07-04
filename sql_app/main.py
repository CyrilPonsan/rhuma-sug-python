from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/catalogue", response_model=list[schemas.Produit])
def get_produits(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_produits(db, skip, limit)


@app.post("/produit", response_model=schemas.Produit)
def create_produit(produit: schemas.ProduitCreate, db: Session = Depends(get_db)):
    return crud.create_produit(db=db, produit=produit)


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post("/vente/")
def create_vente(
        user_id: int,
        vente: schemas.VenteCreate,
        # produit_in_panier = {"id": int, "quantite": int}
        produits_in_panier: list[dict],
        db: Session = Depends(get_db)):
    vente_id = crud.create_vente(db=db, vente=vente, user_id=user_id).id
    for item in produits_in_panier:
        db_produit = crud.get_produit(db, produit_id=item["id"])
        crud.create_panier_record(db=db, vente_id=vente_id, produit=db_produit, quantite=item["quantite"])
    return vente_id


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
