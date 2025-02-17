# core/ui.py
import colorama
import json
import os

class UI:
    """Manages the user interface, including display and input."""

    def __init__(self, theme_name="default"):
        """Initializes the UI with the specified theme."""
        colorama.init(autoreset=True)  # Initialize colorama
        self.theme = self.load_theme(theme_name)


    def load_theme(self, theme_name):
        """Loads a theme from a JSON file."""
        theme_path = os.path.join("assets", "themes", f"{theme_name}.json")
        try:
            with open(theme_path, 'r', encoding='utf-8') as f:  # Add encoding='utf-8'
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Theme file not found: {theme_path}")
            # Load a fallback default theme
            return self.load_theme("default")  # Prevent infinite recursion
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in theme file: {theme_path}")
            return self.load_theme("default")
    def colorize(self, text, color_name):
        """Applies a color to the given text using the current theme."""
        color = self.theme["colors"].get(color_name)
        if color:
            # Use colorama's color names (uppercase)
            colorama_color = getattr(colorama.Fore, color.upper(), colorama.Fore.WHITE)
            return colorama_color + text
        else:
            return text

    def display_message(self, message, color="text_normal"):
        """Displays a message to the user with the specified color."""
        print(self.colorize(message, color))

    def centered_input(self, prompt):
        """Gets input from the user, centered on the screen."""
        terminal_width, _ = os.get_terminal_size()
        padding = (terminal_width - len(prompt)) // 2
        input_str = input(' ' * padding + prompt)
        return input_str

    def get_player_action(self):
        """Gets the player's next action."""
        return self.centered_input("What would you like to do? (c/b/h/p/u/quit): ").lower()

    def draw_frame(self, frame_style, width, height):
        """Draws a frame using the specified style from the theme."""

        frame_data = self.theme.get("frames", {}).get(frame_style) #get frame data
        if not frame_data:
            print("Error no frame data")
            return # Exit if no frame data of that name

        #characters for building up frame
        top_left = frame_data["top_left"]
        top_right = frame_data["top_right"]
        bottom_left = frame_data["bottom_left"]
        bottom_right = frame_data["bottom_right"]
        horizontal = frame_data["horizontal"]
        vertical = frame_data["vertical"]

        # Top border
        print(self.colorize(top_left + horizontal * (width - 2) + top_right, "border"))

        # Middle lines (empty for now, will be filled with content)
        for _ in range(height - 2):
            print(self.colorize(vertical, "border") + " " * (width - 2) + self.colorize(vertical, "border"))

        # Bottom border
        print(self.colorize(bottom_left + horizontal * (width - 2) + bottom_right, "border"))

    def display_status(self, game):
        """Displays the main game status screen."""
        width = 80 #example width and height
        height = 12
        self.draw_frame("main_screen", width, height) #draw the frame

        # Calculate the starting row for content (inside the frame)
        start_row = 2  #  lines from the top

        # Use a helper function to print lines at specific positions
        def print_at(row, col, text, color="text_normal"):
            # Calculate padding for centering based on width.
            padding = (width - len(text)) // 2
            print("\033[{};{}H{}{}".format(row, col + padding, self.colorize(text, color), colorama.Style.RESET_ALL), end="")

        print_at(start_row, 0, f"Turn: {game.turn}")
        print_at(start_row + 1, 0, f"Wood: {game.resources['wood']}") #now uses __str__
        print_at(start_row + 2, 0, f"Stone: {game.resources['stone']}")
        print_at(start_row + 3, 0, f"Food: {game.resources['food']}")
        print_at(start_row + 4, 0, f"People: {game.people}")

        # --- Display Buildings ---
        building_row = start_row + 6
        for building_type, building_list in game.buildings.items():
            building_names = [b.name for b in building_list]  # Get names
            print_at(building_row, 0, f"{building_type}: {', '.join(building_names)}")
            building_row += 1

        # --- Display Hero Availability ---
        print_at(start_row + 5, 0, f"Hero: {'Available' if game.hero.available else 'Unavailable'}",
                 "hero_available" if game.hero.available else "hero_unavailable")

        # Reset cursor to a position below the frame, so next print displays correctly.
        print(f"\033[{height + 1};0H", end="")
    def display_hero_screen(self, game):
        """Displays the hero screen."""
        width = 60
        height = 12  # Increased height for more info
        self.draw_frame("hero_screen", width, height)

        start_row = 2

        def print_at(row, col, text, color="text_normal"):
            padding = (width - len(text)) // 2
            print("\033[{};{}H{}{}".format(row, col + padding, self.colorize(text, color), colorama.Style.RESET_ALL), end="")

        print_at(start_row, 0, "Hero Screen", "text_highlight")
        print_at(start_row + 2, 0, f"Name: {game.hero.name}", "text_normal")
        print_at(start_row + 3, 0, f"Class: {game.hero.hero_class}", "text_normal")  # Display class
        print_at(start_row + 4, 0, f"Level: {game.hero.level}", "text_normal") #display level
        print_at(start_row + 5, 0, game.hero.get_class_bonus(), "text_normal") #display bonus
        print_at(start_row + 6, 0, f"Status: {'Available' if game.hero.available else 'Unavailable'}", "text_normal")
        if game.hero.assigned_to:
            print_at(start_row + 7, 0, f"Assigned to: {game.hero.assigned_to}", "text_normal")
        if game.hero.on_quest:
            print_at(start_row + 7, 0, "On a quest!", "text_normal")

        print_at(start_row + 9, 0, "Actions: assign, quest, back", "text_normal")
        print(f"\033[{height + 1};0H", end="")  # Move cursor below frame


    def display_people_screen(self, game):
        """Displays the people management screen."""
        width = 60
        height = 8
        self.draw_frame("people_screen", width, height)
        start_row = 2
        def print_at(row, col, text, color="text_normal"):
            padding = (width - len(text)) // 2
            print("\033[{};{}H{}{}".format(row, col + padding, self.colorize(text, color), colorama.Style.RESET_ALL), end="")

        print_at(start_row, 0, "People Screen", "text_highlight")
        print_at(start_row + 2, 0, "No people management implemented yet.", "text_normal")
        print_at(start_row + 4, 0, "Press 'back' to return to the main screen.", "text_normal")
        print(f"\033[{height+1};0H", end="")



    def display_upgrades_screen(self, game):
        """Displays the building upgrades screen."""
        width = 60
        height = 12

        self.draw_frame("upgrades_screen", width, height)
        start_row = 2
        def print_at(row, col, text, color="text_normal"):
            padding = (width- len(text)) // 2
            print("\033[{};{}H{}{}".format(row, col + padding, self.colorize(text,color), colorama.Style.RESET_ALL), end="")

        print_at(start_row, 0, "Upgrades Screen", "text_highlight")
        if not any(game.buildings.values()):  # Check if any buildings exist at all
            print_at(start_row + 2, 0, "No buildings to upgrade yet.", "text_normal")
        else:
            building_row = start_row + 2
            for building_type, building_list in game.buildings.items():
                for building in building_list:
                    if building.can_upgrade():
                        upgrade_cost = building.get_upgrade_cost()
                        cost_str = ", ".join(f"{res}: {amt}" for res, amt in upgrade_cost.items())
                        print_at(building_row, 0, f"{building.name} (Level {building.level}) - Upgrade Cost: {cost_str}", "text_normal")
                    else:
                        print_at(building_row, 0, f"{building.name} (Level {building.level}) - Max Level", "text_normal")
                    building_row += 1
        print_at(start_row + 4, 0, "Press 'b' to build, 'u' to upgrade or 'back' to return to the main screen.", "text_normal")
        print(f"\033[{height+1};0H", end="") #put cursor to correct place