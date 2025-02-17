# core/events.py
import json
import random
import os

class Event:
    """Base class for all game events."""

    def __init__(self, event_id, description, audio_cue=None):
        self.event_id = event_id
        self.description = description
        self.audio_cue = audio_cue
        self.triggered = False

    def trigger(self, game, ui_manager, audio_manager):
        """Triggers the event, applying its effects to the game."""
        ui_manager.display_message(self.description, "text_warning")
        if self.audio_cue:
            audio_manager.play_sound(self.audio_cue)
        self.triggered = True


class ResourceEvent(Event):
    """An event that affects a specific resource."""

    def __init__(self, event_id, description, resource, amount, audio_cue=None):
        super().__init__(event_id, description, audio_cue)
        self.resource = resource
        self.amount = amount

    def trigger(self, game, ui_manager, audio_manager):
        super().trigger(game, ui_manager, audio_manager)
        if self.resource in game.resources:
            game.resources[self.resource] += self.amount
            ui_manager.display_message(f"{self.resource}: {game.resources[self.resource]}", "text_normal")
        else:
            print(f"Error: Invalid resource type in ResourceEvent: {self.resource}")

class ChainedEvent(Event):
    """An event that can trigger other events."""
    def __init__(self, event_id, description, initial_event, subsequent_events, audio_cue = None):
        super().__init__(event_id, description, audio_cue)
        self.initial_event = initial_event
        self.subsequent_events = subsequent_events

    def trigger(self, game, ui_manager, audio_manager):
        super().trigger(game, ui_manager, audio_manager)
        if self.initial_event:
            self.initial_event.trigger(game, ui_manager, audio_manager)

        for subsequent_event_data in self.subsequent_events:
            if random.random() < subsequent_event_data["probability"]:
                subsequent_event_data["event"].trigger(game, ui_manager, audio_manager)

# --- NEW: StoryEvent ---
class StoryEvent(Event):
    """An event that primarily advances the story."""

    def __init__(self, event_id, description, audio_cue=None):
        super().__init__(event_id, description, audio_cue)

    # The trigger method is inherited from Event, and already does what we need
    # (display the description and play the sound).  We don't need to override it.


class EventManager:
    """Manages game events."""

    def __init__(self):
        self.events = []
        self.triggered_events = set()

    def load_events(self, filename):
        filepath = os.path.join("data", filename)
        try:
            with open(filepath, 'r') as f:
                event_data_list = json.load(f)
                for event_data in event_data_list:
                    event = self.create_event(event_data)
                    if event:
                        self.events.append(event)
        except FileNotFoundError:
            print(f"Error: Event file not found: {filepath}")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in event file: {filepath}")
        except KeyError as e:
            print(f"KeyError {e} in event file: {filepath}")

    def create_event(self, event_data):
        event_type = event_data["type"]
        event_id = event_data["event_id"]
        description = event_data["description"]
        audio_cue = event_data.get("audio_cue")

        if event_type == "ResourceEvent":
            resource = event_data["resource"]
            amount = event_data["amount"]
            return ResourceEvent(event_id, description, resource, amount, audio_cue)

        elif event_type == "ChainedEvent":
            if "initial_event" not in event_data:
                print(f"Error: ChainedEvent '{event_id}' missing 'initial_event'.")
                return None
            if "subsequent_events" not in event_data:
                print(f"Error: ChainedEvent '{event_id}' missing 'subsequent_events'.")
                return None
            initial_event_data = event_data.get("initial_event")
            initial_event = self.create_event(initial_event_data) if initial_event_data else None
            subsequent_events_data = event_data.get("subsequent_events", [])
            subsequent_events = []
            for sub_event_data in subsequent_events_data:
                probability = sub_event_data["probability"]
                sub_event = self.create_event(sub_event_data["event"])
                subsequent_events.append({"probability": probability, "event": sub_event})

            return ChainedEvent(event_id, description, initial_event, subsequent_events, audio_cue)

        # --- NEW: Handle StoryEvent ---
        elif event_type == "StoryEvent":
            return StoryEvent(event_id, description, audio_cue)

        else:
            print(f"Error: Unknown event type: {event_type}")
            return None


    def get_random_event(self, game):
        if self.events:
            return random.choice(self.events)
        else:
            return None

    def trigger_event(self, game, ui_manager, audio_manager, event):
        if event:
            event.trigger(game, ui_manager, audio_manager)

    def get_event_by_id(self, event_id):
        for event in self.events:
            if event.event_id == event_id:
                return event
        return None

    def is_event_triggered(self, event_id):
      for event in self.events:
        if event.event_id == event_id:
          return event.triggered
      return False