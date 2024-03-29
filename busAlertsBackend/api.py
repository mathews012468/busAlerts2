from flask import Flask
from flask import request
from flask import render_template
from yagmail.validate import validate_email_with_regex
from yagmail.error import YagInvalidEmailAddress
import busAlertScraper as bas
from multiprocessing import Process
import re
import logging
from datetime import date
import urllib.parse

app = Flask(__name__)
#How to make log messages from other libraries not appear: https://stackoverflow.com/a/8269542
#the idea is to set the logging level for other libraries higher than for my code
#another answer on that post says that's not ideal, since it doesn't really stop
#the other libraries from logging, but it's good enough for me.
logging.basicConfig(filename=f'/app/logs/log_{date.today().strftime("%Y-%m-%d")}', level=logging.ERROR, format='%(asctime)s %(name)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger("api")
logger.setLevel(logging.DEBUG)

@app.route('/', methods=["GET"])
def entry():
    return render_template("index.html")

def render(goodOrBad, message):
    return render_template("index.html", alert={"goodOrBad": goodOrBad, "message": message})

#message: {"busStopID":, "busRouteID":, "number": , "units": , "email": , "phone":} (number is 1-20, units is "stops" or "minutes")
@app.route('/alert', methods=["POST"])
def setUpAlerts(api=False):
    #busStopID, busRouteID, and email are all required in order to move forward
    busStopID = request.form.get("busStopID")
    busRouteID = request.form.get("busRouteID")
    missingStopID = busStopID == "" or busStopID is None
    missingRouteID = busRouteID == "" or busRouteID is None
    returnDict = {
        "busStopID": busStopID,
        "busRouteID": busRouteID,
        "email": None,
        "phone": None,
        "success": False,
        "error": None
    }

    if missingRouteID or missingStopID:
        message = "One of the following necessary pieces of information is missing: the bus route (busRouteID) or the bus stop (busStopID)"
        logger.error(f"In /alert. Stop ID or Route ID missing. stopID: {busStopID}, routeID: {busRouteID}")

        if api:
            returnDict["error"] = message
            return returnDict, 400
        else:
            return render("bad", message), 400
    if not bas.BusAlert.isValidBusRoute(busRouteID):
        message = f"Not a valid route."
        logger.error(f"In /alert. Invalid routeID. routeID: {busRouteID}")

        if api:
            returnDict["error"] = message
            return returnDict, 400
        else:
            return render("bad", message), 400
    if not bas.BusAlert.isValidBusStop(busStopID, busRouteID):
        message = f"Either invalid stop or stop doesn't belong to given route."
        logger.error(f"In /alert. Either invalid stop or stop doesn't belong to route. routeID: {busRouteID}, stopID: {busStopID}")

        if api:
            returnDict["error"] = message
            return returnDict, 400
        else:
            return render("bad", message), 400

    email = request.form.get("email")
    phone = request.form.get("phone")
    isUsingEmail = True
    isUsingPhone = True
    if email == "" or email is None:
        isUsingEmail = False
        #making sure the value is None makes checking for
        # its presence a little less annoying in busAlertScraper
        email = None
    if phone == "" or phone is None:
        isUsingPhone = False
        #same comment as above, but applied to phone
        phone = None

    returnDict["email"] = email
    returnDict["phone"] = phone
    if not isUsingEmail and not isUsingPhone:
        message = "Email and phone number are missing: at least one must be provided"
        logger.error(f"In /alert. Email and phone number both missing. stopID: {busStopID}, routeID: {busRouteID}")

        if api:
            returnDict["error"] = message
            return returnDict, 400
        else:
            return render("bad", message), 400

    if isUsingEmail:
        try:
            validate_email_with_regex(email)
        except YagInvalidEmailAddress:
            message = "Invalid email format."
            logger.error(f"In /alert. Invalid email format. email: {email}, routeID: {busRouteID}, stopID: {busStopID}")

            if api:
                returnDict["error"] = message
                return returnDict, 400
            else:
                return render("bad", message), 400

    phoneRegex = re.compile("^(?:\+1[-. ]?)?\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$")
    if isUsingPhone and phoneRegex.match(phone) is None:
        message = "Phone number not in valid format"
        logger.error(message)

        if api:
            returnDict["error"] = message
            return returnDict, 400
        else:
            return render("bad", message), 400
    if isUsingPhone:
        phone = phone.lstrip("+1")
        phone = "+1" + "".join([d for d in phone if d.isdigit()])
    
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
    if number < 1:
        message = "The number of minutes/bus stops must be positive."

        if api:
            returnDict["error"] = message
            return returnDict, 400
        else:
            return render("bad", message), 400

    alertLog = f"In /alert. Ready to set up alert. Stop ID: {busStopID}, Route ID: {busRouteID}, Number: {number}, Units: {units}"
    if isUsingEmail:
        alertLog += f", Email: {bas.BusAlert.emailLoggingFormat(email)}"
    if isUsingPhone:
        alertLog += f", Phone: {bas.BusAlert.phoneLoggingFormat(phone)}"
    logger.info(alertLog)
    #start separate process for new request
    alert = bas.BusAlert(busStopID, busRouteID, number, units, email=email, phone=phone)
    p = Process(target=alert.setupAlerts)
    p.start()

    message = "Alert set up successfully!"

    if api:
        returnDict["error"] = None
        returnDict["success"] = True
        return returnDict, 200
    return render("good", message), 200

@app.route('/alertinfo', methods=["GET"])
def displayAlertInformation(api=False):
    routeID = request.args.get("routeID")
    stopID = request.args.get("stopID")

    returnDict = {
        "routeName": None,
        "stopName": None,
        "routeID": routeID,
        "stopID": stopID,
        "error": None
    }

    if not bas.BusAlert.isValidBusStop(stopID, routeID):
        message = "Either invalid stop, invalid route, or stop doesn't belong to route."
        logger.error(f"In /alertinfo. Something wrong with stopId and/or routeID. stopID: {stopID}, routeID: {routeID}")
        if api:
            returnDict["error"] = message
            return returnDict, 400
        else:
            return render("bad", message), 400

    routeName = bas.BusAlert.busRouteIdToCommonName(routeID)
    stopName = bas.BusAlert.busStopIdToCommonName(stopID, routeID)
    logger.info(f"In /alertinfo. Rendering setup-alert.html. routeName: {routeName}, stopName: {stopName}, routeID: {routeID}, stopID: {stopID}")

    if api:
        returnDict["routeName"] = routeName
        returnDict["stopName"] = stopName
        return returnDict, 200
    else:
        return render_template("setup-alert.html", routeName=routeName, stopName=stopName, routeID=routeID, stopID=stopID), 200

@app.route('/getbusstops', methods=["GET"])
def getBusStops(api=False):
    busCommonName = request.args.get("commonName")

    returnDict = {
        "routeName": busCommonName,
        "routeID": None,
        "destinations": None,
        "stops": None,
        "error": None
    }

    if busCommonName is None or (busRouteID := bas.BusAlert.busCommonNameToRouteId(busCommonName)) is None:
        message = "Not a common name we recognize for a bus route"
        logger.error(f"In /getbusstops. Not a common name we recognize for a bus route. routeName: {busCommonName}")
        
        if api:
            returnDict["error"] = message
            return returnDict, 400
        else:
            return render("bad", message), 400
    #some routes have a + in their id, which gets treated as a space in url
    #to avoid that we url encode the +
    encodedRouteID = urllib.parse.quote(busRouteID)

    response = bas.BusAlert.getAllStopsOnRoute(busRouteID)
    destinations = list(response.keys())
    logger.info(f"In /getbusstops. Rendering index.html. routeName: {busCommonName}, routeID: {busRouteID}, destinations: {destinations}, not showing stops")

    if api:
        returnDict["routeID"] = encodedRouteID
        returnDict["destinations"] = destinations
        returnDict["stops"] = response
        return returnDict, 200
    else:
        return render_template("index.html", routeName=busCommonName, routeID=encodedRouteID, destinations=destinations, stops=response), 200

@app.route('/possibleroutes', methods=["GET"])
def getPossibleRoutes():
    routeSnippet = request.args.get("snippet")
    if len(routeSnippet) < 2:
        return [], 200
    possibleRoutes = bas.BusAlert.routesMatchingSnippet(routeSnippet)
    logger.info(f"In /possibleroutes. routeSnippet: {routeSnippet}, possibleRoutes: {possibleRoutes}")
    return possibleRoutes, 200

############################################################
############################################################
############################################################
# API VERSIONS OF MOST OF THE ABOVE FUNCTIONS FOLLOW  ######
############################################################
############################################################
############################################################

@app.route('/api/alert', methods=["POST"])
def setUpAlertsAPI():
    return setUpAlerts(api=True)

@app.route('/api/alertinfo', methods=["GET"])
def displayAlertInformationAPI():
    return displayAlertInformation(api=True)

@app.route('/api/getbusstops', methods=["GET"])
def getBusStopsAPI():
    return getBusStops(api=True)