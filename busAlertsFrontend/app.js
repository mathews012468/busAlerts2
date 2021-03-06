const express = require('express')
const path = require('path');
const app = express()
const port = 3000

// app.get('/', (req, res) => {
//   res.sendFile(path.join(__dirname, '/pages/index.html'))
// })
app.get('/', (req, res) => {
  res.send(`<!DOCTYPE html>
    <html>
    
    <head>
        <title>MTA Bus Alerts</title>
        <script type="text/javascript" defer>
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
    
            function verifyBusLine() {
                const commonBusName = document.getElementById("busCommonName").value
                const url = \`http://${process.env.IP_ADDRESS}:${process.env.BACKEND_PORT}/getbusstops?commonName=\${commonBusName}\`
                fetch(url, {
                    method: "GET"
                }).then(response => {
                    if (!response.ok) {
                        throw new Error(\`HTTP error: \${response.status}\`)
                    }
                    return response.json()
                }).then(jsonData => {
                    //add the name of the bus to the text of the element with id busLine
                    //set the name attribute of that element to the busLineID
                    let busLineElement = document.getElementById("busLine")
                    busLineElement.setAttribute("name", jsonData["busLineID"])
                    busLineElement.textContent = "Bus Line: "
                    busLineElement.textContent += commonBusName
    
                    let busLineInputElement = document.getElementById("busLineID")
                    busLineInputElement.value = jsonData["busLineID"]
                    delete jsonData["busLineID"]
    
                    const stopsElement = document.getElementById("stops")
                    stopsElement.innerHTML = ""
                    Object.keys(jsonData).forEach((destination => {
                        stopsElement.innerHTML += \`<div id="\${destination}">\${destination}</div>\`
                        for (let i = 0; i < jsonData[destination].length; i++) {
                            const destinationElement = document.getElementById(destination)
                            let code = jsonData[destination][i].code
                            let name = jsonData[destination][i].name
                            destinationElement.innerHTML += \`<li id="\${code}" onclick="clickedOnBusStop(this)">\${name}</li>\`
                        }
                        stopsElement.innerHTML += "<br>"
                    }))
                })
            }
    
        </script>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/css/bootstrap.min.css" rel="stylesheet"
            integrity="sha384-0evHe/X+R7YkIZDRvuzKMRqM+OrBnVFBL6DOitfPri4tjfHxaWutUpFmBp4vmVor" crossorigin="anonymous">
    
    
    
    </head>
    
    <body onload="document.body.style.opacity='1'">
    
        <style type="text/css">
            body {
                background: #528AAD;
                opacity: 0;
                transition: opacity 5s;
                font-family: "Lucida Console", "Courier New", monospace;
            }
    
            .textbox {
                background-color: #427ABD;
            }
    
    
            ::placeholder {
                color: black;
                opacity: 1;
                /* Firefox */
            }
    
            ::-ms-input-placeholder {
                /* Microsoft Edge */
                color: black;
            }
    
            .content {
                max-width: 500px;
                margin: auto;
                padding: 10px;
            }
    
            .buttonstyle {
                display: inline-block;
                padding: 0.3em 1.2em;
                margin: 0 0.3em 0.3em 0;
                border-radius: 2em;
                box-sizing: border-box;
                text-decoration: none;
                font-family: 'Roboto', sans-serif;
                font-weight: 300;
                color: #FFFFFF;
                background-color: #4eb5f1;
                text-align: center;
                transition: all 0.2s;
            }
    
            .buttonstyle:hover {
                background-color: #3573CA;
            }
    
            @media all and (max-width:30em) {
                .buttonstyle {
                    display: block;
                    margin: 0.2em auto;
                }
    
            }
        </style>
        <div class="content">
            <h1 style="color:rgb(12, 71, 129);">MTA Bus Alerts</h1><br>
            <img text-align: center;
                src="https://media.wired.com/photos/5ade58f0d6f7d02c2d3fd0ca/master/pass/FINALMTAelectricbusfinal240938522044_d7f745d0e5_o.jpg"
                alt="mta bus" width="570" height="280"><br>
            <br>
            <div>
                <input class="textbox" type="text" id="busCommonName" name="busCommonName" placeholder="Bus Common Name"
                    required></input>
            </div>
            <div>
                <button class="buttonstyle" onclick="verifyBusLine()">Submit</button>
            </div><br>
            <div id="stops"></div><br>
            <h5 style="color:rgb(12, 71, 129);" id="busLine">Bus Line: </h3>
                <h5 style="color:rgb(12, 71, 129);" id="busStop">Bus Stop: </h5>
                <form action="/alert" method="post">
                    <input class="textbox" type="text" name="busLineID" placeholder="Bus Line" id="busLineID" required><br>
                    <input class="textbox" type="text" name="busStopID" placeholder="Bus Stop" id="busStopID" required><br>
                    <input class="textbox" type="number" name="number" min="1" placeholder="Number" required>
                    <input type="checkbox" type="radio" id="minutes" name="units" value="minutes" checked>
                    <label for="minutes">minutes</label>
                    <input type="checkbox" type="radio" id="bus stops" name="units" value="bus stops">
                    <label for="bus stops">bus stops</label><br>
                    <input class="textbox" type="email" name="email" placeholder="Email Address" required><br>
                    <button class="buttonstyle" type="submit">Set up alert</button>
                </form>
        </div>
    
    </body>
    
    </html>`)
})

app.post('/alert', (req, res) => {
  res.redirect(307, `http://${process.env.IP_ADDRESS}:${process.env.BACKEND_PORT}/alert`)
})

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})