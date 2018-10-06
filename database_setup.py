import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.types import TIMESTAMP
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    password_hash = Column(String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


class Catagory(Base):
    __tablename__ = 'catagory'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    date = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    catagory_id = Column(Integer, ForeignKey('catagory.id'))
    catagory = relationship(Catagory)
    date = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    @property
    def serialize(self):
        # Returns object data in easily serializable format
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
        }

engine = create_engine('sqlite:///catalogproject.db')


Base.metadata.create_all(engine)
