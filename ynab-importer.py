import csv
import json
import time

import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from config import budget, token, mail, pw


# set auth header
headers = {"Authorization": f"Bearer {token}"}


def main():
    scrape_finanzblick()


def scrape_finanzblick():
    """Scrape Finanzblick for transaction data"""

    # set webdriver
    driver = webdriver.Chrome("chromedriver/chromedriver")

    driver.get("https://www.buhl.de/finanzblick/")

    # get field for login and password
    email = driver.find_element_by_id('ms-input-uname')
    passwort = driver.find_element_by_id("ms-input-pword")

    # fill in login and password
    email.send_keys(mail)
    passwort.send_keys(pw)
    # submit login form
    passwort.send_keys(Keys.RETURN)

    # manual timeout till transactions are fetched
    time.sleep(20)
    # click okay button
    try:
        driver.find_element_by_id("popup-modal-btn-ok").click()
    except:
        print("Keine Umsatzabfrage stattgefunden")
        pass
    # popup-pin-getbookings

    # Go to all acounts
    driver.find_element_by_id("menu-account").click()
    time.sleep(5)

    # find booking grid wrapper
    booking_grid = driver.find_element_by_xpath('//*[@id="booking-grid-wrapper"]/ul')
    for li_item in booking_grid.find_elements_by_tag_name("li"):
        li_item.click()
        try:
            booking_date = driver.find_element_by_id("input-chartdate")
        except:
            continue
        if booking_date.get_attribute("value") == "Heute":
            print("This is for YNAB!")
        purpose = driver.find_element_by_id("input-purpose")
        print(booking_date, purpose)


def transform_transactions(account):
    """Create an array of transactions from input csv"""
    # create the array to use for the final post request
    transactions = []

    # just for now hardcoded
    # TODO dynamic account selection from json / or request for accounts
    account = "6bfb4dab-b461-4fc8-b964-a4ffa0dc5da3"

    with open("import/ynab.csv", "r") as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=";")

        for line in csv_reader:
            # create a transaction for each line
            transaction = {
                "account_id":   account, # string
                "date":         line['date'], # string [YYYY-MM-DD]
                "amount":       line['inflow'], # int, [Amount x 1000]
                "payee_name":   " ".join(line['payee'].split()), # string
                "memo":         " ".join(line['memo'].split()), # string
                "import_id":  f"YNAB:{line['inflow']}:{line['date']}:1" # Format: [YNAB]:Amount:Date:[Ocurrences of same amount and date]
            }
            # append this transaction to final array of transactions
            transactions.append(transaction)
    return transactions


def get_all_accounts(budget_id, token):
    """get all accounts from given budget"""
    
    # get all accounts
    response = requests.get(
        f"https://api.youneedabudget.com/v1/budgets/{budget_id}/accounts", headers=headers).json()
    # create array for the accounts
    accounts = []
    for account in response["data"]["accounts"]:
        accounts.append({"id": account["id"], "name": account["name"]})
    # write to json file
    with open("accounts.json", "w") as wf:
        json.dump(accounts, wf, indent=4)


def post_transactions(budget_id, transactions):

    # set data for new transaction posting
    data = {"transactions": transactions}

    # post new transaction(s)
    post_response = requests.post(
        f"https://api.youneedabudget.com/v1/budgets/{budget_id}/transactions", headers=headers, json=data)

    # print response
    print(post_response)


if __name__ == "__main__":
    main()