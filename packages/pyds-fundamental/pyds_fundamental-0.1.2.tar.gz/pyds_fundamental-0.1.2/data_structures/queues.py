"""Various implementations of queue data structure."""

from .linked_list import LinkedList
from .node import NodePriorityQueue

# [ front ... end ]


class QueueArray:
    """Queue data structure using basic arrays.

    Attributes:
        array (List): Empty array. This will contain the data.
    """

    def __init__(self, *args):
        """Initialize a QueueArray.

        The constructor will accept a variable number of elements and enqueue each
        element into the array.

        Args:
            *args: Variable length argument list. Those are basically elements to be stored.
        """
        self.array = []
        for arg in args:
            self.enqueue(arg)

    @property
    def size(self):
        """int: Size of the array."""
        return len(self.array)

    @property
    def front(self):
        """any: The value at front if the queue is not empty. Otherwise None."""
        return self.array[0] if not self.is_empty() else None

    @property
    def rear(self):
        """any: The value at the rear if the queue is not empty. Otherwise None."""
        return self.array[-1] if not self.is_empty() else None

    def __str__(self):
        """str: String representation of the QueueArray."""
        return "[ " + " ".join(str(element) for element in self.array) + " ]"

    def __len__(self):
        """int: Size of the QueueArray."""
        return self.size

    def __getitem__(self, index):
        """Dunder method to make QueueArray indexable.

        Args:
            index (int): Index of `LinkedList` object to return the value at that position.

        Raises:
            IndexError: If the `index` is out of range.
        """
        if index < 0:
            index += self.size
        if not 0 <= index < self.size:
            raise IndexError(f"Index {index} is out of bounds")
        else:
            return self.array[index]

    def enqueue(self, value):
        """Enqueue the element inside the array.

        Args:
            value (any): Value to be enqueued.
        """
        self.array.append(value)

    def dequeue(self):  # O(n)
        """Dequeue the element from the array.

        Since this operation is using `.pop(0)`, it has O(n) time complexity because
        all the values in the array is shifted.

        Args:
            value (any): Value to be dequeued.
        """
        return self.array.pop(0)

    def is_empty(self):
        """bool: Return True if the size is 0, else False."""
        return self.size == 0

    def clear(self):
        """Clears the whole array of the QueueArray."""
        self.array.clear()

    def copy(self):
        """Return a deep copy of the QueueArray object with the same values in the same order."""
        return QueueArray(*self.array)


class LinkedQueue(LinkedList):
    """A queue that's using LinkedList object."""

    def __init__(self, *values):
        """Initialize a queue based on linked list data structure.

        Args:
            *values (List): Variable length argument list. Those are the elements to be stored in the linked queue.
        """
        super().__init__()
        for value in values:
            self.insert_tail(value)

    @property
    def front(self):
        """any: The value at front if the linked queue is not empty. Otherwise None."""
        return self.head_node.value if not self.is_empty() else None

    @property
    def rear(self):
        """any: The value at rear if the linked queue is not empty. Otherwise None."""
        return self.tail_node.value if not self.is_empty() else None

    def enqueue(self, value):  # O(1)
        """Enqueue an element inside the linked queue.

        This method uses the `insert_tail(value)` method from the LinkedList.

        Args:
            value (any): Value to insert.
        """
        self.insert_tail(value)

    def dequeue(self):  # O(1)
        """Dequeue an element from the linked queue.

        This method uses the `insert_tail(value)` method from the LinkedList.

        Raises:
            Exception: If the list is empty.
        """
        return self.delete_head()

    def is_empty(self):
        """bool: Return True if the size is 0, else False."""
        return self.size == 0

    def clear(self):
        """Clears the whole array of the LinkedQueue.

        Raises:
            Exception: If the list is empty.
        """
        while not self.is_empty():
            self.delete_head()

    def copy(self):
        """Returns a deep copy of the LinkedQueue object with the same values."""
        return LinkedQueue(*self)


class CircularQueue:
    """Circular queue implementation to handle empty space problem at the front.

    Attributes:
        capacity (int): Capacity of the circular queue. Default size is 50.
        array (List[any]): The list to be behaved as a circular queue.
        front_idx (int): Index of the front value of the array. -1 if the array is empty.
        rear_idx (int): Index of the rear value of the array. -1 if the array is empty.
        size (int): Size of the circular array.
    """

    def __init__(self, *values, capacity=50):
        """Initialize a CircularQueue object.

        Args:
            capacity (int): Capacity of the circular queue. Default size is 50.
            array (List[any]): The list to be behaved as a circular queue.
            front_idx (int): Index of the front value of the array. -1 if the array is empty.
            rear_idx (int): Index of the rear value of the array. -1 if the array is empty.
            size (int): Size of the circular array.
            *values (List): Variable length argument list. Those are the elements to be stored in the linked queue.
        """
        self.capacity = capacity
        self.array = [None] * self.capacity
        self.front_idx = -1
        self.rear_idx = -1
        self._size = 0
        for value in values:
            self.enqueue(value)

    @property
    def size(self):
        """int: Size of the array."""
        return self._size

    @property
    def front(self):
        """any: The value at front if the circular queue is not empty. Otherwise None."""
        return self.array[self.front_idx] if not self.is_empty() else None

    @property
    def rear(self):
        """any: The value at rear if the circular queue is not empty. Otherwise None."""
        return self.array[self.rear_idx] if not self.is_empty() else None

    def __str__(self):
        """str: String representation of the CircularQueue object."""
        string = "[ "
        idx = self.front_idx
        for _ in range(self.size):
            string += str(self.array[idx]) + " "
            idx = (idx + 1) % self.capacity
        return string + "]"

    def __repr__(self):
        """str: Representation of CircularQueue object for debugging."""
        return (
            f"CircularQueue(array={self.array}, "
            f"capacity={self.capacity}, "
            f"front_idx={self.front_idx}, "
            f"rear_idx={self.rear_idx}, "
            f"size={self.size})"
        )

    def __len__(self):
        """int: Size of the array."""
        return self._size

    def __getitem__(self, index):
        """Make CircularQueue class indexable.

        Args:
            index (int): Index of `CircularQueue` object to return the value at that position.

        Raises:
            IndexError: If the `index` is out of range.
        """
        if index < 0:
            index += self.size
        if not 0 <= index < self.size:
            raise IndexError(f"Index {index} is out of bounds")
        else:
            physical_index = (self.front_idx + index) % self.capacity
            return self.array[physical_index]

    def __iter__(self):
        """Dunder method to make `CircularQueue` iterable."""
        for i in range(self.size):
            physical_index = (self.front_idx + i) % self.capacity
            yield self.array[physical_index]

    def enqueue(self, value):
        """Enqueue data for a circular queue.

        This is a manual implementation instead of using %. Each time a new insertion is
        made, the front_idx and rear_idx changes.

        Args:
            value (any): To enqueue inside the CircularQueue.

        Raises:
            Exception: If the CircularQueue is full.
        """
        if self.is_full():
            raise Exception("The circular queue is full")
        elif self.is_empty():
            self.front_idx = self.rear_idx = 0
        elif self.is_rear_idx_reached() and self.front_idx != 0:
            self.rear_idx = 0
        else:
            self.rear_idx = self.rear_idx + 1
        self.array[self.rear_idx] = value
        self._size += 1

    def dequeue(self):
        """Dequeue an element from the CircularQueue.

        Using the modular arithmetics, front and rear indices are updated.

        Raises:
            Exception: If the circular queue is empty.
        """
        if self.is_empty():
            raise Exception("The circular queue is empty")
        value = self.array[self.front_idx]
        self.array[self.front_idx] = None
        self.front_idx = (self.front_idx + 1) % self.capacity
        self._size -= 1
        if self._size == 0:
            self.front_idx = -1
            self.rear_idx = -1
        return value

    def is_empty(self):
        """bool: Return True if the size is 0, else False."""
        return self.size == 0

    def is_full(self):
        """bool: Return True if the queue is full capacity, else False."""
        return (self.rear_idx + 1) % self.capacity == self.front_idx

    def is_rear_idx_reached(self):
        """bool: Return True if the `rear_idx` reached at the end, else False.

        This is used to check if the rear_idx should be jumped to the front of the circular queue.
        """
        return self.rear_idx == self.capacity - 1

    def clear(self):
        """Clears the whole CircularQueue object.

        Creates the default array representation. Reset the front and rear indices, set the size to 0.
        """
        self.array = [None] * self.capacity
        self.front_idx = -1
        self.rear_idx = -1
        self._size = 0

    def copy(self):
        """Return a deep copy of the CircularQueue object."""
        return CircularQueue(*self, capacity=self.capacity)


class PriorityQueue(LinkedList):
    """Implementation of priority queue, where queue is made up of linked lists with priority levels.

    Attributes:
        value (Any): Value of the node.
    """

    def __init__(self, value=None):
        """Initialize a PriorityQueue object.

        This is used a specialized node class called `NodePriorityQueue`.

        Args:
            value (Any): Value of the node.
        """
        super().__init__(value, node=NodePriorityQueue)

    @property
    def front(self):
        """Return the value at the front of the queue, or None if empty."""
        return self.head_node.value if not self.is_empty() else None

    @property
    def rear(self):
        """any: The value at front (tail node's value of the linked list) if the queue is not empty. Otherwise None."""
        return self.tail_node.value if not self.is_empty() else None

    def enqueue(self, value, priority):
        """Enqueue the element inside the linked queue.

        First, a value is wrapped inside the node object. If there's a node with a higher priority,
        it's inserted to front. The nodes with the same priority level are behaved like a regular queue (FIFO).

        Args:
            value (any): Value to be enqueued.
            priority (int): Priority level
        """
        new_node = self._Node(value, priority)
        current_node = self.head_node
        prev_node = None

        while current_node is not None:
            if new_node.priority > current_node.priority:
                if prev_node is None:
                    self._insert_node_head(new_node)
                    return
                else:
                    prev_node.next_node = new_node
                    new_node.next_node = current_node
                    self._size += 1
                return
            elif new_node.priority == current_node.priority:
                new_node.next_node = current_node.next_node
                current_node.next_node = new_node
                self._size += 1
                return
            prev_node = current_node
            current_node = current_node.next_node

        if prev_node is not None:
            prev_node.next_node = new_node
            self.tail_node = new_node
        else:
            self.head_node = new_node
        self._size += 1

    def dequeue(self):
        """Dequeue the element (remove the head node from the list).

        Raises:
            Exception: If the priority queue is empty.
        """
        if self.size == 0:
            raise Exception("The priority queue is empty")
        value = self.head_node.value
        self.delete_head()
        return value

    def _insert_node_head(self, new_node):
        new_node.next_node = self.head_node
        self.head_node = new_node
        self._size += 1
        if self._size == 1:
            self.tail_node = new_node

    def is_empty(self):
        """bool: Return True if the size is 0, else False."""
        return self.size == 0

    def clear(self):
        """Clear the whole PriorityQueue object."""
        while not self.is_empty():
            self.delete_head()

    def copy(self):
        """Return a deep copy of the current PriorityQueue object."""
        new_queue = PriorityQueue()
        current_node = self.head_node
        while current_node is not None:
            new_queue.enqueue(current_node.value, current_node.priority)
            current_node = current_node.next_node
        return new_queue
