from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func

engine = create_engine('sqlite:///db/packages.db')
Base = declarative_base()


Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True)
    profession = Column(String)
    city = Column(String)
    regularity = Column(Integer)
    last_update = Column(DateTime(timezone=True), default=func.now())
    vacancies = relationship("Vacancy", back_populates="user")

class Vacancy(Base):
    __tablename__ = "vacancies"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    link = Column(String)
    # regularity = Column(Integer)

    user = relationship("User", back_populates="vacancies")

Base.metadata.create_all(engine)