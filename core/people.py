# core/people.py
import json
import os

class Person:
    def __init__(self, person_class_data):
        self.class_id = person_class_data["class_id"] # Use class_id
        self.person_class = person_class_data["class_name"] # Keep class_name for display
        self.bonuses = person_class_data.get("bonuses", {})

    def get_bonus(self, building_type):
        return self.bonuses.get(building_type, {}).get("production", 0)

    def __str__(self):
        return self.person_class  # Use class_name for display


class PeopleManager:
    def __init__(self):
        self.people_classes = {}  # Store by class_id
        self.load_people_classes("data/people.json")

    def load_people_classes(self, filename):
        filepath = os.path.join(filename)
        try:
            with open(filepath, 'r') as f:
                classes_data = json.load(f)
                for class_data in classes_data:
                    class_id = class_data["class_id"]  # Use class_id
                    self.people_classes[class_id] = class_data  # Store by class_id
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading people classes: {e}")

    def create_person(self, class_id):  # Use class_id
        """Creates a Person object of the specified class."""
        if class_id in self.people_classes:
            return Person(self.people_classes[class_id])
        else:
            print(f"Error: Unknown person class ID '{class_id}'.")
            return None

    def get_available_classes(self):
        """Returns a list of available person class IDs."""
        return list(self.people_classes.keys())  # Return class_ids

    def get_person_class_data(self, class_id): # Use class_id
        """Returns data of person class"""
        return self.people_classes.get(class_id)