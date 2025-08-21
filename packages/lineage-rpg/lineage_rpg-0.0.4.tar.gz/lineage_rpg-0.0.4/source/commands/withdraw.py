def execute(player_data, amount):
    try:
        amount = int(amount)
        if amount <= 0:
            print("Please enter a valid amount to withdraw.")
            return
        if amount > player_data['bank_balance']:
            print(f"You cannot withdraw more than your current bank balance of ${player_data['bank_balance']}.")
            return
        player_data['bank_balance'] -= amount
        player_data['balance'] += amount
        print(f"Successfully withdrew ${amount}.")
    except ValueError:
        print("Invalid amount. Please enter a numeric value.")
