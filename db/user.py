from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func

from typing import Optional

from logger import logger
from parsers.parse_work_ua import WorkUaParser
from parsers.parse_djini import DjiniParser

engine = create_engine('sqlite:///packages.db')
Base = declarative_base()


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


class UserService:
    def __init__(self):
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def add_user(self, tg_id: int, profession: str, city: str, regularity: int = 1, ) -> None:
        """
        Add a new user to the database with the given Telegram ID, profession,
        vacancy name, and regularity.
        """

        try:
            user = User(tg_id=tg_id, profession=profession, city=city, regularity=regularity)
            self.session.add(user)
            self.session.commit()
            logger.info(f"New user {tg_id} created")
        except ValueError as e:
            self.session.rollback()
            logger.error(f"User {tg_id} already exists")
            raise e
        except Exception as e:
            self.session.rollback()
            logger.error(f"There was an error {e}")
            raise e

    def update_time(self, tg_id: int) -> None:
        """
        Update the last update time for the user with the given Telegram ID.
        """
        try:
            user = self.session.query(User).filter_by(tg_id=tg_id).first()
            if not user:
                logger.error(f"User {tg_id} not found")
                raise ValueError("User not found")
            user.last_update = func.now()
            self.session.commit()

            logger.info(f"User {tg_id} updated")

        except ValueError as e:
            logger.error(str(e))
            raise e
        except Exception as e:
            raise e

    def process_vacancies(self, tg_id: int, data: dict) -> list[dict]:
        existing_vacancies = [i.link for i in self.session.query(Vacancy).filter_by(user_id=tg_id).all()]
        result = []

        for vacancy in data:
            if not existing_vacancies or vacancy["link"] not in existing_vacancies:
                logger.info(f"Found new vacancyes for {tg_id}")
                result.append(vacancy)
                self.session.add(
                    Vacancy(
                        user_id=tg_id,
                        link=vacancy["link"],
                        name=vacancy["name"]
                    )
                )
            else:
                logger.info(f"There is no new vacancyes for {tg_id}")
        self.session.commit()
        return result

    def get_update(self):
        users = self.session.query(User).all()
        r =[]
        for user in users:
            result = DjiniParser(user.profession, user.city).get_result() + WorkUaParser(user.profession, user.city).get_result()
            r.append((user.tg_id, self.process_vacancies(tg_id=user.tg_id, data=result)))
        return r




user_service = UserService()
