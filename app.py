#!/usr/bin/env python

import urllib
import requests
import requests_cache
import json
import os
import time

from datetime import date, timedelta
from flask import Flask
from flask import request, Response
from flask import make_response, current_app
from flask.ext.cache import Cache
from geopy.geocoders import Nominatim
from functools import update_wrapper

geolocator = Nominatim()
requests_cache.install_cache('moves-data')


# Flask app should start in global layout
app = Flask(__name__)
cache = Cache(app,config={'CACHE_TYPE': 'simple'})

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

@app.route('/webhook', methods=['POST'])
@crossdomain(origin='*')
@cache.cached(timeout=50)
def webhook():
    start_time = time.time()
    req = request.get_json(silent=True, force=True)
    res = processHumanAPIRequest(req)
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Access-Control-Allow-Origin'] = "*"
    print("--- %s seconds ---" % (time.time() - start_time))
    return r

def processHumanAPIRequest(req):
    activityurl = "https://api.humanapi.co/v1/human/activities/summaries?access_token="
    locationurl = "https://api.humanapi.co/v1/human/locations?access_token="
    user_tokens = {'daskalov':'HUMANAPI_ACCESS_TOKEN_DASKALOV','ari':'HUMANAPI_ACCESS_TOKEN_ARI','nadim':'HUMANAPI_ACCESS_TOKEN_NADIM', 'alex':'HUMANAPI_ACCESS_TOKEN_ALEXANDRA'}
    user_data = [None]*4
    yesterday = date.today() - timedelta(1)
    for key, value in user_tokens.iteritems():
        access_token = os.environ[value]
        activity_url = activityurl + access_token + "&source=moves&end_date="+ date.today().strftime('%Y-%m-%d') + "&limit=1"
        location_url = locationurl + access_token + "&source=moves&end_date="+ date.today().strftime('%Y-%m-%d') + "&limit=1"
        activity = requests.get(activity_url)
        location = requests.get(location_url)
        activity_data = json.loads(activity.content)
        location_data = json.loads(location.content)
        data = parseHumanData(activity_data, location_data)
        if key == 'ari':
            user_data[0] = data
        if key == 'alex':
            user_data[1] = data
        if key == 'daskalov':
            user_data[2] = data
        if key == 'nadim':
            user_data[3] = data
    res = makeWebhookResult(user_data)
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


def makeWebhookResult(user_data):
    return {
    "Ari":
        {
        "steps": user_data[0][0],
        "calories": user_data[0][1],
        "city": user_data[0][2],
        "state": user_data[0][3]
        },
    "Alexandra":
        {
        "steps": user_data[1][0],
        "calories": user_data[1][1],
        "city": user_data[1][2],
        "state": user_data[1][3]
        },
    "Daskalov":
        {
        "steps": user_data[2][0],
        "calories": user_data[2][1],
        "city": user_data[2][2],
        "state": user_data[2][3]
        },
    "Nadim":
        {
        "steps": user_data[3][0],
        "calories": user_data[3][1],
        "city": user_data[3][2],
        "state": user_data[3][3]
        },
    "Imran":
        {
        "steps": user_data[3][0],
        "calories": user_data[3][1],
        "city": user_data[3][2],
        "state": user_data[3][3]
        }
    }



if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=True, port=port, host='0.0.0.0')
