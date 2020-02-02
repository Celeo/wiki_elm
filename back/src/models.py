from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from .db import Base


class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    password = Column(String)

    articles_created = relationship('Article', back_populates='creator')


class Article(Base):

    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    content = Column(String)
    created_by = Column(Integer, ForeignKey('users.id'))
    time_created = Column(DateTime)

    creator = relationship('User', back_populates='articles_created')
