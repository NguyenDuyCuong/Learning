import React, {Component} from "react";
import { FormGroup, FormControl, Button } from "react-bootstrap";
import { Link } from "react-router-dom";
import Transaction from "./Transaction";

const POOL_INERVAL_MS = 10000;

class TransactionPool extends Component  {
    state = {transactionPoolMap: {}};

    fetchTransactionPoolMap = () => {
        fetch(`http://localhost:3000/api/transaction-pool-map`)
        .then(response => response.json())
        .then(json => this.setState({ transactionPoolMap: json }));
    }

    fetchMineTransactions = () => {
        fetch(`http://localhost:3000/api/mine-transactions`)
        .then(response => response.json())
        .then(json => {
            console.log(json);
        });
    }

    componentDidMount() {
        this.fetchTransactionPoolMap();

        this.fetchPoolMapInterval = setInterval(() => {
            this.fetchTransactionPoolMap();
        }, POOL_INERVAL_MS);
    }

    componentWillUnmount() {
        clearInterval(this.fetchPoolMapInterval);
    }

    render() {
        return (
            <div className="TransactionPool">
                <Link to="/">Home</Link>
                <h3>Transaction Pool</h3>
                {
                    Object.values(this.state.transactionPoolMap).map(transaction => {
                        return (
                            <div key={transaction.id}>
                                <hr />
                                <Transaction transaction={transaction} />
                            </div>
                        )
                    })
                }
                <hr />
                <Button variant="danger" onClick={this.fetchMineTransactions} >Mine the Transactions</Button>
            </div>
        )
    }
}

export default TransactionPool;