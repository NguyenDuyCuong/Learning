const express = require('express')
const minimist = require('minimist')
const morgan = require('morgan')
const path = require('path')
const rfs = require('rotating-file-stream') 

let args = minimist(process.argv.slice(2), {
    alias: {
        p: 'port',
        h: 'help',
        v: 'version'
    },
    default: {
        port: 3000
    },
});

const notify = require('./notify')

const app = express()
const port = args.port

var accessLogStream = rfs.createStream('access.log', {
    interval: '1d', // rotate daily
    path: path.join(__dirname, 'log')
  })
app.use(morgan('combined', { stream: accessLogStream }))

app.get('/', (req, res) => res.send('Hello World!'))
app.post('/notify', notify.notify)

app.listen(port, () => console.log(`Example app listening at http://localhost:${port}`))