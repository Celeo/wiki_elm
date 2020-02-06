from datetime import datetime
from typing import List, Optional

import bcrypt
from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, id: int) -> models.User:
    """Return a single user by id.

    Args:
        db (Session): database connection
        id (int): id of the user

    Returns:
        models.User: user
    """
    return db.query(models.User).filter(models.User.id == id).first()


def get_user_by_name(db: Session, name: str) -> models.User:
    """Return a single user by name.

    Args:
        db (Session): database connection
        name (str): name of the user

    Returns:
        models.User: user
    """
    return db.query(models.User).filter(models.User.name == name).first()


def get_all_articles(db: Session) -> List[models.Article]:
    """Return all articles.

    Args:
        db (Session): database connection

    Returns:
        List[models.Article]: list of articles
    """
    return db.query(models.Article).all()


def get_article(db: Session, id: int) -> models.Article:
    """Return a single article by id.

    Args:
        db (Session): database connection
        id (int): id of the article

    Returns:
        models.Article: article
    """
    return db.query(models.Article).filter(models.Article.id == id).first()


def create_user(db: Session, user: schemas.UserCreate) -> None:
    """Create a new user.

    Args:
        db (Session): database connection
        user: (schemas.UserCreate): creation data
    """
    new_user = models.User(name=user.name)
    new_user.password = bcrypt.hashpw(user.password, bcrypt.gensalt())
    db.add(new_user)
    db.commit()


def check_user(db: Session, name: str, password: str) -> Optional[models.User]:
    """Return true if the name and password match.

    Args:
        db (Session): database connection
        name (str): name of the user to check
        password (str): password to check against

    Returns:
        Optional[models.User]: user if the password matches, otherwise None
    """
    from_db = get_user_by_name(db, name)
    if not from_db:
        return None
    if bcrypt.checkpw(password.encode('UTF-8'), from_db.password.encode('UTF-8')):
        return from_db
    return None


def create_article(db: Session, article: schemas.ArticleCreate, creator_id: int) -> None:
    """Create a new article.

    Args:
        db (Session): database connection
        article (schemas.ArticleCreate): data creation data
        creator_id (int): user id of the creator
    """
    new_article = models.Article(**article.dict(), created_by=creator_id, time_created=datetime.utcnow())
    db.add(new_article)
    db.commit()


def update_article(db: Session, article: schemas.ArticleUpdate) -> None:
    """Update an article.

    Args:
        db (Session): database connection
        article (schemas.ArticleUpdate): data update data
    """
    from_db = get_article(db, article.id)
    if article.title:
        from_db.title = article.title
    if article.content:
        from_db.content = article.content
    db.commit()
