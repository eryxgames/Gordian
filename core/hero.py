# core/hero.py
import random

class Hero:
    def __init__(self, name=None, hero_class="Scout"):  # Default class
        self.available = True
        self.assigned_to = None
        self.on_quest = False
        self.name = name if name else self.generate_name()  # Generate if not provided
        self.hero_class = hero_class #hero class
        # --- Placeholders for future attributes ---
        self.stats = {}  # e.g., {"strength": 5, "intelligence": 3}
        self.equipment = {  # e.g., {"weapon": "Sword", "armor": "Leather Armor"}
            "weapon": None,
            "armor": None,
            "steed": None,  # Mount
            "item": None   # Misc item
        }
        self.level = 1
        self.experience = 0


    def generate_name(self):
        """Generates a random fantasy-style hero name."""
        first_names = ["Aric", "Lysandra", "Torvin", "Elara", "Darius", "Seraphina", "Ragnar", "Faelan", "Nyx", "Kazimir"]
        last_names = ["Stonebeard", "Swiftarrow", "Moonwhisper", "Ironheart", "Stormblade", "Shadowwalker", "Dragonslayer", "Lightbringer", "Ravenclaw", "Wolfsbane"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    def assign_to(self, building_name):
        """Assigns the hero to a building."""
        self.assigned_to = building_name
        self.available = False

    def unassign(self):
        """Unassigns the hero from any building."""
        self.assigned_to = None
        self.available = True

    def send_on_quest(self):
        """Sends the hero on a quest"""
        self.on_quest = True
        self.available = False

    def return_from_quest(self):
      """Return hero from quest"""
      self.on_quest = False
      self.available = True

    def get_class_bonus(self):
        """Returns a description of the hero's class bonus."""
        if self.hero_class == "Scout":
            return "Bonus to resources brought back from quests."
        elif self.hero_class == "Defender":
            return "Bonus to defense when defending buildings."
        elif self.hero_class == "Avenger":
            return "Bonus to attack (future combat)."
        elif self.hero_class == "Enchanter":
            return "Bonus to gaining/bringing followers from quests."
        # Add other classes here
        else:
            return "No class bonus."
    def add_experience(self, amount):
        """Adds experience to the hero and handles level-ups."""
        self.experience += amount
        # Simple level-up system (you can expand this)
        if self.experience >= 10 * self.level:
            self.level_up()

    def level_up(self):
        """Increases the hero's level and potentially improves stats."""
        self.level += 1
        self.experience = 0  # Reset experience
        print(f"{self.name} leveled up to level {self.level}!")  # Placeholder message
        # Improve stats based on class (example)
        if self.hero_class == "Scout":
            self.stats["resource_bonus"] = self.stats.get("resource_bonus", 0) + 1 #example stat
        # ... (add stat improvements for other classes) ...