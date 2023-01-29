function clickedOnBusStop(busStopElement) {
    //add the name of bus stop to the text of the element with id busStop
    //set the name attribute of that element to the bus stop code
    //jump to the bottom of the page where the rest of the info needs to get entered
    chosenStopElement = document.getElementById("busStop")
    chosenStopElement.setAttribute("name", busStopElement.id)
    chosenStopElement.textContent = "Bus Stop: "
    chosenStopElement.textContent += busStopElement.textContent

    let busStopInputElement = document.getElementById("busStopID")
    busStopInputElement.value = busStopElement.id
    document.getElementById("busStop").scrollIntoView({ behavior: 'smooth' });
}

//must have at least one of the following: phone number, email address
function hasUserProvidedContact() {
    //all of these keys come from the name attribute
    let alertForm = document.forms["alert"]
    phoneNumber = alertForm["phone"].value
    email = alertForm["email"].value
    if ((phoneNumber != "") || (email != "")) {
        return true
    } else {
        alert("Must provide either a phone number or an email address")
        return false
    }
}

function displayPossibleRoutes(possibleRoutes) {
    possibleRouteDisplay = document.querySelector("#possible-buses")
    //clear old data before displaying new
    possibleRouteDisplay.innerHTML = ""
    for (let i = 0; i < possibleRoutes.length; i++) {
        possibleRouteDisplay.innerHTML += `<p class="possible-route" onclick="setRouteOnceClicked(this)">${possibleRoutes[i]}</p>`
    }
}

let highlightedRouteIndex = 0
function getPossibleRoutes() {
    //should reset every time new results display
    highlightedRouteIndex = 0

    routeSnippet = document.querySelector("#busCommonName").value

    displayPossibleRoutes([]) //clear display before continuing
    if (routeSnippet.length < 2) {
        return
    }

    const url = `/possibleroutes?snippet=${routeSnippet}`
    fetch(url, {
        method: "GET"
    }).then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`)
        }
        return response.json()
    }).then(jsonData => {
        displayPossibleRoutes(jsonData)
    })
}

function setRouteOnceClicked(routeElement) {
    let routeInputElement = document.querySelector("#busCommonName")
    routeInputElement.value = routeElement.textContent
    displayPossibleRoutes([])
}

function clearPossibleRoutes() {
    let routes = document.querySelectorAll(".possible-route")
    for (let i = 0; i < routes.length; i++) {
        routes[i].style = "background-color: white;"
    }
}

function detectTabbingThroughRoutes(event) {
    if (event.key !== "ArrowDown" && event.key !== "ArrowUp") {
        return
    }

    if (event.key === "ArrowDown") {
        highlightedRouteIndex += 1
    } else if (event.key === "ArrowUp") {
        highlightedRouteIndex -= 1
    }

    //we want routeIndex to be in the range of 1 to the number of routes displayed
    //this achieves a wrap-around behavior. If they go up when they're already at
    //the top, we want to send the them to the bottom (and vice versa)
    let numberOfDisplayedRoutes = document.querySelector("#possible-buses").childElementCount
    if (highlightedRouteIndex < 1) {
        highlightedRouteIndex = numberOfDisplayedRoutes
    } else if (highlightedRouteIndex > numberOfDisplayedRoutes) {
        highlightedRouteIndex = 1
    }

    //clear everything, then highlight the correct one
    clearPossibleRoutes()
    let highlightedRoute = document.querySelector(`.possible-route:nth-child(${highlightedRouteIndex})`)
    highlightedRoute.style = "background-color: gray;"
}

function selectRoute(event) {
    let numberOfDisplayedRoutes = document.querySelector("#possible-buses").childElementCount
    if (event.key !== "Enter" || highlightedRouteIndex === 0 || numberOfDisplayedRoutes === 0) {
        return
    }

    //set the selected bus and hide all possible routes
    let highlightedRoute = document.querySelector(`.possible-route:nth-child(${highlightedRouteIndex})`)
    let routeInputElement = document.querySelector("#busCommonName")
    routeInputElement.value = highlightedRoute.textContent
    displayPossibleRoutes([])
}

function getStopsForRouteEnter() {
    //only move forward if user hits enter, there is text in the input
    let routeInputElement = document.querySelector("#busCommonName")
    if (event.key !== "Enter" || routeInputElement.value == "") {
        return
    }
    
    displayPossibleRoutes([])
    verifyBusLine()
}

function addEventToDetectRouteEdit() {
    let routeInputElement = document.querySelector("#busCommonName")
    routeInputElement.addEventListener("input", getPossibleRoutes)
    routeInputElement.addEventListener("keydown", detectTabbingThroughRoutes)
    routeInputElement.addEventListener("keydown", selectRoute)
    routeInputElement.addEventListener("keydown", getStopsForRouteEnter)
}