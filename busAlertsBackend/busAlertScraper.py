import requests
import json
import time
from datetime import datetime
import yagmail #send email with just a subject and body text easily
from enum import Enum
import csv

#TODO: incorporate logging into the project
#get API key as environment variable

class Units(Enum):
    BUS_STOPS = "stops"
    MINUTES = "minutes"

class BusAlert:
    API_KEY = "8127ca5e-2293-444b-b56e-a41d79604969"
    BUS_ROUTES_FILE_PATH = "staticMtaInfo/busRoutes.csv"
    BUS_STOPS_FILE_PATH = "staticMtaInfo/stopsByRoute"

    def __init__(self, busStopID, busLineID, email, number=5, units=Units.MINUTES):
        if not BusAlert.isValidBusLine(busLineID):
            raise ValueError("Bus line ID is not valid.")
        if not BusAlert.isValidBusStop(busStopID, busLineID):
            raise ValueError("Either bus stop ID is not valid or does not belong to bus line ID.")
        self.busStopID = busStopID
        self.busLineID = busLineID
        self.recipientEmail = email
        self.number = number
        self.units = units

    def isValidBusLine(busLineID):
        """
        Check if the bus line id is valid.

        busLineID: str
        return: bool
        """
        if BusAlert.busLineIdToCommonName(busLineID) == None:
            return False
        return True

    def isValidBusStop(busStopID, busLineID):
        """
        Check if the bus stop id is valid and belongs to the bus line id.

        busStopID: str
        busLineID: str
        return: bool
        """
        if BusAlert.busStopIdToCommonName(busStopID, busLineID) == None:
            return False
        return True

    def getClosestBus(self):
        """
        Returns the time until the bus arrives and the number of stops away.

        return: (int, int)
        The first element in the tuple is the number of seconds until the bus arrives.
        The second element in the tuple is how far the bus is by the number of stops.
        """
        url = f"https://bustime.mta.info/api/siri/stop-monitoring.json?key={self.API_KEY}&MonitoringRef={self.busStopID}&LineRef={self.busLineID}&version=2"
        responseJSON = json.loads( requests.get(url).content )

        #try to extract the time of the response
        try:
            now = responseJSON["Siri"]["ServiceDelivery"]["ResponseTimestamp"]
        except KeyError:
            print("Something likely went wrong with the request.")
            return None, None

        #try to extract the list of buses nearby
        try:
            busesOnTheWay = responseJSON["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"]
        except KeyError:
            print("No buses nearby.") #debug
            return None, None
        
        #try to extract the arrival time of the nearest bus
        try:
            expectedArrivalTime = busesOnTheWay[0]["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedArrivalTime"]
            numberOfStopsAway = busesOnTheWay[0]["MonitoredVehicleJourney"]["MonitoredCall"]["NumberOfStopsAway"]
        except (KeyError, IndexError):
            print("Error extracting expected arrival time, number of stops away, or current time from JSON response.") #debug
            return None, None

        #determine the number of seconds until the bus arrives
        expectedArrivalTime = datetime.fromisoformat(expectedArrivalTime)
        now = datetime.fromisoformat(now)
        timeUntilBusArrives = int( (expectedArrivalTime - now).total_seconds() )

        return timeUntilBusArrives, numberOfStopsAway

    def sendEmailIfBusIsClose(self, busArrivalDistance, busAlertDistance):
        """
        If the bus is close enough, send an email alerting the user.

        busArrivalDistance: int
        busAlertDistance: int
        The arguments both represent either a number of bus stops or seconds
        depending on the value of self.units.

        return: bool, depending on whether the email was sent
        """

        #if bus is too far away, no email is sent
        if busArrivalDistance > busAlertDistance:
            return False

        msg = f"{BusAlert.busLineIdToCommonName(self.busLineID)} is less than {self.number} {self.units.value} away from {BusAlert.busStopIdToCommonName(self.busStopID, self.busLineID)}!"
        me = "nycbusalerts@gmail.com"
        yag = yagmail.SMTP(me, "qupxvewoewdgsmee")
        yag.send(self.recipientEmail, subject="Bus Alert", contents=msg)

        print("email sent", self.busLineID, self.busStopID, self.recipientEmail)
        return True

    def setupAlerts(self):
        """
        Query the location of the nearest bus every few seconds and send
        an email if the bus gets close enough to the desired stop.
        """
        while True:
            timeUntilBusArrives, numberOfStopsAway = self.getClosestBus()
            if (timeUntilBusArrives, numberOfStopsAway) == (None, None):
                time.sleep(15)
                continue
            print(BusAlert.numberOfSecondsToHMS(timeUntilBusArrives), numberOfStopsAway, self.busLineID, self.busStopID, self.recipientEmail) #debug

            if self.units == Units.MINUTES:
                secondsUntilAlertIsSent = self.number*60
                if self.sendEmailIfBusIsClose(timeUntilBusArrives, secondsUntilAlertIsSent):
                    break
            else:
                busStopsUntilAlertIsSent = self.number
                if self.sendEmailIfBusIsClose(numberOfStopsAway, busStopsUntilAlertIsSent):
                    break
            
            time.sleep(15)

            

    #CONVENIENCE METHODS
    def busLineIdToCommonName(busLineID):
        """
        Return common name of busLineID. (e.g. go from MTABC_Q39 to Q39)

        busLineID: str
        return: str?
        """
        with open(BusAlert.BUS_ROUTES_FILE_PATH) as f:
            busRoutesFile = csv.DictReader(f, delimiter=";")
            for route in busRoutesFile:
                if route["id"] == busLineID:
                    return route["shortName"]

    def busCommonNameToLineId(busCommonName):
        """
        Return the bus line ID of busCommonName. (e.g. go from Q39 to MTABC_Q39)

        busCommonName: str
        return: str?
        """
        with open(BusAlert.BUS_ROUTES_FILE_PATH) as f:
            busRoutesFile = csv.DictReader(f, delimiter=";")
            for route in busRoutesFile:
                if route["shortName"].upper() == busCommonName.upper():
                    return route["id"]

    def busStopIdToCommonName(busStopID, busLineID):
        """
        Return common name of busStopID. (e.g. go from 504263 to METROPOLITAN AV/71 ST)
        busStopID must be a bus stop for busLineID.

        busStopID: str
        busLineID: str
        return: str?
        """
        if not (busCommonName := BusAlert.busLineIdToCommonName(busLineID)):
            return None
        with open(f"{BusAlert.BUS_STOPS_FILE_PATH}/busStops_{busCommonName}/allStops.csv") as f:
            fieldnames = ["code","id","name","mainRoute","routeIds","destination"]
            busStopsFile = csv.DictReader(f, fieldnames=fieldnames, delimiter=";")
            for stop in busStopsFile:
                if stop["code"] == busStopID:
                    return stop["name"]

    def getAllStopsOnLine(busLineID):
        if not (busCommonName := BusAlert.busLineIdToCommonName(busLineID)):
            return None

        """
        {
        "DESTINATION1": [LIST OF STOPS, each stop {"name": , "code": }],
        "DESTINATION2": [LIST OF STOPS]
        }

        1. Reads the destinations.txt file to get the names of all of the route's directions
        2. Convert each destination to the proper format
        3. Open the file with the formatted destination name in step 2 to get all the stops

        destination to file name:
          replace spaces with underscores
          replace / with double underscores
        """
        busRouteStopsDirectory = f"{BusAlert.BUS_STOPS_FILE_PATH}/busStops_{busCommonName}"
        destinationsFilePath = f"{busRouteStopsDirectory}/destinations.txt"
        with open(destinationsFilePath) as f:
            busStops = {}

            for destination in f:
                destination = destination.strip()
                destinationFileName = destination.replace(" ", "_").replace("/", "__")
                
                with open(f"{busRouteStopsDirectory}/{destinationFileName}.csv") as g:
                    fieldnames = ["code","id","name","mainRoute","routeIds","destination"]
                    busStopsFile = csv.DictReader(g, fieldnames=fieldnames, delimiter=";")
                    busStops[destination] = [{"name": stop["name"], "code": stop["code"]} for stop in busStopsFile]

            return busStops
                    

    def numberOfSecondsToHMS(numberOfSeconds):
        """
        Converts from a number of seconds to the number of hours,
        minutes, and seconds.

        numberOfSeconds: int
        return: str
        """
        hours = numberOfSeconds // 3600
        numberOfSeconds = numberOfSeconds - hours * 3600

        minutes = numberOfSeconds // 60
        numberOfSeconds = numberOfSeconds - minutes * 60

        return f"Hours: {hours}, Minutes: {minutes}, Seconds: {numberOfSeconds}"
    
if __name__ == "__main__":
    # print( BusAlert.getAllStopsOnLine("MTA NYCT_Q54") )
    busStopID = "504306"
    busLineID = "MTA NYCT_Q54"
    email = "busalertsrecipient@gmail.com"
    stops = 20
    units = Units.BUS_STOPS
    busAlerter = BusAlert(busStopID, busLineID, email, stops, units)
    busAlerter.setupAlerts()