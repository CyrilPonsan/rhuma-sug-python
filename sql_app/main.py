from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware


from . import crud, models, schemas, jwt
from .database import SessionLocal, engine


# to get a string like this run:
# openssl rand -hex 32
from .jwt import Token

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# liste des domaines autorisés
origins = [
    "http://localhost:4200",
]

# politique CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/catalogue/", response_model=list[schemas.Produit])
def get_produits(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_produits(db, skip, limit)


@app.post("/produit/", response_model=schemas.Produit)
def create_produit(produit: schemas.ProduitCreate, db: Session = Depends(get_db)):
    return crud.create_produit(db=db, produit=produit)


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = jwt.authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.jwt.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


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
