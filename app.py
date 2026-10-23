import sqlite3
from pathlib import Path
from datetime import datetime

def setup_database():
    database_path = Path(__file__).resolve().with_name("budget.db")
    connection = sqlite3.connect(database_path)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY,
            month TEXT NOT NULL UNIQUE,
            income REAL NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            budget_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY (budget_id) REFERENCES budget(id)
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS debts (
            id INTEGER PRIMARY KEY,
            budget_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            balance REAL NOT NULL,
            apr REAL NOT NULL,
            minimum_payment REAL NOT NULL,
            paid_this_month REAL NOT NULL,
            FOREIGN KEY (budget_id) REFERENCES budget(id)
        )
    """)

    connection.commit()
    connection.close()

def get_month():
    while True:
        month = input("Enter the month (YYYY-MM): ").strip()

        try:
            date = datetime.strptime(month, "%Y-%m")

            if date.strftime("%Y-%m") != month:
                print("Use YYYY, for example 2026-10")
                continue

            return month

        except ValueError:
            print("Invalid month format. Please use YYYY-MM.")

def get_income():
    while True:
        try:
            income = float(input("Enter your monthly income: $"))

            if income < 0:
                print("Income cannot be negative. Please try again.")
                continue

            return income

        except ValueError:
            print("Please enter a valid number.")


def get_expenses():
    expenses = 0
    expenses_list = []

    while True:
        expense_name = input(
            "Enter an expense name (or type 'done' to move to debts): "
        ).strip()

        if expense_name.lower() == "done":
            break

        if not expense_name:
            print("Please enter an expense name.")
            continue

        while True:
            try:
                amount = float(input(f"Enter the amount for {expense_name}: $"))

                if amount < 0:
                    print("Expenses cannot be negative. Please try again.")
                    continue

                break

            except ValueError:
                print("Please enter a valid number.")

        expenses = expenses + amount
        expenses_list.append((expense_name, amount))

    return expenses, expenses_list


def show_payoff_estimate(debt):
    debt_name = debt["name"]
    debt_balance = debt["balance"]
    apr = debt["apr"]
    payment = debt["minimum_payment"]
    paid_this_month = debt["paid_this_month"]

    monthly_rate = apr / 100 / 12
    monthly_interest = debt_balance * monthly_rate

    if payment <= monthly_interest:
        print(f"\nDebt: {debt_name}")
        print(f"Estimated first-month interest: ${monthly_interest:.2f}")
        print(f"Current minimum payment: ${payment:.2f}")
        print(f"Paid this month: ${paid_this_month:.2f}")

        print("\nNo payoff date can be estimated using this fixed minimum.")
        print("The minimum does not exceed the estimated monthly interest.")

        if payment < monthly_interest:
            estimated_increase = monthly_interest - payment

            print(
                f"At that minimum, the balance would initially grow "
                f"by about ${estimated_increase:.2f} per month."
            )
        else:
            print("At that minimum, the balance would stay unchanged.")

        print(
            f"A fixed payment must exceed ${monthly_interest:.2f} "
            "to start reducing this balance under this estimate."
        )
        print("Your payment this month is still included in your budget.")
        print("This estimate excludes new charges and fees.\n")
        return

    balance = debt_balance
    total_paid = 0
    months = 0

    while balance > 0:
        interest = balance * monthly_rate
        balance = balance + interest

        actual_payment = min(payment, balance)
        balance = balance - actual_payment

        total_paid = total_paid + actual_payment
        months = months + 1

    total_interest = total_paid - debt_balance

    print(f"\nEstimated payoff for {debt_name}:")
    print(f"Months to pay off: {months}")
    print(f"Total interest: ${total_interest:.2f}")
    print(f"Total paid including interest: ${total_paid:.2f}\n")


def get_debts():
    debt_payments = 0
    debt_list = []

    while True:
        debt_name = input(
            "Enter a debt name (or type 'done' to finish): "
        ).strip()

        if debt_name.lower() == "done":
            break

        if not debt_name:
            print("Please enter a debt name.")
            continue

        try:
            debt_balance = float(
                input(f"Enter the total balance for {debt_name}: $")
            )
            apr = float(input("Enter the APR (for example, 20 for 20%): "))
            payment = float(
                input("Enter your current minimum monthly payment: $")
            )
            paid_this_month = float(
                input("How much did you pay this month? $")
            )

        except ValueError:
            print("Please enter numbers only for the balance, APR, and payments.")
            print("Please enter this debt again.")
            continue

        if debt_balance <= 0 or apr < 0 or payment <= 0:
            print("Balance and minimum payment must be positive.")
            print("APR cannot be negative.")
            print("Please enter this debt again.")
            continue

        if paid_this_month < 0:
            print("Payment cannot be negative. Please enter this debt again.")
            continue

        debt_payments = debt_payments + paid_this_month

        debt = {
            "name": debt_name,
            "balance": debt_balance,
            "apr": apr,
            "minimum_payment": payment,
            "paid_this_month": paid_this_month
        }

        debt_list.append(debt)
        show_payoff_estimate(debt)

    return debt_payments, debt_list


def show_summary(income, expenses, expenses_list, debt_payments, debt_list, month):
    total_expenses = expenses + debt_payments
    remaining_balance = income - total_expenses

    print("\nYour Expenses")

    if not expenses_list:
        print("No expenses entered.")
    else:
        for name, amount in expenses_list:
            print(f"{name}: ${amount:.2f}")

    print("\nYour Debts")

    if not debt_list:
        print("No debts entered.")
    else:
        for debt in debt_list:
            print(f"\nName: {debt['name']}")
            print(f"Balance: ${debt['balance']:.2f}")
            print(f"APR: {debt['apr']:.2f}%")
            print(f"Current minimum payment: ${debt['minimum_payment']:.2f}")
            print(f"Paid this month: ${debt['paid_this_month']:.2f}")

    print("\nPayoff estimates assume the entered minimum stays constant,")
    print("with monthly interest, an unchanged APR, and no new charges or fees.")

    print(f"\nMonthly income: ${income:.2f}")
    print(f"Regular expenses: ${expenses:.2f}")
    print(f"Monthly debt payments: ${debt_payments:.2f}")
    print(f"Total monthly expenses: ${total_expenses:.2f}")

    remaining_balance = round(remaining_balance, 2)

    month_name = datetime.strptime(month, "%Y-%m").strftime("%B %Y")

    if remaining_balance < 0:
        print("Money left: $0.00")
        print(
            f"You went ${abs(remaining_balance):.2f} "
            f"over budget for {month_name}!"
        )
    elif remaining_balance == 0:
        print("Money left: $0.00")
        print(f"You are right on budget for {month_name}!")
    else:
        print(f"Money left: ${remaining_balance:.2f}")
        print(
            f"You have ${remaining_balance:.2f} left. "
            f"You stayed within your budget for {month_name}!"
        )

def save_budget(month, income, expenses_list, debt_list):
    database_path = Path(__file__).resolve().with_name("budget.db")
    connection = sqlite3.connect(database_path)

    try:
        cursor = connection.execute(
            "INSERT INTO budget (month, income) VALUES (?, ?)",
            (month, income)
        )

        budget_id = cursor.lastrowid

        for name, amount in expenses_list:
            connection.execute(
                """
                INSERT INTO expenses (budget_id, name, amount)
                VALUES (?, ?, ?)
                """,
                (budget_id, name, amount)
            )

        for debt in debt_list:
            connection.execute(
                """
                INSERT INTO debts (
                    budget_id,
                    name,
                    balance,
                    apr,
                    minimum_payment,
                    paid_this_month
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    budget_id,
                    debt["name"],
                    debt["balance"],
                    debt["apr"],
                    debt["minimum_payment"],
                    debt["paid_this_month"]
                )
            )    

        connection.commit()
        print(f"\nBudget for {month} saved with its expenses and debts!")

    except sqlite3.IntegrityError:
        connection.rollback()
        print(f"\nA budget for {month} already exists. It was not replaced.")

    finally:
        connection.close()

def view_previous_budgets():
    database_path = Path(__file__).resolve().with_name("budget.db")
    connection = sqlite3.connect(database_path)

    try:
        budgets = connection.execute(
            "SELECT month, income FROM budget ORDER BY month DESC"
        ).fetchall()

        if not budgets:
            print("\nNo saved budgets yet.")
            return

        print("\nPrevious Budgets")

        for month, income in budgets:
            month_name = datetime.strptime(month, "%Y-%m").strftime("%B %Y")
            print(f"{month_name} — Income: ${income:.2f}")

        print("\nWhich month would you like to view?")
        month = get_month()

        budget = connection.execute(
            "SELECT id, income FROM budget WHERE month = ?",
            (month,)
        ).fetchone()

        if budget is None:
            print("\nNo budget saved for that month.")
            return

        budget_id, income = budget

        expenses_list = connection.execute(
            """
            SELECT name, amount
            FROM expenses
            WHERE budget_id = ?
            ORDER BY id
            """,
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

        debt_list = []

        for name, balance, apr, minimum_payment, paid_this_month in debt_rows:
            debt_list.append({
                "name": name,
                "balance": balance,
                "apr": apr,
                "minimum_payment": minimum_payment,
                "paid_this_month": paid_this_month
            })

        expenses = sum(amount for name, amount in expenses_list)

        debt_payments = sum(
            debt["paid_this_month"] for debt in debt_list
        )

        show_summary(
            income,
            expenses,
            expenses_list,
            debt_payments,
            debt_list,
            month
        )

    finally:
        connection.close()

def main():
    setup_database()

    while True:
        print("\nBudget Tracker")
        print("1. Create a new budget")
        print("2. See previous budgets")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            month = get_month()
            income = get_income()
            expenses, expenses_list = get_expenses()
            debt_payments, debt_list = get_debts()

            show_summary(
                income,
                expenses,
                expenses_list,
                debt_payments,
                debt_list,
                month
            )

            save_budget(month, income, expenses_list, debt_list)

        elif choice == "2":
            view_previous_budgets()

        elif choice == "3":
            print("Thank you for using the Budget Tracker!")
            break

        else:
            print("Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()