from data_structures.doubly_linked_list import DoublyLinkedList
import unittest

# python -m unittest test.test_doubly_linked_list

class TestDoublyLinkedList(unittest.TestCase):
    def setUp(self):
        self.ll = DoublyLinkedList()
        self.ll.insert_head(0)
        self.ll.insert_tail(1)
        self.ll.insert_tail(2)
        self.ll.insert_tail(3)
        self.ll.insert_tail(4)
        self.ll.insert_tail(5)
        self.ll.insert_tail(6)
        # [ 0 1 2 3 4 5 6 ]
        # return super().setUp()
    
    def test_insert_head(self):
        self.ll.insert_head(35)
        self.assertEqual(self.ll.head_node.value, 35)
        self.assertEqual(len(self.ll), 8)

    def test_insert_tail(self):
        self.ll.insert_tail(90)
        self.assertEqual(self.ll.tail_node.value, 90)
        self.assertEqual(len(self.ll), 8)
        
    def test_delete_head(self):
        self.ll.delete_head()
        self.assertEqual(self.ll.head_node.value, 1)
        self.assertEqual(len(self.ll), 6)

    def test_delete_tail(self):
        self.ll.delete_tail()
        self.assertEqual(self.ll.tail_node.value, 5)
        self.assertEqual(len(self.ll), 6)
    
    def test_delete_index(self):
        # [ 0 1 2 3 4 5 6 ]
        
        self.ll.delete_index(3) # the value at index 3 is 3
        self.assertEqual(len(self.ll), 6)
        
        self.ll.delete_index(0)
        self.assertEqual(self.ll.head_node.value, 1)
        self.assertEqual(len(self.ll), 5)
        
        self.ll.delete_index(len(self.ll) - 1)
        self.assertEqual(self.ll.tail_node.value, 5)
        self.assertEqual(len(self.ll), 4)

    def test_delete_value(self):
        # [ 0 1 2 3 4 5 6 ]
        
        self.ll.delete_value(5)
        self.assertTrue(5 not in self.ll)
        self.assertEqual(len(self.ll), 6)
        
    def test_find_by_index(self):
        # [ 0 1 2 3 4 5 6 ]
        
        for idx in range(len(self.ll)):
            self.assertEqual(self.ll.find_by_index(idx), self.ll[idx])
