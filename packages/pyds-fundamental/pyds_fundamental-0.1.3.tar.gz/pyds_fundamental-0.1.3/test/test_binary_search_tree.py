import unittest
from data_structures.binary_search_tree import BinarySearchTree

# python -m unittest test.test_binary_search_tree

class TestBinarySearchTree(unittest.TestCase):
    def setUp(self):
        self.bst = BinarySearchTree(5)
        # return super().setUp()
        self.bst.insert(2)
        self.bst.insert(9)
        self.bst.insert(1)
        self.bst.insert(3)
        self.bst.insert(7)
        self.bst.insert(13)
        self.bst.insert(8)
    
    def test_check_root(self):
        self.assertEqual(self.bst.root.value, 5)
    
    def test_if_empty(self):
        bst = BinarySearchTree()
        with self.assertRaises(Exception):
            bst._check_empty()

    def test_check_output_type(self):
        with self.assertRaises(TypeError):
            self.bst._check_param_type()
        with self.assertRaises(TypeError):
            self.bst._check_param_type(123)
        with self.assertRaises(Exception):
            self.bst._check_param_type("something else")
    
    def test_inorder_traversal(self):
        # list
        self.assertEqual(self.bst.inorder_traversal(), [1, 2, 3, 5, 7, 8, 9, 13])
    
    def test_preorder_traversal(self):
        # list
        self.assertEqual(self.bst.preorder_traversal(), [5, 2, 1, 3, 9, 7, 8, 13])
        
    def test_postorder_traversal(self):
        # list
        self.assertEqual(self.bst.postorder_traversal(), [1, 3, 2, 8, 7, 13, 9, 5])
    
    def test_levelorder_traversal(self):
        self.assertEqual(self.bst.levelorder_traversal(), [5, 2, 9, 1, 3, 7, 13, 8])
        bst = BinarySearchTree()
        self.assertIsNone(bst.levelorder_traversal())
    