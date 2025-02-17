# core/game.py
import core.events as events
import core.buildings as buildings
import core.hero as hero
import core.resources as resources
import json
import os

class StoryManager:
    def __init__(self, game):
        self.game = game
        self.story_data = self.load_story_data()
        self.triggered_chapters = set()  # Keep track of triggered chapters


    def load_story_data(self):
        filepath = os.path.join("data", "story.json")
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error story.json not found")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in story.json")
            return {}

    def check_triggers(self, ui_manager, audio_manager):
        """Checks for story triggers and displays story elements."""
        for chapter_id, chapter_data in self.story_data.items():
            if chapter_id == "intro":  # Handle intro separately
                continue

            # --- Check if chapter has already been triggered ---
            if chapter_id in self.triggered_chapters:
                continue  # Skip if already triggered

            if self.is_triggered(chapter_data["trigger"]):
                # Display story text
                for line in chapter_data["text"]:
                    ui_manager.display_message(line, "text_highlight")
                # Trigger associated event (if any)
                if "event" in chapter_data:
                    event = self.game.event_manager.get_event_by_id(chapter_data["event"])
                    if event:
                        self.game.event_manager.trigger_event(self.game, ui_manager, audio_manager, event)
                #play audio:
                if "audio_cue" in chapter_data:
                    audio_manager.play_sound(chapter_data["audio_cue"])

                # --- Mark chapter as triggered ---
                self.triggered_chapters.add(chapter_id)


    def is_triggered(self, trigger_conditions):
        """Checks if the given trigger conditions are met."""
        for condition, value in trigger_conditions.items():
            if condition == "turn":
                if self.game.turn < value:
                    return False
            elif condition == "event":
                if not self.game.event_manager.is_event_triggered(value):
                    return False
            elif condition == "building":
                building_type = value
                required_count = trigger_conditions.get("count", 1)  # Default to 1

                if building_type not in self.game.buildings:
                    return False

                if len(self.game.buildings[building_type]) < required_count:
                    return False
            #Removed triggered condition as not necessary.

        return True

class Game:
    def __init__(self, player_name, config):
        self.player_name = player_name
        self.config = config
        self.turn = 0  # Initialize turn
        self.resources = {
            "wood": resources.Resource("wood", self.config["starting_resources"]["wood"]),
            "stone": resources.Resource("stone", self.config["starting_resources"]["stone"]),
            "food": resources.Resource("food", self.config["starting_resources"]["food"])
        }
        self.people = 0
        self.victory_condition = config["victory_conditions"]["standard"]
        self.buildings = {
            "House": [],
            "Farm": [],
            "Mine": [],
            "Wonder": []
        }
        self.hero = self.load_hero()
        self.current_screen = "main"
        self.event_manager = events.EventManager()
        self.event_manager.load_events("events.json")
        self.story_manager = StoryManager(self) #create story manager


    def load_hero(self):
        """Loads the hero data from characters.json."""
        filepath = os.path.join("data", "characters.json")
        try:
            with open(filepath, 'r') as f:
                characters_data = json.load(f)
                for char_id, char_data in characters_data.items():
                    if char_data.get("hero") == True:  # Check for the "hero" flag
                        return hero.Hero(name=char_data["name"], hero_class=char_data["hero_class"])
                print("Error: No hero found in characters.json.")
                return hero.Hero()  # Return a default hero if none is found
        except FileNotFoundError:
            print(f"Error characters.json not found")
            return hero.Hero() # Return a default hero
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in characters.json")
            return hero.Hero() #return a default hero
        except KeyError as e:
            print(f"KeyError {e} in characters.json")
            return hero.Hero() #failsafe

    def build_building(self, building_type, ui_manager, audio_manager):
        """Builds a new building of the specified type."""
        if building_type not in self.buildings:
            ui_manager.display_message("Invalid building type!", "text_warning")
            return  # Early exit

        new_building = None
        if building_type == "House":
            new_building = buildings.House()
        elif building_type == "Farm":
            new_building = buildings.Farm()
        elif building_type == "Mine":
            new_building = buildings.Mine()
        elif building_type == "Wonder":
            new_building = buildings.Wonder()

        if new_building is None: #failsafe if building is still none
            return

        cost = new_building.get_cost()
        if all(self.resources[res].can_afford(amt) for res, amt in cost.items()):
            for res, amt in cost.items():
                self.resources[res].remove(amt)
            self.buildings[building_type].append(new_building)
            ui_manager.display_message(f"Built a new {new_building.name}!", "text_success")
            audio_manager.play_sound("build.wav")
        else:
            ui_manager.display_message("Not enough resources!", "text_warning")

    def upgrade_building(self, building_type, ui_manager, audio_manager):
      """Upgrades the first building of the specified type (simplified)."""

      if building_type not in self.buildings:
          ui_manager.display_message("Invalid building type!", "text_warning")
          return #early exit

      if not self.buildings[building_type]:
        ui_manager.display_message(f"No {building_type} to upgrade!", "text_warning")
        return #early exit

      building_to_upgrade = self.buildings[building_type][0]  # Simplification: Upgrade the *first* building of that type

      if not building_to_upgrade.can_upgrade():
        ui_manager.display_message(f"{building_to_upgrade.name} is already at max level!", "text_warning")
        return #early exit

      upgrade_cost = building_to_upgrade.get_upgrade_cost()
      if all(self.resources[res].can_afford(amt) for res, amt in upgrade_cost.items()):
          for res, amt in upgrade_cost.items():
              self.resources[res].remove(amt)
          building_to_upgrade.upgrade()
          ui_manager.display_message(f"{building_to_upgrade.building_type} upgraded to {building_to_upgrade.name} (level {building_to_upgrade.level})!", "text_success")
          audio_manager.play_sound("upgrade.wav")
      else:
          ui_manager.display_message("Not enough resources to upgrade!", "text_warning")

    def collect_resources(self, ui_manager):
        """Collects resources from all buildings."""
        for building_list in self.buildings.values():
            for building in building_list:
                production = building.get_production()
                for resource, amount in production.items():
                    self.resources[resource].add(amount)
        ui_manager.display_message("Resources collected!", "text_success") #message only 1

    def check_victory(self):
        """Checks for standard and wonder victory conditions."""
        # Standard Victory
        if all(self.resources[res].amount >= self.victory_condition[res] for res in ["wood", "stone", "food"]) and self.people >= self.victory_condition['people']:
            return True

        # Wonder Victory
        for wonder in self.buildings.get("Wonder", []):  # Safely get the list
            if wonder.name == "Obelisk": #check by name if you have wonder
                return True

        return False

    def show_game_stats(self, ui_manager):
        """Displays game over statistics."""
        ui_manager.display_message("Game Over!", "text_highlight")
        ui_manager.display_message(f"Turns played: {self.turn}", "text_normal")

    def play_turn(self, ui_manager, audio_manager):
      """Plays a single turn of the game."""

      # --- Main Screen ---
      if self.current_screen == "main":
          ui_manager.display_status(self)
          action = ui_manager.get_player_action(["c", "b", "h", "p", "u", "quit"])

          if action == "quit":
              confirm = ui_manager.centered_input("Are you sure you want to quit? (yes/no): ")
              if confirm in ['yes', 'y']:
                  return False  # End the game
              #If not confirmed, just continue
          elif action == "h":
              self.current_screen = "hero"
              audio_manager.play_music(self.config["audio"]["screen_music"]["hero"])
          elif action == "p":
              self.current_screen = "people"
              audio_manager.play_music(self.config["audio"]["screen_music"]["people"])
          elif action == "u":
              self.current_screen = "upgrades"
              audio_manager.play_music(self.config["audio"]["screen_music"]["upgrades"])
          elif action == "c":
              self.collect_resources(ui_manager)
              event = self.event_manager.get_random_event(self)
              self.event_manager.trigger_event(self, ui_manager, audio_manager, event)
              self.turn += 1  # Increment turn counter *only* on actions
          elif action == "b":
              building_type = ui_manager.centered_input("Build (House/Farm/Mine/Wonder, or Back): ").title()
              if building_type in ("House", "Farm", "Mine", "Wonder"):
                self.build_building(building_type, ui_manager, audio_manager)
                self.turn += 1  # Increment turn counter
              elif building_type == "Back" or building_type == "":
                pass #return to main screen
              else:
                ui_manager.display_message("Invalid building type!", "text_warning")


      # --- Hero Screen ---
      elif self.current_screen == "hero":
          ui_manager.display_hero_screen(self)
          action = ui_manager.get_player_action(["assign", "quest", "back"], allow_empty=True)
          if action == "back" or action == "":
              self.current_screen = "main"
              audio_manager.play_music(self.config["audio"]["screen_music"]["main"])
          elif action == "assign":
              building_type = ui_manager.centered_input("Assign to (House/Farm/Mine, or Back): ").title()
              if building_type in self.buildings and self.buildings[building_type]:
                    self.hero.assign_to(building_type)
                    ui_manager.display_message(f"Hero assigned to {building_type}!", "text_success")
                    audio_manager.play_sound("assign.wav")
              elif building_type == "Back" or building_type == "":
                    pass #return to hero screen
              else:
                ui_manager.display_message("Invalid building type.", "text_warning")
          elif action == "quest":
              if self.hero.available:
                  self.hero.send_on_quest()
                  ui_manager.display_message("Hero sent on a quest!", "text_success")
                  audio_manager.play_sound("quest_start.wav")
                  self.turn += 1  # Increment turn counter when sending on quest
              else:
                  ui_manager.display_message("Hero is not available.", "text_warning")

      # --- People Screen ---
      elif self.current_screen == "people":
          ui_manager.display_people_screen(self)
          action = ui_manager.get_player_action(["back"], allow_empty=True)  # Only "back" is valid
          if action == "back" or action == "":
              self.current_screen = "main"
              audio_manager.play_music(self.config["audio"]["screen_music"]["main"])

      # --- Upgrades Screen ---
      elif self.current_screen == "upgrades":
          ui_manager.display_upgrades_screen(self)
          action = ui_manager.get_player_action(["u", "back"], allow_empty=True)
          if action == "back" or action == "":
              self.current_screen = "main"
              audio_manager.play_music(self.config["audio"]["screen_music"]["main"])
          elif action == "u":
            building_type = ui_manager.centered_input("Upgrade which building type (House/Farm/Mine, or Back)? ").title()
            if building_type in ("House", "Farm", "Mine"):
                self.upgrade_building(building_type, ui_manager, audio_manager)
                self.turn += 1 # Increment turn
            elif building_type == "Back" or building_type == "":
                pass #return to upgrades screen
            else:
                ui_manager.display_message("Invalid building type!", "text_warning")

      self.story_manager.check_triggers(ui_manager, audio_manager)  # Check for story triggers
      return True  # Continue playing