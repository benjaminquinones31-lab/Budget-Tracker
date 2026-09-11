income = float(input("Enter your monthly income: $"))
expenses = 0

while True:
    expense_name = input("Enter an expense name (or type 'done' to move to debts): ")

    if expense_name.lower() == "done":
        break

    amount = float(input(f"Enter the amount for {expense_name}: $"))
    expenses = expenses + amount

debt_payments = 0

while True:
    debt_name = input("Enter a debt name (or type 'done' to finish): ")

    if debt_name.lower() == "done":
        break

    debt_balance = float(input(f"Enter the total balance for {debt_name}: $"))
    apr = float(input("Enter the APR as a percentage (example: 20): "))
    payment = float(input("Enter your monthly payment: $"))

    if debt_balance <= 0 or apr < 0 or payment <= 0:
        print("Balance and payment must be positive. APR cannot be negative.")
        print("Please enter this debt again.")
        continue

    debt_payments = debt_payments + payment

    monthly_rate = apr / 100 / 12

    if payment <= debt_balance * monthly_rate:
        print("This payment will not pay off the debt.")
        print("It must be greater than the monthly interest.")
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