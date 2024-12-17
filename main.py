from flask import json
from ofxtools.header import make_header
import plaid
from plaid.api import plaid_api
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.accounts_get_request import AccountsGetRequest 
from ofxtools.models import *
from ofxtools.utils import UTC  
import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal

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

def construct_ofx(transactions):
    # for account_id in transactions.keys():
    #     account_transactions = transactions[account_id]

    ledgerbal = LEDGERBAL(balamt=Decimal("150.65"), dtasof=datetime(2024, 1, 1, tzinfo=UTC))
    bankacctfrom = BANKACCTFROM(bankid="1234", acctid="4321", accttype="CHECKING")
    stmtrs = STMTRS(curdef="USD", bankacctfrom=bankacctfrom, ledgerbal=ledgerbal)

    # wrappers
    status = STATUS(code = 0, severity="INFO")
    stmttrnrs = STMTTRNRS(trnuid="0", status=status, stmtrs=stmtrs)
    bankmsgsrs = BANKMSGSRSV1(stmttrnrs)
    sonrs = SONRS(status=status, dtserver=datetime.now(UTC), language="ENG")
    signonmsgs = SIGNONMSGSRSV1(sonrs=sonrs)

    # finish 
    ofx_root = OFX(signonmsgsrsv1=signonmsgs, bankmsgsrsv1=bankmsgsrs).to_etree()
    message = ET.tostring(ofx_root).decode()
    header = str(make_header(version=220))
    return header + message
    

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

    print(convert_transactions_to_ofx("test"))

if __name__ == "__main__":
    main()

