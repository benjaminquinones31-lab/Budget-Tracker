import streamlit as st
from datetime import datetime

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

if "expenses" not in st.session_state:
    st.session_state.expenses = []

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

if st.session_state.expenses:
    st.write("Expenses added:")

    for expense_category, expense_amount in st.session_state.expenses:
        st.write(f"{expense_category}: ${expense_amount:,.2f}")

    total = sum(amount for _, amount in st.session_state.expenses)
    st.write(f"**Total expenses: ${total:,.2f}**")

if st.button("Continue"):
    st.write(f"Budget month: {month_name} {year}")
    st.write(f"Monthly income: ${income:,.2f}")