import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager  # TODO change webdriver to undetected chrome
import undetected_chromedriver as uc

keywords_to_search = []  # initialize list for keywords
list_of_links = []  # initialize list for links


def get_search_word():
    search_word = input("Search query for ejobs: ")
    search_word.replace(" ", "-")
    return search_word


def get_url_list():
    keyword = get_search_word()
    j = 1  # init. incrementing variable for showing progress
    page_number = 1
    more_pages = True
    while more_pages:
        base_url = f"https://www.ejobs.ro/locuri-de-munca/{keyword}/sort-publish/pagina{page_number}"

        chrome_options = Options()
        chrome_options.add_argument("--headless")  # open chrome in headless mode

        driver = uc.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)  # use undetected chromedriver to get around cloudflare
        #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)  # install chrome webdriver on first run

        driver.get(base_url)

        time.sleep(5)  # TODO change this to a proper wait until load

        scroll_pause_time = 1  # wait between scrolls to make sure pages load
        screen_height = driver.execute_script("return window.screen.height;")  # get the screen height of the web
        i = 1

        while True:
            # scroll one screen height each time
            driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
            i += 1
            time.sleep(scroll_pause_time)
            # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
            scroll_height = driver.execute_script("return document.body.scrollHeight;")
            # Break the loop when the height we need to scroll to is larger than the total scroll height
            if (screen_height) * i > scroll_height:
                break


        html = driver.page_source

        soup = BeautifulSoup(html, "html.parser")
        list_of_divs = soup.findAll("div", class_="JCContentMiddle")  # find job containers based on class name
        for div in list_of_divs:
            link = div.find("a")
            list_of_links.append(f'https://www.ejobs.ro{link.get("href")}')
            print(f"link#{j} added to list")
            j += 1
        if soup.find("a", class_="JLPButton JLPButton--Next") is not None:  # if there's a next page button, load next page, otherwise stop searching
            page_number += 1
        else:
            more_pages = False
    print(f"Number of links: {len(list_of_links)}, URL list in getlinks: {list_of_links}")
    return [list_of_links, keyword]
