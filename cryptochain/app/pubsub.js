const { json } = require('body-parser');
const redis = require('redis');

const CHANELS = {
    TEST: 'TEST',
    BLOCKCHAIN: 'BLOCKCHAIN'
}

class PubSub {
    constructor({blockchain}) {
        this.blockchain = blockchain;

        this.publisher = redis.createClient();
        this.subscriber = redis.createClient();

        this.subscribeToChanels();

        this.subscriber.on('message', 
            (chanel, message) => this.handleMessage(chanel, message));
    }

    handleMessage(chanel, message) {
        console.log(`Message recived. Chanel: ${chanel}. Message: ${message}`);

        const parsedMessage = JSON.parse(message);

        if (chanel === CHANELS.BLOCKCHAIN) {
            this.blockchain.replaceChain(parsedMessage);
        }
    }

    subscribeToChanels() {
        Object.values(CHANELS).forEach(chanel => {
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
            chanel: CHANELS.BLOCKCHAIN,
            message: JSON.stringify(this.blockchain.chain)
        })
    }
}

module.exports = PubSub;