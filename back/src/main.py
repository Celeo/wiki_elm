from typing import List

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from . import models, schemas, crud
from .db import SessionLocal, engine


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get('/articles', response_model=List[schemas.Article])
def articles_list(db: Session = Depends(get_db)):
    return db.query(models.Article).all()


@app.post('/articles')
def articles_create(article: schemas.ArticleCreate, db: Session = Depends(get_db)):
    crud.create_article(db, article, -1)  # TODO need to have the current user here
    return {}


@app.put('/articles')
def article_update(article: schemas.ArticleUpdate, db: Session = Depends(get_db)):
    crud.update_article(db, article)
    return {}
