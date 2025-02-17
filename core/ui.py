# core/ui.py
import colorama
import json
import os

class UI:
    """Manages the user interface."""

    def __init__(self, theme_name="default"):
        colorama.init(autoreset=True)
        self.theme = self.load_theme(theme_name)
        self.max_log_entries = 5
        self.event_log = []

    def load_theme(self, theme_name):
        theme_path = os.path.join("assets", "themes", f"{theme_name}.json")
        try:
            with open(theme_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading theme: {e}")
            return self.default_theme()

    def default_theme(self):
        return {
            "colors": {
                "text_normal": "white", "text_highlight": "yellow",
                "text_warning": "red", "text_success": "green",
                "background": "black", "border": "lightgray",
                "resource_wood": "brown", "resource_stone": "gray",
                "resource_food": "green", "building_house": "cyan",
                "building_farm": "green", "building_mine": "gray",
                "hero_available": "green", "hero_unavailable": "red"
            },
            "symbols": {"wood": "W", "stone": "S", "food": "F",
                        "House": "H", "Farm": "F", "Mine": "M", "Wonder":"W"}
        }

    def colorize(self, text, color_name):
        color = self.theme["colors"].get(color_name, "white")
        colorama_color = getattr(colorama.Fore, color.upper(), colorama.Fore.WHITE)
        return colorama_color + text

    def display_message(self, message, color="text_normal"):
        self.event_log.append(message)
        if len(self.event_log) > self.max_log_entries:
            self.event_log.pop(0)

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def centered_input(self, prompt):
        terminal_width, _ = os.get_terminal_size()
        padding = (terminal_width - len(prompt)) // 2
        result = input(' ' * padding + prompt)
        return result.strip().lower()

    def get_player_action(self, valid_actions, allow_empty=False):
        while True:
            action = self.centered_input("Action: ").lower()
            if action in valid_actions:
                return action
            elif allow_empty and action == "":
                return "back"
            else:
                self.display_message("Invalid action.", "text_warning")

    def display_status(self, game):
        self.clear_screen()
        self.display_top_bar(game)  # Combined title, turn, and resources
        self.display_buildings_and_people(game) # Combined buildings and people
        self.display_event_log()
        print("Actions: (C)ollect, (B)uild, (H)ero, (P)eople, (U)pgrades, (Q)uit")

    def display_top_bar(self, game):
        """Displays the top bar with title, turn, and resources."""
        terminal_width, _ = os.get_terminal_size()

        # --- Title and Turn ---
        title_str = self.colorize("GORDIAN", "text_highlight")
        turn_str = f"Turn: {game.turn}"
        title_turn = f"{title_str}  {turn_str}"

        # --- Resources ---
        resource_str = " | ".join([
            f"{self.colorize(self.theme['symbols'].get('food', 'F'), 'resource_food')}: {game.resources['food'].amount}",
            f"{self.colorize(self.theme['symbols'].get('wood', 'W'), 'resource_wood')}: {game.resources['wood'].amount}",
            f"{self.colorize(self.theme['symbols'].get('stone', 'S'), 'resource_stone')}: {game.resources['stone'].amount}",
        ])
        # --- Combine and Center ---
        combined_str = title_turn.ljust(30) + resource_str.rjust(terminal_width-30) #adjust space for title and turn
        print(combined_str)
        print("-" * terminal_width)

    def display_buildings_and_people(self, game):
        """Displays buildings, people, and hero status concisely."""
        terminal_width, _ = os.get_terminal_size()

        # --- People and Hero ---
        people_str = f"People: {game.people}"
        hero_str = f"Hero: {'Avl' if game.hero.available else 'Unavl'}"
        if game.hero.assigned_to:
            hero_str += f" ({game.hero.assigned_to})"
        elif game.hero.on_quest:
            hero_str += " (Quest)"

        people_hero_str = f"{people_str}  |  {hero_str}"

        # --- Buildings ---
        building_strs = []
        for building_type, building_list in game.buildings.items():
            if building_list:
                symbol = self.theme["symbols"].get(building_type, building_type[0]).upper()
                building_strs.append(f"{symbol}:{len(building_list)}")
        buildings_str = "  ".join(building_strs)

        # --- Combine and Center ---, put strings on their lines
        print(people_hero_str.center(terminal_width))
        print(f"Structures: {buildings_str}".center(terminal_width))
        print("-" * terminal_width)

    def display_event_log(self):
        """Displays the event log."""
        terminal_width, _ = os.get_terminal_size()
        print(self.colorize("--- Events ---", "text_highlight"))
        for message in self.event_log:
            for line in self.wrap_text(message, terminal_width - 4):
                print("  " + line)  # Indent
        print("-" * terminal_width)

    def wrap_text(self, text, width):
        """Wraps text to the specified width."""
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= width:
                current_line += (" " if current_line else "") + word
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def display_hero_screen(self, game):
        """Displays the hero screen."""
        self.clear_screen()
        print(self.colorize("--- Hero Screen ---", "text_highlight"))
        print(f"Name: {game.hero.name}")
        print(f"Class: {game.hero.hero_class}")
        print(f"Level: {game.hero.level}")
        print(game.hero.get_class_bonus())
        print(f"Status: {'Available' if game.hero.available else 'Unavailable'}")
        if game.hero.assigned_to:
            print(f"Assigned to: {game.hero.assigned_to}")
        if game.hero.on_quest:
            print("On a quest!")
        print("\nActions: (Assign), (Quest), (Back)")

    def display_people_screen(self, game):
        """Displays the people management screen."""
        self.clear_screen()
        print(self.colorize("--- People Screen ---", "text_highlight"))
        print("No people management implemented yet.")
        print("Press 'Enter' or type 'back' to return to the main screen.")

    def display_upgrades_screen(self, game):
        """Displays the building upgrades screen."""
        self.clear_screen()
        print(self.colorize("--- Upgrades Screen ---", "text_highlight"))
        if not any(game.buildings.values()):
            print("No buildings to upgrade yet.")
        else:
            for building_type, building_list in game.buildings.items():
                for building in building_list:
                    if building.can_upgrade():
                        upgrade_cost = building.get_upgrade_cost()
                        cost_str = ", ".join(f"{res}: {amt}" for res, amt in upgrade_cost.items())
                        print(f"{building.name} (Level {building.level}) - Upgrade Cost: {cost_str}")
                    else:
                        print(f"{building.name} (Level {building.level}) - Max Level")
        print("\nPress 'u' to select building to upgrade, or 'back' to return")


    def display_logo(self, logo_lines):
        """Displays the ASCII art logo, centered."""
        terminal_width, _ = os.get_terminal_size()
        for line in logo_lines:
            print(line.center(terminal_width))