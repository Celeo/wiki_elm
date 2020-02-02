from datetime import datetime
from typing import List

from pydantic import BaseModel


class Article(BaseModel):
    id: int
    title: str
    content: str
    created_by: int
    time_created: datetime

    class Config:
        orm_mode = True


class ArticleCreate(BaseModel):
    title: str
    content: str


class ArticleUpdate(BaseModel):
    id: int
    title: str
    content: str


class UserBase(BaseModel):
    name: str


class User(UserBase):
    articles_created: List[Article] = []

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str


class UserLogin(UserBase):
    password: str