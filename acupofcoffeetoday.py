from flask import Flask
app = Flask(__name__)
import requests, time
from flask import render_template, request, jsonify, json

import os
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
access_token_file = os.path.join(THIS_FOLDER, 'access_token.txt')

YELP_SEARCH_URL = "https://api.yelp.com/v3/businesses/search"
YELP_ACCESS_TOKEN_URL = "https://api.yelp.com/oauth2/token"

@app.route('/', methods=['GET'])
def get_user_location():
  return render_template("index.html")

@app.route('/search', methods=['GET']) 
def get_coffee_places(): # get coffee places near user's location using Yelp API
  # TODO: factor out access token grabbing - "token = get_access_token()"
  # get access token; if it's expired, re-request Yelp
  file = open(access_token_file, "r+")
  file_json = file.read()
  expire_date = json.loads(file_json)['expire_date']

  if expire_date <= time.time():
    # TODO: put this in a secure location not tracked by git
    client_id = "IN6MlR4jtubt2QFdP2oFbg"
    client_secret = "O2ag7NpZkhLqlReZkr0XlFPHgqE8VfKVQvWAsLhmSbiPsJu2lgTPSAQLuxV8mPjs"

   # TODO: handle requests.post erroring or http status != 200
    access_token_response = requests.post(
      YELP_ACCESS_TOKEN_URL,
      data={
	"grant_type": "client_credentials",
	"client_id": client_id,
	"client_secret": client_secret,
      },
    )
    
    parsed_access_token_response = access_token_response.json()
    access_token = parsed_access_token_response['access_token']
    expires_in = parsed_access_token_response['expires_in']
    expire_date = expires_in + time.time()
    
    # save token to the file
    new_file_json = json.dumps({
      "access_token": access_token,
      "expire_date": expire_date,
    })
    file.write(new_file_json)
    file.truncate() # in order to overwrite
    file.close()

  else: # else bring saved access token from the file
    access_token = json.loads(file_json)['access_token']
    file.close()

  # get Yelp search results
  latitude = request.args.get('latitude')
  longitude = request.args.get('longitude')
  # when geolocation doesn't work
  location = request.args.get('location')

  sort_by = "rating" # TODO: enable different options in html, and receive chosen option
  params = {
    "latitude": latitude,
    "longitude": longitude,
    "location": location,
    "categories": "coffee",
    "sort_by": sort_by,
    "open_now": True,
  }
  headers = { "Authorization": "Bearer {}".format(access_token), "Content-type": "application/json" }

  # TODO: handle non-200 responses and errors
  response = requests.get(YELP_SEARCH_URL, params=params, headers=headers)

  # TODO: jsonify(success=True, error_message="", yelp_api_response=response.content)
  return jsonify(response.content) 
