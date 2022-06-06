from flask import Flask
from flask import request
from flask_cors import CORS
from . import busAlertScraper as bas
from multiprocessing import Process

app = Flask(__name__)
CORS(app)

#message: {"busStopID":, "busLineID":, "number": , "units": , "email": } (number is 1-20, units is "stops" or "minutes")
@app.route('/alert', methods=["POST"])
def setUpAlerts():
    #busStopID, busLineID, and email are all required in order to move forward
    try:
        busStopID = request.form["busStopID"]
        busLineID = request.form["busLineID"]
        email = request.form["email"]
    except KeyError:
        return "One of the following necessary pieces of information is missing: the bus line (busLineID), the bus stop (busStopID), the email address (email).", 400

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
    alert = bas.BusAlert(busStopID, busLineID, email, number, units)
    p = Process(target=alert.setupAlerts)
    p.start()
    return """Alert set up successfully!
<form action="http://0.0.0.0:3000/" method="get">
    <button>Return to home</button>
</form>""", 200


@app.route('/getbusstops', methods=["GET"])
def getBusStops():
    busCommonName = request.args.get("commonName")
    if (busLineID := bas.BusAlert.busCommonNameToLineId(busCommonName)) == None:
        return "Not a common name we recognize for a bus line", 400

    response = bas.BusAlert.getAllStopsOnLine(busLineID)
    response["busLineID"] = busLineID
    return response, 200
