def execute(playerData, amount):
    try:
        amount = int(amount)
        if amount <= 0:
            print("Please enter a valid amount to deposit.")
            return
        if amount > playerData['balance']:
            print(f"You cannot deposit more than your current balance of ${playerData['balance']}.")
            return
        playerData['balance'] -= amount
        playerData['bank_balance'] += amount
        print(f"Successfully deposited ${amount}.")
    except ValueError:
        print("Invalid amount. Please enter a numeric value.")