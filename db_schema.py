from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin

BaseORM = declarative_base()


class Subject(BaseORM):
    __tablename__ = 'subjects'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    articles = relationship('Article')


class Article(BaseORM):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    preview = Column(String)
    contents = Column(String)
    is_featured = Column(Boolean)
    subject_id = Column(Integer, ForeignKey('subjects.id'))


class User(UserMixin, BaseORM):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(250))
    password = Column(String(250))

