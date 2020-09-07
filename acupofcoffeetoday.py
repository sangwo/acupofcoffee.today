from flask import Flask
app = Flask(__name__)
import requests, time
from flask import render_template, request, jsonify, json

import os
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
access_token_file = os.path.join(THIS_FOLDER, 'access_token.txt')

YELP_SEARCH_URL = "https://api.yelp.com/v3/businesses/search"

@app.route('/', methods=['GET'])
def get_user_location():
  return render_template("index.html")

@app.route('/search', methods=['GET'])
def get_coffee_places(): # get coffee places near user's location using Yelp API
  # TODO: factor out access token grabbing - "token = get_access_token()"
  # read access token from file
  file = open(access_token_file, "r+")
  file_json = file.read()
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
