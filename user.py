from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError

from db.db_config import session, User, Vacancy
from logger import logger
from parsers.parse_work_ua import WorkUaParser
from parsers.parse_djini import DjiniParser
from parsers.parse_dou import DouParser


class UserParser:
    """
    A class for processing user requests.
    """

    def __init__(self, user_data: dict):
        """
        Initializes UserParser with the given user data.

        Args:
            user_data (dict): A dictionary containing user data, including 'tg_id', 'state', 'source', 'city', and 'profession'.
        """
        self.tg_id = None if "tg_id" not in user_data else user_data["tg_id"]
        self.state = user_data["state"]
        self.source = None if "source" not in user_data else user_data["source"]
        self.city = user_data["city"]
        self.profession = user_data["profession"]

    def process_user_request(self):

        if self.state == 1:
            return self.process_state_one()
        elif self.state == 2:
            return self.process_state_two()
        elif self.state == 3:
            return self.process_state_three()
        else:
            raise TypeError(f"Got unexpected state code {self.state}")

    def process_state_one(self) -> list[dict]:
        """
        Requests vacancyes fom all sources
        :return: list of dicts with requested vacancyes
        """
        try:
            return WorkUaParser(vacancy=self.profession, city=self.city).get_result() \
                + DjiniParser(vacancy=self.profession, city=self.city).get_result() \
                + DouParser(vacancy=self.profession, city=self.city).get_result()
        except Exception as err:
            logger.error(f"Error processing state one request: {err}")
            raise err

    def process_state_two(self) -> list[dict]:
        """
        Check source and requests vacancyes from requested source
        :return: list of dicts with requested vacancyes
        """
        try:
            if self.source == "Dou":
                return DouParser(vacancy=self.profession, city=self.city).get_result()
            elif self.source == "Djini":
                return DjiniParser(vacancy=self.profession, city=self.city).get_result()
            elif self.source == "Work.ua":
                return WorkUaParser(vacancy=self.profession, city=self.city).get_result()
            else:
                raise TypeError(f"Got unexpected source {self.source} in state two")
        except Exception as err:
            logger.error(f"Error processing state two request: {err}")
            raise err

    def process_state_three(self):
        """
        Process user subscribtion, add current user to db
        :return: Nothing
        """
        try:
            user_service.add_user(tg_id=self.tg_id, profession=self.profession, city=self.city)
        except Exception as err:
            logger.error(f"Error processing state three request: {err}")
            raise err


class UserService:

    @staticmethod
    def add_user(tg_id: int, profession: str, city: str, regularity: int = 1, ) -> None:
        """
        Add a new user to the database with the given Telegram ID, profession,
        vacancy name, and regularity.
        :param tg_id: user id from Telegram
        :param profession: searched word for user
        :param city: region, where the search will be performed
        :param regularity: default 1
        :return: Nothing
        """

        try:
            user = User(tg_id=tg_id, profession=profession, city=city, regularity=regularity)
            session.add(user)
            session.commit()
            logger.info(f"New user {tg_id} created")
        except IntegrityError:
            session.rollback()
            logger.error(f"User {tg_id} already exists")
            raise ValueError
        except Exception as e:
            session.rollback()
            logger.error(f"There was an error {e}")
            raise e

    @staticmethod
    def update_time(tg_id: int) -> None:
        """
        Update the last update time for the user with the given Telegram ID.
        :param tg_id: user id from Telegram
        :return: Nothing
        """
        try:
            user = session.query(User).filter_by(tg_id=tg_id).first()
            if not user:
                logger.error(f"User {tg_id} not found")
                raise ValueError("User not found")
            user.last_update = func.now()
            session.commit()

            logger.info(f"User {tg_id} updated")

        except ValueError as e:
            logger.error(str(e))
            raise e
        except Exception as e:
            raise e

    @staticmethod
    def process_vacancies(tg_id: int, data: dict) -> list[dict]:
        """
        Add to database new vacancyes from sources if don`t exist in db
        :param tg_id: user id from Telegram
        :param data: list of current vacancyes
        :return: newly added vacancyes or empty list
        """
        existing_vacancies = [i.link for i in session.query(Vacancy).filter_by(user_id=tg_id).all()]
        result = []

        for vacancy in data:
            if not existing_vacancies or vacancy["link"] not in existing_vacancies:
                logger.info(f"Found new vacancyes for {tg_id}")
                result.append(vacancy)
                session.add(
                    Vacancy(
                        user_id=tg_id,
                        link=vacancy["link"],
                        name=vacancy["name"]
                    )
                )
            else:
                logger.info(f"There is no new vacancyes for {tg_id}")
        session.commit()
        return result

    @classmethod
    def get_update(cls) -> list[tuple]:
        """
        Requests if there are new vacancyes
        :return: list of tuples, where are users Telegram id and newly added vacancyes for each user
        """

        users = session.query(User).all()
        relult = []
        for user in users:
            result = DjiniParser(user.profession, user.city).get_result() \
                     + WorkUaParser(user.profession, user.city).get_result() \
                     + DouParser(user.profession, user.city).get_result()
            relult.append((user.tg_id, cls.process_vacancies(tg_id=user.tg_id, data=result)))
        return relult


user_service = UserService()
