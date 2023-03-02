import requests
import json
import time
from datetime import datetime
import yagmail #send email with just a subject and body text easily
from enum import Enum
import csv
import os
from twilio.rest import Client
import logging

logger = logging.getLogger("api.busAlertScraper")

class Units(Enum):
    BUS_STOPS = "stops"
    MINUTES = "minutes"

class BusAlert:
    API_KEY = os.environ["MTA_API_KEY"]
    BUS_ROUTES_FILE_PATH = "staticMtaInfo/busRoutes.csv"
    BUS_STOPS_FILE_PATH = "staticMtaInfo/stopsByRoute"

    def __init__(self, busStopID, busRouteID, number=5, units=Units.MINUTES, email=None, phone=None):
        #responsibility is on the creator of a BusAlert object to make
        #sure that the inputs are valid
        self.busStopID = busStopID
        self.busRouteID = busRouteID
        self.recipientEmail = email
        self.recipientPhone = phone
        self.number = number
        self.units = units

        #use the start time to implement a timeout feature
        #should not be tracking a bus for more than an hour
        self.alertStartTime = time.time()

    def isValidBusRoute(busRouteID):
        """
        Check if the bus route id is valid.

        busRouteID: str
        return: bool
        """
        if BusAlert.busRouteIdToCommonName(busRouteID) == None:
            return False
        return True

    def isValidBusStop(busStopID, busRouteID):
        """
        Check if the bus stop id is valid and belongs to the bus route id.

        busStopID: str
        busRouteID: str
        return: bool
        """
        if BusAlert.busStopIdToCommonName(busStopID, busRouteID) == None:
            return False
        return True

    def getClosestBus(self):
        """
        Returns the time until the bus arrives and the number of stops away.

        return: (int, int)
        The first element in the tuple is the number of seconds until the bus arrives.
        The second element in the tuple is how far the bus is by the number of stops.
        """
        url = f"https://bustime.mta.info/api/siri/stop-monitoring.json?key={self.API_KEY}&MonitoringRef={self.busStopID}&LineRef={self.busRouteID}&version=2"
        responseJSON = json.loads( requests.get(url).content )

        #try to extract the time of the response
        try:
            now = responseJSON["Siri"]["ServiceDelivery"]["ResponseTimestamp"]
        except KeyError:
            logger.error(f"In getClosestBus. Something likely went wrong with the request. routeID: {self.busRouteID}, stopID: {self.busStopID}")
            return None, None

        #try to extract the list of buses nearby
        try:
            busesOnTheWay = responseJSON["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"]
        except KeyError:
            logger.info(f"In getClosestBus. No buses nearby. routeID: {self.busRouteID}, stopID: {self.busStopID}")
            return None, None
        
        #try to extract the arrival time of the nearest bus
        try:
            expectedArrivalTime = busesOnTheWay[0]["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedArrivalTime"]
            numberOfStopsAway = busesOnTheWay[0]["MonitoredVehicleJourney"]["MonitoredCall"]["NumberOfStopsAway"]
        except (KeyError, IndexError):
            logger.error(f"In getClosestBus. Error extracting expected arrival time, number of stops away, or current time from JSON response. routeID: {self.busRouteID}, stopID: {self.busStopID}")
            return None, None

        #determine the number of seconds until the bus arrives
        expectedArrivalTime = datetime.fromisoformat(expectedArrivalTime)
        now = datetime.fromisoformat(now)
        timeUntilBusArrives = int( (expectedArrivalTime - now).total_seconds() )

        return timeUntilBusArrives, numberOfStopsAway

    def sendAlertIfBusIsClose(self, busArrivalDistance, busAlertDistance, timeout=False):
        """
        If the bus is close enough, alert the user.

        busArrivalDistance: int
        busAlertDistance: int
        timeout: bool
        The arguments both represent either a number of bus stops or seconds
        depending on the value of self.units.
        timeout lets us know if the alert timed out before a bus arrived.
        If timeout is True, let the user know they should set up another alert.

        return: bool, depending on whether the alert was sent
        """

        #if bus is too far away, no email is sent
        if busArrivalDistance > busAlertDistance:
            return False

        if timeout:
            msg = f"Unfortunately, {BusAlert.busRouteIdToCommonName(self.busRouteID)} is still more than {self.number} {self.units.value} away from {BusAlert.busStopIdToCommonName(self.busStopID, self.busRouteID)}, so we have stopped tracking it. If you would like to continue, please set up another alert."
        else:
            msg = f"{BusAlert.busRouteIdToCommonName(self.busRouteID)} is less than {self.number} {self.units.value} away from {BusAlert.busStopIdToCommonName(self.busStopID, self.busRouteID)}!"
        if self.recipientEmail != "":
            self.sendEmail(msg)
        if self.recipientPhone != "":
            self.sendText(msg)
        return True

    def sendEmail(self, msg):
        me = "nycbusalerts@gmail.com"
        yag = yagmail.SMTP(me, os.environ["BUS_ALERTS_APP_PASSWORD"])
        yag.send(self.recipientEmail, subject="Bus Alert", contents=msg)

        logger.info(f"In sendEmail. email sent. routeID: {self.busRouteID}, stopID: {self.busStopID}, recipientEmail: {BusAlert.emailLoggingFormat(self.recipientEmail)}")
    
    def sendText(self, msg):
        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        client = Client(account_sid, auth_token)

        message = client.messages \
                        .create(
                            body=msg,
                            from_='+13474921832',
                            to=self.recipientPhone
                        )
        
        logger.info(f"In sendText. text sent. routeID: {self.busRouteID}, stopID: {self.busStopID}, recipientPhone: {BusAlert.phoneLoggingFormat(self.recipientPhone)} ")

    def setupAlerts(self):
        """
        Query the location of the nearest bus every few seconds and send
        an email if the bus gets close enough to the desired stop.
        """
        HOUR = 3600
        while time.time() - self.alertStartTime < HOUR:
            timeUntilBusArrives, numberOfStopsAway = self.getClosestBus()
            if (timeUntilBusArrives, numberOfStopsAway) == (None, None):
                logger.info(f"In setupAlerts. No buses nearby. routeID: {self.busRouteID}, stopID: {self.busStopID}")
                time.sleep(15)
                continue
            logger.info(f"In setupAlerts. Time until bus arrives: {BusAlert.numberOfSecondsToHMS(timeUntilBusArrives)}, numberOfStopsAway: {numberOfStopsAway}, threshold: {self.number} {self.units}, routeID: {self.busRouteID}, stopID: {self.busStopID}")

            if self.units == Units.MINUTES:
                secondsUntilAlertIsSent = self.number*60
                if self.sendAlertIfBusIsClose(timeUntilBusArrives, secondsUntilAlertIsSent):
                    return
            else:
                busStopsUntilAlertIsSent = self.number
                if self.sendAlertIfBusIsClose(numberOfStopsAway, busStopsUntilAlertIsSent):
                    return
            
            time.sleep(15)
        #the first two arguments don't have any special significance,
        #except that the first number should be less than the second
        #since that allows the rest of the function to run
        logger.info(f"In /alert. Bus has been tracked for an hour, timeout alert will be sent. threshold: {self.number} {self.units}, routeID: {self.busRouteID}, stopID: {self.busStopID}")
        self.sendAlertIfBusIsClose(0, 1, timeout=True)

    def routesMatchingSnippet(routeSnippet):
        """
        Return a list of bus routes whose common names partially match
        the snippet provided
        
        e.g. if routeSnippet is Q3, this function would return buses like
        the Q3, Q30, Q31, Q32, Q33, and so on.
        """
        if type(routeSnippet) != str or routeSnippet == "":
            return []
        
        with open(BusAlert.BUS_ROUTES_FILE_PATH) as f:
            routeReader = csv.DictReader(f, delimiter=";")
            return [route["shortName"] for route in routeReader if route["shortName"].upper().find(routeSnippet.upper()) != -1]

    #CONVENIENCE METHODS
    def busRouteIdToCommonName(busRouteID):
        """
        Return common name of busRouteID. (e.g. go from MTABC_Q39 to Q39)

        busRouteID: str
        return: str?
        """
        with open(BusAlert.BUS_ROUTES_FILE_PATH) as f:
            busRoutesFile = csv.DictReader(f, delimiter=";")
            for route in busRoutesFile:
                if route["id"] == busRouteID:
                    return route["shortName"]

    def busCommonNameToRouteId(busCommonName):
        """
        Return the bus route ID of busCommonName. (e.g. go from Q39 to MTABC_Q39)

        busCommonName: str
        return: str?
        """
        with open(BusAlert.BUS_ROUTES_FILE_PATH) as f:
            busRoutesFile = csv.DictReader(f, delimiter=";")
            for route in busRoutesFile:
                if route["shortName"].upper() == busCommonName.upper():
                    return route["id"]

    def busStopIdToCommonName(busStopID, busRouteID):
        """
        Return common name of busStopID. (e.g. go from 504263 to METROPOLITAN AV/71 ST)
        busStopID must be a bus stop for busRouteID.

        busStopID: str
        busRouteID: str
        return: str?
        """
        if not (busCommonName := BusAlert.busRouteIdToCommonName(busRouteID)):
            logger.info(f"In busStopIdToCommonName. Route ID not found. routeID: {busRouteID}")
            return None
        with open(f"{BusAlert.BUS_STOPS_FILE_PATH}/busStops_{busCommonName}/allStops.csv") as f:
            fieldnames = ["code","id","name","mainRoute","routeIds","destination"]
            busStopsFile = csv.DictReader(f, fieldnames=fieldnames, delimiter=";")
            for stop in busStopsFile:
                if stop["code"] == busStopID:
                    return stop["name"]
        logger.info(f"In busStopIdToCommonName. Stop not found in route. routeName: {busCommonName}, routeID: {busRouteID}, stopID: {busStopID}")

    def getAllStopsOnRoute(busRouteID):
        if not (busCommonName := BusAlert.busRouteIdToCommonName(busRouteID)):
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
    
if __name__ == "__main__":
    busStopID = "504306"
    busRouteID = "MTA NYCT_Q54"
    email = "busalertsrecipient@gmail.com"
    stops = 20
    units = Units.BUS_STOPS
    busAlerter = BusAlert(busStopID, busRouteID, email, stops, units)
    busAlerter.setupAlerts()