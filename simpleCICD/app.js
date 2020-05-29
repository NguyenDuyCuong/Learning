const express = require('express')
const minimist = require('minimist')
const morgan = require('morgan')
const path = require('path')
const rfs = require('rotating-file-stream') 
const pino = require('pino');
const fs = require('fs')
const pinoms = require('pino-multi-stream')
const expressPino = require('express-pino-logger');

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
const port = args.port

const notify = require('./notify')

var streams = [
  {stream: rfs.createStream('app.log', {interval: '1d', path: path.join(__dirname, 'logs')})},
  {level: 'fatal', stream: rfs.createStream('app.fatal.log', {interval: '1d', path: path.join(__dirname, 'logs')})}
]
//const logger = pino({ level: process.env.LOG_LEVEL || 'info' })
const logger = pinoms({streams: streams})
const expressLogger = expressPino({ logger })

const app = express()

var accessLogStream = rfs.createStream('access.log', {
    interval: '1d', // rotate daily
    path: path.join(__dirname, 'logs')
  })
//app.use(morgan('combined', { stream: accessLogStream }))
app.use(expressLogger);

app.get('/', (req, res) => {
    req.log.info('Hello World!')
    res.send('Hello World!')
})
app.post('/notify', notify.notifyPine)
app.post('/notifyapi', notify.notifyPineAPI)

app.listen(port, () => console.log(`Example app listening at http://localhost:${port}`))