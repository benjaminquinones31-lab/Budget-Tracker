import streamlit as st
from datetime import datetime
from app import calculate_budget, calculate_payoff, setup_database, save_budget
import sqlite3
from pathlib import Path

st.title("Budget Tracker")
st.write("Let's create your monthly budget.")

current_year = datetime.now().year

month_name = st.selectbox(
    "Choose a month",
    [
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October", "November", "December"
    ]
)

year = st.selectbox(
    "Choose a year",
    range(current_year - 5, current_year + 6),
    index=5
)

income = st.number_input(
    "Enter your monthly income",
    min_value=0.0,
    step=100.0,
    format="%.2f"
)

st.subheader("Expenses")

selected_month_number = datetime.strptime(month_name, "%B").month
selected_month = f"{year}-{selected_month_number:02d}"

setup_database()
database_path = Path(__file__).resolve().with_name("budget.db")

def get_previous_expenses(month):
    with sqlite3.connect(database_path) as connection:
        previous = connection.execute(
            """
            SELECT id, month FROM budget
            WHERE month < ?
            ORDER BY month DESC
            LIMIT 1
            """,
            (month,)
        ).fetchone()

        if previous is None:
            return None, []

        budget_id, previous_month = previous
        expenses = connection.execute(
            """
            SELECT name, amount FROM expenses
            WHERE budget_id = ?
            ORDER BY id
            """,
            (budget_id,)
        ).fetchall()

        return previous_month, expenses


if "expenses" not in st.session_state:
    previous_month, previous_expenses = get_previous_expenses(selected_month)
    st.session_state.expenses = previous_expenses
    st.session_state.expenses_month = selected_month

    if previous_month:
        st.info(f"Expenses copied from the saved budget for {previous_month}.")

if "expenses_month" not in st.session_state:
    st.session_state.expenses_month = selected_month

if st.session_state.expenses_month != selected_month:
    previous_month, previous_expenses = get_previous_expenses(selected_month)

    if previous_month:
        st.info(
            f"The most recent saved budget before this month is "
            f"{previous_month}."
        )

        if st.button("Copy expenses from that budget"):
            st.session_state.expenses = previous_expenses
            st.session_state.expenses_month = selected_month
            st.session_state.editing_expense = None
            st.rerun()
    else:
        st.write("There is no earlier saved budget to copy expenses from.")

    st.caption(
        "Copying expenses replaces the current expense list. "
        "The saved budget stays unchanged."
    )

category = st.selectbox(
    "Expense category",
    [
        "Rent / Mortgage",
        "Car Insurance",
        "Health Insurance",
        "Gas",
        "Electric",
        "Water",
        "Trash",
        "Subscriptions",
        "Eating Out",
        "Groceries",
        "Phone Bill",
        "Internet",
        "Transportation",
        "Entertainment",
        "Miscellaneous",
        "Add Your Own Category"
    ]
)

if category == "Add Your Own Category":
    category = st.text_input("Enter your expense category").strip()

amount = st.number_input(
    "Expense amount",
    min_value=0.0,
    step=10.0,
    format="%.2f"
)

if st.button("Add expense"):
    if not category:
        st.warning("Enter a name for your expense category.")
    elif amount <= 0:
        st.warning("Enter an amount greater than zero.")
    else:
        st.session_state.expenses.append((category, amount))


st.subheader("Debts")

debt_name = st.selectbox(
    "Debt category",
    [
        "Mortgage",
        "Auto Loan",
        "Credit Card Debt",
        "Student Loan",
        "Personal Loan",
        "Medical Debt",
        "Miscellaneous",
        "Add Your Own Category"
    ]
)

if debt_name == "Add Your Own Category":
    debt_name = st.text_input("Enter your debt category").strip()

debt_balance = st.number_input(
    "Remaining balance",
    min_value=0.0,
    step=100.0,
    format="%.2f"
)

apr = st.number_input(
    "Annual interest rate (APR %)",
    min_value=0.0,
    step=1.0,
    format="%.2f"
)

minimum_payment = st.number_input(
    "Minimum monthly payment",
    min_value=0.0,
    step=10.0,
    format="%.2f"
)

paid_this_month = st.number_input(
    "Amount paid this month",
    min_value=0.0,
    step=10.0,
    format="%.2f"
)
if "debts" not in st.session_state:
    st.session_state.debts = []

if st.button("Add debt"):
    if not debt_name:
        st.warning("Enter a name for your debt category.")
    elif debt_balance <= 0 or minimum_payment <= 0:
        st.warning("Enter a balance and minimum payment greater than zero.")
    else:
        debt = {
            "name": debt_name,
            "balance": debt_balance,
            "apr": apr,
            "minimum_payment": minimum_payment,
            "paid_this_month": paid_this_month
        }

        st.session_state.debts.append(debt)

if "editing_expense" not in st.session_state:
    st.session_state.editing_expense = None

if st.session_state.expenses:
    st.write("Expenses added:")

    for i, (expense_category, expense_amount) in enumerate(
        st.session_state.expenses
    ):
        name_col, edit_col, delete_col = st.columns([4, 1, 1])

        with name_col:
            st.write(f"{expense_category}: ${expense_amount:,.2f}")

        with edit_col:
            if st.button("Edit", key=f"edit_{i}"):
                st.session_state.editing_expense = i

        with delete_col:
            if st.button("Delete", key=f"delete_{i}"):
                st.session_state.expenses.pop(i)
                st.session_state.editing_expense = None
                st.rerun()

    total = sum(amount for _, amount in st.session_state.expenses)
    st.write(f"**Total expenses: ${total:,.2f}**")

    if st.session_state.editing_expense is not None:
        i = st.session_state.editing_expense
        current_name, current_amount = st.session_state.expenses[i]

        st.write(f"Editing: {current_name}")

        with st.form("edit_expense"):
            new_name = st.text_input("Expense name", value=current_name)
            new_amount = st.number_input(
                "Expense amount",
                min_value=0.0,
                value=current_amount,
                step=10.0,
                format="%.2f"
            )
            save_change = st.form_submit_button("Save change")

        if save_change:
            if not new_name.strip() or new_amount <= 0:
                st.warning("Enter a name and an amount greater than zero.")
            else:
                st.session_state.expenses[i] = (new_name.strip(), new_amount)
                st.session_state.editing_expense = None
                st.rerun()

if st.session_state.debts:
    st.write("Debts added:")

    for debt in st.session_state.debts:
        st.write(
            f"{debt['name']}: ${debt['balance']:,.2f} balance, "
            f"${debt['paid_this_month']:,.2f} paid this month"
        )

        estimate = calculate_payoff(debt)

        if estimate["months"] is None:
            st.warning(
                "The minimum payment does not cover the estimated "
                "monthly interest, so a payoff date cannot be estimated."
            )
        else:
            st.write(
                f"Estimated payoff: {estimate['months']} months. "
                f"Estimated interest: ${estimate['total_interest']:,.2f}."
            )

    st.caption(
        "Estimates assume the minimum payment and APR stay the same, "
        "with no new charges or fees."
    )
    
if st.button("Continue"):
    summary = calculate_budget(
        income,
        st.session_state.expenses,
        st.session_state.debts
    )

    st.subheader(f"Budget summary for {month_name} {year}")
    st.write(f"Monthly income: ${income:,.2f}")
    st.write(f"Regular expenses: ${summary['expenses']:,.2f}")
    st.write(f"Debt payments: ${summary['debt_payments']:,.2f}")
    st.write(f"Total expenses: ${summary['total_expenses']:,.2f}")
    st.write(f"**Remaining balance: ${summary['remaining_balance']:,.2f}**")

if st.button("Save budget"):
    month_number = datetime.strptime(month_name, "%B").month
    month = f"{year}-{month_number:02d}"

    setup_database()

    saved = save_budget(
        month,
        income,
        st.session_state.expenses,
        st.session_state.debts
    )

    if saved:
        st.success(f"Budget for {month_name} {year} saved!")
    else:
        st.warning(f"A budget for {month_name} {year} already exists.")

st.subheader("Saved budgets")

setup_database()
database_path = Path(__file__).resolve().with_name("budget.db")

with sqlite3.connect(database_path) as connection:
    budgets = connection.execute(
        "SELECT id, month, income FROM budget ORDER BY month DESC"
    ).fetchall()

    if not budgets:
        st.write("No saved budgets yet.")
    else:
        selected_budget = st.selectbox(
            "Choose a saved budget",
            budgets,
            format_func=lambda budget: datetime.strptime(
                budget[1], "%Y-%m"
            ).strftime("%B %Y")
        )

        budget_id, saved_month, saved_income = selected_budget

        saved_expenses = connection.execute(
            "SELECT name, amount FROM expenses WHERE budget_id = ? ORDER BY id",
            (budget_id,)
        ).fetchall()

        debt_rows = connection.execute(
            """
            SELECT name, balance, apr, minimum_payment, paid_this_month
            FROM debts
            WHERE budget_id = ?
            ORDER BY id
            """,
            (budget_id,)
        ).fetchall()

        saved_debts = []
        for name, balance, apr, minimum, paid in debt_rows:
            saved_debts.append({
                "name": name,
                "balance": balance,
                "apr": apr,
                "minimum_payment": minimum,
                "paid_this_month": paid
            })

        st.write(f"Income: ${saved_income:,.2f}")

        st.write("**Expenses**")
        if saved_expenses:
            for name, amount in saved_expenses:
                st.write(f"{name}: ${amount:,.2f}")
        else:
            st.write("No expenses saved.")

        st.write("**Debts**")
        if saved_debts:
            for debt in saved_debts:
                st.write(
                    f"{debt['name']}: ${debt['balance']:,.2f} balance, "
                    f"${debt['paid_this_month']:,.2f} paid that month"
                )
        else:
            st.write("No debts saved.")

        saved_summary = calculate_budget(
            saved_income, saved_expenses, saved_debts
        )
        st.write(
            f"**Remaining balance: "
            f"${saved_summary['remaining_balance']:,.2f}**"
        )

        confirm_delete = st.checkbox(
            "I want to delete this saved budget",
            key=f"confirm_delete_{budget_id}"
        )

        if st.button("Delete saved budget", disabled=not confirm_delete):
            connection.execute(
                "DELETE FROM expenses WHERE budget_id = ?", (budget_id,)
            )
            connection.execute(
                "DELETE FROM debts WHERE budget_id = ?", (budget_id,)
            )
            connection.execute(
                "DELETE FROM budget WHERE id = ?", (budget_id,)
            )
            connection.commit()
            st.rerun()