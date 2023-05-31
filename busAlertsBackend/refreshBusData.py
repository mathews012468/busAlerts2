import requests
import json
import csv
import os
import shutil

DATA_FOLDER = "staticMtaInfo"
BUS_STOPS_FILE = "busStops.csv"
BUS_STOPS_PATH = os.path.join(DATA_FOLDER, BUS_STOPS_FILE)
BUS_ROUTES_FILE = "busRoutes.csv"
BUS_ROUTES_PATH = os.path.join(DATA_FOLDER, BUS_ROUTES_FILE)
STOPS_BY_ROUTE_PATH = os.path.join(DATA_FOLDER, "stopsByRoute")
MTA_API_KEY = "8127ca5e-2293-444b-b56e-a41d79604969"

def getRouteData(busRouteId):
    url = f"https://bustime.mta.info/api/where/stops-for-route/{busRouteId}.json?key={MTA_API_KEY}&includePolylines=false&version=2"
    page = requests.get(url)
    stopsForRouteJSON = json.loads(page.content)
    return stopsForRouteJSON["data"]

def formatDestination(destination):
    """
    Turn destination (as returned by the MTA API) into a file name
    """
    return destination.replace(" ", "_").replace("/", "__")

def busLineIdToCommonName(busLineID):
    """
    Return common name of busLineID. (e.g. go from MTABC_Q39 to Q39)

    busLineID: str
    return: str?
    """
    with open(BUS_ROUTES_PATH) as f:
        busRoutesFile = csv.DictReader(f, delimiter=";")
        for route in busRoutesFile:
            if route["id"] == busLineID:
                return route["shortName"]

def getRouteFolder(busRouteId):
    busCommonName = busLineIdToCommonName(busRouteId)
    return os.path.join(STOPS_BY_ROUTE_PATH, f"busStops_{busCommonName}")

def getDestinationFile(busRouteId, destination):
    routeFolder = getRouteFolder(busRouteId)
    formattedDestination = formatDestination(destination)
    return os.path.join(routeFolder, f"{formattedDestination}.csv")

def writeDestinationsFile(busRouteId, stopGroups):
    routeFolder = getRouteFolder(busRouteId)
    destinationsPath = os.path.join(routeFolder, "destinations.txt")

    with open(destinationsPath, "w") as f:
        for group in stopGroups:
            destination = group["name"]["name"]
            f.write(destination)
            f.write("\n")

def writeStopsByDestinationFile(busRouteId, data, group):
    destination = group["name"]["name"]
    destinationStopsPath = getDestinationFile(busRouteId, destination)

    with open(destinationStopsPath, "w") as f:
        fieldnames = ["code","id","name","mainRoute","routeIds","destination"]
        busWriter = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')

        #I want to get all of the stops to one destination in the right order
        #the list of stops I'm pulling the data from does not have it in order
        #but the stop ids list for each destination is in order
        #so I'm first extracting the stop info for all of the stops along the destination
        #then I'm sorting those stops by when they appear in the stop ids to destination list
        stopIdsToOurDestination = group["stopIds"]
        busStopsToOurDestination = [busStop for busStop in data["references"]["stops"] if busStop["id"] in stopIdsToOurDestination]
        busStopToIndex = {busStopId: index for index, busStopId in enumerate(stopIdsToOurDestination)}
        busStopsToOurDestination.sort(key = lambda busStop: busStopToIndex[busStop["id"]])

        for busStop in busStopsToOurDestination:
            row = {"code": busStop["code"], "id": busStop["id"], "name": busStop["name"], "mainRoute": busRouteId, "routeIds": busStop["routeIds"], "destination": destination}
            busWriter.writerow(row)

def writeAllStopsForRouteFile(busRouteId):
    routeFolder = getRouteFolder(busRouteId)

    #concatenate the two stops for destination files
    destinationsPath = os.path.join(routeFolder, "destinations.txt")
    with open(destinationsPath) as f:
        destinations = f.read().strip().split("\n")
        #eliminate any empty destinations. This would happen if the route has no destinations
        #I've seen this on shuttle buses like SHUT5, SHGRD, and SHNRD
        destinations = [destination for destination in destinations if destination != ""]

    allStopsForRoutePath = os.path.join(routeFolder, "allStops.csv")
    with open(allStopsForRoutePath, "w") as f:
        for destination in destinations:
            destinationStopsPath = getDestinationFile(busRouteId, destination)
            with open(destinationStopsPath) as g:
                f.write(g.read())

def createRouteFolder(busRouteId, data):
    routeFolder = getRouteFolder(busRouteId)
    try:
        os.mkdir(routeFolder)
    except FileExistsError:
        #this is a really weird one, it looks like at least one route exists under both bus companies,
        # NYCT and MTABC. MTA bus time website seems to say that both routes are the same, so if a route
        # already exists just keep the original files as is and don't proceed with the rest of the code.
        return

    stopGroups = data["entry"]["stopGroupings"][0]["stopGroups"]
    writeDestinationsFile(busRouteId, stopGroups)
    #stopGroups separates stops by their destinations
    for group in stopGroups:
        writeStopsByDestinationFile(busRouteId, data=data, group=group)

    writeAllStopsForRouteFile(busRouteId)

def updateBusRoutes():
    with open(BUS_ROUTES_PATH, 'w') as f:
        fieldnames = ["id", "longName", "shortName"]
        routeWriter = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        routeWriter.writeheader()
        
        url = f"https://bustime.mta.info/api/where/routes-for-agency/MTABC.json?key={MTA_API_KEY}"
        page = requests.get(url)
        abcRoutesJSON = json.loads(page.content)
        abcRoutesList = abcRoutesJSON["data"]["list"]
        for route in abcRoutesList:
            f.write(f"{route['id']};{route['longName']};{route['shortName']}\n")
            print(route)

        url = f"https://bustime.mta.info/api/where/routes-for-agency/MTA%20NYCT.json?key={MTA_API_KEY}"
        page = requests.get(url)
        nyctRoutesJSON = json.loads(page.content)
        nyctRoutesList = nyctRoutesJSON["data"]["list"]
        for route in nyctRoutesList:
            f.write(f"{route['id']};{route['longName']};{route['shortName']}\n")

def updateBusStops():
    with open(BUS_STOPS_PATH, "w") as f, open(BUS_ROUTES_PATH) as g:
        os.mkdir(STOPS_BY_ROUTE_PATH)

        busStopWriter = csv.DictWriter(f, fieldnames=["code", "id", "name", "mainRoute", "routeIds"], delimiter=";")
        busStopWriter.writeheader()
        routeReader = csv.DictReader(g, delimiter=";")

        allStopIds = set()
        for route in routeReader:
            print(route["id"])
            data = getRouteData(route["id"])
            if data == None:
                print("PROBLEM")
                continue
            createRouteFolder(route["id"], data)

            for stop in data["references"]["stops"]:
                if stop["id"] in allStopIds:
                    continue
                allStopIds.add(stop["id"])
                stopInfo = {"code": stop["code"], "id": stop["id"], "name": stop["name"], "mainRoute": route["id"], "routeIds": stop["routeIds"]}
                busStopWriter.writerow(stopInfo)

def updateStaticMtaInfo():
    try:
        shutil.rmtree("staticMtaInfo")
    except FileExistsError:
        #either way, we're clear of the old data
        pass
    os.mkdir("staticMtaInfo")

    print(os.listdir("staticMtaInfo"))
    updateBusRoutes()
    print(os.listdir("staticMtaInfo"))
    updateBusStops()

if __name__ == "__main__":
    updateStaticMtaInfo()