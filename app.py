while True:
    try:
        income = float(input("Enter your monthly income: $"))

        if income < 0:
            print("Income Cannot be negative. Please try again.")
            continue

        break
    except ValueError:
        print("Please enter a valid number.")

expenses = 0

expenses_list = []

while True:
    expense_name = input("Enter an expense name (or type 'done' to move to debts): ")

    if expense_name.lower() == "done":
        break

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

debt_payments = 0
debt_list = []

while True:
    debt_name = input("Enter a debt name (or type 'done' to finish): ")

    if debt_name.lower() == "done":
        break

    try:

        debt_balance = float(input(f"Enter the total balance for {debt_name}: $"))
        apr = float(input("Enter the APR: "))
        payment = float(input("Enter your current minimum monthly payment: $"))
        paid_this_month = float(input("How much did you pay this month? $"))

    except ValueError:
        print("Please enter numbers only for the balance, APR, and payment.")
        continue

    if debt_balance <= 0 or apr < 0 or payment <= 0:
        print("Balance and payment must be positive. APR cannot be negative.")
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
        continue

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

total_expenses = expenses + debt_payments
remaining_balance = income - total_expenses


print("\nYour Expenses")

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
print("with an unchanged APR and no new charges or fees.")


print(f"\nRegular expenses: ${expenses:.2f}")
print(f"Monthly debt payments: ${debt_payments:.2f}")
print(f"Total monthly expenses: ${total_expenses:.2f}")
print(f"Money left: ${remaining_balance:.2f}")

if remaining_balance < 0:
    print("You went over budget!")
elif remaining_balance == 0:
    print("You are right on budget!")
else:
    print("You are under budget!")