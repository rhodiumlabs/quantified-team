#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

rhodium_email = 'hello@rhodium.io'

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
    baseurl = "https://api.humanapi.co/v1/human/activities/summaries?access_token="
    access_token = os.environ['HUMANAPI_ACCESS_TOKEN']
    human_url = baseurl + access_token
    result = urllib.urlopen(human_url).read()
    data = json.loads(result)
    res = makeWebhookResult(parseHumanData(data))
    return res

def parseHumanData(data):
    steps = data[0]["steps"]
    calories = data[0]["calories"]
    data = [steps, calories]
    return data

def makeWebhookResult(data):
    return {
        "steps": data[0],
        "calories": data[1]
    }



if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
