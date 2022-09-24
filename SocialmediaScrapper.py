import json
import random
from pathlib import Path

from selenium import webdriver
import requests
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By

import os


def establish_tor_proxy(user_agent):
    firefox_profile = FirefoxProfile(r'C:\Tor\Tor Browser\Browser\TorBrowser\Data\Browser\profile.default')
    firefox_profile.set_preference('network.proxy.type', 1)
    firefox_profile.set_preference('network.proxy.socks', '127.0.0.1')
    firefox_profile.set_preference('network.proxy.socks_port', 9050)
    firefox_profile.set_preference("network.proxy.socks_remote_dns", False)
    firefox_profile.set_preference("general.useragent.override", f'{user_agent}')
    firefox_profile.update_preferences()
    return firefox_profile


def get_tor_session():
    torexe = os.popen(r'C:\Tor\Tor Browser\Browser\TorBrowser\Tor\tor.exe')
    options = Options()
    user_agent = random_useragent()
    firefox_profile = establish_tor_proxy(user_agent)
    options.add_argument("--headless")
    options.profile = firefox_profile
    browser = webdriver.Firefox(options=options)
    return browser


def initial_Browser():
    browser = get_tor_session()
    browser.get("https://httpbin.org/get/")
    # agent = browser.execute_script("return navigator.userAgent")
    element = browser.page_source
    # element = browser.find_element(By.CSS_SELECTOR, "span.r-1awozwy > span:nth-child(1) > span:nth-child(1)")
    print(element)
    browser.quit()


def random_useragent():
    data_folder = Path(os.getcwd())
    file_path = data_folder / "user_agents.json"
    if os.path.exists(file_path):
        print("Random User-Agent will be picked")
        with open("user_agents.json", "r", encoding="utf-8") as f:
            result = json.load(f)

        user_agent = random.choice(result)["useragent"]
        print(f"{user_agent} was picked!")
        return user_agent
    else:
        print("File could not be found")



def Local_IP():
    options = Options()
    driver = webdriver.Firefox(options=options)
    driver.get("https://check.torproject.org/")


if __name__ == '__main__':
    initial_Browser()
    # random_useragent()
