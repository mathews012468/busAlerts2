const express = require('express')
const path = require('path');
const app = express()
const port = 3000

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '/pages/index.html'))
})

app.post('/alert', (req, res) => {
  res.redirect(307, 'http://0.0.0.0:10000/alert')
})

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})