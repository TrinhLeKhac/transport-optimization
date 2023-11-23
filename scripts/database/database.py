from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from config import Config

# engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True)
port = 'postgresql://postgres:123456@localhost:5432/db_supership_ai'
engine = create_engine(port)

Base = declarative_base()
session = sessionmaker(bind=engine)

print("Creating database...")
Base.metadata.create_all(engine)
