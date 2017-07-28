from flask import Flask
app = Flask(__name__)
import requests, time
from flask import render_template, request, jsonify, json

@app.route('/', methods=['GET'])
def get_user_location():
  return render_template("index.html")

@app.route('/search', methods=['GET']) 
def get_coffee_places(): # get coffee places near user's location using Yelp API
  # get access token; if it's expired, re-request Yelp
  file = open("access_token.txt", "r+")
  file_json = file.read()
  expire_date = json.loads(file_json)['expire_date']

  if expire_date <= time.time():
    access_token_url = "https://api.yelp.com/oauth2/token"
    grant_type = "client_credentials"
    client_id = "IN6MlR4jtubt2QFdP2oFbg"
    client_secret = "O2ag7NpZkhLqlReZkr0XlFPHgqE8VfKVQvWAsLhmSbiPsJu2lgTPSAQLuxV8mPjs"
    access_token_response = requests.post(access_token_url, data={ "grant_type": grant_type, "client_id": client_id, "client_secret": client_secret })
    
    access_token = access_token_response.json()['access_token']
    expires_in = access_token_response.json()['expires_in']
    expire_date = expires_in + time.time()
    
    # save token to the file
    new_file_json = json.dumps({ "access_token": access_token, "expire_date": expire_date })
    file.write(new_file_json)
    file.close()
  else: # else bring saved access token from the file
    access_token = json.loads(file_json)['access_token']
    file.close()

  # get Yelp search results
  url = "https://api.yelp.com/v3/businesses/search"
  latitude = request.args.get('latitude')
  longitude = request.args.get('longitude')
  params = { "latitude": latitude, "longitude": longitude }
  headers = { "Authorization": "Bearer {}".format(access_token) }
  response = requests.get(url, params=params, headers=headers)
  return jsonify(response.content) 
