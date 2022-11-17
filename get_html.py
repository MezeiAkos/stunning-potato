import time
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager  # TODO change webdriver to undetected chrome
import undetected_chromedriver as uc


chrome_options = Options()
chrome_options.add_argument("--headless") # run chrome webdriver in headless mode

driver = uc.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


def get_html(url, scroll=False):
    driver.get(url)

    time.sleep(3)  # TODO change this to a proper wait until load

    if scroll is True:
        screen_height = driver.execute_script("return window.screen.height;")  # get the screen height of the web
        i = 1
        while True:
            # scroll one screen height each time
            driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
            i += 1
            time.sleep(0.5)
            # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
            scroll_height = driver.execute_script("return document.body.scrollHeight;")
            # Break the loop when the height we need to scroll to is larger than the total scroll height
            if (screen_height) * i > scroll_height:
                break

    raw_html = driver.page_source
    #soup = BeautifulSoup(raw_html, "html.parser")
    #body = soup.find('body')
    #html = body.findChildren(recursive=False)
    return raw_html
