import csv
import json
import locale

import requests

from datetime import datetime
from config import budget, token

# set locale
locale.setlocale(locale.LC_ALL, 'de')

# set auth header
headers = {"Authorization": f"Bearer {token}"}


def main():
    print(transform_transactions("todo"))


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
                "date":         line['Buchungstag'].strftime('%Y-%m-%d'), # string [YYYY-MM-DD]
                "amount":       line['Betrag'] * 1000, # int, [Amount x 1000]
                "payee_name":   " ".join(line['Empfänger'].split()), # string
                "memo":         " ".join(line['Verwendungszweck'].split()), # string
                "import_id":  f"YNAB:{line['Betrag'] * 1000}:{line['Buchungstag'].strftime('%Y-%m-%d')}:1" # Format: [YNAB]:Amount:Date:[Ocurrences of same amount and date]
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