# core/resources.py

class Resource:
    """Represents a single resource type."""

    def __init__(self, name, initial_amount=0):
        self.name = name
        self.amount = initial_amount
        self.max_amount = 100  # Example maximum storage (can be changed)

    def add(self, amount):
        """Adds to the resource amount, respecting the maximum."""
        self.amount = min(self.amount + amount, self.max_amount)
        # You could add a check here to see if max_amount was reached
        # and print a "Storage full!" message.

    def remove(self, amount):
        """Removes from the resource amount (cannot go below zero)."""
        self.amount = max(self.amount - amount, 0)

    def can_afford(self, amount):
        """Checks if a given amount of the resource is available."""
        return self.amount >= amount

    def __str__(self):  # Added for easy printing
        return str(self.amount)

    def __repr__(self): # Added for debugging
        return f"Resource(name={self.name}, amount={self.amount}, max_amount={self.max_amount})"

    def __iadd__(self, other):
        """Overloads the += operator"""
        self.add(other)
        return self

    def __isub__(self, other):
        """Overloads the -= operator"""
        self.remove(other)
        return self