"""Implementation of stack data structure in two different ways."""

from .linked_list import LinkedList


class StackArray:
    """Stack data structure using an array.

    Attributes:
        array (List): Empty array. This will contain the data.
    """

    def __init__(self, *args):
        """Initialize a `StackArray` object.

        Args:
            *args: Variable length argument list. Those are basically the elements to be stored.
        """
        self.array = []
        for arg in args:
            self.push(arg)

    @property
    def size(self):
        """int: Size of the array."""
        return len(self.array)

    @property
    def top(self):
        """any: The value at the top. Otherwise None."""
        return self.array[-1] if not self.is_empty() else None

    def __str__(self):
        """str: String representation of `StackArray` object."""
        return "[ " + " ".join(str(element) for element in reversed(self.array)) + " ]"

    def __len__(self):
        """int: Return the size of the stack."""
        return self.size

    def __iter__(self):
        """Dunder method to make `StackArray` object iterable."""
        return reversed(self.array)

    def __contains__(self, value):
        """Dunder method to have a more pythonic experience.

        Args:
            value (any): The value to be pushed into the stack.

        Example:
            >>> stack = StackArray(1, 2, 3)
            >>> if 3 in stack:
            >>>     print("3 is inside the stack")
        """
        return value in self.array

    def push(self, value):
        """Push an element into the stack.

        Args:
            value (any): Value to be inserted.
        """
        self.array.append(value)

    def pop(self):
        """Pop an element from the stack.

        Raises:
            IndexError: If the stack is empty.
        """
        if self.size == 0:
            raise IndexError("The stack is empty")
        else:
            value = self.array.pop()
            return value

    def peek(self):
        """Return the top element without popping the element.

        Raises:
            IndexError: If the stack is empty.
        """
        if self.size == 0:
            raise IndexError("The stack is empty")
        else:
            return self.top

    def is_empty(self):
        """bool: Return True if the size is 0. Otherwise False."""
        return self.size == 0

    def clear(self):
        """Clear the whole `StackArray` object."""
        self.array.clear()

    def copy(self):
        """Return a deep copy of the `StackArray` object.

        The `*self.array` unpacks elements into a new stack.
        """
        return StackArray(*self.array)


class LinkedStack(LinkedList):
    """This is the stack implementation using linked lists. It has all the functionality a `LinkedList` has."""

    def __init__(self, *values):
        """Initialize a `LinkedStack` object.

        Args:
            *values: Variable length argument list. Those are basically the elements to be stored.
        """
        super().__init__()
        for value in values:
            self.insert_head(value)

    @property
    def top(self):
        """any: The value at the top. Otherwise None."""
        return self.head_node.value if self.head_node else None

    def push(self, value):
        """Push an element into the stack.

        Since it's using a linked list, this method is inserting the value to the head of the list.

        Args:
            value (any): Value to be inserted.
        """
        self.insert_head(value)

    def pop(self):
        """Pop an element from the stack.

        Raises:
            Exception: If the stack is empty.
        """
        if self.size > 0:
            element = self.head_node.value
            self.delete_value(self.head_node.value)
            return element
        else:
            raise Exception("The stack list is empty")

    def peek(self):
        """Return the top element without popping the element.

        Raises:
            IndexError: If the stack is empty.
        """
        if self.size == 0:
            raise IndexError("The stack is empty")
        else:
            return self.top

    def is_empty(self):
        """bool: Return True if the size is 0. Otherwise False."""
        return self.size == 0

    def clear(self):
        """Clear the whole `LinkedArray` object."""
        while self.size != 0:
            self.delete_head()

    def copy(self):
        """Return a deep copy of the `LinkedStack` object."""
        return LinkedStack(*reversed(list(self)))
