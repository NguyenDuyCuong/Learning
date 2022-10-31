const Block = require('./block');
const cryptoHash = require('./crypto-hash');
const {GENESIS_DATA, MINE_RATE} = require('./config');
const hexToBinary = require('hex-to-binary');

describe('Block', () => {
    const timestamp = 2000;
    const lastHash = 'foo-hash';
    const hash = 'bar-hash';
    const data = ['blockchain', 'data']
    const nonce = 1;
    const difficulty = 1;
    const block = new Block({timestamp, lastHash, hash, data, nonce, difficulty});

    it('has a timestamp', () => {
        expect(block.timestamp).toEqual(timestamp);
        expect(block.lastHash).toEqual(lastHash);
        expect(block.hash).toEqual(hash);
        expect(block.data).toEqual(data);
        expect(block.nonce).toEqual(nonce);
        expect(block.difficulty).toEqual(difficulty);
    });

    describe('genesis', () => {
        const genesisBlock = Block.genesis();

        it('genesis instance', () => {
            expect(genesisBlock instanceof Block).toBe(true);
        });

        it('genesis data', () => {
            expect(genesisBlock).toEqual(GENESIS_DATA);
        });
    });

    describe('mine block', () => {
        const lastBlock = Block.genesis();
        const data = 'mined data';
        const mineBLock = Block.mineBlock({lastBlock, data})

        it('mine block instance', () => {
            expect(mineBLock instanceof Block).toBe(true);
        });

        it('lastHash is hash', () => {
            expect(mineBLock.lastHash).toEqual(lastBlock.hash);
        });

        it('set data', () => {
            expect(mineBLock.data).toEqual(data);
        });

        it('set timestamp', () => {
            expect(mineBLock.timestamp).not.toEqual(undefined);
        });

        it('create sha-256', () => {
            expect(mineBLock.hash)
                .toEqual(cryptoHash(
                    mineBLock.timestamp,
                    mineBLock.nonce,
                    mineBLock.difficulty,
                    lastBlock.hash, 
                    data));
        });

        it('set hash match difficulty', () => {
            expect(hexToBinary(mineBLock.hash).substring(0,mineBLock.difficulty))
                .toEqual('0'.repeat(mineBLock.difficulty));
        });

        it('adjust difficulty', () => {
            const possibleResults = [lastBlock.difficulty+1,lastBlock.difficulty-1]
            expect(possibleResults.includes(mineBLock.difficulty)).toBe(true);
        });
    });

    describe('adjustDifficulty', () => {
        it(' raise difficulty', () => {
            expect(Block.adjustDifficulty({
                originalBlock: block,
                timestamp: block.timestamp + MINE_RATE - 100
            })).toEqual(block.difficulty + 1);
        });

        it('lower difficulty', () => {
            expect(Block.adjustDifficulty({
                originalBlock: block,
                timestamp: block.timestamp + MINE_RATE + 100
            })).toEqual(block.difficulty - 1);
        });

        it('lower limit of 1', () => {
            block.difficulty = -1;
            expect(Block.adjustDifficulty({
                originalBlock: block
            })).toEqual(1);
        });
    });
});