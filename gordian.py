# gordian.py
import os
import json
import signal
import core.game as game
import core.ui as ui
import core.audio as audio
import random  # If you use random name generation
import time

def signal_handler(sig, frame):
    print("\nCtrl-C detected. Exiting gracefully...")
    exit(0)

def generate_random_name():
    first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def main():
    signal.signal(signal.SIGINT, signal_handler)
    os.system('cls' if os.name == 'nt' else 'clear')

    # Load configuration
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found.")
        exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in config.json.")
        exit(1)

    # Initialize audio manager
    audio_manager = audio.AudioManager(config)

    # Initialize UI with the selected theme
    ui_manager = ui.UI(config["theme"])


    ui_manager.display_message("Welcome to Gordian!", "text_highlight") #use ui class
    #print(center_text(ascii_art)) #we will use it later
    player_name = ui_manager.centered_input("Enter your name (or press Enter for a random name): ").strip()
    if not player_name:
        player_name = generate_random_name()  # You might want to move this to a separate function
    ui_manager.display_message(f"Welcome, {player_name}!", "text_highlight")

    # Start music
    audio_manager.play_music(config["audio"]["screen_music"]["main"])

    # Display intro story
    for line in config.get("intro", []):  # Handle missing intro gracefully
        ui_manager.display_message(line, "text_highlight")
        time.sleep(1)  # Pause between lines (optional)

    while True:
        # Create the Game instance, passing in config
        current_game = game.Game(player_name, config)
        try:
            while current_game.play_turn(ui_manager, audio_manager):  # Pass ui and audio to play_turn
                if current_game.check_victory():
                    #current_game.update_hall_of_fame() #we do not have it yet
                    current_game.show_game_stats(ui_manager)
                    break
        except KeyboardInterrupt:
            print("\nCtrl-C detected during game. Exiting gracefully...")
            current_game.show_game_stats(ui_manager)
            break  # Exit the game loop

        play_again = ui_manager.centered_input("Do you want to play again? (yes/no): ").lower()
        if play_again != 'yes':
            break

if __name__ == "__main__":
    main()