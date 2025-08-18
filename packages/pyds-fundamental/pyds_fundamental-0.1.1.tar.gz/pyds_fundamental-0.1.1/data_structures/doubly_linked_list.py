"""Implementation of Doubly Linked List. Used a new class Node which inherits NodeCore."""

from .node import NodeCore


class Node(NodeCore):
    """Base node for DoublyLinkedList. Inherits all attributes from NodeCore.

    Attributes:
        prev_node (None | Node): Pointer to the previous node.
    """

    def __init__(self, value, next_node=None, prev_node=None):
        """Initialize a Node.

        Args:
            value
            value (any): Value (data) stored in node.
            next_node (Node | None): A pointer to the next node if exists.
            prev_node (Node | None): A pointer to the previous node if exists.
        """
        super().__init__(value, next_node)
        self._prev_node = prev_node

    @property
    def prev_node(self):
        """Node | None: Return the previous node."""
        return self._prev_node

    @prev_node.setter
    def prev_node(self, value):
        """Set the previous node's value.

        Args:
            value (any): Value of the previous `Node` object.
        """
        self._prev_node = value


class DoublyLinkedList:
    """This is the doubly linked list implementation.

    Attributes:
        _Node (Any): This is the node object used to create a list. Custom node objects can be used. Defaults to NodeCore.
        head_node (None or Node): The first node in the list.
        tail_node (None or Node): The last node in the list.
        size (int): The number of elements in the list.
        value (Any): Value of the node.
    """

    def __init__(self, value=None, node=Node):
        """Initialize the `DoublyLinkedList`.

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

    def __str__(self):
        """Return the string representation of the `LinkedList` object."""
        return "[ " + " ".join(str(node) for node in self) + " ]"

    def __len__(self):
        """Return the size of the linked list."""
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
        if self._size == 0:
            self.head_node = self._Node(value)
            self.tail_node = self.head_node
        else:
            new_node = self._Node(value)
            new_node.next_node = self.head_node
            self.head_node.prev_node = new_node
            self.head_node = new_node
        self._size += 1

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
            final_node = self.tail_node.next_node
            final_node.prev_node = self.tail_node
            self.tail_node = final_node
        self._size += 1

    def delete_head(self):
        """Delete the first element in the list.

        Raises:
            Exception: If the list is empty.
        """
        if self._size == 0:
            raise Exception("Cannot delete from an empty list")
        elif self._size == 1:
            self.head_node = None
            self.tail_node = None
        else:
            self.head_node = self.head_node.next_node
            self.head_node.prev_node = None
        self._size -= 1

    def delete_tail(self):
        """Delete the last element in the list.

        Raises:
            Exception: If the size is 0.
        """
        if self._size == 0:
            raise Exception("Cannot delete from an empty list")
        elif self._size == 1:
            self.head_node = None
            self.tail_node = None
        else:
            self.tail_node = self.tail_node.prev_node
            self.tail_node.next_node = None
        self._size -= 1

    def delete_index(self, index):
        """Delete the element at the given index.

        Args:
            index (int): The index where the node will be deleted.

        Raises:
            IndexError: If the `index` is out of range.
        """
        if index < 0 or index > self._size - 1:
            raise IndexError(f"Index {index} is out of bounds")
        current_node = self.head_node
        counter = 0
        if self._size == 1 or index == 0:
            self.delete_head()
        else:
            while counter < index - 1:
                current_node = current_node.next_node
                counter += 1
            next_node = current_node.next_node.next_node
            current_node.next_node = next_node
            if next_node is None:
                self.tail_node = current_node
            else:
                next_node.prev_node = current_node
            self._size -= 1
            return

    def delete_value(self, value):
        """Delete a node with the given value.

        Args:
            value (any): Value that a node contains.

        Raises:
            Exception: If the list is empty.
            ValueError: If the `value` is not found in the list.
        """
        if self._size == 0:
            raise Exception(f"Cannot delete from an empty list")
        else:
            current_node = self.head_node
            prev_node = None
            while current_node is not None:
                if current_node.value == value:
                    if prev_node is None:  # if it's the first node
                        self.delete_head()
                    else:
                        next_node = current_node.next_node
                        prev_node.next_node = next_node
                        if next_node is None:
                            self.tail_node = prev_node
                        else:
                            next_node.prev_node = prev_node
                        self._size -= 1
                    return
                prev_node = current_node
                current_node = current_node.next_node
        raise ValueError(f"{value} cannot be found in the list")

    def find_by_index(self, index):
        """Find and return the value of a node of a given index.

        Args:
            index (int): The index of the node whose value is wanted.

        Returns:
            any: value of the node at `index`

        Raises:
            IndexError: If the `index` is out of range.
        """
        if index < 0 or index > self._size - 1:
            raise IndexError(f"Index {index} is out of bounds")
        counter = 0
        current_node = self.head_node
        while current_node is not None:
            if counter == index:
                return current_node.value
            current_node = current_node.next_node
            counter += 1

    def find_by_value(self, value):
        """Find the first occurence of a node by value.

        Args:
            value (any): Value of the node.

        Raises:
            Exception: If the list is empty.
            ValueError: If the `value` is not found in the list.
        """
        if self._size == 0:
            raise Exception("Cannot find a value in an empty list.")
        else:
            current_node = self.head_node
            idx = 0
            while current_node is not None:
                if current_node.value == value:
                    print(f"{value} is found at index {idx}")
                    return
                else:
                    current_node = current_node.next_node
                    idx += 1
        raise ValueError(f"{value} cannot be found in the list")

    def reverse_find_by_value(self, value):
        """Find the last occurence of the value. Starts traversing from the tail node.

        Args:
            value (any): Value of the node.

        Raises:
            Exception: If the `value` isn't found in the list.
        """
        if self._size == 0:
            raise Exception("Cannot find a value in an empty list.")
        current_node = self.tail_node
        reverse_idx = 0
        while current_node is not None:
            if current_node.value == value:
                print(f"{value} is found at index {self._size - reverse_idx - 1}")
                return
            current_node = current_node.prev_node
            reverse_idx += 1
        raise Exception("f{value} cannot be found in the list")

    def traverse(self):
        """Traverse the list and print each value."""
        current_node = self.head_node
        while current_node is not None:
            print(current_node.value)
            current_node = current_node.next_node
