from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from app import dburl
from app import dburlcba


print dburl


engine = create_engine(
    dburl, convert_unicode=True,
    pool_recycle=3600, pool_size=10)
db_session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))


engine_cba = create_engine(
    dburlcba, convert_unicode=True,
    pool_recycle=3600, pool_size=10)
db_session_cba = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))
