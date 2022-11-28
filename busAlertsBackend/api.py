from flask import Flask
from flask import request
from flask_cors import CORS
import busAlertScraper as bas
from multiprocessing import Process
import os

app = Flask(__name__)
CORS(app)

#message: {"busStopID":, "busLineID":, "number": , "units": , "email": , "phone":} (number is 1-20, units is "stops" or "minutes")
@app.route('/alert', methods=["POST"])
def setUpAlerts():
    #busStopID, busLineID, and email are all required in order to move forward
    try:
        busStopID = request.form["busStopID"]
        busLineID = request.form["busLineID"]
    except KeyError:
        return "One of the following necessary pieces of information is missing: the bus line (busLineID) or the bus stop (busStopID)", 400

    #I probably should verify that at least one is provided
    email = request.form.get("email")
    phone = request.form.get("phone")
    if email == "" and phone == "":
        return "Email and phone number are missing: at least one must be provided", 400

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
    return f"""Alert set up successfully!
<form action="/" method="get">
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
