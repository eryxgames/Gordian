# core/events.py
import json
import random
import os

class Event:
    """Base class for all game events."""

    def __init__(self, event_id, description, audio_cue=None): #added id
        self.event_id = event_id #unique id
        self.description = description
        self.audio_cue = audio_cue  # Can be a string or a list of strings
        self.triggered = False # Add a triggered flag


    def trigger(self, game, ui_manager, audio_manager):
        """Triggers the event, applying its effects to the game."""
        # Basic implementation: just display the description
        ui_manager.display_message(self.description, "text_warning")
        if self.audio_cue:
            audio_manager.play_sound(self.audio_cue)
        self.triggered = True #set flag after triggering


class ResourceEvent(Event):
    """An event that affects a specific resource."""

    def __init__(self, event_id, description, resource, amount, audio_cue=None):
        super().__init__(event_id, description, audio_cue)
        self.resource = resource
        self.amount = amount

    def trigger(self, game, ui_manager, audio_manager):
        super().trigger(game, ui_manager, audio_manager)  # Display description & play sound
        # Modify the resource amount
        if self.resource in game.resources:
            game.resources[self.resource] += self.amount
            ui_manager.display_message(f"{self.resource}: {game.resources[self.resource]}", "text_normal") #show new resource
        else:
            print(f"Error: Invalid resource type in ResourceEvent: {self.resource}")

class ChainedEvent(Event):
    """An event that can trigger other events."""
    def __init__(self, event_id, description, initial_event, subsequent_events, audio_cue = None):
        super().__init__(event_id, description, audio_cue)
        self.initial_event = initial_event
        self.subsequent_events = subsequent_events #list of dicts

    def trigger(self, game, ui_manager, audio_manager):
        super().trigger(game, ui_manager, audio_manager)  # Display main event description
        # Trigger the initial event
        if self.initial_event:
            self.initial_event.trigger(game, ui_manager, audio_manager) #recursive call

        # Trigger subsequent events based on probability
        for subsequent_event_data in self.subsequent_events:
            if random.random() < subsequent_event_data["probability"]:
                subsequent_event_data["event"].trigger(game, ui_manager, audio_manager)

class EventManager:
    """Manages game events, including loading, selection, and triggering."""

    def __init__(self):
        self.events = []
        self.triggered_events = set()  # Keep track of triggered events by ID

    def load_events(self, filename):
        """Loads event definitions from a JSON file."""
        filepath = os.path.join("data", filename)
        try:
            with open(filepath, 'r') as f:
                event_data_list = json.load(f)
                for event_data in event_data_list:
                    event = self.create_event(event_data)
                    if event:  # Only add if create_event was successful
                        self.events.append(event)
        except FileNotFoundError:
            print(f"Error: Event file not found: {filepath}")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in event file: {filepath}")
        except KeyError as e:
            print(f"KeyError {e} in event file: {filepath}")


    def create_event(self, event_data):
        """Creates an Event object from the given data (recursive)."""
        event_type = event_data["type"]
        event_id = event_data["event_id"] #get id
        description = event_data["description"]
        audio_cue = event_data.get("audio_cue")  # Use .get() to handle missing audio_cue

        if event_type == "ResourceEvent":
            resource = event_data["resource"]
            amount = event_data["amount"]
            return ResourceEvent(event_id, description, resource, amount, audio_cue)

        elif event_type == "ChainedEvent":
            initial_event_data = event_data.get("initial_event")  # Can be None
            initial_event = self.create_event(initial_event_data) if initial_event_data else None
            subsequent_events_data = event_data.get("subsequent_events", []) #list of dicts
            subsequent_events = []
            for sub_event_data in subsequent_events_data:
                probability = sub_event_data["probability"]
                sub_event = self.create_event(sub_event_data["event"])
                subsequent_events.append({"probability": probability, "event": sub_event})

            return ChainedEvent(event_id, description, initial_event, subsequent_events, audio_cue)

        else:
            print(f"Error: Unknown event type: {event_type}")
            return None


    def get_random_event(self, game):
        """Selects a random event (placeholder for now)."""

        # Basic implementation: choose any event at random
        # TODO: Add conditions and probabilities
        if self.events:  # Check if there are any events loaded
            return random.choice(self.events)
        else:
            return None #return nothing

    def trigger_event(self, game, ui_manager, audio_manager, event):
        if event: #check if not None
            event.trigger(game, ui_manager, audio_manager)

    def get_event_by_id(self, event_id):
        """Retrieves an event by its ID."""
        for event in self.events:
            if event.event_id == event_id:
                return event
        return None

    def is_event_triggered(self, event_id):
        """Checks if an event with the given ID has been triggered."""
        for event in self.events:
            if event.event_id == event_id:
                return event.triggered  # Return the triggered status
        return False  # Return False if event not found