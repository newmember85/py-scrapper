import requests
from requests_html import HTMLSession
import re
import json
import time
import constants as API_K
from bs4 import BeautifulSoup


def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http': 'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session


def get_url_from_local(user):
    session = HTMLSession()
    r = session.get(f'https://twitter.com/{user}')
    r.html.render()
    about = r.html.find('body > script:nth-child(3)', first=True)
    script = about.text
    session.close()
    return script


def get_url_from_tor(user):
    session = get_tor_session()
    script = session.get(f"https://twitter.com/{user}")
    return script


def return_html_script_json(script_user):
    split_script = script_user.split(";window.__META_DATA")[0].split("window.__INITIAL_STATE__=")[1]
    json_acceptable_string = split_script.replace("'", "\"")
    return json.loads(json_acceptable_string)


def return_user_value(json_dict, user):
    user_url = f"https://twitter.com/{user}"
    user_exists_value = json_dict["featureSwitch"]["user"]["config"]["machine_translation_logged_out_enabled"]
    if user_exists_value["value"]:
        print(f"USER COULD BE FOUND: \nURL for {user}: {user_url}")
    else:
        print(f"No User with {user} Username")
    return user_exists_value


def run_twitter_demo(user):
    script = get_url_from_local(user)
    # script = get_url_from_tor()
    json_dict = return_html_script_json(script)
    return return_user_value(json_dict, user)


def update_json_file():
    with open("API_CALLS.json", "r", encoding="utf-8") as df:
        data = json.load(df)

    with open("API_CALLS.json", "w", encoding="utf-8") as file:
        data["Instagram47"]["Calls"] += 1
        data["Instagram188"]["Calls"] += +1
        json.dump(data, file)


def run_instagram_lockup(user_name):
    session = get_tor_session()
    update_json_file()

    instagram_urls = ["https://instagram47.p.rapidapi.com/get_user_id",
                      f"https://instagram188.p.rapidapi.com/userinfo/{user_name}"]

    try:
        for apis in instagram_urls:

            querystring = {"username": user_name}

            headers = {
                "X-RapidAPI-Key": API_K.API_KEY_SERVICE,
                "X-RapidAPI-Host": f"({apis}".split("://")[1].split("m/")[0] + "m)"
            }
            if "instagram188" in apis:
                response = session.request("GET", apis, headers=headers)
            else:
                response = session.request("GET", apis, headers=headers, params=querystring)

            if response.status_code != 200:
                print("Error fetching page probably Maximum Calls")
                continue
            api_result = json.loads(response.text)
            if api_result.get("status") == "Success" or api_result.get("success") is True:
                print(f"The Username: {user_name} was found!!\nURL: https://www.instagram.com/{user_name}/")
                if api_result.get("success") is True:
                    check_biography_for_email(api_result)
                    check_biography_for_external_url(api_result)
            else:
                print(f"The Username : {user_name} was not found, Try again!!")
            time.sleep(5)
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



if __name__ == '__main__':
    run_instagram_lockup("maxi_q1")
    # # run_twitter_demo()
