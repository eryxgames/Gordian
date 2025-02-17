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
        self.max_log_entries = 5  # Number of events to show in the log
        self.event_log = []  # Initialize an empty event log



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
        """Displays a message to the user, adding it to the event log."""
        self.event_log.append(message)
        if len(self.event_log) > self.max_log_entries:
            self.event_log.pop(0)  # Remove oldest entry if log is full
        #  don't print the message here, but in the main display

    def centered_input(self, prompt):
        """Gets input from the user, centered on the screen."""
        terminal_width, _ = os.get_terminal_size()
        padding = (terminal_width - len(prompt)) // 2
        input_str = input(' ' * padding + prompt)
        return input_str

    def get_player_action(self):
        """Gets the player's next action."""
        return self.centered_input("Action (c/b/h/p/u/quit): ").lower()


    def display_status(self, game):
      """Displays the main game status screen (compact design)."""
      terminal_width, _ = os.get_terminal_size()

      # --- Resource Display (Horizontal) ---
      resource_str = " | ".join([
          f"{self.colorize('W', 'resource_wood')}:{game.resources['wood']}",
          f"{self.colorize('S', 'resource_stone')}:{game.resources['stone']}",
          f"{self.colorize('F', 'resource_food')}:{game.resources['food']}",
          f"{self.colorize('P', 'text_normal')}:{game.people}"
      ])
      # Center the resource string
      resource_str = resource_str.center(terminal_width)
      print(resource_str)


      # --- Building Display (Horizontal, Abbreviations) ---
      building_str = ""
      for building_type, building_list in game.buildings.items():
          if building_list:  # Only show if there are buildings of this type
                #get building symbol or first letter from theme, or use default
                symbol = self.theme["symbols"].get(building_type, building_type[0]).upper()
                #color = self.theme["colors"].get(f"building_{building_type.lower()}", "text_normal") #get color from theme
                building_str += f"{self.colorize(symbol, f'building_{building_type.lower()}')}:{len(building_list)} "
      building_str = building_str.center(terminal_width)
      print(building_str)


      # --- Hero Status (Horizontal) ---
      hero_status = f"Hero: {'Avl' if game.hero.available else 'Unavl'}"
      if game.hero.assigned_to:
        hero_status += f" @ {game.hero.assigned_to}"
      elif game.hero.on_quest:
        hero_status += " (Quest)"

      hero_status = hero_status.center(terminal_width)
      print(hero_status)
      # --- Turn Number (Horizontal) ---
      print(f"Turn: {game.turn}".center(terminal_width))

      # --- Event Log (Scrolling) ---
      print("-" * terminal_width)  # Separator line
      for message in self.event_log:
          # Wrap long messages to fit the terminal width
          wrapped_message = self.wrap_text(message, terminal_width - 4)  # Leave some margin
          for line in wrapped_message:
              print("  " + line)  # Indent the log entries
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
        print("\n--- Hero Screen ---")
        print(f"Name: {game.hero.name}")
        print(f"Class: {game.hero.hero_class}")
        print(f"Level: {game.hero.level}")
        print(game.hero.get_class_bonus())
        print(f"Status: {'Available' if game.hero.available else 'Unavailable'}")
        if game.hero.assigned_to:
            print(f"Assigned to: {game.hero.assigned_to}")
        if game.hero.on_quest:
            print("On a quest!")

        print("Actions: assign, quest, back")


    def display_people_screen(self, game):
        """Displays the people management screen."""
        print("\n--- People Screen ---")
        print("No people management implemented yet.")
        print("Press 'back' to return to the main screen.")



    def display_upgrades_screen(self, game):
        """Displays the building upgrades screen."""
        print("\n--- Upgrades Screen ---")
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
            print("Press 'b' to build, 'u' to upgrade or 'back' to return to the main screen.")

    def display_logo(self, logo_lines):
        """Displays the ASCII art logo, centered."""
        terminal_width, _ = os.get_terminal_size()
        for line in logo_lines:
            print(line.center(terminal_width))