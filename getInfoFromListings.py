import requests
from bs4 import BeautifulSoup
import pymongo
import time
from getLinks import get_url_list
from jobAnalyserWithPlotly import strip_accents
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager  # TODO change webdriver to undetected chrome
import undetected_chromedriver as uc
from OCRSpaceApi import get_text_from_images
#  TODO get this working with undetected webdriver too
def do_stuff():
    print("getting url list")
    # the url list consists of a list of tuples of [url, keyword]
    url_list_with_keyword = get_url_list()
    url_list = url_list_with_keyword[0]
    keyword = url_list_with_keyword[1]

    # database stuffs
    password = input("Password: ")
    myclient = pymongo.MongoClient(f"mongodb+srv://Admin:{password}"
                                   f"@jobanalyzer.vydrnyx.mongodb.net/?retryWrites=true&w=majority")
    mydb = myclient["jobAnalyzer"]
    mycol = mydb[f"{keyword}_jobs"]

    links_in_db = []  # create a list of all the links already in the database before on extracting info
    # TODO optimize it, check if link exists before even appending to list of links
    for col in mycol.find():
        links_in_db.append(col["link"])

    number_of_links = len(url_list)
    i = 1

    #chrome_options = Options()
    #chrome_options.add_argument("--headless")

    #driver = uc.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


    class Job:  # create job object
        def __init__(self, link=None, location=None, time=None, onsite_experience=[], description_raw=None,
                     is_active=True, is_processed=False, keywords=[], experience_description=[]):
            self.link = link
            self.location = location
            self.time = time
            self.onsite_experience = onsite_experience
            self.description_raw = description_raw
            self.is_active = is_active
            self.is_processed = is_processed
            self.keywords = keywords
            self.experience_description = experience_description


    print(f"url list in getinfo: {url_list}")
    for URL in url_list:
        if URL not in links_in_db:  # skip getting info and appending for listings that already exist in the database
            try:  # TODO do something about the unholy cursed mile long try except

                #driver.get(URL)
                #page = driver.page_source

                page = requests.get(URL)

                time.sleep(1)  # ghetto ass ddos protection
                soup = BeautifulSoup(page.content, "html.parser")
                primary_result = soup.find("div", class_="JMDContent")  # get description
                if type(primary_result) is not None:  # TODO handle images too, OCR them
                    try:
                        primary_result = primary_result.text  # convert desc. to raw text
                        primary_result = primary_result.replace("\n", " ").replace("\r", " ")  # get rid of newlines and breaks
                        description = " ".join(primary_result.split())  # get rid of excess whitespace inside text
                    except Exception as exception:  # TODO make exceptions write to file or database
                        print("\n-----ERROR-----\n")
                        print(f"Exception: {exception}\n")
                        print(f"URL: {URL}\n")
                        print("\n-----ERROR-----\n")
                    job = Job()  # initialize a new job object

                    summaries = soup.find("div", class_="JDSummaries")  # get location, time, experience container
                    if type(summaries) is not None:  # summaries is the container for the on-site basic job info, check if it exists
                        job_info = summaries.findAll("a", class_="JDSummary__Link", limit=3)  # find the first 3 fields, which are, in order: location, time, onsite_experience
                        try:
                            job_location = " ".join(job_info[0].text.split())
                            job.location = strip_accents(job_location)

                            job_time = " ".join(job_info[1].text.split())
                            job_time = job_time.replace(",", "")
                            job.time = job_time

                            job_onsite_experience = " ".join(job_info[2].text.split())
                            job.onsite_experience = job_onsite_experience  # only gets first exp, TODO make it get more of it
                        except Exception as exception:  # TODO make exceptions write to file or database
                            print("\n-----ERROR-----\n")
                            print(f"Exception: {exception}\n")
                            print(f"Job info: {job_info}\n")
                            print(f"URL: {URL}\n")
                            print("\n-----ERROR-----\n")

                        job.description_raw = description

                        job.link = URL

                        dictionary = vars(job)
                        if len(description) > 10:  # check if description actually has content or not
                            mycol.insert_one(dictionary)
                            print("added job to db")
                        else:
                            print(f"desc. too short, URL: {URL}")
                            # TODO check if it's an image, if it is get_text_from_images(URL)
                else:
                    print(f"Description empty: {URL}")
                percent = (i * 100) / number_of_links
                print(f"{i}/{number_of_links} done, {percent:.2f}% done")
                i += 1
            except:
                pass  # TODO error handle this properly
    for link in links_in_db:
        for URL in url_list:
            if URL not in links_in_db:
                pass  # TODO update "link" in db to inactive
