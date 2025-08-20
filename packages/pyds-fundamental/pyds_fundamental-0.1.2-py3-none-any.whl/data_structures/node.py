"""This module contains basic Node classes to construct data structures."""


class NodeCore:
    """This is the fundamental class that's used & inherited for linear data structures.

    Attributes:
        value (any): Value (data) stored in node.
        next_node (Node | None): A pointer to the next node if exists.
    """

    def __init__(self, value, next_node=None):
        """Initialize a NodeCore object.

        Args:
            value (Any, optional): First value to add to the list. Defaults to None.
            next_node (NodeCore, optional): Node class used to create list nodes. Defaults to Node.
        """
        self._value = value
        self._next_node = next_node

    @property
    def value(self):
        """Any: The stored value in the `Node` object."""
        return self._value

    @property
    def next_node(self):
        """Return the next node. If there are no next node, returns `None`."""
        return self._next_node

    @next_node.setter
    def next_node(self, node):
        """Set the next node.

        Args:
            node (Node | None): new `Node` object or None if it's the tail node.
        """
        self._next_node = node


class NodePriorityQueue(NodeCore):
    """This is the base node used to construct a priority queue. Inherits the NodeCore.

    Attributes:
        value (any): Value (data) stored in node.
        priority (int): Priority value for each node.
        next_node (Node | None): Next node for the current node.
    """

    def __init__(self, value, priority=None, next_node=None):
        """Initialize a NodePriorityQueue object. This is used for creating priority queues. Inherits NodeCore.

        Args:
            value (Any, optional): First value to add to the list. Defaults to None.
            next_node (type, optional): Node class used to create list nodes. Defaults to Node.
            priority (int): The priority value for the node. This will set the position of the node in the list.
        """
        super().__init__(value, next_node)
        self.priority = priority


class TreeNode:
    """This is the base node used when implementing binary search trees.

    Args:
        value (Any): The stored value in the node.
        left_child (Node | None): Left child of the current node.
        right_child (Node | None): Right child of the current node.
        parent (Node | None): Parent node of the current node.
    """

    def __init__(self, value=None, left_child=None, right_child=None, parent=None):
        """Initialize a TreeNode object. Used in data_structures.BinarySearchTree.

        Args:
            value (Any): The stored value in the node.
            left_child (Node | None): Left child of the current node.
            right_child (Node | None): Right child of the current node.
            parent (Node | None): Parent node of the current node.
        """
        self._value = value
        self._left_child = left_child
        self._right_child = right_child
        self._parent = parent

    @property
    def value(self):
        """Any: The stored value in the `TreeNode` object."""
        return self._value

    @value.setter
    def value(self, value):
        """Set a new value for the node.

        Args:
            value (Any): The new value of the node.
        """
        self._value = value

    @property
    def left_child(self):
        """None | TreeNode: Returns left child the TreeNode object if exists."""
        return self._left_child

    @left_child.setter
    def left_child(self, left_child):
        """Set the left_child of the TreeNode.

        Args:
            left_child (TreeNode | None): Left child of the node object.
        """
        self._left_child = left_child

    @property
    def right_child(self):
        """TreeNode: Returns the right child TreeNode object."""
        return self._right_child

    @right_child.setter
    def right_child(self, right_child):
        """Set the right_child of the TreeNode.

        Args:
            right_child (TreeNode | None): Right child of the node object.
        """
        self._right_child = right_child

    @property
    def left_value(self):
        """Any: Value of the left_child node."""
        return self._left_child.value if self._left_child else None

    @property
    def right_value(self):
        """Any: Value of the right_child node."""
        return self._right_child.value if self._right_child else None

    @property
    def parent(self):
        """None | TreeNode: Returns the parent node (TreeNode) object if exists."""
        return self._parent

    @parent.setter
    def parent(self, parent):
        """Set the parent node.

        Args:
            parent (TreeNode | None): Parent of the node object.
        """
        self._parent = parent
