"""Implementation of AVL Trees."""

from .node import TreeNode
from .binary_search_tree import BinarySearchTree
import logging

_sentinel = object()
ENABLE_AVL_LOGGING = False

if ENABLE_AVL_LOGGING:
    ENABLE_AVL_LOGGING = logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        # format='%(levelname)s: %(message)s', only print the text
        handlers=[logging.StreamHandler()]
    )
else:
    logging.disable(logging.CRITICAL)

class AVLTreeNode(TreeNode):
    """This is the default used node for `AVLTree`. Inherits `TreeNode`.
    
    Attributes:
        balance_factor (int): Balance factor of the node (height of the left subree - height of the right subtree).
    """
    def __init__(self, value=None, left_child=None, right_child=None, parent=None, balance_factor=0):
        super().__init__(value, left_child, right_child, parent)
        self._balance_factor =  balance_factor
    
    @property
    def balance_factor(self):
        """int: Return `balance_factor` attribute of the object."""
        return self._balance_factor
    
    @balance_factor.setter
    def balance_factor(self, value):
        """Set the value of the `balance_factor`."""
        self._balance_factor = value
    
class AVLTree(BinarySearchTree):
    """AVL Trees are self-balancing binary search trees. Thus, `AVLTree` object inherits `BinarySearchTree` class."""
    
    def __init__(self, value=None, node=AVLTreeNode):
        """Initialize an AVL Tree.
        
        Args:
            value (any): Value of the root node (if exists).
            node (any): Default node to construct the tree. Defaults to `AVLTreeNode`.
        """
        self._Node = node
        if value is None:
            self.root = None
            self._size = 0
        else:
            self._root = self._Node(value)
            self._size = 1
    
    def calculate_balance_factor(self, node=_sentinel):
        if node is _sentinel:
            return self.height(self.root.left_child) - self.height(self.root.right_child)
        else:
            return self.height(node.left_child) - self.height(node.right_child)

    def insert(self, data):
        node = self.insert_iterative(data)
        self._rebalance_path(node)
        
    def _rebalance_path(self, node, deletion=False):
        while node is not None:
            node.balance_factor = self.calculate_balance_factor(node)
            if abs(node.balance_factor) > 1:
                self._rebalance(node, deletion)
            # after rebalancing, calculate balance factors again
            node = node.parent
    
    def _rebalance(self, node, deletion=False):
        case = self._get_rotation_case(node, deletion) 
        match case:
            case "LL":
                logging.info(f"Case {case} at node {node.value}, pivot={self._get_pivot(node, case).value}")
                self._rotate_right(node)
            case "LR":
                logging.info(f"Case {case} at node {node.value}, pivot={self._get_pivot(node, case).value}")
                self._rotate_left_right(node)
            case "RR":
                logging.info(f"Case {case} at node {node.value}, pivot={self._get_pivot(node, case).value}")
                self._rotate_left(node)
            case "RL":
                logging.info(f"Case {case} at node {node.value}, pivot={self._get_pivot(node, case).value}")
                self._rotate_right_left(node)
            case "R0":
                logging.info(f"Case {case} at node {node.value}, "
                             f"node.bf = {node.balance_factor}, "
                             f"child.bf = {node.right_child.balance_factor}"
                             )
                self._rotate_right(node)
            case "R-1":
                logging.info(f"Case {case} at node {node.value}, "
                             f"node.bf = {node.balance_factor}, "
                             f"child.bf = {node.right_child.balance_factor}"
                             )
                self._rotate_left_right(node)
            case "R1":
                logging.info(f"Case {case} at node {node.value}, "
                             f"node.bf = {node.balance_factor}, "
                             f"child.bf = {node.right_child.balance_factor}"
                             )
                self._rotate_right(node)
            case "L0":
                logging.info(f"Case {case} at node {node.value}, "
                             f"node.bf = {node.balance_factor}, "
                             f"child.bf = {node.right_child.balance_factor}"
                             )
                self._rotate_left(node)
            case "L-1":
                logging.info(f"Case {case} at node {node.value}, "
                             f"node.bf = {node.balance_factor}, "
                             f"child.bf = {node.right_child.balance_factor}"
                             )
                self._rotate_right_left(node)
            case "L1":
                logging.info(f"Case {case} at node {node.value}, "
                             f"node.bf = {node.balance_factor}, "
                             f"child.bf = {node.right_child.balance_factor}"
                             )
                self._rotate_left(node)
    
    def _rotate_right(self, node): # LL
        target_node = node.left_child
        if node.parent is not None:
            if node.parent.left_child == node:
                node.parent.left_child = target_node
            elif node.parent.right_child == node:
                node.parent.right_child = target_node
        else:
            self.root = target_node
            self.root.parent = None
        
        node.left_child = target_node.right_child
        if target_node.right_child is not None:
            target_node.right_child.parent = node
            
        target_node.right_child = node
        target_node.parent = node.parent
        node.parent = target_node
        
        # fix balance factor
        target_node.balance_factor = self.calculate_balance_factor(target_node)
        node.balance_factor = self.calculate_balance_factor(node)
        
    def _rotate_left(self, node): # RR
        target_node = node.right_child
        if node.parent is not None:
            if node.parent.left_child == node:
                node.parent.left_child = target_node
            elif node.parent.right_child == node:
                node.parent.right_child = target_node
        else:
            self.root = target_node
            self.root.parent = None
        
        node.right_child = target_node.left_child
        if target_node.left_child is not None:
            target_node.left_child.parent = node
            
        target_node.left_child = node
        target_node.parent = node.parent
        node.parent = target_node
        
        # fix balance factor
        target_node.balance_factor = self.calculate_balance_factor(target_node)
        node.balance_factor = self.calculate_balance_factor(node)

    def _rotate_left_right(self, node): # LR
        self._rotate_left(node.left_child)
        self._rotate_right(node)
        
        node.balance_factor = self.calculate_balance_factor(node)
        if node.left_child:
            node.left_child.balance_factor = self.calculate_balance_factor(node.left_child)
        pivot = node.parent if node.parent is not None else self.root
        pivot.balance_factor = self.calculate_balance_factor(pivot)
    
    def _rotate_right_left(self, node): # RL
        self._rotate_right(node.right_child)
        self._rotate_left(node)

        node.balance_factor = self.calculate_balance_factor(node)
        if node.right_child:
            node.right_child.balance_factor = self.calculate_balance_factor(node.right_child)
        pivot = node.parent if node.parent is not None else self.root
        pivot.balance_factor = self.calculate_balance_factor(pivot)
    
    def _get_pivot(self, node, case):
        match case:
            case "LL":
                return node.left_child
            case "LR":
                return node.left_child.right_child
            case "RR":
                return node.right_child
            case "RL":
                return node.right_child.left_child
    
    def _get_rotation_case(self, node, deletion=False):
        if deletion is True:
            if node.balance_factor > 1:
                match node.left_child.balance_factor:
                    case 0:
                        return "R0"
                    case -1:
                        return "R-1"
                    case 1:
                        return "R1"
            elif node.balance_factor < -1:
                match node.right_child.balance_factor:
                    case 0:
                        return "L0"
                    case -1:
                        return "L1"
                    case 1:
                        return "L-1"
        else: # insertion
            if node.balance_factor > 1:
                if node.left_child.balance_factor >= 0:
                    return "LL"
                return "LR" # node.left_child.balance_factor < 0
            elif node.balance_factor < -1:
                if node.right_child.balance_factor <= 0:
                    return "RR"
                return "RL" # node.right_child.balance_factor > 0
    
    def delete(self, value):
        node = self.search_element(value)
        parent_node = node.parent
        self.delete_node(node.value, node)
        self._rebalance_path(parent_node, deletion=True)


if __name__ == "__main__":
    import random
    bst = AVLTree()
    for _ in range(20):
        bst.insert(random.randint(0, 100))
    bst.pretty_print()