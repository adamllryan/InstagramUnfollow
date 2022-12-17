from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import time


def try_load_element(driver, locator, find):
    # Load element with timeout set to x seconds
    timeout = 10
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((locator, find))
        )
    finally:
        return element


def login(driver, site_info, login_info):
    # Load login page and make sure fully loaded
    driver.get(site_info['url'])
    assert site_info['site_title'] in driver.title
    # Get login box and find login fields
    login_box = try_load_element(driver, By.XPATH, site_info['login_xpath'])
    login_box.find_element(By.NAME, "username") \
        .send_keys(login_info['username'])
    login_box.find_element(By.NAME, "password") \
        .send_keys(login_info['password'])
    # Submit login
    login_box.find_element(By.XPATH, site_info['submit_xpath']) \
        .click()
    # Before continuing, make sure fully logged in
    try_load_element(driver, By.XPATH, site_info['loaded_element_check'])


def get_following(driver, site_info, login_info):
    # load https://www.instagram.com/'username'/following
    url = site_info['data_prefix'] + login_info['username'] + site_info['following_suffix']
    driver.get(url)
    # Load count
    count = int(try_load_element(driver, By.XPATH, site_info['following_count']).text)
    # Grab window path
    window = try_load_element(driver, By.XPATH, site_info['following_window_path'])
    # Scroll to the end of user list and collect users
    accounts = {}
    while count != len(accounts):
        window.send_keys(Keys.PAGE_DOWN, Keys.PAGE_DOWN, Keys.PAGE_DOWN)
        time.sleep(.25)
        accounts = window.find_elements(By.XPATH, "./div/div/div")
    # We only care about usernames so put all usernames into a list and return
    people = list()
    for a in accounts:
        people.append(a.find_element(By.XPATH, "./div[2]").text)
    return people


def get_followers(driver, site_info, login_info):
    # load https://www.instagram.com/'username'/following
    url = site_info['data_prefix'] + login_info['username'] + site_info['followers_suffix']
    driver.get(url)
    # Load Count
    count = int(try_load_element(driver, By.XPATH, site_info['followers_count']).text)
    # Grab window path
    window = try_load_element(driver, By.XPATH, site_info['followers_window_path'])
    # Scroll to the end of user list and collect users
    accounts = {}
    while count != len(accounts):
        window.send_keys(Keys.PAGE_DOWN, Keys.PAGE_DOWN, Keys.PAGE_DOWN)
        time.sleep(.25)
        accounts = window.find_elements(By.XPATH, "./div/div/div")
    # We only care about usernames so put all usernames into a list and return
    people = list()
    for a in accounts:
        people.append(a.find_element(By.XPATH, "./div[2]").text)
    return people


def main():
    site_elements = {
        'url':                      "http://www.instagram.com/accounts/login",
        'site_title':               "Instagram",
        # XPath for login window
        'login_xpath':              "//*[@id=\"loginForm\"]",
        # XPath for the login button
        'submit_xpath':             "/html/body/div[2]/div/div/div/div[1]/div/div/div/div["
                                    "1]/section/main/div/div/div[1]/div[2]/form/div/div[3]/button",
        # XPath to check if page successfully logged in
        'loaded_element_check':     "/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div["
                                    "1]/div/div/div/div/div[2]/div[8]/div/div/a/div/div[2]/div/div",
        # URL to combine with username for data
        'data_prefix':              "https://www.instagram.com/",
        'followers_suffix':         "/followers/",
        'following_suffix':         "/following/",
        # XPath for element containing following count
        'following_count':          "/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div["
                                    "2]/section/main/div/header/section/ul/li[3]/a/div/span/span",
        # XPath for element containing follower count
        'followers_count':          "/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div["
                                    "2]/section/main/div/header/section/ul/li[2]/a/div/span/span ",
        # XPath for window containing people who follow you (scrollable content)
        'followers_window_path':    "/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div["
                                    "2]/div/div/div/div/div[2]/div/div/div[2]",
        # XPath for window containing people you follow (scrollable content)
        'following_window_path':    "/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div["
                                    "2]/div/div/div/div/div[2]/div/div/div[3]"
    }

    # Prompt for username and password

    login_details = {'username': input("Username: "), 'password': input("Password: ")}

    # Initialize Driver
    driver = webdriver.Firefox()

    # Log in to instagram
    login(driver, site_elements, login_details)

    # Navigate to Followers/Following Pages to scrape users
    followers = get_followers(driver, site_elements, login_details)
    following = get_following(driver, site_elements, login_details)

    # Probably smarter way to do this, but I do not use python normally
    not_following_back = list()
    for person in following:
        if person not in followers:
            not_following_back.append(person)

    # Clear console for readability
    os.system('cls' if os.name == 'nt' else 'clear')

    # Display final results
    print("People who don't follow you back: ")
    for p in not_following_back:
        print(p.split('\n', 1)[0])
    time.sleep(1)
    driver.quit()
    input("\nPress ENTER to continue")


if __name__ == "__main__":
    main()
