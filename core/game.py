# core/game.py
import core.events as events
import core.buildings as buildings
import core.hero as hero
import core.resources as resources
import core.people as people
import json
import os
import random

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
        self.turn = 0
        self.resources = {
            "wood": resources.Resource("wood", self.config["starting_resources"]["wood"], self.config["max_amounts"]["wood"]),
            "stone": resources.Resource("stone", self.config["starting_resources"]["stone"], self.config["max_amounts"]["stone"]),
            "food": resources.Resource("food", self.config["starting_resources"]["food"], self.config["max_amounts"]["food"])
        }
        self.people = []  # Store Person objects
        self.total_people = 0
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
        self.story_manager = StoryManager(self)
        # --- People Manager ---
        self.people_manager = people.PeopleManager()  # Create a PeopleManager


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
            return

        if building_type == "House":
            new_building = buildings.House()
        elif building_type == "Farm":
            new_building = buildings.Farm()
        elif building_type == "Mine":
            new_building = buildings.Mine()
        elif building_type == "Wonder":
            new_building = buildings.Wonder()
        else:
            ui_manager.display_message("Invalid building type!", "text_warning")
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
            return

        if not self.buildings[building_type]:
            ui_manager.display_message(f"No {building_type} to upgrade!", "text_warning")
            return

        building_to_upgrade = self.buildings[building_type][0]

        if not building_to_upgrade.can_upgrade():
            ui_manager.display_message(f"{building_to_upgrade.name} is already at max level!", "text_warning")
            return

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
        for building_list in self.buildings.values():
            for building in building_list:
                production = building.get_production()
                # --- Get bonuses from assigned people ---
                for person in building.assigned_people:
                    # Get the building-specific bonuses from the person
                    building_bonuses = person.bonuses.get(building.building_type, {})
                    # Iterate through the resources in *that* bonus dictionary
                    for resource, bonus_amount in building_bonuses.items():
                        production[resource] = production.get(resource, 0) + bonus_amount #add bonuses

                for resource, amount in production.items():
                    self.resources[resource].add(amount)
        ui_manager.display_message("Resources collected!", "text_success")


    def check_victory(self):
        """Checks for standard and wonder victory conditions."""
        # Standard Victory
        if all(self.resources[res].amount >= self.victory_condition[res] for res in ["wood", "stone", "food"]) and self.total_people >= self.victory_condition['people']:
            return True

        # Wonder Victory
        for wonder in self.buildings.get("Wonder", []):
            if wonder.name == "Obelisk":
                return True

        return False

    def show_game_stats(self, ui_manager):
        """Displays game over statistics."""
        ui_manager.display_message("Game Over!", "text_highlight")
        ui_manager.display_message(f"Turns played: {self.turn}", "text_normal")

    def add_person(self, ui_manager):
        base_probability = 0.15
        building_bonus = 0.01 * sum(len(buildings) for buildings in self.buildings.values())
        total_probability = base_probability + building_bonus

        if random.random() < total_probability:
            # --- Choose a person class (data-driven) ---
            available_classes = self.people_manager.get_available_classes()
            if available_classes:
                new_person_class_id = random.choice(available_classes) #choose class id
                new_person = self.people_manager.create_person(new_person_class_id)  # Create a Person instance
                if new_person:
                    self.people.append(new_person)
                    self.total_people += 1
                    ui_manager.display_message(f"A new {new_person.person_class} has arrived!", "text_success")
            else: #failsafe
                print("Error: no people classes defined") #should not happen
                new_person = people.Person("Citizen")
                self.people.append(new_person)
                self.total_people += 1
                ui_manager.display_message(f"A new {new_person.person_class} has arrived!", "text_success")

    def assign_person(self, building_type, person, ui_manager):
        """Assigns a person to a building."""
        if building_type not in self.buildings:
            ui_manager.display_message("Invalid building type!", "text_warning")
            return False

        if not self.buildings[building_type]:
            ui_manager.display_message(f"No {building_type} buildings exist!", "text_warning")
            return False

        # Find an available building of the specified type
        available_building = None
        for building in self.buildings[building_type]:
            if building.can_assign_person():
                available_building = building
                break

        if available_building:
            if available_building.assign_person(person):
                ui_manager.display_message(f"{person.person_class} assigned to {available_building.name}!", "text_success")
                return True
            else:
                ui_manager.display_message(f"Could not assign {person.person_class} to {available_building.name} - building full!", "text_warning")
                return False
        else:
            ui_manager.display_message(f"No {building_type} buildings with available space!", "text_warning")
            return False

    def unassign_person(self, building_type, person, ui_manager):
        """Unassign a person"""
        if building_type not in self.buildings:
            ui_manager.display_message("Invalid building type!", "text_warning")
            return False # Fail, if invalid building type

        if not self.buildings[building_type]:
            ui_manager.display_message(f"No {building_type} buildings exist!", "text_warning")
            return False # Fail, if no building

        for building in self.buildings[building_type]:
            if building.unassign_person(person):
                ui_manager.display_message(f"Unassigned {person} from {building.name}", "text_success")
                return True #success

        #if we are here, there is no such person assigned
        ui_manager.display_message(f"No {person} assigned to {building_type}!", "text_warning")
        return False # Fail, If no such person assigned to this type of building

    def get_unassigned_people(self):
        """Returns a list of people who are not assigned to any building."""
        assigned_people = []
        for building_list in self.buildings.values():  # Iterate through building lists
            for building in building_list:             # Iterate through buildings
                assigned_people.extend(building.assigned_people) # Get assigned people

        unassigned_people = [person for person in self.people if person not in assigned_people]
        return unassigned_people

    def play_turn(self, ui_manager, audio_manager):
        """Plays a single turn of the game."""

        if self.current_screen == "main":
            ui_manager.display_status(self)
            action = ui_manager.get_player_action(["c", "b", "h", "p", "u", "quit"])

            if action == "quit":
                confirm = ui_manager.centered_input("Are you sure you want to quit? (yes/no): ")
                if confirm in ['yes', 'y']:
                    return False
            elif action == "h":
                self.current_screen = "hero"
                audio_manager.play_music(self.config["audio"]["screen_music"]["hero"])
            elif action == "p":
                self.current_screen = "people"
                audio_manager.play_music(self.config["audio"]["screen_music"]["people"])
            elif action == "u":
                self.current_screen = "upgrades"
                audio_manager.play_music(self.config["audio"]["screen_music"]["upgrades"])
            elif action == 'c':
                self.collect_resources(ui_manager)
                event = self.event_manager.get_random_event(self)
                self.event_manager.trigger_event(self, ui_manager, audio_manager, event)
                self.add_person(ui_manager)
                self.turn += 1
            elif action == 'b':
                building_type = ui_manager.centered_input("Build (House/Farm/Mine/Wonder, or Back): ").title()
                if building_type in ("House", "Farm", "Mine", "Wonder"):
                    self.build_building(building_type, ui_manager, audio_manager)
                    self.turn += 1
                elif building_type == "Back" or building_type == "":
                    pass
                else:
                    ui_manager.display_message("Invalid building type!", "text_warning")

            elif action == 'u':
                building_type = ui_manager.centered_input("Upgrade which building type (House/Farm/Mine, or Back)? ").title()
                if building_type in ("House", "Farm", "Mine"):
                  self.upgrade_building(building_type, ui_manager, audio_manager)
                  self.turn += 1
                elif building_type == "Back" or building_type == "":
                    pass #return to upgrades screen

                else:
                  ui_manager.display_message("Invalid building type!", "text_warning")
            else:
                ui_manager.display_message("Invalid action.", "text_warning")


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
                    pass
                else:
                    ui_manager.display_message("Invalid building type.", "text_warning")
            elif action == "quest":
                if self.hero.available:
                    self.hero.send_on_quest()
                    ui_manager.display_message("Hero sent on a quest!", "text_success")
                    audio_manager.play_sound("quest_start.wav")
                    self.turn += 1  # Increment turn counter
                else:
                    ui_manager.display_message("Hero is not available.", "text_warning")

        elif self.current_screen == "people":
            self.handle_people_screen(ui_manager, audio_manager) # Refactored people screen


        elif self.current_screen == "upgrades":
            ui_manager.display_upgrades_screen(self)
            action = ui_manager.get_player_action(["u", "back"], allow_empty=True)
            if action == "back" or action == "":
                self.current_screen = "main"
                audio_manager.play_music(self.config["audio"]["screen_music"]["main"])
            elif action == 'u':
                building_type = ui_manager.centered_input("Upgrade which building type (House/Farm/Mine, or Back)? ").title()
                if building_type in ("House", "Farm", "Mine"):
                  self.upgrade_building(building_type, ui_manager, audio_manager)
                  self.turn += 1
                elif building_type == "Back" or building_type == "":
                    pass
                else:
                  ui_manager.display_message("Invalid building type!", "text_warning")
        self.story_manager.check_triggers(ui_manager, audio_manager)
        return True

    def handle_people_screen(self, ui_manager, audio_manager):
        """Handles the people management screen logic."""

        self.current_screen = "people"
        audio_manager.play_music(self.config["audio"]["screen_music"]["people"])
        ui_manager.display_people_screen(self) #display

        while self.current_screen == "people":
            action = ui_manager.get_player_action(["assign", "unassign", "back"], allow_empty=True)

            if action == "back" or action == "":
                self.current_screen = "main"
                audio_manager.play_music(self.config["audio"]["screen_music"]["main"])
                return  # Exit the people management loop

            elif action == "assign":
                self.handle_assign_people(ui_manager)

            elif action == "unassign":
                self.handle_unassign_people(ui_manager)

    def handle_assign_people(self, ui_manager):
      """Handles the 'assign' action on the people screen."""

      unassigned_people = self.get_unassigned_people()
      if not unassigned_people:
          ui_manager.display_message("No unassigned people available.", "text_warning")
          return

      # Display available people
      ui_manager.display_message("Unassigned People:", "text_highlight")
      for i, person in enumerate(unassigned_people):
          ui_manager.display_message(f"{i + 1}. {person.person_class}")

      # Get person selection
      while True: #input loop
        try:
          person_index = ui_manager.centered_input("Select person to assign (or Back): ")
          if person_index.lower() == "back" or person_index == "":
            return #exit
          person_index = int(person_index) - 1  # Adjust for 0-indexing
          if 0 <= person_index < len(unassigned_people):
              selected_person = unassigned_people[person_index]
              break #if correct, break input loop
          else:
              ui_manager.display_message("Invalid person selection.", "text_warning")
        except ValueError:
          ui_manager.display_message("Invalid input. Please enter a number.", "text_warning")


      # Get building type selection
      while True: #input loop for building
        building_type = ui_manager.centered_input("Assign to building type (House/Farm/Mine, or Back): ").title()
        if building_type in self.buildings:
            if self.assign_person(building_type, selected_person, ui_manager):
                break  # Exit on successful assignment
        elif building_type == "Back" or building_type == "":
            return  # Go back to the people screen main menu
        else:
            ui_manager.display_message("Invalid building type.", "text_warning")

    def handle_unassign_people(self, ui_manager):
      """Handles the 'unassign' action on the people screen."""
      # Display assigned people with building info
      ui_manager.display_message("Assigned People:", "text_highlight")

      #create list of assigned people to select:
      assigned_people_list = []
      for building_type, building_list in self.buildings.items():
            for building in building_list:
                for i, person in enumerate(building.assigned_people):
                    assigned_people_list.append((person, building, building_type)) #tuple of necessary data

      if not assigned_people_list:
            ui_manager.display_message("No people are currently assigned.", "text_warning")
            return #exit if no assigned people

      for i, (person, building, building_type) in enumerate(assigned_people_list):
          ui_manager.display_message(f"{i + 1}. {person.person_class} (in {building.name} - {building_type})")

      # Get person selection
      while True: #input loop
        try:
          person_index = ui_manager.centered_input("Select person to unassign (or Back): ")
          if person_index.lower() == "back" or person_index == "":
                return
          person_index = int(person_index) - 1

          if 0 <= person_index < len(assigned_people_list):
                selected_person, selected_building, selected_building_type = assigned_people_list[person_index]
                if self.unassign_person(selected_building_type, selected_person, ui_manager):
                    break # Success
          else:
              ui_manager.display_message("Invalid person selection.", "text_warning")

        except ValueError:
          ui_manager.display_message("Invalid input, enter a number", "text_warning")