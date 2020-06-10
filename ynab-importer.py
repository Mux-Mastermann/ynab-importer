import codecs
import csv
import json
import locale
from datetime import datetime

import requests

from config import budget, token

# set locale
locale.setlocale(locale.LC_ALL, '')

# set auth header
headers = {"Authorization": f"Bearer {token}"}


def main():
    post_transactions(budget, transform_transactions("TODO"))


def transform_transactions(account):
    """Create an array of transactions from input csv"""
    # create the array to use for the final post request
    transactions = []

    # just for now hardcoded
    # TODO dynamic account selection from json / or request for accounts
    account = "6bfb4dab-b461-4fc8-b964-a4ffa0dc5da3"

    with codecs.open("import/ynab.csv", "r", "utf-16") as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=";")

        for line in csv_reader:
            # transform date
            posting_date = datetime.strptime(line['Buchungstag'], "%d.%m.%Y").strftime('%Y-%m-%d')
            # transform amount to float and multiply by 1000
            amount = int(locale.atof(line['Betrag']) * 1000)

            # create a transaction for each line
            transaction = {
                "account_id":   account, # string
                "date":         posting_date, # string [YYYY-MM-DD]
                "amount":       amount, # int, [Amount x 1000]
                "payee_name":   " ".join(line['Empfänger'].split()), # string
                "memo":         " ".join(line['Verwendungszweck'].split()), # string
                "import_id":  f"YNAB:{amount}:{posting_date}:1" # Format: [YNAB]:Amount:Date:[Ocurrences of same amount and date]
            }
            # append this transaction to final array of transactions
            transactions.append(transaction)
    return transactions


def get_budgets(token):
    """returns all budgets from YNAB"""
    return requests.get("https://api.youneedabudget.com/v1/budgets", headers=headers).json()


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
    print(post_response.json())


if __name__ == "__main__":
    main()
