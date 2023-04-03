import requests
from bs4 import BeautifulSoup as BS


class DjiniParser:
    def __init__(self, vacancy: str = "python", city: str = "", experience: str = "") -> None:
        # self.user = user
        self.vacancy = vacancy.replace(' ', '+')
        self.city = f"{city}"
        self.experience = experience


    def get_result(self):
        result = requests.get(f"https://djinni.co/jobs/?keywords={self.vacancy}&all-keywords=&any-of-keywords=&exclude-keywords=&region=UKR&location={self.city}&exp_level={self.experience}")
        data = BS(result.text, "lxml")
        result = {}
        for el in data.select("ul > li > div > div > a"):
            if el.find('span') is None or len(el.find('span')) > 2 or 'company' in el.get('href'):
                pass
            else:
                result[f"https://djinni.co/{el.get('href')}"] = el.find('span').text
        return result


# print(DjiniParser().get_result())
