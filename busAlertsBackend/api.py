from flask import Flask
from flask import request
from flask import render_template
import busAlertScraper as bas
from multiprocessing import Process
import re
import logging
from datetime import date

app = Flask(__name__)
#How to make log messages from other libraries not appear: https://stackoverflow.com/a/8269542
#the idea is to set the logging level for other libraries higher than for my code
#another answer on that post says that's not ideal, since it doesn't really stop
#the other libraries from logging, but it's good enough for me.
logging.basicConfig(filename=f'/app/logs/log_{date.today().strftime("%Y-%m-%d")}', level=logging.ERROR, format='%(asctime)s %(name)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@app.route('/', methods=["GET"])
def entry():
    return render_template("index.html")

def render(goodOrBad, message):
    return render_template("index.html", alert={"goodOrBad": goodOrBad, "message": message})

def emailLoggingFormat(email):
    """
    Return first four characters of email and the domain.
    To promote privacy, this is what I will be logging
    """
    name, domain = email.split("@")
    loggedName = name[:4]
    loggedEmail = f"{loggedName}@{domain}"
    return loggedEmail

def phoneLoggingFormat(phone):
    """
    Return last four number of phone
    To promote privacy, this is what I will be logging
    """
    return phone[-4:]

#message: {"busStopID":, "busLineID":, "number": , "units": , "email": , "phone":} (number is 1-20, units is "stops" or "minutes")
@app.route('/alert', methods=["POST"])
def setUpAlerts():
    #busStopID, busLineID, and email are all required in order to move forward
    busStopID = request.form.get("busStopID")
    busLineID = request.form.get("busLineID")
    missingStopID = busStopID == "" or busStopID is None
    missingLineID = busLineID == "" or busLineID is None
    if missingLineID or missingStopID:
        message = "One of the following necessary pieces of information is missing: the bus line (busLineID) or the bus stop (busStopID)"
        logger.error(f"In /alert. Stop ID or Route ID missing. stopID: {busStopID}, routeID: {busLineID}")
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
        logger.error("In /alert. Email and phone number both missing. stopID: {busStopID}, routeID: {busLineID}")
        return render("bad", message), 400

    phoneRegex = re.compile("^\+1\d{10}$")
    if isUsingPhone and phoneRegex.match(phone) is None:
        message = "Phone number not in valid format"
        logger.error(message)
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

    logger.info(f"In /alert. Ready to set up alert. Stop ID: {busStopID}, Route ID: {busLineID}, Number: {number}, Units: {units}, Email: {emailLoggingFormat(email)}, Phone: {phoneLoggingFormat(phone)}")
    #start separate process for new request
    alert = bas.BusAlert(busStopID, busLineID, number, units, email=email, phone=phone)
    p = Process(target=alert.setupAlerts)
    p.start()

    message = "Alert set up successfully!"
    return render("good", message), 200

@app.route('/alertinfo', methods=["GET"])
def displayAlertInformation():
    routeID = request.args.get("routeID")
    stopID = request.args.get("stopID")

    if not bas.BusAlert.isValidBusStop(stopID, routeID):
        message = "Either invalid stop, invalid route, or stop doesn't belong to route."
        logger.error(f"In /alertinfo. Something wrong with stopId and/or routeID. stopID: {stopID}, routeID: {routeID}")
        return render("bad", message), 400

    routeName = bas.BusAlert.busLineIdToCommonName(routeID)
    stopName = bas.BusAlert.busStopIdToCommonName(stopID, routeID)
    logger.info(f"In /alertinfo. Rendering setup-alert.html. routeName: {routeName}, stopName: {stopName}, routeID: {routeID}, stopID: {stopID}")
    return render_template("setup-alert.html", routeName=routeName, stopName=stopName, routeID=routeID, stopID=stopID), 200

@app.route('/getbusstops', methods=["GET"])
def getBusStops():
    busCommonName = request.args.get("commonName")
    if (busLineID := bas.BusAlert.busCommonNameToLineId(busCommonName)) == None:
        message = "Not a common name we recognize for a bus line"
        logger.error(f"In /getbusstops. Not a common name we recognize for a bus route. routeName: {busCommonName}")
        return render("bad", message), 400

    response = bas.BusAlert.getAllStopsOnLine(busLineID)
    destinations = list(response.keys())
    logger.info(f"In /getbusstops. Rendering index.html. routeName: {busCommonName}, routeID: {busLineID}, destinations: {destinations}, not showing stops")
    return render_template("index.html", routeName=busCommonName, routeID=busLineID, destinations=destinations, stops=response), 200

@app.route('/possibleroutes', methods=["GET"])
def getPossibleRoutes():
    routeSnippet = request.args.get("snippet")
    if len(routeSnippet) < 2:
        return [], 200
    possibleRoutes = bas.BusAlert.routesMatchingSnippet(routeSnippet)
    logger.info(f"In /possibleroutes. routeSnippet: {routeSnippet}, possibleRoutes: {possibleRoutes}")
    return possibleRoutes, 200
