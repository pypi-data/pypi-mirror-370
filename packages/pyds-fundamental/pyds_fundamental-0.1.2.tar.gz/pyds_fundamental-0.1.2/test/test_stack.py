import unittest
from data_structures.stack import StackArray, LinkedStack

# python -m unittest test.test_stack

class StackTestMixin:
    StackClass = None  # will be set in subclasses

    def test_initialization_empty(self):
        stack = self.StackClass()
        self.assertTrue(stack.is_empty())
        self.assertEqual(len(stack), 0)
        self.assertIsNone(stack.top)
        
    def test_initialization_with_values(self):
        stack = self.StackClass(1, 2, 3)
        self.assertEqual(len(stack), 3)
        self.assertEqual(stack.top, 3)
        
    def test_push_and_top(self):
        stack = self.StackClass()
        stack.push(5)
        self.assertEqual(stack.top, 5)
        self.assertEqual(len(stack), 1)

    def test_pop(self):
        stack = self.StackClass(1, 2)
        top = stack.pop()
        self.assertEqual(top, 2)
        self.assertEqual(len(stack), 1)

    def test_pop_empty_raises(self):
        stack = self.StackClass()
        with self.assertRaises(Exception):
            stack.pop()
            
    def test_peek(self):
        stack = self.StackClass(1, 2)
        self.assertEqual(stack.peek(), 2)
        self.assertEqual(len(stack), 2)

    def test_peek_empty_raises(self):
        stack = self.StackClass()
        with self.assertRaises(IndexError):
            stack.peek()

    def test_clear(self):
        stack = self.StackClass(1, 2, 3)
        stack.clear()
        self.assertTrue(stack.is_empty())

    def test_copy(self):
        stack = self.StackClass(1, 2, 3)
        copy_stack = stack.copy()
        self.assertEqual(len(copy_stack), len(stack))
        self.assertEqual(list(copy_stack), list(stack))
        stack.pop()
        self.assertNotEqual(len(copy_stack), len(stack))  # deep copy check

    def test_iter_and_contains(self):
        stack = self.StackClass(1, 2, 3)
        self.assertEqual(list(stack), [3, 2, 1])  # top first
        self.assertIn(2, stack)
        self.assertNotIn(99, stack)
        
class TestStackArray(StackTestMixin, unittest.TestCase):
    StackClass = StackArray
    
class TestLinkedStack(StackTestMixin, unittest.TestCase):
    StackClass = LinkedStack
    