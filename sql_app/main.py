from datetime import timedelta, datetime

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from sql_app.database import engine, SessionLocal
from sql_app import models, crud, schemas

# to get a string like this run:
# openssl rand -hex 32

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


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def authenticate_user(db_user: models.User, plain_password):
    password_hasher = crud.pwd_context
    if not password_hasher.verify(plain_password, db_user.hashed_password):
        return False
    return True


async def is_email_available(username: str, db: Session):
    db_user = crud.get_user_by_email(db=db, username=username)
    if not db_user:
        return True
    return False


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return TokenData(username=username)
    except JWTError:
        raise credentials_exception


@app.get("/catalogue/", response_model=list[schemas.Produit])
def get_produits(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_produits(db, skip, limit)


@app.post("/produit/", response_model=schemas.Produit)
def create_produit(produit: schemas.ProduitCreate, db: Session = Depends(get_db)):
    return crud.create_produit(db=db, produit=produit)


@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if await authenticate_user(user, form_data.password):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        return False


@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    token_data = await get_current_user(token)
    db_user = crud.get_user_by_email(db=db, username=token_data.username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/new", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if not await is_email_available(user.username, db):
        raise HTTPException(status_code=404, detail="Email not available")
    return crud.create_user(db=db, user=user)


@app.post("/vente/")
async def create_vente(
        # produit_in_panier = {"id": int, "quantite": int}
        produits_in_panier: list[dict],
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)):
    token_data = await get_current_user(token)
    # on récupère l'id de l'utilisateur qui passe la commande
    user_id = crud.get_user_by_email(db=db, username=token_data.username).id
    # id de la dernière vente enregistrée
    vente_id = crud.create_vente(db=db, user_id=user_id)
    for item in produits_in_panier:
        db_produit = crud.get_produit(db, produit_id=item["id"])
        crud.create_panier_record(db=db, vente_id=vente_id, produit=db_produit, quantite=item["quantite"])
    return vente_id


@app.post('/fixtures/')
def write_fixtures(liste_produits: list[schemas.ProduitCreate], db: Session = Depends(get_db)):
    crud.create_fixtures(db=db, liste_produits=liste_produits)
    return {"message": "Done"}


if __name__ == "__main__":
    uvicorn.run("sql_app.main:app", host='127.0.0.1', port=8000, reload=True)