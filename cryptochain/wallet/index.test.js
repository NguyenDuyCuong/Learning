const Wallet = require('./index');
const Transaction = require('./transaction');
const {verifySignature} = require('../util');
const Blockchain = require('../blockchain');
const { STARTING_BALANCE } = require('../config');

describe('Wallet', () => {
    let wallet;

    beforeEach(() => {
        wallet = new Wallet();
    });

    it('has a `balance`', () => {
        expect(wallet).toHaveProperty('balance');
    });

    it('has a `publicKey`', () => {
        expect(wallet).toHaveProperty('publicKey');
    });

    describe('signing data', () => {
        let data = "foo";
    
        it('verifies a signature', () => {            
            expect(
                verifySignature({
                    publicKey: wallet.publicKey,
                    data,
                    signature: wallet.sign(data)
                })
            ).toBe(true);
        });
    
        it('invalid signature', () => {
            expect(
                verifySignature({
                    publicKey: wallet.publicKey,
                    data,
                    signature: new Wallet().sign(data)
                })
            ).toBe(false);
        });
    });

    describe('createTransaction', () => {
        describe('and the amount exceeds the balance', () => {
            it(`throw an error`, () => {
                expect(()=> wallet.createTransaction({amount: 9999, recipient: 'foo'}))
                    .toThrow('Amount exceeds balance.');
            });
        });

        describe('and the amount is valid', () => {
            let transaction, amount, recipient;

            beforeEach(() => {
                amount = 50;
                recipient = 'foo';
                transaction = wallet.createTransaction({amount, recipient});
            });

            it(`create an instance od Transaction`, () => {
                expect(transaction instanceof Transaction).toBe(true);
            });

            it(`matches the transaction input with the wallet`, () => {
                expect(transaction.input.address).toEqual(wallet.publicKey);
            });

            it(`outputs the amount the recipient`, () => {
                expect(transaction.outputMap[recipient]).toEqual(amount);
            });
        });

        describe('and a chain is passed', () => {
            it(`call Wallet.calculateBalance`, () => {
                const calculateBalanceMock = jest.fn();
                const originalCalculateBalance = Wallet.calculateBalance;

                Wallet.calculateBalance = calculateBalanceMock;

                wallet.createTransaction({
                    recipient: 'foo',
                    amount: 40,
                    chain: new Blockchain().chain
                });

                expect(calculateBalanceMock)
                    .toHaveBeenCalled();
                Wallet.calculateBalance = originalCalculateBalance;
            });
        });
    });

    describe('calculateBalance', () => {
        let blockchain;

        beforeEach(() => {
            blockchain = new Blockchain();
        });
    
        describe('there are no outputs for the wallet', () => {
            it('return STARTING_BALANCE', () => {            
                expect(
                    Wallet.calculateBalance({
                        chain: blockchain.chain,
                        address: wallet.publicKey
                    })
                ).toEqual(STARTING_BALANCE);
            });
        });

        describe('there are outputs for the wallet', () => {
            let transactionOne, transactionTwo;

            beforeEach(() => {
                transactionOne = new Wallet().createTransaction({
                    recipient: wallet.publicKey,
                    amount: 50
                });

                transactionTwo = new Wallet().createTransaction({
                    recipient: wallet.publicKey,
                    amount: 60
                });

                blockchain.addBlock({data: [transactionOne, transactionTwo]});
            });

            it('sum of all outputs to the wallet balance', () => {            
                expect(
                    Wallet.calculateBalance({
                        chain: blockchain.chain,
                        address: wallet.publicKey
                    })
                ).toEqual(STARTING_BALANCE +
                    transactionOne.outputMap[wallet.publicKey] +
                    transactionTwo.outputMap[wallet.publicKey]);
            });
        });
    });
});