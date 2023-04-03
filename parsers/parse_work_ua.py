import requests
from bs4 import BeautifulSoup as BS

class WorkUaParser:
    def __init__(self, vacancy: str = "", city: str = "", experience: str = "") -> None:
        # self.user = user
        self.vacancy = vacancy.replace(' ', '+')
        self.city = f"{city}-"
        self.experience = experience

    def get_result(self):
        print(f"https://www.work.ua/jobs-{self.city}{self.vacancy}/?advs=1")
        result = requests.get(f"https://www.work.ua/jobs-{self.city}{self.vacancy}/?advs=1")
        data = BS(result.text, "lxml")
        return {f"https://www.work.ua{el.get('href')}": el.text for el in data.select('div > h2 >a')}




# print(WorkUaParser("Python", "dnipro").get_result())