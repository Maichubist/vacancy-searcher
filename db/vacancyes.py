from sqlalchemy import create_engine, Column, Integer, String, Table, MetaData, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

from logger import logger


class Vacancy:
    def __init__(self) -> None:
        self.engine = create_engine("sqlite:///db/users.db")
        self.metadata = MetaData()
        self.Base = declarative_base(metadata=self.metadata)
        self.table = Table("vacancyes", self.metadata,
                           Column("id", Integer, primary_key=True),
                           Column("tg id", Integer),
                           Column("link", String),
                           Column("name", String),
                           )
        self.metadata.create_all(self.engine)
