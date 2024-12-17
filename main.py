from flask import json
import plaid
from plaid.api import plaid_api
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.accounts_get_request import AccountsGetRequest 

def get_transactions():
    response = client.transactions_sync(
        TransactionsSyncRequest(access_token = secrets["access_token"])
    )
    unsorted_transactions = response["added"]

    while (response["has_more"]): 
        response = client.transactions_sync(TransactionsSyncRequest(
            access_token = secrets["access_token"],
            cursor = response["next_cursor"]
        ))
        unsorted_transactions += response["added"]

    transactions = {}
    for account in get_accounts():
        transactions[account["account_id"]] = list(filter(
            lambda t : t["account_id"] == account["account_id"], 
            unsorted_transactions
        )) 
    return transactions

def get_accounts():
    response = client.accounts_get(
        AccountsGetRequest(access_token=secrets["access_token"])
    )
    return response["accounts"]

def main():
    global client
    global secrets

    with open("secrets.json") as file:
        secrets = json.load(file)
    
    configuration = plaid.Configuration(
        host=plaid.Environment.Production,
        api_key={
            "clientId": secrets["client_id"],  
            "secret": secrets["secret"]
        }
    )

    api_client = plaid.ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)

    transactions = get_transactions()
    print(transactions)


if __name__ == "__main__":
    main()

