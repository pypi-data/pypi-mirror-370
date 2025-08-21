import importlib
from lineage_rpg import data

def start_game():
    print("Welcome to Lineage RPG! Type 'exit' or CTRL+C to quit.")
    player_data = data.load_save()

    try:
        while True:
            user_input = input("> ").strip()
            if not user_input:
                continue

            parts = user_input.split()
            command = parts[0].lower()
            args = parts[1:]

            if command in ["exit", "quit"]:
                print("Saving progress and exiting...")
                break

            try:
                cmd_module = importlib.import_module(f"lineage_rpg.commands.{command}")

                from inspect import signature
                sig = signature(cmd_module.execute)
                required_arg_count = len([
                    p for p in list(sig.parameters.values())[1:]
                    if p.default == p.empty and p.kind in (p.POSITIONAL_OR_KEYWORD, p.POSITIONAL_ONLY)
                ])

                if len(args) < required_arg_count:
                    print(f"Too few arguments for '{command}'. Expected at least {required_arg_count}.\n")
                    continue

                if len(args) > (len(sig.parameters) - 1):
                    print(f"Too many arguments for '{command}'. Expected at most {len(sig.parameters) - 1}.\n")
                    continue

                print('\n' + '-' * 40 + '\n')
                cmd_module.execute(player_data, *args)
                print('\n' + '-' * 40 + '\n')
                data.save_data(player_data)

            except ModuleNotFoundError:
                print(f"Unknown command: {command}")
            except Exception as e:
                print(f"An error occurred while executing '{command}': {e}")

    except KeyboardInterrupt:
        print("\nSaving progress and exiting...")
        data.save_data(player_data)
    except Exception as e:
        print(f"\nUnexpected error: {e}. Saving progress and exiting...")
        data.save_data(player_data)