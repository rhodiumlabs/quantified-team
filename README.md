# Quantified Team - a Python webhook implementation of quantified self data for the Rhodium team

This is a really simple webhook implementation that uses the [Human API](https://www.humanapi.co/). It parses movement data and sends it to the [rhodium website](http://rhodium.io).


# Deploy to:
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

# What does the service do?
It returns physical activity information from the Moves App via [Human API](https://www.humanapi.co/).
The services takes the `steps` and `calories` parameters from the action.

The service packs the result in a webhook response JSON and returns it to the rhodium website frontend.
