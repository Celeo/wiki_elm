from datetime import datetime
from typing import List

import bcrypt
from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, id: int) -> models.User:
    return db.query(models.User).filter(models.User.id == id).first()


def get_user_by_name(db: Session, name: str) -> models.User:
    return db.query(models.User).filter(models.User.name == name).first()


def get_all_articles(db: Session) -> List[models.Article]:
    return db.query(models.Article).all()


def get_article(db: Session, id: int) -> models.Article:
    return db.query(models.Article).filter(models.Article.id == id).first()


def create_user(db: Session, user: schemas.UserCreate):
    new_user = models.User(name=user.name)
    new_user.password = bcrypt.hashpw(user.password, bcrypt.gensalt())
    db.add(new_user)
    db.commit()


def check_user(db: Session, user: schemas.UserLogin) -> bool:
    from_db = get_user_by_name(db, user.name)
    return bcrypt.checkpw(user.password, from_db.password)


def create_article(db: Session, article: schemas.ArticleCreate, creator_id: int):
    new_article = models.Article(**article.dict(), created_by=creator_id, time_created=datetime.utcnow())
    db.add(new_article)
    db.commit()


def update_article(db: Session, article: schemas.ArticleUpdate):
    from_db = get_article(db, article.id)
    if article.title:
        from_db.title = article.title
    if article.content:
        from_db.content = article.content
    db.commit()
