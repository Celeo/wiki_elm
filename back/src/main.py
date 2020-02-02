import os

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from . import models
from .db import SessionLocal, engine


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get('/')
def index():
    return {
        "message": "Index page"
    }


@app.get('/articles')
def articles_list(db: Session = Depends(get_db)):
    return db.query(models.Article).all()


@app.post('/articles')
def articles_create(db: Session = Depends(get_db)):
    pass
