import plaid
from plaid.api import plaid_api
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from flask import Flask, json, jsonify, send_from_directory, request

app = Flask(__name__)

@app.route("/")
def serve_index():
    return send_from_directory("static", "index.html")

@app.route("/api/create_link_token", methods=["GET"])
def create_link_token():
    try:
        request = plaid_api.LinkTokenCreateRequest(
            products=[Products("transactions")],
            client_name="dominic",
            country_codes=[CountryCode("US")],
            language="en",
            user=LinkTokenCreateRequestUser(
                client_user_id="dominic"
            )
        )

        response = jsonify(client.link_token_create(request).to_dict())
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    except plaid.ApiException as e:
        print(e)
        return json.loads(e.body)

@app.route("/api/save_access_token", methods=["POST"])
def save_access_token():
    try:
        public_token = request.args.get("public_token")
        print(f"public token: {public_token}")
        if public_token is None:
            raise ValueError("public_token query parameter is required") 

        exchange_response = client.item_public_token_exchange(plaid_api.ItemPublicTokenExchangeRequest(
            public_token=public_token
        ))
        access_token = exchange_response["access_token"]

        with open("secrets.json", "r+") as file:
            data = json.load(file)
            data["access_token"] = access_token
        
        response = jsonify({ "message": "access token successfully saved", "access_token": access_token }) 
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    except plaid.ApiException as e:
        print(e)
        return json.loads(e.body)



if __name__ == "__main__":
    secret = ""
    client_id = ""
    
    with open("secrets.json") as file:
        data = json.load(file)
        secret = data["secret"]
        client_id = data["client_id"]

    configuration = plaid.Configuration(
        host=plaid.Environment.Production,
        api_key={
            "clientId": client_id,  
            "secret": secret
        }
    )

    api_client = plaid.ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)

    app.run(port=8000)
