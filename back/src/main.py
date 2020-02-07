from datetime import datetime, timedelta
import os
import sys
from typing import Any, Generator, List

from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt import PyJWTError
from six import Iterator
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from . import models, schemas, crud
from .db import SessionLocal, engine


# =============================
# Setup
# =============================

app = FastAPI()
models.Base.metadata.create_all(bind=engine)
oauth2_schema = OAuth2PasswordBearer(tokenUrl='/token')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_MINUTES = 30

if os.path.exists('.env'):
    load_dotenv()
JWT_SECRET = os.environ.get('JWT_SECRET')
if not JWT_SECRET:
    print("No 'JWT_SECRET' environment variable set")
    sys.exit(1)


def get_db() -> Generator[SessionLocal]:
    """Yield a connection to the database.

    This connection is closed after the calling method returns.

    Returns:
        Generator[SessionLocal]: db connection
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# =============================
# Auth
# =============================


def create_access_token(*, data: models.User, expires_delta: timedelta = None) -> bytes:
    """Create an access token for the user's login.

    Args:
        data (models.User): the user to create the token for
        expires_delta (timedelta): optional override for
            the duration of the token

    Returns:
        bytes: JWT
    """
    to_encode = data.to_dict()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(JWT_EXPIRATION_MINUTES)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, JWT_SECRET, JWT_ALGORITHM)


def decode_token(token: str, db: Session) -> models.User:
    """Returns the user for the token.

    Args:
        token (str): JWT
        db (Session): database connection

    Returns:
        models.User: user for the token

    Raises:
        HTTPException: if the token couldn't be decoded
            or didn't match a user
    """
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


async def get_current_user(
    token: str = Depends(oauth2_schema),
    db: Session = Depends(get_db)
) -> models.User:
    """Get a user for the token.

    This method gets the user's token through a `Depend` and processeses it
    into a `models.User` object (if it's valid).

    Args:
        token (str): user's session token ('Authorization' header)
        db (Session): database connection

    Returns:
        models.User: user for the token

    Raises:
        HTTPException: if the token couldn't be decoded
            or didn't match a user
    """
    return decode_token(token, db)


@app.post('/token')
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> dict:
    """Endpoint: logs in a user

    Args:
        form_data (OAuth2PasswordRequestForm): login form submission data
        db (Session): database connection

    Returns:
        dict: the generated OAuth token information
    """
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
async def get_current_username(user: models.User = Depends(get_current_user)) -> str:
    """Endpoint: returns the current user's name

    Args:
        user (models.User): current user (through Dependency on token)

    Returns:
        str: user's name
    """
    return user.name


# =============================
# Actual endpoints
# =============================


@app.get('/articles', response_model=List[schemas.Article])
async def articles_list(db: Session = Depends(get_db)) -> List[models.Article]:
    """Returns a list of all articles.

    Args:
        db (Session): database connection

    Returns:
        List[models.Article]: articles
    """
    return db.query(models.Article).all()


@app.post('/articles')
async def articles_create(
    article: schemas.ArticleCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
) -> dict:
    """Creates a new article.

    Args:
        article (schemas.ArticleCreate): creation data
        db (Session): database connection
        user (models.User): current user

    Returns:
        dict: empty dict
    """
    crud.create_article(db, article, user.id)
    return {}


@app.put('/articles/{id}')
async def article_update(
    id: int,
    article: schemas.ArticleUpdate,
    db: Session = Depends(get_db),
    _user: models.User = Depends(get_current_user)
) -> dict:
    """Updates an existing article.

    Args:
        id (int): id of the article
        article (schemas.ArticleUpdate): new data
        db (Session): database connection
        _user (models.User): current user
    """
    article.id = id
    crud.update_article(db, article)
    return {}
