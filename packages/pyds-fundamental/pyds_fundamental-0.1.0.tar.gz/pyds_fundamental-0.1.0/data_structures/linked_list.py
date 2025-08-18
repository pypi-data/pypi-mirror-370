"""Implementation of linked list. Default node is NodeCore."""

from .node import NodeCore as Node


class LinkedList:
    """This is the singly linked list implementation.

    Attributes:
        _Node (Any): This is the node object used to create a list. Custom node objects can be used. Defaults to NodeCore.
        head_node (None or Node): The first node in the list.
        tail_node (None or Node): The last node in the list.
        size (int): The number of elements in the list.
        value (Any): Value of the node.
    """

    def __init__(self, value=None, node=Node):
        """Initialize the `LinkedList`.

        Args:
            head_node (None or Node): The first node in the list.
            tail_node (None or Node): The last node in the list.
            size (int): The number of elements in the list.
            value (Any): Value of the node.
            node (any | Node): Node container to construct a doubly linked list. Defaults to Node.
        """
        self._Node = node
        if value is not None:
            self.head_node = self._Node(value)
            self.tail_node = self.head_node
            self._size = 1
        else:
            self.head_node = None
            self.tail_node = None
            self._size = 0

    @property
    def size(self):
        """int: How many elements in the linked list."""
        return self._size

    def __str__(self):
        """str: A string representation of nodes in the list."""
        return "[ " + " ".join(str(node) for node in self) + " ]"

    def __len__(self):
        """int: How many elements in the linked list."""
        return self._size

    def __getitem__(self, index):
        """Make LinkedList class indexable.

        Args:
            index (int): Index of `LinkedList` object to return the value at that position.

        Raises:
            IndexError: If the `index` is out of range.
        """
        if index < 0:
            index += self._size
        if not 0 <= index < self._size:
            raise IndexError(f"Index {index} is out of bounds")
        else:
            return self.find_by_index(index)

    def __iter__(self):
        """Dunder method to make `LinkedList` iterable."""
        current_node = self.head_node
        while current_node:
            yield current_node.value
            current_node = current_node.next_node

    def insert_head(self, value):
        """Inserts a value at head. Wraps the value inside the Node object.

        Args:
            value (any): Value to be inserted.
        """
        new_node = self._Node(value)
        new_node.next_node = self.head_node
        self._size += 1
        self.head_node = new_node
        if self._size == 1:
            self.tail_node = new_node

    def insert_tail(self, value):
        """Inserts a value at tail. Wraps the value inside the Node object.

        Args:
            value (any): Value to be inserted.
        """
        new_node = self._Node(value)
        if self._size == 0:
            self.head_node = new_node
            self.tail_node = self.head_node
        else:
            self.tail_node.next_node = new_node
            self.tail_node = new_node
        self._size += 1

    def insert_index(self, index, value):
        """Insert the value inside the given index. Shifts the elements coming after that index.

        Args:
            index (int): Index position to insert the node.
            value (any): Value wrapped inside a Node to be inserted.

        Raises:
            IndexError: If the `index` is out of range.
        """
        if index < 0 or index > self._size - 1:
            raise IndexError(f"Index {index} out of bounds for insertion")
        else:
            if index == 0:
                self.insert_head(value)
                return
            current_node = self.head_node
            counter = 0
            while counter < index - 1:
                current_node = current_node.next_node
                counter += 1
            new_node = self._Node(value)
            next_node = current_node.next_node
            current_node.next_node = new_node
            self._size += 1
            new_node.next_node = next_node

    def delete_head(self):
        """Delete the first element in the list.

        Raises:
            Exception: If the list is empty.
        """
        if self.head_node is None:
            raise Exception("Cannot delete from an empty list")
        second_node = self.head_node.next_node
        self._size -= 1
        self.head_node = second_node

    def delete_tail(self):
        """Delete the last element in the list.

        Raises:
            Exception: If the `head_node` is None.
        """
        if self.head_node is None:
            raise Exception("Cannot delete from an empty list")
        elif self._size == 1:
            self.head_node = None
            self.tail_node = None
        else:
            current_node = self.head_node
            while current_node.next_node.next_node is not None:
                current_node = current_node.next_node
            self.tail_node = current_node
            current_node.next_node = None
        self._size -= 1

    def delete_index(self, index):
        """Delete the element at the given index.

        Args:
            index (int): The index where the node will be deleted.

        Raises:
            IndexError: If the `index` is out of range.
        """
        if index < 0 or index > self._size - 1:
            raise IndexError(
                f"Index {index} is out of bounds for deletion - List size: {self._size}"
            )
        current_node = self.head_node
        counter = 0
        if self._size == 1 or index == 0:
            self.delete_head()
        else:
            while (
                counter < index - 1
            ):  # get to the previous node of the node we want to delete
                current_node = current_node.next_node
                counter += 1
            next_node = current_node.next_node.next_node
            current_node.next_node = next_node
            self._size -= 1

    def delete_value(self, value):
        """Delete a node with the given value.

        Args:
            value (any): Value that a node contains.

        Raises:
            Exception: If the list is empty.
            ValueError: If the `value` is not found in the list.
        """
        current_node = self.head_node
        previous_node = None

        while current_node is not None:
            if current_node.value == value:
                if previous_node is None:
                    self.delete_head()
                    return
                else:
                    previous_node.next_node = current_node.next_node
                    self._size -= 1
                    return
            previous_node = current_node
            current_node = current_node.next_node

        raise ValueError(f"{value} is not in the list")

    def find_by_index(self, index):
        """Find and return the value of a node of a given index.

        Args:
            index (int): The index of the node whose value is wanted.

        Returns:
            any: value of the node at `index`

        Raises:
            IndexError: If the `index` is out of range.
        """
        if index < 0:
            index += self._size
        if index > self._size - 1:
            raise IndexError(f"Index {index} is out of bounds for check")
        current_node = self.head_node
        counter = 0
        while current_node is not None:
            if counter == index:
                return current_node.value
            else:
                current_node = current_node.next_node
                counter += 1

    def traverse(self):
        """Traverse and print the each value in the list."""
        current_node = self.head_node
        while current_node is not None:
            print(current_node.value)
            current_node = current_node.next_node
