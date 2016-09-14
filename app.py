#!/usr/bin/env python

import urllib
import requests
import json
import os

from datetime import date, timedelta
from flask import Flask
from flask import request, Response
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

    # username = '31c54b1e5bb56c1e8c4a49e22df3254d20eaed3f:'
    # password = None
    # clientID = "b7cfb75957a179cc624695699ce5a136a01a9196"
    # yesterday = date.today() - timedelta(1)
    # url = "https://api.humanapi.co/v1/apps/"+ clientID +"/users/activities/summaries?updated_since=" + yesterday.strftime("%Y%m%d%H%M%S%Z" )+"&source=moves&limit=1"
    # r = requests.get(url, auth=(username, password))
    # print r.json()

    activityurl = "https://api.humanapi.co/v1/human/activities/summaries?access_token="
    locationurl = "https://api.humanapi.co/v1/human/locations?access_token="
    daskalov_access_token = os.environ['HUMANAPI_ACCESS_TOKEN_DASKALOV']
    daskalov_activity_url = activityurl + daskalov_access_token + "&source=moves&limit=1"
    daskalov_location_url = locationurl + daskalov_access_token + "&source=moves&limit=1"
    daskalov_activity = urllib.urlopen(daskalov_activity_url).read()
    daskalov_location = urllib.urlopen(daskalov_location_url).read()
    daskalov_activity_data = json.loads(daskalov_activity)
    daskalov_location_data = json.loads(daskalov_location)
    daskalov_data = parseHumanData(daskalov_activity_data, daskalov_location_data)


    ari_access_token = os.environ['HUMANAPI_ACCESS_TOKEN_ARI']
    ari_activity_url = activityurl + ari_access_token + "&source=moves&limit=1"
    ari_location_url = locationurl + ari_access_token + "&source=moves&limit=1"
    ari_activity = urllib.urlopen(ari_activity_url).read()
    ari_location = urllib.urlopen(ari_location_url).read()
    ari_activity_data = json.loads(ari_activity)
    ari_location_data = json.loads(ari_location)
    ari_data = parseHumanData(ari_activity_data, ari_location_data)
    res = makeWebhookResult(ari_data,daskalov_data)
    return res

def parseHumanData(activity_data,location_data):
    steps = activity_data[0]["steps"]
    calories = activity_data[0]["calories"]
    lat = str(location_data[0]["location"]["lat"])
    lon = str(location_data[0]["location"]["lon"])
    coord = lat + "," + lon
    location = geolocator.reverse(coord, exactly_one=True)
    address = location.raw['address']
    city = address.get('city', '')
    state = address.get('state', '')
    data = [steps, calories,city, state]
    return data


def makeWebhookResult(ari_data, daskalov_data):
    return {
    "Ari":
        {
        "steps": ari_data[0],
        "calories": ari_data[1],
        "city": ari_data[2],
        "state": ari_data[3]
        },
    "Alexandra":
        {
        "steps": ari_data[0],
        "calories": ari_data[1],
        "city": ari_data[2],
        "state": ari_data[3]
        },
    "Daskalov":
        {
        "steps": daskalov_data[0],
        "calories": daskalov_data[1],
        "city": daskalov_data[2],
        "state": daskalov_data[3]
        },
    "Nadim":
        {
        "steps": ari_data[0],
        "calories": ari_data[1],
        "city": ari_data[2],
        "state": ari_data[3]
        },
    "Imran":
        {
        "steps": ari_data[0],
        "calories": ari_data[1],
        "city": ari_data[2],
        "state": ari_data[3]
        }
    }



if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
