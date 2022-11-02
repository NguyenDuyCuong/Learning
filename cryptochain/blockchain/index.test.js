const Blockchain = require('./index');
const Block = require('./block');
const cryptoHash = require('../util/crypto-hash');

describe('Blockchain', () => {
    let blockchain, newChain, originalChain;

    beforeEach(() => {
        blockchain = new Blockchain();
        newChain = new Blockchain();

        originalChain = blockchain.chain;
    });

    it('contain chain Array', () => {
        expect(blockchain.chain instanceof Array).toBe(true);
    });

    it('start with genesis', () => {
        expect(blockchain.chain[0]).toEqual(Block.genesis());
    });

    it('add new block', () => {
        const newData = 'foo';
        blockchain.addBlock({data: newData});

        expect(blockchain.chain[blockchain.chain.length-1].data).toEqual(newData);
    });

    describe('ValidChain', () => {
        describe('chain is not start with genesis', () => {
            it('return false', () =>{
                blockchain.chain[0] = {data: 'fake'};

                expect(Blockchain.isValidChain(blockchain.chain)).toBe(false);
            })
        });

        describe('chain is start with genesis and has multiple blocks', () => {
            beforeEach(() => {
                blockchain.addBlock({data: 'Bears'});
                blockchain.addBlock({data: 'Beers'});
                blockchain.addBlock({data: 'Bats'});
            });
        
            describe('lastHash has changed', () => {
                it('return false', () =>{
                    blockchain.chain[2].lastHash = 'invalid-hash';
    
                    expect(Blockchain.isValidChain(blockchain.chain)).toBe(false);
                })
            });

            describe('chain has block contain  invalid field', () => {
                it('return false', () =>{
                    blockchain.chain[2].data = 'invalid-data';
    
                    expect(Blockchain.isValidChain(blockchain.chain)).toBe(false);
                })
            });

            describe('chain has block with jumped difficulty', () => {
                it('return false', () =>{
                    const lastBlock = blockchain.chain[blockchain.chain.length-1];
                    const lastHash = lastBlock.hash;
                    const timestamp = Date.now();
                    const nonce = 0;
                    const data = []
                    const difficulty = lastBlock.difficulty - 3;

                    const hash = cryptoHash(timestamp, lastHash, difficulty, nonce, data);
                    const badBlock = new Block({
                        timestamp, lastHash, hash, nonce, difficulty, data
                    });
                    blockchain.chain.push(badBlock);
    
                    expect(Blockchain.isValidChain(blockchain.chain)).toBe(false);
                })
            });

            describe('all block is valid', () => {
                it('return false', () =>{
                    expect(Blockchain.isValidChain(blockchain.chain)).toBe(true);
                })
            });
        });
    });

    describe('replace chain', () => {
        let errorMock, logMock;

        beforeEach(() => {
            errorMock = jest.fn();
            logMock = jest.fn();

            global.console.log = logMock;
            global.console.error = errorMock;
        })

        describe('new chain is not longer', () => {
            beforeEach(() => {
                newChain.chain[0] = {new: 'chain'};
                blockchain.replaceChain(newChain.chain);
            });

            it('does not replace chain', () =>{
                expect(blockchain.chain).toEqual(originalChain);
            });

            if('log an error', () => {
                expect(errorMock).toHaveBeenCalled();
            });
        });

        describe('new chain is longer', () => {
            beforeEach(() => {
                newChain.addBlock({data: 'Bears'});
                newChain.addBlock({data: 'Beers'});
                newChain.addBlock({data: 'Bats'});
            });

            describe('new chain is invalid', () => {
                beforeEach(() => {
                    newChain.chain[2].hash = 'invalid-hash';
                    blockchain.replaceChain(newChain.chain);
                });

                it('does not replace chain', () =>{
                    expect(blockchain.chain).toEqual(originalChain);
                });

                if('log an error', () => {
                    expect(errorMock).toHaveBeenCalled();
                });
            });

            describe('new chain is valid', () => {
                beforeEach(() => {
                    blockchain.replaceChain(newChain.chain);
                });

                it('replace chain', () =>{
                    expect(blockchain.chain).toEqual(newChain.chain);
                });

                if('log', () => {
                    expect(logMock).toHaveBeenCalled();
                });
            });
        });
    });
});