import "./Expenses.css";
import ExpenseItem from "./ExpenseItem";
import Card from "../UI/Card";
import ExpensesFilter from "./ExpensesFilter";
import { useState } from "react";

const Expenses = (props) => {
  const expenses = props.expenses;

  const [yearVal, setYear] = useState('2020');

  const yearSelectedHandler = (year) => {
    console.log("Expenses");
    console.log(year);
    setYear(year);
  };

  return (
    <Card className="expenses">
      <ExpensesFilter selected={yearVal} onYearSelect={yearSelectedHandler} />

      <ExpenseItem 
        title={expenses[0].title}
        amount={expenses[0].amount}
        date={expenses[0].date}
        year={yearVal}
      ></ExpenseItem>
      <ExpenseItem
        title={expenses[1].title}
        amount={expenses[1].amount}
        date={expenses[1].date}
        year={yearVal}
      ></ExpenseItem>
      <ExpenseItem
        title={expenses[2].title}
        amount={expenses[2].amount}
        date={expenses[2].date}
        year={yearVal}
      ></ExpenseItem>
      <ExpenseItem
        title={expenses[3].title}
        amount={expenses[3].amount}
        date={expenses[3].date}
        year={yearVal}
      ></ExpenseItem>
    </Card>
  );
};

export default Expenses;
