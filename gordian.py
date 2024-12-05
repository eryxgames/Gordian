import random
import os
import json

class Game:
    def __init__(self, player_name):
        self.wood = 10
        self.stone = 10
        self.food = 10
        self.houses = 0
        self.farms = 0
        self.mines = 0
        self.turn = 0
        self.victory_condition = {'wood': 50, 'stone': 50, 'food': 50, 'people': 50}
        self.player_name = player_name
        self.command_history = []
        self.command_index = 0
        self.hall_of_fame = self.load_hall_of_fame()
        self.people = 0
        self.people_in_houses = 0
        self.people_in_farms = 0
        self.people_in_mines = 0
        self.hero_available = False
        self.hero_assigned_to = None
        self.hero_on_quest = False
        self.total_resources_harvested = 0
        self.total_people_joined = 0
        self.popularity_points = 0

    def load_hall_of_fame(self):
        if os.path.exists('hall_of_fame.json'):
            with open('hall_of_fame.json', 'r') as file:
                return json.load(file)
        return []

    def save_hall_of_fame(self):
        with open('hall_of_fame.json', 'w') as file:
            json.dump(self.hall_of_fame, file)

    def display_status(self):
        print(f"\nTurn: {self.turn}")
        print(f"Resources - Wood: {self.wood}, Stone: {self.stone}, Food: {self.food}")
        print(f"Structures - Houses: {self.houses}, Farms: {self.farms}, Mines: {self.mines}")
        print(f"People - Total: {self.people}, In Houses: {self.people_in_houses}", end="")
        if self.hero_assigned_to == 'house':
            print(" (H)")
        else:
            print()
        print(f"In Farms: {self.people_in_farms}", end="")
        if self.hero_assigned_to == 'farm':
            print(" (H)")
        else:
            print()
        print(f"In Mines: {self.people_in_mines}", end="")
        if self.hero_assigned_to == 'mine':
            print(" (H)")
        else:
            print()
        print(f"Hero Available: {'Yes' if self.hero_available else 'No'}")
        print(f"Popularity Points: {self.popularity_points}")
        print(f"Victory Condition - Wood: {self.victory_condition['wood']}, Stone: {self.victory_condition['stone']}, Food: {self.victory_condition['food']}, People: {self.victory_condition['people']}")

    def collect_resources(self):
        self.wood += 5 + self.houses + self.people_in_mines
        self.stone += 5 + self.mines + self.people_in_mines
        self.food += 5 + self.farms + self.people_in_farms
        self.total_resources_harvested += 5 + self.houses + self.people_in_mines + 5 + self.mines + self.people_in_mines + 5 + self.farms + self.people_in_farms
        print("Resources collected!")

    def build_structure(self, structure):
        if structure in ['house', 'h']:
            if self.wood >= 10 and self.stone >= 5:
                self.wood -= 10
                self.stone -= 5
                self.houses += 1
                print("House built!")
            else:
                print("Not enough resources to build a house.")
        elif structure in ['farm', 'f']:
            if self.wood >= 5 and self.food >= 5:
                self.wood -= 5
                self.food -= 5
                self.farms += 1
                print("Farm built!")
            else:
                print("Not enough resources to build a farm.")
        elif structure in ['mine', 'm']:
            if self.stone >= 10 and self.food >= 5:
                self.stone -= 10
                self.food -= 5
                self.mines += 1
                print("Mine built!")
            else:
                print("Not enough resources to build a mine.")
        else:
            print("Invalid structure type.")

    def random_event(self):
        events = [
            ("A storm hits! You lose 5 wood.", lambda: self.adjust_resource('wood', -5)),
            ("A raid! You lose 5 stone.", lambda: self.adjust_resource('stone', -5)),
            ("A drought! You lose 5 food.", lambda: self.adjust_resource('food', -5)),
            ("A lucky find! You gain 10 wood.", lambda: self.adjust_resource('wood', 10)),
            ("A hidden cache! You gain 10 stone.", lambda: self.adjust_resource('stone', 10)),
            ("A bountiful harvest! You gain 10 food.", lambda: self.adjust_resource('food', 10)),
            ("Monster rampage! You lose resources and possibly a person.", self.monster_rampage)
        ]
        event, effect = random.choice(events)
        print(self.format_event(event))
        effect()

    def adjust_resource(self, resource, amount):
        if resource == 'wood':
            self.wood = max(0, self.wood + amount)
        elif resource == 'stone':
            self.stone = max(0, self.stone + amount)
        elif resource == 'food':
            self.food = max(0, self.food + amount)

    def format_event(self, event):
        return f"\n{'='*40}\n{event.center(40)}\n{'='*40}\n"

    def adversary_attack(self):
        if random.random() < 0.2:  # 20% chance of an adversary attack
            print(self.format_event("An adversary attacks and steals some resources!"))
            if self.people_in_houses > 0:
                print("People in houses defend successfully!")
                self.popularity_points += 1
                if not self.hero_available:
                    self.hero_available = True
                    print(self.format_event("Hero emerged!"))
            else:
                self.wood = max(0, self.wood - random.randint(1, 5))
                self.stone = max(0, self.stone - random.randint(1, 5))
                self.food = max(0, self.food - random.randint(1, 5))

    def monster_rampage(self):
        print("Monster rampage! You lose resources and possibly a person.")
        self.wood = max(0, self.wood - random.randint(1, 5))
        self.stone = max(0, self.stone - random.randint(1, 5))
        self.food = max(0, self.food - random.randint(1, 5))
        if self.people > 0 and random.random() < 0.5:  # 50% chance of losing a person
            self.people -= 1
            print("A person was killed by the monster!")

    def check_victory(self):
        if (self.wood >= self.victory_condition['wood'] and
            self.stone >= self.victory_condition['stone'] and
            self.food >= self.victory_condition['food'] and
            self.people >= self.victory_condition['people']):
            print("Congratulations! You have achieved the victory condition!")
            return True
        return False

    def check_defeat(self):
        if self.wood < 0 or self.stone < 0 or self.food < 0:
            print("You have been defeated! Game over.")
            return True
        return False

    def redistribute_people(self):
        total_buildings = self.houses + self.farms + self.mines
        if total_buildings > self.people:
            self.people_in_houses = min(self.houses, self.people)
            self.people_in_farms = min(self.farms, self.people - self.people_in_houses)
            self.people_in_mines = min(self.mines, self.people - self.people_in_houses - self.people_in_farms)
        else:
            self.people_in_houses = self.houses
            self.people_in_farms = self.farms
            self.people_in_mines = self.mines

        # Automatically move people to other buildings if housing is at full capacity
        if self.people_in_houses > self.houses:
            excess_people = self.people_in_houses - self.houses
            if self.farms < self.farms + excess_people:
                self.people_in_farms += excess_people
                self.people_in_houses = self.houses
            elif self.mines < self.mines + excess_people:
                self.people_in_mines += excess_people
                self.people_in_houses = self.houses

    def add_person(self):
        base_probability = 0.15
        building_bonus = 0.01 * (self.houses + self.farms + self.mines)
        house_bonus = 0.01 * self.houses
        popularity_bonus = 0.02 * self.popularity_points
        total_probability = min(0.62, base_probability + building_bonus + house_bonus + popularity_bonus)

        if self.houses > 0 and random.random() < total_probability:
            self.people += 1
            self.total_people_joined += 1
            print(self.format_event("A new person has arrived!"))

    def manage_hero(self):
        if self.hero_available:
            while True:
                action = input("What would you like to do with the hero? (assign/quest/back): ").lower()
                if action in ['assign', 'a']:
                    building = input("Assign hero to which building? (house/farm/mine): ").lower()
                    if building in ['house', 'h'] and self.houses > 0:
                        self.assign_hero('house')
                    elif building in ['farm', 'f'] and self.farms > 0:
                        self.assign_hero('farm')
                    elif building in ['mine', 'm'] and self.mines > 0:
                        self.assign_hero('mine')
                    else:
                        print("Invalid building type or building does not exist.")
                    break
                elif action in ['quest', 'q']:
                    self.send_hero_on_quest()
                    break
                elif action in ['back', 'b']:
                    break
                else:
                    print("Invalid action.")
        else:
            print("Hero is not available.")

    def assign_hero(self, building):
        if self.hero_available:
            self.hero_assigned_to = building
            self.hero_available = False
            print(f"Hero assigned to {building}!")
        else:
            print("Hero is not available.")

    def send_hero_on_quest(self):
        if self.hero_available:
            self.hero_available = False
            self.hero_on_quest = True
            print("Hero sent on a quest!")
        else:
            print("Hero is not available.")

    def hero_returns(self):
        if self.hero_on_quest:
            resource_types = ['wood', 'stone', 'food']
            resource = random.choice(resource_types)
            amount = max(1, (self.wood + self.stone + self.food) // 10)
            print(f"Hero returns with {amount} {resource}!")
            self.adjust_resource(resource, amount)

            # Random chance to bring 1-2 people
            if random.random() < 0.5:  # 50% chance
                people_brought = random.randint(1, 2)
                self.people += people_brought
                self.total_people_joined += people_brought
                print(f"Hero also brought {people_brought} people!")

            self.hero_available = True
            self.hero_on_quest = False

    def play_turn(self):
        action_performed = False
        while not action_performed:
            self.display_status()
            action = self.get_player_action()
            if action in ['collect', 'c']:
                self.collect_resources()
                action_performed = True
            elif action in ['build', 'b']:
                structure = input("What would you like to build? (house/farm/mine): ").lower()
                self.build_structure(structure)
                action_performed = True
            elif action in ['status', 's']:
                self.display_status()
            elif action in ['hero', 'h']:
                self.manage_hero()
            elif action in ['quit', 'q']:
                self.show_game_stats()
                print("Thanks for playing!")
                return False
            else:
                print("Invalid action.")

        # Ensure only one event per turn
        event_occurred = False
        if random.random() < 0.5:  # 50% chance of a random event
            self.random_event()
            event_occurred = True

        self.adversary_attack()
        if not event_occurred:
            self.redistribute_people()
            self.add_person()

        self.hero_returns()

        if self.check_defeat():
            return False
        if self.check_victory():
            return False
        self.turn += 1
        return True

    def get_player_action(self):
        while True:
            action = input("What would you like to do? (collect/build/status/hero/quit): ").lower()
            if action in ['collect', 'build', 'status', 'hero', 'quit', 'c', 'b', 's', 'h', 'q']:
                self.command_history.append(action)
                self.command_index = len(self.command_history)
                return action
            elif action == '\x1b[A' and self.command_index > 0:  # Up arrow key
                self.command_index = max(0, self.command_index - 1)
                print(self.command_history[self.command_index])
            elif action == '\x1b[B' and self.command_index < len(self.command_history):  # Down arrow key
                self.command_index = min(len(self.command_history), self.command_index + 1)
                print(self.command_history[self.command_index])
            else:
                print("Invalid action.")

    def calculate_score(self):
        return max(1, 1000 - self.turn * 10)

    def update_hall_of_fame(self):
        score = self.calculate_score()
        self.hall_of_fame.append({'name': self.player_name, 'score': score})
        self.hall_of_fame.sort(key=lambda x: x['score'], reverse=True)
        self.hall_of_fame = self.hall_of_fame[:10]  # Keep only top 10 scores
        self.save_hall_of_fame()
        print("Hall of Fame:")
        for entry in self.hall_of_fame:
            print(f"{entry['name']}: {entry['score']}")

    def show_game_stats(self):
        print(f"\nGame Stats for {self.player_name}:")
        print(f"You have harvested {self.total_resources_harvested} units of resources.")
        print(f"{self.total_people_joined} people joined your cause.")
        rank = self.determine_rank()
        print(f"You are remembered as {rank}.")

    def determine_rank(self):
        score = self.calculate_score()
        if score >= 900:
            return "Legendary Hero"
        elif score >= 700:
            return "Renowned Champion"
        elif score >= 500:
            return "Valiant Warrior"
        elif score >= 300:
            return "Brave Adventurer"
        else:
            return "Novice Explorer"

def generate_random_name():
    first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def main():
    print("Welcome to Gordian!")
    player_name = input("Enter your name (or press Enter for a random name): ").strip()
    if not player_name:
        player_name = generate_random_name()
    print(f"Welcome, {player_name}!")

    while True:
        game = Game(player_name)
        while game.play_turn():
            if game.check_victory():
                game.update_hall_of_fame()
                game.show_game_stats()
                break
        play_again = input("Do you want to play again? (yes/no): ").lower()
        if play_again != 'yes':
            break

if __name__ == "__main__":
    main()
