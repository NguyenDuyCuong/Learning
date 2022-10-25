const Blockchain = require('./index');
const Block = require('./block');

describe('Block', () => {
    let bc, bc2;

    beforeEach(() => {
        bc = new Blockchain();
        bc2 = new Blockchain();
    })

    it('start with genesis', () => {
        expect(bc.chain[0]).toEqual(Block.genesis());
    });

    it('add new block', () => {
        const data = 'foo';
        bc.addBlock(data);

        expect(bc.chain[bc.chain.length-1].data).toEqual(data);
    });

    it('validate a valid chain', () => {
        bc2.addBlock('foo');

        expect(bc2.isValidChain(bc2.chain)).toBe(true);
    }); 

    it('invalidate a valid chain with corrupt genesis block', () => {
        bc2.chain[0].data = 'foo';

        expect(bc2.isValidChain(bc2.chain)).toBe(false);
    });

    it('invalidate a corrupt chain', () => {
        bc2.addBlock('foo');
        bc2.chain[1].data = 'Not foo';

        expect(bc2.isValidChain(bc2.chain)).toBe(false);
    });

    it('replace valid chain', () => {
        bc2.addBlock('goo');
        bc.replaceChain(bc2.chain);

        expect(bc.chain).toEqual(bc2.chain);
    });

    it('nor replace valid chain', () => {
        bc.addBlock('foo');
        bc.replaceChain(bc2.chain);

        expect(bc.chain).not.toEqual(bc2.chain);
    });
});