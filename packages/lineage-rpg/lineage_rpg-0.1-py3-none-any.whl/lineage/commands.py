from lineage import storage, utility

def handle_command(cmd, data):
    if cmd == "daily":
        handle_daily(data)
    elif cmd == "inventory":
        handle_inventory(data)
    else:
        print("Unknown command.")

def handle_daily(data):
    last_collected = data.get("last_daily")
    if utility.can_collect_daily(last_collected):
        print("You collected your daily reward!")
        data["last_daily"] = utility.current_time_iso()
        data["coins"] = data.get("coins", 0) + 100
        print(f"You now have {data['coins']} coins.")
        storage.save_data(data)
    else:
        print(f"You can collect your daily reward in {utility.time_left(last_collected)}!")

def handle_inventory(data):
    inventory = data.get("inventory", [])
    if inventory:
        print("Inventory:", ", ".join(inventory))
    else:
        print("Your inventory is empty.")
