#database file:
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine


SQLALCHEMY_DATABASE_URL = 'sqlite:///./MorizApp.db'

engine=create_engine(SQLALCHEMY_DATABASE_URL)
SessionMoriz=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()