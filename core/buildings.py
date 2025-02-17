# core/buildings.py
import json
import os

class Building:
    """Base class for all buildings."""

    def __init__(self, building_data, level=1): # Pass in building_data
        self.data = building_data  # Use the passed-in data!
        self.name = self.data["name"]
        self.building_type = self.data["building_type"]
        self.level = level
        self.max_level = len(self.data["levels"])
        self.assigned_people = []  # Initialize assigned_people

    def get_cost(self):
        return self.data["levels"].get(str(self.level), {}).get("cost", {})

    def get_production(self):
        return self.data["levels"].get(str(self.level), {}).get("production", {})

    def get_capacity(self):
        return self.data["levels"].get(str(self.level), {}).get("capacity", 0)

    def can_upgrade(self):
        return self.level < self.max_level

    def get_upgrade_cost(self):
        if self.can_upgrade():
            return self.data["levels"].get(str(self.level + 1), {}).get("cost", {})
        return {}

    def get_next_level_name(self):
        if self.can_upgrade():
            next_level = self.level + 1
            for building_data in self._building_data_list: #static data
                if (building_data.get("building_type") == self.building_type and
                    str(next_level) in building_data.get("levels", {})):
                    return building_data["name"]
        return None

    def upgrade(self):
        if self.can_upgrade():
            next_level_name = self.get_next_level_name()
            if next_level_name:
                self.level += 1
                self.name = next_level_name
                # Reload data based on the NEW name
                for building_data in self._building_data_list:
                    if building_data["name"] == self.name:
                        self.data = building_data
                        break
                print(f"{self.building_type} upgraded to {self.name} (level {self.level})!")
            else:
                print(f"Error during upgrading {self.building_type}")
        else:
            print(f"Cannot upgrade {self.name} further!")

    def can_assign_person(self):
        return len(self.assigned_people) < self.get_capacity()

    def assign_person(self, person):
        if self.can_assign_person():
            self.assigned_people.append(person)
            return True
        else:
            return False

    def unassign_person(self, person):
        if person in self.assigned_people:
            self.assigned_people.remove(person)
            return True
        return False

    def get_assigned_people_count(self):
      return len(self.assigned_people)

    def get_assigned_people_by_class(self):
        counts = {}
        for person in self.assigned_people:
            counts[person.person_class] = counts.get(person.person_class, 0) + 1
        return counts

class House(Building):
    def __init__(self, building_data, level=1):
        super().__init__(building_data, level) # Pass data to base class

class Farm(Building):
    def __init__(self, building_data, level=1):
        super().__init__(building_data, level)

class Mine(Building):
    def __init__(self, building_data, level=1):
        super().__init__(building_data, level)

class Wonder(Building):
    def __init__(self, building_data, level=1):
        super().__init__(building_data, level)