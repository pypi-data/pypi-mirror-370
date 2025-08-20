class LRUSet:
    """
    A set-like data structure with Least Recently Used (LRU) eviction policy.

    This class maintains insertion order based on recency and enforces uniqueness
    using equality comparison (`==`), not hashing. Unlike standard sets, it does not
    require elements to be hashable—only that they implement `__eq__`.

    Internally, items are stored in a list in LRU order (oldest at index 0).
    Both `add` and `contains` operations have O(n) time complexity.

    When the capacity is exceeded, the least recently used item is evicted.
    """

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.data: list = []  # Maintain LRU order: oldest at index 0

    def add(self, value):
        # Remove existing value (if any)
        for i, v in enumerate(self.data):
            if v == value:
                self.data.pop(i)
                break
        # Append to end (most recent)
        self.data.append(value)
        # Trim if over capacity
        if len(self.data) > self.capacity:
            self.data.pop(0)

    def contains(self, value) -> bool:
        return any(v == value for v in self.data)
