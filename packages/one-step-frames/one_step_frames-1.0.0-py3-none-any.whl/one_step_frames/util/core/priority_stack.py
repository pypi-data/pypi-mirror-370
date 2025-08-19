import heapq

class PriorityStack:
    """A priority stack that uses a max-heap
     to manage items based on their priority.
    """
    def __init__(self):
        self.heap = []
        self.counter = 0  # Increases with every push

    def push(self, priority:int, item):
        """Push an item onto the stack with a given priority.

        Args:
            priority (int): The priority of the item. Higher values indicate higher priority.
            item (any): The item to be pushed onto the stack.
        """
        # Negate priority because heapq is a min-heap (higher priority first)
        # Negate counter so newer items come out first when priorities are equal
        heapq.heappush(self.heap, (-priority, -self.counter, item))
        self.counter += 1

    def pop(self):
        """ Pop the item with the highest priority from the stack.

        Returns:
            any: The item with the highest priority, or None if the stack is empty.
        """
        if self.heap:
            return heapq.heappop(self.heap)[-1]
        return None

    def empty(self):
        """ Check if the stack is empty.

        Returns:
            bool: True if the stack is empty, False otherwise.
        """
        return not self.heap
