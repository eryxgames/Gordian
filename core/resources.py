# core/resources.py

class Resource:
    """Represents a single resource type."""

    def __init__(self, name, initial_amount=0, max_amount=100):  # Add max_amount
        self.name = name
        self.amount = initial_amount
        self.max_amount = max_amount  # Use the provided max_amount

    def add(self, amount):
        """Adds to the resource amount, respecting the maximum."""
        self.amount = min(self.amount + amount, self.max_amount)

    def remove(self, amount):
        """Removes from the resource amount (cannot go below zero)."""
        self.amount = max(self.amount - amount, 0)

    def can_afford(self, amount):
        """Checks if a given amount of the resource is available."""
        return self.amount >= amount

    def __str__(self):
        return str(self.amount)

    def __repr__(self):
        return f"Resource(name={self.name}, amount={self.amount}, max_amount={self.max_amount})"

    def __iadd__(self, other):
        self.add(other)
        return self

    def __isub__(self, other):
        self.remove(other)
        return self