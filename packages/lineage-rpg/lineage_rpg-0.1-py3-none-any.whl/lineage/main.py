from lineage import storage, commands

def start_game():
    print("Welcome to Lineage RPG!. Type 'exit' or CTRL+C to quit.")
    data = storage.load_save()

    while True:
        try:
            command = input("> ").strip().lower()
            if command in ["exit", "quit"]:
                break
            elif command:
                commands.handle_command(command, data)
        except KeyboardInterrupt:
            print("\nWe hope you had fun!")
            break