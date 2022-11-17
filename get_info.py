from bs4 import BeautifulSoup
from get_html import get_html


def formatter(text):
    text = text.replace("\n", " ").replace("\r", " ").replace(",", "")  # TODO get all cities, only gets one
    text = " ".join(text.split())
    return text


class Job:
    def __init__(self, link, industry, city=None, county=None, type=None, listed_career_level=None, keywords=None,
                 job_description=None, salary=None):
        self.link = link
        self.industry = industry
        self.city = city
        self.county = county
        self.type = type
        self.listed_career_level = listed_career_level
        self.keywords = keywords
        self.job_description = job_description
        self.salary = salary


def get_info(link, industry):
    job = Job(link, industry)
    html = get_html(link)
    soup = BeautifulSoup(html, "html.parser")

    card = soup.find("div", class_="JDCard")
    if type(card) is not None:
        card_fields = card.find_all("div", class_="JDSummary")
        for field in card_fields:
            if field.find("span", title="Salariu") is not None:
                salary = field.find("span", class_="JDSummary__Value").text
                job.salary = formatter(salary)
            if field.find("span", title="Oraș de lucru") is not None:
                city = field.find("a", class_="JDSummary__Link").text
                # TODO get all cities, only gets one
                job.city = formatter(city)
            if field.find("span", title="Judetele") is not None:
                county = field.find("a", class_="JDSummary__Link").text
                # TODO get all counties, only gets one
                job.county = formatter(county)
            if field.find("span", title="Tipul job-ului") is not None:
                job_type = field.find("a", class_="JDSummary__Link").text
                job.type = formatter(job_type)
            if field.find("span", title="Nivel carieră") is not None:
                listed_career_level = field.find("a", class_="JDSummary__Link").text
                # TODO get all levels, only gets one
                job.listed_career_level = formatter(listed_career_level)
            # TODO get language and driving license too if needed here

    job_main_description = soup.find("div", class_="JobMainDescription")
    job.job_description = formatter(job_main_description.text)
    dictionary = vars(job)
    return dictionary
    #  TODO return dictionary with Job object
