import ExpenseForm from './ExpenseForm';
import './NewExpense.css'

const NewExpense = (props) => {
    const saveEnxpenseDataHandler = (enteredExpenseDAta) => {
        const expenseData = {
            ...enteredExpenseDAta,
            id: Math.random().toString()
        }

        props.onAddExpense(expenseData);
    }

    return (
        <div className='new-expense'>
            <ExpenseForm onSaveExpenseData={saveEnxpenseDataHandler} />
        </div>
    );
}

export default NewExpense;
