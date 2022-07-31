const express = require('express')
const path = require('path');
const app = express()
const port = 3000

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '/pages/index.html'))
})

app.get('/getbusstops', (req, res) => {
    res.redirect(307, `http://${process.env.IP_ADDRESS}:${process.env.BACKEND_PORT}/getbusstops?commonName=${req.query.commonName}`)
})

app.post('/alert', (req, res) => {
  res.redirect(307, `http://${process.env.IP_ADDRESS}:${process.env.BACKEND_PORT}/alert`)
})

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})