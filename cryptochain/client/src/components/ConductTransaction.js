import React, {Component} from "react";
import { FormGroup, FormControl, Button } from "react-bootstrap";
import { Link, Redirect, useNavigate, useLocation } from "react-router-dom";

class ConductTransaction extends Component {
    state = {recipient: '', amount: 0};

    updateRecipient = event => {
        this.setState({recipient: event.target.value});
    }

    updateAmount = event => {
        this.setState({amount: Number( event.target.value)});
    }

    conductTransaction = () => {
        const {recipient, amount} = this.state;

        fetch(`http://localhost:3000/api/transact`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({recipient, amount})
        }).then(response => response.json())
        .then(json => {
            console.log(json);
            // navigate('/transaction-pool');
        });
    }

    render() {
        return (
            <div className="ConductTransaction">
                <Link to="/">Home</Link>
                <h3>Conduct a Transaction</h3>
                <FormGroup>
                    <FormControl inputMode="text" placeholder="recipient" value={this.state.recipient} onChange={this.updateRecipient}></FormControl>
                </FormGroup>
                <FormGroup>
                    <FormControl inputMode="text" placeholder="amount" value={this.state.amount} onChange={this.updateAmount}></FormControl>
                </FormGroup>
                <div>
                    <Button onClick={this.conductTransaction}>Submit</Button>
                </div>
            </div>
        )
    }
};

export default ConductTransaction;