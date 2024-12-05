import random
import os
import json
import textwrap

class Game:
    def __init__(self, player_name):
        self.wood = 10
        self.stone = 10
        self.food = 10
        self.houses = 0
        self.farms = 0
        self.mines = 0
        self.turn = 0
        self.victory_condition = {'wood': 50, 'stone': 50, 'food': 50}
        self.player_name = player_name
        self.command_history = []
        self.command_index = 0
        self.hall_of_fame = self.load_hall_of_fame()
        self.people = 0
        self.people_in_houses = 0
        self.people_in_farms = 0
        self.people_in_mines = 0

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
        print(f"People - Total: {self.people}, In Houses: {self.people_in_houses}, In Farms: {self.people_in_farms}, In Mines: {self.people_in_mines}")
        print(f"Victory Condition - Wood: {self.victory_condition['wood']}, Stone: {self.victory_condition['stone']}, Food: {self.victory_condition['food']}")

    def collect_resources(self):
        self.wood += 5 + self.houses + self.people_in_mines
        self.stone += 5 + self.mines + self.people_in_mines
        self.food += 5 + self.farms + self.people_in_farms
        print("Resources collected!")

    def build_structure(self, structure):
        if structure == 'house':
            if self.wood >= 10 and self.stone >= 5:
                self.wood -= 10
                self.stone -= 5
                self.houses += 1
                print("House built!")
            else:
                print("Not enough resources to build a house.")
        elif structure == 'farm':
            if self.wood >= 5 and self.food >= 5:
                self.wood -= 5
                self.food -= 5
                self.farms += 1
                print("Farm built!")
            else:
                print("Not enough resources to build a farm.")
        elif structure == 'mine':
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
            ("A storm hits! You lose 5 wood.", lambda: self.wood - 5),
            ("A raid! You lose 5 stone.", lambda: self.stone - 5),
            ("A drought! You lose 5 food.", lambda: self.food - 5),
            ("A lucky find! You gain 10 wood.", lambda: self.wood + 10),
            ("A hidden cache! You gain 10 stone.", lambda: self.stone + 10),
            ("A bountiful harvest! You gain 10 food.", lambda: self.food + 10),
        ]
        event, effect = random.choice(events)
        print(self.format_event(event))
        effect()

    def format_event(self, event):
        return f"\n{'='*40}\n{event.center(40)}\n{'='*40}\n"

    def adversary_attack(self):
        if random.random() < 0.2:  # 20% chance of an adversary attack
            print(self.format_event("An adversary attacks and steals some resources!"))
            self.wood = max(0, self.wood - random.randint(1, 5) - self.people_in_houses)
            self.stone = max(0, self.stone - random.randint(1, 5) - self.people_in_houses)
            self.food = max(0, self.food - random.randint(1, 5) - self.people_in_houses)

    def check_victory(self):
        if (self.wood >= self.victory_condition['wood'] and
            self.stone >= self.victory_condition['stone'] and
            self.food >= self.victory_condition['food']):
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

    def add_person(self):
        if self.houses > 0 and random.random() < 0.2:  # 20% chance of a new person appearing
            self.people += 1
            print(self.format_event("A new person has arrived!"))

    def play_turn(self):
        self.display_status()
        action = self.get_player_action()
        if action in ['collect', 'c']:
            self.collect_resources()
        elif action in ['build', 'b']:
            structure = input("What would you like to build? (house/farm/mine): ").lower()
            self.build_structure(structure)
        elif action in ['status', 's']:
            self.display_status()
        elif action in ['quit', 'q']:
            print("Thanks for playing!")
            return False
        else:
            print("Invalid action.")
        self.turn += 1
        self.random_event()
        self.adversary_attack()
        self.redistribute_people()
        self.add_person()
        if self.check_defeat():
            return False
        return True

    def get_player_action(self):
        while True:
            action = input("What would you like to do? (collect/build/status/quit): ").lower()
            if action in ['collect', 'build', 'status', 'quit', 'c', 'b', 's', 'q']:
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

def generate_random_name():
    first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def main():
    player_name = input("Enter your name (or press Enter for a random name): ").strip()
    if not player_name:
        player_name = generate_random_name()
    print(f"Welcome, {player_name}!")

    while True:
        game = Game(player_name)
        while game.play_turn():
            if game.check_victory():
                game.update_hall_of_fame()
                break
        play_again = input("Do you want to play again? (yes/no): ").lower()
        if play_again != 'yes':
            break

if __name__ == "__main__":
    main()
