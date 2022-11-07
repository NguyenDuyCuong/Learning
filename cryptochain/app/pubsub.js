const { json } = require('body-parser');
const redis = require('redis');

const CHANNELS = {
    TEST: 'TEST',
    BLOCKCHAIN: 'BLOCKCHAIN',
    TRANSACTION: 'TRANSACTION'
}

class PubSub {
    constructor({blockchain,transactionPool}) {
        this.blockchain = blockchain;
        this.transactionPool = transactionPool;

        this.publisher = redis.createClient();
        this.subscriber = redis.createClient();

        this.subscribeToChannels();

        this.subscriber.on('message', 
            (chanel, message) => this.handleMessage(chanel, message));
    }

    handleMessage(chanel, message) {
        console.log(`Message received. Chanel: ${chanel}. Message: ${message}`);

        const parsedMessage = JSON.parse(message);

        switch(chanel) {
            case CHANNELS.BLOCKCHAIN:
                this.blockchain.replaceChain(parsedMessage, ()=>{
                    this.transactionPool.clearBlockchainTransactions({
                        chain: parsedMessage
                    });
                });
                break;
            case CHANNELS.TRANSACTION:
                this.transactionPool.setTransaction(parsedMessage);
                break;
            default:
                return;
        }
    }

    subscribeToChannels() {
        Object.values(CHANNELS).forEach(chanel => {
            this.subscriber.subscribe(chanel);
        });
    }

    publish({chanel, message}) {
        this.subscriber.unsubscribe(chanel, () => {
            this.publisher.publish(chanel, message, () => {
                this.subscriber.subscribe(chanel);
            });
        });
        
    }

    broadcastChain() {
        this.publish({
            chanel: CHANNELS.BLOCKCHAIN,
            message: JSON.stringify(this.blockchain.chain)
        })
    }

    broadcastTransaction(transaction) {
        this.publish({
            chanel: CHANNELS.TRANSACTION,
            message: JSON.stringify(transaction)
        })
    }
}

module.exports = PubSub;