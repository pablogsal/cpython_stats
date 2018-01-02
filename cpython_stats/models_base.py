import os

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

from .models import *


def init_db(db_uri=None):
    if db_uri is None:
        db_uri = os.getenv("DATABASE_URL")
    engine = sqlalchemy.create_engine(db_uri)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    return engine, Base, Session
