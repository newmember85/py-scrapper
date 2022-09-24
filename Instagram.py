import json
import random
from pathlib import Path
import os
import requests
from requests_html import HTMLSession
import re
import json
import time
from bs4 import BeautifulSoup
from decimal import *
import constants as API_K
from datetime import datetime


# Updates the JSON File for every Call in Function "run_instagram_lockup"
def update_instagram_calls(api_type):
    with open("API_CALLS.json", "r", encoding="utf-8") as df:
        data = json.load(df)

    with open("API_CALLS.json", "w", encoding="utf-8") as file:
        data[f"Instagram{api_type}"]["Calls"] += 1
        json.dump(data, file)


# Picks random user_agent String from JSON FILE user_agents.json
def get_random_user_agent():
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


# Creates Session Header with user_agent
def create_session_header():
    #
    user_agent = get_random_user_agent()
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        # "Accept-Encoding": "gzip,deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": f"{user_agent}"
    }

    return headers


# Tor Proxy Connection
def tor_proxy():
    # Tor uses the 9050 port as the default socks port
    proxies = {'http': 'socks5://localhost:9050',
               'https': 'socks5://localhost:9050'}
    return proxies


# Create Request with given URL
def create_tor_request(url):
    result = requests.get(url, proxies=tor_proxy(), headers=create_session_header())
    result.cookies.clear()
    return result


# Converts Media ID into URL short code
def media_id_converter(media_id):
    postid = ""
    try:
        id = int(media_id)
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

        while id > 0:
            remainder = (id % 64)
            id = Decimal((id - remainder)) / Decimal(64)
            postid = alphabet[int(remainder)] + postid
        print(postid)
        url = f"https://instagram.com/p/{postid}"
        return url
    except Exception as e:
        print(e)


def check_biography_for_email(script):
    biography = script.get("data").get("biography")
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    wordlist = biography.split()
    [email] = [email for email in wordlist if "@" in email] or ["N0 Email was found"]
    if email == "N0 Email was found":
        print(email)
    else:
        if re.fullmatch(regex, email):
            print(f"Valid Email was found: {email}")

        else:
            print("Invalid Email")


def check_biography_for_external_url(script):
    url = script.get("data").get("external_url")
    if url is None:
        print("No URL was found")
    elif "http" in url:
        print(f"External URL was found {url}")


def display_biography(script):
    biography = script.get("data").get("biography")
    print(biography)


def display_full_name(script):
    full_name = script.get("data").get("full_name")
    # is_verified
    # connected_fb_page
    print(full_name)


def user_dictionary_creation(user_name):
    try:
        os.mkdir(f'./data/{user_name}')
    except:
        print('Dictionary already exists')


class InstagramSearch:
    def __init__(self, user_name, *args):
        self.user_name = user_name
        if len(args) != 0:
            self.user_id = args[0]
        user_dictionary_creation(self.user_name)

    # Returns User_Name Informations ,Followers ,Following,Posts
    def check_username_instagram(self):
        # Establish Tor Seeion
        res = create_tor_request(f'https://www.instagram.com/{self.user_name}')
        soup = BeautifulSoup(res.text, 'html.parser')

        # Username, Followers, Following, Posts Amount
        user_infos = soup.select('head > meta:nth-child(89)')
        attributes_user = user_infos[0].attrs["content"]
        user_list = [value.strip() for value in re.split('[",-]', attributes_user)]
        if "Posts" not in user_list[2]:
            user_list[2] = user_list[2] + "," + user_list[3]
            user_list.pop(3)
        #
        # Profile Pic
        profile_pic_element = soup.select('head > meta:nth-child(97)')
        profile_pic_url = profile_pic_element[0].attrs["content"]
        print("User Informations: ")
        # Return User Information
        user_dict = {re.split("[()]", user_list[3])[1]: {"Followers": user_list[0], "Following": user_list[1],
                                                         "Posts": user_list[2], "Profile_Pic": profile_pic_url}}
        print(user_dict)
        return user_dict

    def get_user_name_information(self):
        url = f"https://instagram188.p.rapidapi.com/userinfo/{self.user_name}"

        headers = {
            "X-RapidAPI-Key": API_K.API_KEY_SERVICE,
            "X-RapidAPI-Host": "instagram188.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, proxies=tor_proxy())
        time.sleep(2)
        if response.status_code == 200:
            update_instagram_calls(headers["X-RapidAPI-Host"][9:12])
            with open(
                    f"./data/{self.user_name}/{self.user_name}-user-information-{datetime.now().strftime('%d.%m.%Y')}.json",
                    "w", encoding="utf-8") as file:
                json.dump(response.json(), file)

    def test_proxy(self):
        result = requests.get("https://httpbin.org/get", proxies=tor_proxy())
        print(result)


if __name__ == '__main__':
    instagram = InstagramSearch("basostream")
    # instagram.get_user_name_information()
    instagram.test_proxy()
