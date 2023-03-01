from flask import Flask,jsonify,request,redirect,url_for
import hashlib
import hmac
from urllib.parse import urlencode
import json
import requests
import pymongo


client = pymongo.MongoClient("mongodb://localhost:27017")
print("Connection Successful")

db = client['Shopify']
collection = db['Store']


app = Flask(__name__)
client_id = "0061e058915bd365bedd9be89d42f751"
client_secret="8f1e2766833b1a71b9bdf534a2c72611"
scope = "write_products"
shop="priyanjalistore.myshopify.com"
access = dict()

@app.route('/install')
def home():
    try:
        args = request.args
        if args:
            args = args.to_dict()
            app.logger.info('keys : ' + str(args))

        hmac_value = args.pop('hmac')
        cleaned_params = []
        for key, value in sorted(args.items()):
            cleaned_params.append((key, value))
        secret_key = "8f1e2766833b1a71b9bdf534a2c72611"
        secret_key = secret_key.encode()
        sorted_qs = urlencode(cleaned_params, safe=":/")
        h = hmac.new(secret_key, sorted_qs.encode("utf8"),hashlib.sha256).hexdigest()
        print(hmac.compare_digest(h,hmac_value))
        if(hmac.compare_digest(h,hmac_value)):
            return redirect(url_for('hello'))
    except Exception as e:
        print("--ERROR in home function-----",e)
    return jsonify()


@app.route('/admin/oauth/authorize')
def hello():
    try:
        return redirect("https://"+(shop)+"/admin/oauth/authorize?client_id=" +(client_id)+"&scope="+(scope)+"&redirect_uri=https://priyanjali.pythonanywhere.com/register")
    except Exception as e:
        print("---ERROR in hello function----",e)
    return jsonify()


@app.route('/register')
def apiAuth():
    try:
        args = request.args
        if args:
            args = args.to_dict()
            app.logger.info('keys : ' + str(args))
            print("Success")
        auth_code = args.pop('code')
        print("!!!!!!!!!!!!!!!!!!!!!!!!",auth_code)
        resp = requests.post("https://"+(shop)+"/admin/oauth/access_token?client_id="+(client_id)+"&client_secret="+(client_secret)+"&code="+(auth_code))
        print("1111111111111111")

        print(resp.text)
        # token = resp.json()
        token = resp.text
        json_data = json.loads(token)
        # session['access_token'] = json_data.get("access_token")
        print("2222222222222222")
        access = json_data
        print(access['access_token'])
        
        return redirect(url_for('shopDetails'))
    except Exception as e:
        print("----ERROR------",e)
    return jsonify()

@app.route('/details')
def shopDetails():
    try:        
        headers = {
            'X-Shopify-Access-Token': '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',
        }
        resp = requests.get("https://"+(shop)+"/admin/api/2023-01/shop.json",headers=headers)
        print(type(resp))
        data = resp.text
        jsonData = json.loads(data)
        print("------------")
        collection.insert_one(jsonData)
        return jsonify({"status":"insertion successful"})
    except Exception as e:
        print("!!!!!!!!!!!!",e)
    return jsonify({"status":"error"})


if __name__ == '__main__':
    app.run(debug=True)