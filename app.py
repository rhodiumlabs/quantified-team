#!/usr/bin/env python

import urllib
import requests
import json
import os

from datetime import date, timedelta
from flask import Flask
from flask import request, Response
from flask import make_response, current_app
from geopy.geocoders import Nominatim
from functools import update_wrapper

# Flask app should start in global layout
app = Flask(__name__)

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
def webhook():
    req = request.get_json(silent=True, force=True)
    res = processHumanAPIRequest(req)
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Access-Control-Allow-Origin'] = "*"
    return r

def processHumanAPIRequest(req):
    activityurl = "https://api.humanapi.co/v1/human/activities/summaries?access_token="
    locationurl = "https://api.humanapi.co/v1/human/locations?access_token="
    HUMANAPI_ACCESS_TOKEN_ARI = '4srO2WURoAjbcu6Nb7o17I0rts4=XlfWVVEs07c3d5ff6201e82d11c3c92d7c5d78e6ac8cd292d8463932d917895b328523502060ff64e43e9a006ef701f7ebe69d1fab932bad9de927fd81972edfc639e965278ee5b6b156c10b828e13280cc93c47b9570f05f6b41add138add836130d4efba3b562a7e1ec8c748852e34bec0cb15'
    HUMANAPI_ACCESS_TOKEN_NADIM = '4pvKEvkKl97XyQTDfDoLUl9IkwA=z_OsbYVm59c5a2230442cfa1a6a9dec06f306b4835341e9eba6c0705a51fea71d7be7b7ae30e81dc93e6ef1990e871de4ed1d99b788be294c22ff52f4edc88e77074414a009b894d6944c47cbe70fcc264c0b4822eb765e1fb4e97b58b630372a86a4601c438507cbe5a4a6d9977fe10db6d2462'
    HUMANAPI_ACCESS_TOKEN_DASKALOV = 'ixrUiUHcgvhnT4H-NE0s7kXk10I=b2f_bH3z23a1bf0d2f3f8f71795d7801e5ecd6e84a6c51074fbecf6846308bb2334d08807e5934d86a3af4d3820e04c431ed297d84932080c51edd9c9f6d6f68c8b0150692dc1d3b43914bb049273b698b406ca42aada2c941a3cfc7fe85d9a6212f4e5fdaf314d6010fea0aecd5f1b2fb615429'
    HUMANAPI_ACCESS_TOKEN_ALEXANDRA = 'x3ovk9gP_iZcAfitukPF5pp-4Ug=ZsoWo0sL3a59668cb4f2057b3e26e73bb31f4418402898722d9917c44600fe28b668f1791ef9047bb7d2c3e4267a7e348e203c92ed56c409b39fee7397f68aec18d56eb4afd6d4662ad2952de3ffdb0528aa367577b033e4d0704860b0df4c711d770601a16aa38f61f2bc9dd773079628a1b822'
    user_tokens = {'daskalov':HUMANAPI_ACCESS_TOKEN_DASKALOV,'ari':HUMANAPI_ACCESS_TOKEN_ARI,'nadim':HUMANAPI_ACCESS_TOKEN_NADIM, 'alex':HUMANAPI_ACCESS_TOKEN_ALEXANDRA}
    user_data = [None]*4
    yesterday = date.today() - timedelta(1)
    for key, value in user_tokens.iteritems():
        #access_token = os.environ[value]
        access_token = value
        activity_url = activityurl + access_token + "&source=moves&end_date="+ date.today().strftime('%Y-%m-%d') + "&limit=1"
        location_url = locationurl + access_token + "&source=moves&end_date="+ date.today().strftime('%Y-%m-%d') + "&limit=1"
        activity = urllib.urlopen(activity_url).read()
        location = urllib.urlopen(location_url).read()
        activity_data = json.loads(activity)
        location_data = json.loads(location)
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
    geolocator = Nominatim()
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

    app.run(debug=False, port=port, host='0.0.0.0')
