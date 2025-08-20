from .node import TreeNode
from .queues import QueueArray

traversal_keywords = ["print", "list", "generator"]
copy_keywords = ["iterative", "recursive"]
default_keyword = "list"
_sentinel = object()

class BinarySearchTree:
    def __init__(self, value=None, node=TreeNode):
        self._Node = node
        if value is None:
            self._root = None
            self._size = 0
        else:
            self._root = self._Node(value)
            self._size = 1

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, value):
        self._root = value

    @property
    def min(self):
        return self.find_min().value

    @property
    def max(self):
        return self.find_max().value

    @property
    def size(self):
        return self._size

    @property
    def is_empty(self):
        return self.root is None

    def __len__(self):
        return self._size

    def __iter__(self):
        for node in self._inorder(self.root):
            yield node

    def __contains__(self, value):
        node = self.search_element(value)
        if node is not None:
            return True
        else:
            return False

    def _check_empty(self):
        if self.root is None:
            raise Exception("Binary search tree is empty")

    def _check_param_type(self, param_type, keyword_list):
        if not isinstance(param_type, str):
            raise TypeError(
                f"Invalid type: {type(param_type)} for argument. Enter relevant 'str'"
                + "keywords from the list {keyword_list}"
            )
        elif param_type not in keyword_list:
            raise Exception(
                f"Invalid keyword. Choose one in between the list: {keyword_list}"
            )

    def inorder_traversal(self, output_type=default_keyword):
        self._check_param_type(output_type, traversal_keywords)
        self._check_empty()

        if output_type == "list":
            return list(node.value for node in self._inorder(self.root))
        elif output_type == "print":
            for i in self._inorder(self.root):
                print(i.value)
        elif output_type == "generator":
            return self._inorder(self.root)

    def _inorder(self, node):
        if node is None:
            return
        yield from self._inorder(node.left_child)
        yield node
        yield from self._inorder(node.right_child)

    def preorder_traversal(self, output_type=default_keyword):
        self._check_param_type(output_type, traversal_keywords)
        self._check_empty()

        if output_type == "list":
            return list(node.value for node in self._preorder(self.root))
        elif output_type == "print":
            for i in self._preorder(self.root):
                print(i.value)
        elif output_type == "generator":
            return self._preorder(self.root)

    def _preorder(self, node):
        if node is None:
            return
        yield node
        yield from self._preorder(node.left_child)
        yield from self._preorder(node.right_child)

    def postorder_traversal(self, output_type=default_keyword):
        self._check_param_type(output_type, traversal_keywords)
        self._check_empty()

        if output_type == "list":
            return list(node.value for node in self._postorder(self.root))
        elif output_type == "print":
            for i in self._postorder(self.root):
                print(i.value)
        elif output_type == "generator":
            return self._postorder(self.root)

    def _postorder(self, node):
        if node is None:
            return
        yield from self._postorder(node.left_child)
        yield from self._postorder(node.right_child)
        yield node

    def levelorder_traversal(self):
        if self.root is None:
            return None
        queue = QueueArray(self.root)
        result = []
        while queue.size != 0:
            current_node = queue.dequeue()
            result.append(current_node.value)
            if current_node.left_child is not None:
                queue.enqueue(current_node.left_child)
            if current_node.right_child is not None:
                queue.enqueue(current_node.right_child)
        return result

    def insert(self, data, node=None):
        if not isinstance(data, self._Node):
            new_node = self._Node(data)
        else:
            new_node = data

        if self._root is None:
            self.root = new_node
            self._size += 1
            return new_node
        else:
            current_node = self.root if node is None else node
            if new_node.value >= current_node.value:
                if current_node.right_child is None:
                    current_node.right_child = new_node
                    new_node.parent = current_node
                    self._size += 1
                    return new_node
                else:
                    return self.insert(new_node, current_node.right_child)
            else:
                if current_node.left_child is None:
                    current_node.left_child = new_node
                    new_node.parent = current_node
                    self._size += 1
                    return new_node
                else:
                    return self.insert(new_node, current_node.left_child)
    
    def insert_iterative(self, data):
        if not isinstance(data, self._Node):
            new_node = self._Node(data)
        else:
            new_node = data

        if self.root is None:
            self.root = new_node
            self._size += 1
            return new_node
        else:
            current_node = self.root
            while True:
                if new_node.value >= current_node.value:
                    if current_node.right_child is None:
                        current_node.right_child = new_node
                        new_node.parent = current_node
                        return new_node
                    current_node = current_node.right_child
                elif new_node.value < current_node.value:
                    if current_node.left_child is None:
                        current_node.left_child = new_node
                        new_node.parent = current_node
                        return new_node
                    current_node = current_node.left_child
        
    def search_element(self, value, node=None):
        if not isinstance(value, self._Node):
            searched_node = self._Node(value)
        else:
            searched_node = value
        current_node = self.root if node is None else node

        if self._root is None:
            raise Exception("Binary search tree is empty")
        elif current_node.value == searched_node.value:
            return current_node
        else:
            if searched_node.value < current_node.value:
                if current_node.left_child is None:
                    return None
                return self.search_element(searched_node, current_node.left_child)
            else:
                if current_node.right_child is None:
                    return None
                return self.search_element(searched_node, current_node.right_child)

    def search_iterative(self, value):
        if self._root is None:
            raise Exception("Binary search tree is empty")
        current_node = self.root
        while current_node is not None:
            if current_node.value == value:
                return current_node
            elif current_node.value >= value:
                current_node = current_node.left_child
            else:
                current_node = current_node.right_child
        raise Exception(f"Value {value} is not found")
        
        
    def delete_node(self, value, node=None):
        if node is None:
            node = self.search_element(value, node=node) # returns None if element couldn't be found
        if node is None:
            raise Exception(f"{value} does not exist in the tree")

        parent_node = node.parent
        # deleting a node that has no children
        if node.left_child is None and node.right_child is None:
            if parent_node.left_child == node:
                parent_node.left_child = None
            elif parent_node.right_child == node:
                parent_node.right_child = None
            self._size -= 1
        # deleting a node that has only one child
        elif node.left_child is None and node.right_child is not None:
            if parent_node.left_child == node:
                parent_node.left_child = node.right_child
            else:
                parent_node.right_child = node.right_child
            self._size -= 1
        elif node.left_child is not None and node.right_child is None:
            if parent_node.left_child == node:
                parent_node.left_child = node.left_child
            else:
                parent_node.right_child = node.left_child
            self._size -= 1
        # deleting a node with two children (using in order successor)
        else:
            in_order_successor = node.right_child
            while in_order_successor.left_child:
                in_order_successor = in_order_successor.left_child
            node.value = in_order_successor.value
            # now there are two nodes with the same value. when self.delete() called,       \
            # as a default value None, the search_element() method will start looking       \
            # by the root node. every time this will end up in the first occurence of the   \
            # same value. to avoid this, we can start from node.right_child but we already  \
            # have access to the real in_order_successor, so the function below in fact     \
            # will take O(1) time.
            self.delete_node(in_order_successor.value, in_order_successor)

    def delete_iterative(self, value):
        node = self._root
        parent_node = None
        
        while node is not None and node.value != value:
            parent_node = node
            if node.value > value:
                node = node.left_child
            else:
                node = node.right_child
        
        if node is None:
            raise Exception(f"{value} is not found in the tree")
        
        # deleting a node that has no children
        if node.left_child is None and node.right_child is None:
            if parent_node is None:
                self.root = None
            elif parent_node.left_child == node:
                parent_node.left_child = None
            elif parent_node.right_child == node:
                parent_node.right_child = None
            self._size -= 1
        # deleting a node that has only one child
        elif node.left_child is None or node.right_child is None:
            child_node = node.left_child if node.left_child else node.right_child
            if parent_node is None:
                self.root = child_node
            elif parent_node.left_child == node:
                parent_node.left_child = child_node
            else:
                parent_node.right_child = child_node
            if child_node:
                child_node.parent = parent_node
        # deleting a node with two children (using in order successor)
        else:
            successor_parent = node
            successor = node.right_child
            while successor.left_child is not None:
                successor_parent = successor
                successor = successor.left_child
            
            node.value = successor.value
            if successor_parent.left_child == successor:
                successor_parent.left_child = successor.right_child
            else:
                successor_parent.right_child = successor.right_child
            
            if successor.right_child:  # Update parent if successor had a right child
                successor.right_child.parent = successor_parent
            self._size -= 1
            
    def find_min(self, node=None, return_value=False):
        self._check_empty()
        if node is None:
            current_node = self.root
        else:
            current_node = self.search_element(node)
        while current_node.left_child:
            current_node = current_node.left_child
        if return_value is True:
            return current_node.value
        return current_node

    def find_max(self, node=None, return_value=False):
        self._check_empty()
        if node is None:
            current_node = self.root
        else:
            current_node = self.search_element(node)
        while current_node.right_child:
            current_node = current_node.right_child
        if return_value is True:
            return current_node.value
        return current_node

    def height(self, opt_node=_sentinel):
        if opt_node is _sentinel:
            return self.height(self.root)
        if opt_node is None:
            return 0
        else:
            left_height = self.height(opt_node.left_child)
            right_height = self.height(opt_node.right_child)
            return max(left_height, right_height) + 1

    def get_size(self):
        if self.root is None:
            return 0

        def _size(node=None):
            if node is None:
                return 0
            return _size(node.left_child) + _size(node.right_child) + 1

        ### to be removed later
        if _size(self.root) != self._size:
            print("get_size() fonksiyonundan dönüldü. self_size'da hata olmalı")
            return
        ###
        return _size(self.root)

    def clear(self):
        self.root = None
        self._size = 0

    def copy(self, method="recursive"):
        self._check_empty()
        self._check_param_type(method, copy_keywords)
        tree = BinarySearchTree()

        def _copy_iterative():
            for node in self._preorder(self.root):
                tree.insert(node.value)
            return tree

        def _copy_recursive(node, parent):
            if node is None:
                return None
            new_node = self._Node(node.value)
            new_node.parent = parent
            tree._size += 1
            new_node.left_child = _copy_recursive(node.left_child, new_node)
            new_node.right_child = _copy_recursive(node.right_child, new_node)
            return new_node

        if method == "iterative":
            return _copy_iterative()
        else:
            tree.root = _copy_recursive(self.root, self.root.parent)
            return tree

    def is_balanced(self, node=None):
        if node is None:
            node = self.root
        if not isinstance(node, TreeNode):
            raise Exception(f"Please provide a {TreeNode} object")
        left_subtree_height = self.height(node.left_child)
        right_subtree_height = self.height(node.right_child)
        return False if abs(left_subtree_height - right_subtree_height) > 1 else True

    def pretty_print(self):
        """Prints the tree in a visually appealing way in the terminal."""
        if self._root is None:
            print("(empty tree)")
            return
        
        lines, *_ = self._pretty_print_helper(self._root)
        for line in lines:
            print(line)

    def _pretty_print_helper(self, node):
        """Returns list of strings, width, height, and horizontal coordinate of the root."""
        if node._right_child is None and node._left_child is None:
            line = str(node._value)
            width = len(line)
            height = 1
            middle = width // 2
            return [line], width, height, middle

        # Only left child
        if node._right_child is None:
            lines, n, p, x = self._pretty_print_helper(node._left_child)
            s = str(node._value)
            u = len(s)
            first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s
            second_line = x * ' ' + '/' + (n - x - 1 + u) * ' '
            shifted_lines = [line + u * ' ' for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, n + u // 2

        # Only right child
        if node._left_child is None:
            lines, n, p, x = self._pretty_print_helper(node._right_child)
            s = str(node._value)
            u = len(s)
            first_line = s + x * '_' + (n - x) * ' '
            second_line = (u + x) * ' ' + '\\' + (n - x - 1) * ' '
            shifted_lines = [u * ' ' + line for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, u // 2

        # Two children
        left, n, p, x = self._pretty_print_helper(node._left_child)
        right, m, q, y = self._pretty_print_helper(node._right_child)
        s = str(node._value)
        u = len(s)
        first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s + y * '_' + (m - y) * ' '
        second_line = x * ' ' + '/' + (n - x - 1 + u + y) * ' ' + '\\' + (m - y - 1) * ' '
        if p < q:
            left += [n * ' '] * (q - p)
        elif q < p:
            right += [m * ' '] * (p - q)
        zipped_lines = zip(left, right)
        lines = [first_line, second_line] + [a + u * ' ' + b for a, b in zipped_lines]
        return lines, n + m + u, max(p, q) + 2, n + u // 2