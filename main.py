import traceback

from bs4 import BeautifulSoup
import pymongo
import logging

password = input("Password: ")
myclient = pymongo.MongoClient(f"mongodb+srv://Admin:{password}"
                                   f"@jobanalyzer.vydrnyx.mongodb.net/?retryWrites=true&w=majority")
mydb = myclient["jobAnalyzer"]
mycol = mydb["jobs"]

list_of_links_in_db = []

with open("error.txt", "a") as log:

    def get_links(url):
        html = get_html(url, scroll=True)
        list_of_links = []
        soup = BeautifulSoup(html, "html.parser")
        list_of_divs = soup.findAll("div", class_="JCContentMiddle")  # find job containers based on class name
        for div in list_of_divs:
            link = div.find("a")
            list_of_links.append(f'https://www.ejobs.ro{link.get("href")}')
        print(f"List of links: {list_of_links}")
        return list_of_links


    def next_page_exists(url):
        html = get_html(url, scroll=True)
        soup = BeautifulSoup(html, "html.parser")
        if soup.find("a", class_="JLPButton JLPButton--Next") is not None:  # if there's a next page button return true
            return True
        else:
            return False


    test_url = "https://www.ejobs.ro/user/locuri-de-munca/senior-recruiter-transport-industry/1604043"

    list_of_industries = ["administratie---sector-public", "agrara", "alimentara", "arta---entertainment", "asigurari-"
        , "banci---servicii-financiare", "call-center---bpo", "chimica", "comert---retail", "constructii"
        , "drept", "educatie---training", "energetica", "farma", "imobiliara", "it---telecom", "lemn---pvc"
        , "masini---auto", "media---internet", "medicina---sanatate", "navala---aeronautica"
        , "paza-si-protectie", "petrol---gaze", "prestari-servicii", "manufactura", "protectia--mediului"
        , "publicitate---marketing---pr", "sport---frumusete", "textila"
        , "transport---logistica---import---export", "turism---horeca"]

    if __name__ == '__main__':
        listing_links = []
        from get_html import get_html
        from get_info import get_info


        for industry in list_of_industries:
            print(f"industry: {industry}")
            page_number = 1
            while True:
                link = f"https://www.ejobs.ro/locuri-de-munca/{industry}/sort-publish/{page_number}"
                if next_page_exists(link) is True:
                    page_number += 1
                else:
                    break
                for link in get_links(link):
                    print(f"Inserting {link} to database.")
                    if link not in list_of_links_in_db:
                        try:
                            mycol.insert_one(get_info(link, industry))
                            list_of_links_in_db.append(link)
                        except Exception:
                            traceback.print_exc(file=log)
                            pass

