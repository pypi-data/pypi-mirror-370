from data_structures.linked_list import LinkedList
import unittest

# python -m unittest test.test_linked_list

class TestLinkedList(unittest.TestCase):
    def setUp(self):
        self.ll = LinkedList()
        self.ll.insert_head(1)
        self.ll.insert_tail(2)
        self.ll.insert_tail(3)
        self.ll.insert_tail(4)
        self.ll.insert_head(0)
        self.ll.insert_head(-1)
        self.ll.insert_tail(5)
        # [ -1 0 1 2 3 4 5 ]
        # size: 7
        # print(f"the initial list: {self.ll}")
        # return super().setUp()
    
    def test_insert_head(self):
        self.ll.insert_head(35)
        self.assertEqual(self.ll.head_node.value, 35)
        self.assertEqual(len(self.ll), 8)
        # print(self.ll)
    
    def test_insert_tail(self):
        self.ll.insert_tail(44)
        self.assertEqual(self.ll[-1], 44)
        # print([node for node in self.ll])
        # print(len(self.ll))
        self.assertEqual(len(self.ll), 8)
        self.assertEqual(self.ll.tail_node.value, 44)
    
    def test_insert_index(self):
        # [ -1 0 1 2 3 4 5 ]
        self.ll.insert_index(0, 10)
        self.assertEqual(len(self.ll), 8)
        
        self.ll.insert_index(7, 15)
        self.assertEqual(len(self.ll), 9)
        
    def test_delete_head(self):
        self.ll.delete_head()
        self.assertEqual(len(self.ll), 6)
        self.assertEqual(self.ll.head_node.value, 0)
        self.assertEqual(self.ll.head_node.next_node.value, 1)
        self.assertTrue(self.ll.tail_node.value, 0)
        
    def test_delete_tail(self):
        self.ll.delete_tail()
        self.assertEqual(len(self.ll), 6)
        self.assertEqual(self.ll[-1], 4)
        self.assertEqual(self.ll.tail_node.value, 4)

    def test_delete_index(self):
        # [ -1 0 1 2 3 4 5 ]
        self.ll.delete_index(3) # the value is 2
        self.assertTrue(2 not in self.ll)
        
        self.ll.delete_index(0)
        self.assertEqual(len(self.ll), 5)
        self.assertEqual(self.ll.head_node.value, 0)
        
        self.ll.delete_index(len(self.ll) - 1)
        self.assertEqual(len(self.ll), 4)
        self.assertEqual(self.ll[-1], 4)

    def test_delete_by_value(self):
        # [ -1 0 1 2 3 4 5 ]
        self.ll.delete_value(-1)
        self.assertTrue(-1 not in self.ll)
        self.assertEqual(len(self.ll), 6)
        
        self.ll.delete_value(5)
        self.assertTrue(5 not in self.ll)
        self.assertEqual(len(self.ll), 5)
        self.assertTrue(self.ll[-1], 4)
        
    def test_find_by_index(self):
        # [ -1 0 1 2 3 4 5 ]
        for idx in range(len(self.ll)):
            self.assertEqual(self.ll.find_by_index(idx), self.ll[idx])