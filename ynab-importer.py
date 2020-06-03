import requests

from config import Token

# set authorization header
headers = {"Authorization": f"Bearer {Token}"}

# get all budgets
response = requests.get(
    "https://api.youneedabudget.com/v1/budgets", headers=headers)

# get first budget id 
response_data = response.json()
budget_id = response_data["data"]["budgets"][0]["id"]

# set data for new transaction posting
data = {"transaction": {
    "account_id": "",
    "date": "2020-06-01",
    "amount": -5000,
    "payee_name": "",
    "memo": "",
    # Format: [YNAB]:Amount:Date:[Ocurrences of same amount and date]
    "import_id": "YNAB:5000:2020-06-02:1"}
    }

# post new transaction(s)
r = requests.post(
    f"https://api.youneedabudget.com/v1/budgets/{budget_id}/transactions", headers=headers, json=data)

# print response
print(r.text)
