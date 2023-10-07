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
    let possibleRouteDisplay = document.querySelector("#possible-buses")
    //clear old data before displaying new
    possibleRouteDisplay.innerHTML = ""
    for (let i = 0; i < possibleRoutes.length; i++) {
        possibleRouteDisplay.innerHTML += `<a href="/getbusstops?commonName=${possibleRoutes[i]}"><p class="possible-route">${possibleRoutes[i]}</p></a>`
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
    let highlightedRoute = document.querySelector(`a:nth-child(${highlightedRouteIndex}) .possible-route`)
    highlightedRoute.style = "background-color: gray;"
}

function selectRoute(event) {
    let numberOfDisplayedRoutes = document.querySelector("#possible-buses").childElementCount
    if (event.key !== "Enter" || highlightedRouteIndex === 0 || numberOfDisplayedRoutes === 0) {
        return
    }

    //set the selected bus and hide all possible routes
    let highlightedRoute = document.querySelector(`a:nth-child(${highlightedRouteIndex}) .possible-route`)
    let routeInputElement = document.querySelector("#busCommonName")
    routeInputElement.value = highlightedRoute.textContent
    displayPossibleRoutes([])
}

let helpPopup = document.getElementById("help-popup")
let firstHelp = document.querySelector("#help-popup li:nth-child(1)")
let secondHelp = document.querySelector("#help-popup li:nth-child(2)")
let thirdHelp = document.querySelector("#help-popup li:nth-child(3)")
let upButton = document.getElementById("up")
let downButton = document.getElementById("down")
let padding = 10
function scrollUp() {
    let helpPopupY = helpPopup.getBoundingClientRect().y
    let secondY = secondHelp.getBoundingClientRect().y
    let thirdY = thirdHelp.getBoundingClientRect().y

    if (secondY >= helpPopupY) {
        firstHelp.scrollIntoView()
    } else if (thirdY >= helpPopupY) {
        secondHelp.scrollIntoView()
    } else {
        thirdHelp.scrollIntoView()
    }
}
function scrollDown() {
    let helpPopupY = helpPopup.getBoundingClientRect().y
    let firstY = firstHelp.getBoundingClientRect().y
    let secondY = secondHelp.getBoundingClientRect().y

    //the padding allows the down button to move to the next step instead of staying on the same one
    if (firstY > helpPopupY + padding) {
        firstHelp.scrollIntoView()
    } else if (secondY > helpPopupY + padding) {
        secondHelp.scrollIntoView()
    } else {
        thirdHelp.scrollIntoView()
    }
}
function enableButton(button, enable) {
    /*
    enable: bool
    */
   if (enable) {
    button.removeAttribute("disabled")
   } else {
    button.setAttribute("disabled", "disabled")
   }
}
function enableOrDisableUpDownButtons() {
    let helpPopupY = helpPopup.getBoundingClientRect().y
    let firstY = firstHelp.getBoundingClientRect().y
    let thirdY = thirdHelp.getBoundingClientRect().y

    if (firstY >= helpPopupY) {
        enableButton(upButton, false)
    } else {
        enableButton(upButton, true)
    }

    if (thirdY < helpPopupY + padding) {
        enableButton(downButton, false)
    } else {
        enableButton(downButton, true)
    }

    console.log("what's up")
}

function addEventListeners() {
    let openDialogButton = document.getElementById("open-help")
    let helpWindow = document.getElementById("help-popup")
    openDialogButton.addEventListener("click", () => { 
        helpWindow.showModal()
    })

    let upButton = document.getElementById("up")
    upButton.addEventListener("click", scrollUp)
    let downButton = document.getElementById("down")
    downButton.addEventListener("click", scrollDown)
    setInterval(enableOrDisableUpDownButtons, 500)

    let closeDialogButton = document.querySelector("#end-dialog button")
    closeDialogButton.addEventListener("click", () => {
        helpWindow.close()
    })

    let routeInputElement = document.querySelector("#busCommonName")
    if (routeInputElement === null) {
        return
    }

    routeInputElement.addEventListener("input", getPossibleRoutes)
    routeInputElement.addEventListener("keydown", detectTabbingThroughRoutes)
    routeInputElement.addEventListener("keydown", selectRoute)
}