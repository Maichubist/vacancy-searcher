from sqlalchemy.sql import func

from db.db_config import session, User, Vacancy
from logger import logger
from parsers.parse_work_ua import WorkUaParser
from parsers.parse_djini import DjiniParser
from parsers.parse_dou import DouParser


class UserService:
    def add_user(self, tg_id: int, profession: str, city: str, regularity: int = 1, ) -> None:
        """
        Add a new user to the database with the given Telegram ID, profession,
        vacancy name, and regularity.
        :param tg_id: user id from Telegram
        :param profession: searched word for user
        :param city: region, where the search will be performed
        :param regularity: default 1
        :return:
        """

        try:
            user = User(tg_id=tg_id, profession=profession, city=city, regularity=regularity)
            session.add(user)
            session.commit()
            logger.info(f"New user {tg_id} created")
        except ValueError as e:
            session.rollback()
            logger.error(f"User {tg_id} already exists")
            raise e
        except Exception as e:
            session.rollback()
            logger.error(f"There was an error {e}")
            raise e

    def update_time(self, tg_id: int) -> None:
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

    def process_vacancies(self, tg_id: int, data: dict) -> list[dict]:
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

    def get_update(self) -> list[tuple]:
        """

        :return: list of tuples, where are users Telegram id and newly added vacancyes for each user
        """

        users = session.query(User).all()
        relult =[]
        for user in users:
            result = DjiniParser(user.profession, user.city).get_result() + WorkUaParser(user.profession, user.city).get_result() + DouParser(user.profession, user.city).get_result()
            relult.append((user.tg_id, self.process_vacancies(tg_id=user.tg_id, data=result)))
        return relult




user_service = UserService()
