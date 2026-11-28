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
        # --- NEW: Store last message for display on People screen ---
        self.last_message = None
        self.last_message_color = "text_normal"

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
        # --- Modified: Store message and color ---
        self.last_message = message
        self.last_message_color = color
        self.event_log.append(message)  # Keep the event log
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

    def display_top_bar(self, game):
        """Displays the top bar with title, turn, and resources."""
        terminal_width, _ = os.get_terminal_size()

        title_str = self.colorize("GORDIAN", "text_highlight")
        turn_str = f"Turn: {game.turn}"
        title_turn = f"{title_str}  {turn_str}"

        resource_str = " | ".join([
            f"{self.colorize(self.theme['symbols'].get('food', 'F'), 'resource_food')}: {game.resources['food'].amount}",
            f"{self.colorize(self.theme['symbols'].get('wood', 'W'), 'resource_wood')}: {game.resources['wood'].amount}",
            f"{self.colorize(self.theme['symbols'].get('stone', 'S'), 'resource_stone')}: {game.resources['stone'].amount}",
        ])

        combined_str = title_turn.ljust(30) + resource_str.rjust(terminal_width - 30)
        print(combined_str)
        print("-" * terminal_width)

    def display_status(self, game):
        """Displays the main game status screen."""
        self.clear_screen()
        self.display_top_bar(game)
        self.display_buildings_and_people(game)
        self.display_event_log()
        print("Actions: (C)ollect, (B)uild, (H)ero, (P)eople, (U)pgrades, (Q)uit")

    def display_buildings_and_people(self, game):
        """Displays buildings, people, and hero status concisely."""
        terminal_width, _ = os.get_terminal_size()

        people_str = f"People: {game.total_people}"
        hero_str = f"Hero: {'Avl' if game.hero.available else 'Unavl'}"
        if game.hero.assigned_to:
            hero_str += f" ({game.hero.assigned_to})"
        elif game.hero.on_quest:
            hero_str += " (Quest)"

        people_hero_str = f"{people_str}  |  {hero_str}"

        building_strs = []
        for building_type, building_list in game.buildings.items():
            if building_list:
                symbol = self.theme["symbols"].get(building_type, building_type[0]).upper()
                building_strs.append(f"{symbol}:{len(building_list)}")
        buildings_str = "  ".join(building_strs)

        print(people_hero_str.center(terminal_width))
        print(f"Structures: {buildings_str}".center(terminal_width))
        print("-" * terminal_width)

    def display_event_log(self):
        """Displays the event log."""
        terminal_width, _ = os.get_terminal_size()
        print(self.colorize("--- Events ---", "text_highlight"))
        for message in self.event_log:
            for line in self.wrap_text(message, terminal_width - 4):
                print("  " + line)
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
        self.display_top_bar(game)
        print(self.colorize("--- Hero Details ---", "text_highlight"))
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
        """Displays the people management screen with improved formatting."""
        self.clear_screen()
        self.display_top_bar(game)
        print(self.colorize("--- People Management ---", "text_highlight"))

        # --- Unassigned People ---
        unassigned_people = game.get_unassigned_people()
        print(self.colorize("\nUnassigned People:", "text_normal"))
        if unassigned_people:
            for i, person in enumerate(unassigned_people):
                print(f"  {i + 1}. {person.person_class}")
        else:
            print("  None")

        # --- Assigned People (Consolidated by Building Type and Level) ---
        print(self.colorize("\nAssigned People:", "text_normal"))

        building_info = {}  # Dictionary to store building info

        for building_type, building_list in game.buildings.items():
            if building_list:
                for building in building_list:
                    # Create a key that combines building type and level
                    key = (building.building_type, building.level)
                    if key not in building_info:
                        # Initialize entry: count, capacity, people
                        building_info[key] = {
                            'count': 0,
                            'capacity': 0,
                            'people': {}  # Dictionary to store people by class
                        }
                    building_info[key]['count'] += 1
                    building_info[key]['capacity'] += building.get_capacity()

                    # Count assigned people by class
                    for person in building.assigned_people:
                        person_class = person.person_class
                        if person_class not in building_info[key]['people']:
                            building_info[key]['people'][person_class] = 0
                        building_info[key]['people'][person_class] += 1


        # Now, display the collected building information
        for (building_type, level), info in building_info.items():
            # Example: "House (Level 1): 3/15"  (3 houses, capacity 15)
            building_str = f"  {building_type} (Level {level}): {info['count']}x"
            #calculate capacity used / capacity total, f.e. 5/12
            people_count = sum(info['people'].values())
            capacity_str = f" | {people_count}/{info['capacity']}"

            print(building_str + capacity_str) #print

            # Print assigned people per class, indented
            if info['people']:
                for person_class, count in info['people'].items():
                    print(f"    - {count} {person_class}")
            else:
                print("    - None")


        # --- Display Last Message ---
        if self.last_message:
            print("\n" + self.colorize(self.last_message, self.last_message_color))
            self.last_message = None  # Clear the message after displaying
            self.last_message_color = "text_normal"

        print("\nActions: (Assign), (Unassign), (Back)")


    def display_upgrades_screen(self, game):
        """Displays the building upgrades screen."""
        self.clear_screen()
        self.display_top_bar(game)
        print(self.colorize("--- Building Upgrades ---", "text_highlight"))
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