import requests
from bs4 import BeautifulSoup as BS

from parsers.parser import Parser



class DouParser(Parser):
    def __init__(self, vacancy: str = "python", city: str = "", experience: str = "") -> None:
        self.vacancy = vacancy.replace(' ', '+')
        self.city = f"{city}"
        self.experience = experience
        self.headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

    def get_result(self):
        result = requests.get(f"https://jobs.dou.ua/vacancies/?city={self.city}&search={self.vacancy}", headers=self.headers)
        data = BS(result.text, "lxml")
        return [
            {
                "link": el.get('href'),
                "name": el.text
            } for el in data.select("a.vt")
        ]


# print(DouParser().get_result())