const express = require('express');
const bodyParser = require('body-parser')
const Blockchain = require('../blockchain');
const P2PServer = require('./p2p-server');

const HTTP_PORT = process.env.HTTP_PORT || 3001;

const app = express();
const bc = new Blockchain();
const p2pServer = new P2PServer(bc);

app.use(bodyParser.json());

app.get('/blocks', (req, res) => {
    res.json(bc.chain);
});

app.post('/mine', (req, res) => {
    const block = bc.addBlock(req.body.data);
    console.log(`New block added: ${block.toString()}`)

    p2pServer.syncChains();

    return res.redirect('/blocks');
});

// ($env:HTTP_PORT=3002 $env:P2P_PORT=5002 $env:PEERS="ws://localhost:5001") -and npm run dev 
// npm run dev
app.listen(HTTP_PORT, () => console.log(`Listening in port ${HTTP_PORT}`));
p2pServer.listen()