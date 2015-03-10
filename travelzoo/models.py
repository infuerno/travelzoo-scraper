from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

import settings

DeclarativeBase = declarative_base()

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**settings.DATABASE))

def create_deals_table(engine):
    """"""
    DeclarativeBase.metadata.create_all(engine)

class Deals(DeclarativeBase):
    """Sqlalchemy deals model"""
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    url = Column('url', String)
    category = Column('category', String)
    sub_category = Column('sub_category', String)
    description = Column('description', String, nullable=True)
    why_we_love_it = Column('why_we_love_it', String, nullable=True)
    contact_name = Column('contact_name', String, nullable=True)
    contact_address = Column('contact_address', String, nullable=True)
    contact_map = Column('contact_map', String, nullable=True)
    contact_phone = Column('contact_phone', String, nullable=True)
    contact_website = Column('contact_website', String, nullable=True)
    whats_included = Column('whats_included', String, nullable=True)
    small_print = Column('small_print', String, nullable=True)
    price = Column('price', String, nullable=True)
    value = Column('value', String, nullable=True)
    discount = Column('discount', String, nullable=True)
    created_at = Column('created_at', DateTime)
    updated_at = Column('updated_at', DateTime, nullable=True)

class DealStats(DeclarativeBase):
    """Sqlalchemy deal stats model to record historical information of how many people have bought a particular deal"""
    __tablename__ = "deal_stats"

    id = Column(Integer, primary_key=True) # will automatically autoincrement
    deal_id = Column(Integer)
    bought = Column('bought', String, nullable=True) # type 2
    created_at = Column('created_at', DateTime)
    replaced_at = Column('replaced_at', DateTime, nullable=True)
    original_id = Column(Integer)