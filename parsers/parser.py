from abc import ABC, abstractmethod


class Parser(ABC):
    @abstractmethod
    def __init__(self, vacancy, city, experience):
        self.vacancy = vacancy
        self.city = city
        self.experience = experience

    @abstractmethod
    def get_result(self):
        pass
