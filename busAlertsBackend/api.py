from flask import Flask
from flask import request
from flask import render_template
import busAlertScraper as bas
from multiprocessing import Process
import re
import os

app = Flask(__name__)

@app.route('/', methods=["GET"])
def entry():
    return render_template("index.html")

def render(goodOrBad, message):
    return render_template("index.html", alert={"goodOrBad": goodOrBad, "message": message})

#message: {"busStopID":, "busLineID":, "number": , "units": , "email": , "phone":} (number is 1-20, units is "stops" or "minutes")
@app.route('/alert', methods=["POST"])
def setUpAlerts():
    #busStopID, busLineID, and email are all required in order to move forward
    try:
        busStopID = request.form["busStopID"]
        busLineID = request.form["busLineID"]
    except KeyError:
        message = "One of the following necessary pieces of information is missing: the bus line (busLineID) or the bus stop (busStopID)"
        return render("bad", message), 400

    #I probably should verify that at least one is provided
    email = request.form.get("email")
    phone = request.form.get("phone")
    isUsingEmail = True
    isUsingPhone = True
    if (email == "" or email is None):
        isUsingEmail = False
    if (phone == "" or phone is None):
        isUsingPhone = False
    if not isUsingEmail and not isUsingPhone:
        message = "Email and phone number are missing: at least one must be provided"
        return render("bad", message), 400

    phoneRegex = re.compile("^\+1\d{10}$")
    if isUsingPhone and phoneRegex.match(phone) is None:
        message = "Phone number not in valid format"
        return render("bad", message), 400
    
    #if user doesn't supply a unit, assume it's minutes
    try:
        units = request.form["units"]
        if units == "minutes":
            units = bas.Units.MINUTES
        else:
            units = bas.Units.BUS_STOPS
    except KeyError:
        units = bas.Units.MINUTES
    
    #if the user doesn't supply a value, assume it's 5
    try:
        number = int(request.form["number"])
    except (KeyError, ValueError):
        number = 5

    #start separate process for new request
    alert = bas.BusAlert(busStopID, busLineID, number, units, email=email, phone=phone)
    print(alert.busStopID, alert.busLineID, alert.number, alert.units, alert.recipientEmail, alert.recipientPhone)
    p = Process(target=alert.setupAlerts)
    print("after init process")
    p.start()
    print("after begin process")

    message = "Alert set up successfully!"
    return render("good", message), 200


@app.route('/getbusstops', methods=["GET"])
def getBusStops():
    busCommonName = request.args.get("commonName")
    if (busLineID := bas.BusAlert.busCommonNameToLineId(busCommonName)) == None:
        message = "Not a common name we recognize for a bus line"
        return render("bad", message), 400

    response = bas.BusAlert.getAllStopsOnLine(busLineID)
    destinations = list(response.keys())
    return render_template("index.html", routeName=busCommonName, routeID=busLineID, destinations=destinations, stops=response), 200

@app.route('/possibleroutes', methods=["GET"])
def getPossibleRoutes():
    routeSnippet = request.args.get("snippet")
    if len(routeSnippet) < 2:
        return [], 200
    return bas.BusAlert.routesMatchingSnippet(routeSnippet)
    