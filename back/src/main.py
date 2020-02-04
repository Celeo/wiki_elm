from datetime import datetime, timedelta
import os
import sys
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt import PyJWTError
from sqlalchemy.orm import Session
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from . import models, schemas, crud
from .db import SessionLocal, engine


# =============================
# Setup
# =============================


if os.path.exists('.env'):
    load_dotenv()

app = FastAPI()
models.Base.metadata.create_all(bind=engine)
oauth2_schema = OAuth2PasswordBearer(tokenUrl='/token')

JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_MINUTES = 30
JWT_SECRET = os.environ.get('JWT_SECRET')
if not JWT_SECRET:
    print("No 'JWT_SECRET' environment variable set")
    sys.exit(1)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def create_access_token(*, data: models.User, expires_delta: timedelta = None) -> str:
    to_encode = data.to_dict()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(JWT_EXPIRATION_MINUTES)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, JWT_SECRET, JWT_ALGORITHM)


def decode_token(token: str, db: Session) -> models.User:
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get('name')
        if not username:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    user = crud.get_user_by_name(db, username)
    if not user:
        raise credentials_exception
    return user


async def get_current_user(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)) -> models.User:
    user = decode_token(token, db)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication credentials',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    return user


@app.post('/token')
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> dict:
    user = crud.check_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail='Incorrect username or password'
        )
    return {
        'access_token': create_access_token(data=user),
        'token_type': 'bearer'
    }



@app.get('/users/me')
async def get_current_username(user: models.User = Depends(get_current_user)):
    return user.name


# =============================
# Actual endpoints
# =============================


@app.get('/articles', response_model=List[schemas.Article])
async def articles_list(db: Session = Depends(get_db)) -> dict:
    return db.query(models.Article).all()


@app.post('/articles')
async def articles_create(
    article: schemas.ArticleCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
) -> dict:
    crud.create_article(db, article, user.id)
    return {}


@app.put('/articles/{id}')
async def article_update(
    id: int,
    article: schemas.ArticleUpdate,
    db: Session = Depends(get_db),
    _user: models.User = Depends(get_current_user)
) -> dict:
    article.id = id
    crud.update_article(db, article)
    return {}
