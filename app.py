#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response
from geopy.geocoders import Nominatim
geolocator = Nominatim()

# Flask app should start in global layout
app = Flask(__name__)



@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    res = processHumanAPIRequest(req)
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def processHumanAPIRequest(req):
    activityurl = "https://api.humanapi.co/v1/human/activities/summaries?access_token="
    locationurl = "https://api.humanapi.co/v1/human/locations?access_token="
    access_token = os.environ['HUMANAPI_ACCESS_TOKEN']
    activity_url = activityurl + access_token + "&source=moves&limit=1"
    location_url = locationurl + access_token + "&source=moves&limit=1"
    activity = urllib.urlopen(activity_url).read()
    location = urllib.urlopen(location_url).read()
    activity_data = json.loads(activity)
    location_data = json.loads(location)
    res = makeWebhookResult(parseHumanData(activity_data, location_data))
    return res

def parseHumanData(activity_data,location_data):
    steps = activity_data[0]["steps"]
    calories = activity_data[0]["calories"]
    lat = str(location_data[0]["location"]["lat"])
    lon = str(location_data[0]["location"]["lon"])
    coord = lat + "," + lon
    location = city_and_state(coord)
    city = location[0]
    state = location[1]
    data = [steps, calories,city, state]
    return data

def city_and_state(coord):
    location = geolocator.reverse(coord, exactly_one=True)
    address = location.raw['address']
    city = address.get('city', '')
    state = address.get('state', '')
    return city, state

def makeWebhookResult(data):
    return {
    "Ari":
        {
        "steps": data[0],
        "calories": data[1],
        "city": data[2],
        "state": data[3]
        },
    "Alexandra":
        {
        "steps": data[0],
        "calories": data[1],
        "city": data[2],
        "state": data[3]
        },
    "Daskalov":
        {
        "steps": data[0],
        "calories": data[1],
        "city": data[2],
        "state": data[3]
        },
    "Nadim":
        {
        "steps": data[0],
        "calories": data[1],
        "city": data[2],
        "state": data[3]
        },
    "Imran":
        {
        "steps": data[0],
        "calories": data[1],
        "city": data[2],
        "state": data[3]
        }
    }



if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
