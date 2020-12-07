"""
@author:       Guen Yanik
@Title:        TU Berlin_Isis Crawler
@License:      MIT 
@Description:  Crawler that downloads from all your active modules ( so far only pdf ), as long as it havent already
"""

import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

load_dotenv()
# change in the .env for safety
username: str = os.getenv('ISIS_USERNAME')
password: str = os.getenv('ISIS_PASSWORD')
script_path: str = os.path.realpath(__file__)

try:
    os.mkdir('root/')
    print("Directory ", "root/", " created ")
except FileExistsError:
    print("Directory ", "root/", " already exists")

d = str(os.path.dirname(os.path.abspath(__file__))) + "/root"
direct: str = str(os.path.dirname(os.path.abspath(__file__))) + "/root"

base_url = "https://isis.tu-berlin.de/"
options = Options()
options.headless = False
prefs = {
    'prefs': {
        "download_restrictions": "3",
        # "download.folderList": "2",
        # "download.manager.showWhenStarting": False,
        # "browser.download.manager.showAlertOnComplete": False,
        # "browser.helperApps.neverAsk.saveToDisk": "text/csv",
        # "download.prompt_for_download": False,
        "download.default_directory": direct,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
}
driver = webdriver.Chrome(options=options, desired_capabilities=prefs)
driver.implicitly_wait(30)


# class for better representation
class Course:
    def __init__(self, name, link):
        self.name: str = name
        self.link = link

    def __str__(self):
        print("Coursename: " + self.name)
        print("\nURL :" + self.link)


# back to isis homepage
def to_home():
    return driver.get(base_url)


# get the courses and their links
def get_course_and_links():
    to_home()
    # ausklappen aller kurse muss ergänzt werden !!!!!
    course_container = driver.find_element_by_xpath("//*[div[@id='nav-drawer']]")
    course_list = course_container.find_elements_by_xpath("//*[contains(@data-type,'20')]")
    result = []
    for i in course_list:
        title = i.text
        if str(title).strip() != "":
            link = i.get_attribute("href")
            result.append(Course(title, link))
    return result


def get_weeks_and_pdfs(url):
    driver.get(url)
    link_container: list = driver.find_elements_by_xpath("//*[contains(@href,'mod/resource')]")

    result = []
    for i in link_container:
        title = i.text
        print(title)
        if str(title).strip() != "":
            link = i.get_attribute("href")
            result.append(Course(title, link))
    return result


def download(course):

    dirname = str(course.name).replace('/', '')
    try:
        # Create target Directory
        os.mkdir('root/' + dirname)
        print("Directory ", dirname, " Created ")
    except FileExistsError:
        print("Directory ", dirname, " already exists")

    ff = get_weeks_and_pdfs(course.link)

    for f in ff:
        print(f.name + f.link)
        if f is not None and f.link is not None:
            driver.get(f.link)
            link = driver.current_url
            if ".pdf" in link:
                r = s.get(link, stream=True)
                Path('root/' + dirname + '/' + f.name[:-6] + '.pdf').write_bytes(r.content)
            else:
                continue


driver.get('https://isis.tu-berlin.de/login/index.php')
wait = WebDriverWait(driver, 1000)
driver.find_element_by_id("shibboleth_login").click()
driver.find_element_by_id('username').send_keys(username)
driver.find_element_by_id('password').send_keys(password)
driver.find_element_by_id('login-button').click()
cookies = driver.get_cookies()

s = requests.Session()

# passing the cookies generated from the browser to the session
c = [s.cookies.set(c['name'], c['value']) for c in cookies]

list_of_modules = get_course_and_links()
for loM in list_of_modules:
    download(loM)
# exit
driver.close()
