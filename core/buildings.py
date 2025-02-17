# core/buildings.py
import json
import os

class Building:
    """Base class for all buildings."""

    def __init__(self, name, level=1):
        self.name = name  # "Hut", "Cottage", "House", etc.
        self.level = level
        self.building_type = self._get_building_type()  # "House", "Farm", "Mine", "Wonder"
        self.data = self._load_data()
        self.max_level = len(self.data["levels"]) # Dynamically set max level

    def _get_building_type(self):
        """Determines the base building type (House, Farm, Mine)."""
        # Assumes names follow a pattern:  "Hut" -> "House", "Farmstead" -> "Farm"
        for type_name in ["House", "Farm", "Mine", "Wonder"]:
            if type_name.lower() in self.name.lower():
                return type_name
        return "Unknown"  # Should not happen if names are consistent

    def _load_data(self):
        """Loads building data from buildings.json."""
        filepath = os.path.join("data", "buildings.json")
        try:
            with open(filepath, 'r') as f:
                all_buildings_data = json.load(f)
                # Find the correct building data based on name
                for building_data in all_buildings_data:
                    if building_data["name"] == self.name:
                        return building_data
                print(f"Error: Building data not found for: {self.name}")
                return {}
        except FileNotFoundError:
            print(f"Error: buildings.json not found.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in buildings.json")
            return {}

    def get_cost(self):
        """Returns the cost of the building at its current level."""
        return self.data["levels"].get(str(self.level), {}).get("cost", {})

    def get_production(self):
        """Returns the production of the building at its current level."""
        return self.data["levels"].get(str(self.level), {}).get("production", {})

    def get_capacity(self):
        """Returns the capacity of the building."""
        return self.data["levels"].get(str(self.level), {}).get("capacity", 0)

    def can_upgrade(self):
        """Checks if the building can be upgraded further."""
        return self.level < self.max_level

    def get_upgrade_cost(self):
        """Returns the cost to upgrade to the next level."""
        if self.can_upgrade():
            return self.data["levels"].get(str(self.level + 1), {}).get("cost", {})
        return {}

    def get_next_level_name(self):
        """Gets the name of the building at the next level."""
        if self.can_upgrade():
            next_level = self.level + 1
            for building_data in self._load_all_building_data():
                if (building_data.get("building_type") == self.building_type and
                    str(next_level) in building_data.get("levels", {})):
                    return building_data["name"]
        return None


    def upgrade(self):
        """Upgrades the building to the next level."""
        if self.can_upgrade():
            next_level_name = self.get_next_level_name()
            if next_level_name:
                 self.level += 1
                 self.name = next_level_name  # Update the building's name
                 self.data = self._load_data()  # Reload data for the new level/name
                 print(f"{self.building_type} upgraded to {self.name} (level {self.level})!") #more detailed message
            else:
                print(f"Error during upgrading {self.building_type}")
        else:
            print(f"Cannot upgrade {self.name} further!")

    def _load_all_building_data(self):
        """Helper function to load all building data for get_next_level_name"""
        filepath = os.path.join("data", "buildings.json")
        with open(filepath, 'r') as f:
            return json.load(f)

class House(Building):
      def __init__(self, level=1):
        # Find the correct starting name based on level
        building_data = self._load_all_building_data()
        initial_name = None
        for building in building_data:
            if building["building_type"] == "House" and str(level) in building["levels"]:
                initial_name = building["name"]
                break
        if initial_name is None:
            print ("Error initialising House") #should not happen
            initial_name = "Hut" #failsafe
        super().__init__(initial_name, level)
class Farm(Building):
    def __init__(self, level=1):
        building_data = self._load_all_building_data()
        initial_name = None
        for building in building_data:
            if building["building_type"] == "Farm" and str(level) in building["levels"]:
                initial_name = building["name"]
                break
        if initial_name is None:
            print ("Error initialising Farm")
            initial_name = "Farmstead" #failsafe

        super().__init__(initial_name, level)

class Mine(Building):
    def __init__(self, level=1):
        building_data = self._load_all_building_data()
        initial_name = None
        for building in building_data:
            if building["building_type"] == "Mine" and str(level) in building["levels"]:
                initial_name = building["name"]
                break

        if initial_name is None: #failsafe
            print("Error initialising Mine")
            initial_name = "Quarry"

        super().__init__(initial_name, level)

class Wonder(Building):
    def __init__(self, level=1):
        building_data = self._load_all_building_data()
        initial_name = None
        for building in building_data:
            if building["building_type"] == "Wonder" and str(level) in building["levels"]:
                initial_name = building["name"]
                break
        if initial_name is None:
            print ("Error initialising Wonder") #should not happen
            initial_name = "Obelisk" #failsafe
        super().__init__(initial_name, level)