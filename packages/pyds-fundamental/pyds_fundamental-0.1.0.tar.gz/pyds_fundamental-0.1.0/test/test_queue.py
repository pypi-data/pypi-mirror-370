import unittest
from data_structures.queues import QueueArray, LinkedQueue, CircularQueue, PriorityQueue

# python -m unittest test.test_queue

class QueueTestMixin:
    QueueClass = None
    
    def test_initialization_empty(self):
        queue = self.QueueClass()
        self.assertTrue(queue.is_empty())
        self.assertEqual(queue.size, 0)
        self.assertIsNone(queue.front)
        self.assertIsNone(queue.rear)
    
    def test_initialization_with_values(self):
        queue = self.QueueClass(1, 2, 3)
        self.assertEqual(len(queue), 3)
        self.assertEqual(queue.front, 1)
        self.assertEqual(queue.rear, 3)
    
    def test_enqueue(self):
        queue = self.QueueClass()
        queue.enqueue(5)
        self.assertEqual(queue.front, 5)
        self.assertEqual(len(queue), 1)
    
    def test_dequeue(self):
        queue = self.QueueClass(1, 2, 3, 4, 5)
        initial_size = queue.size
        for i in range(len(queue)):
            self.assertEqual(queue.front, queue[0])
            self.assertEqual(len(queue), initial_size - i)    
            queue.dequeue()
        
    def test_dequeue_raises(self):
        queue = self.QueueClass()
        with self.assertRaises(Exception):
            queue.dequeue()
    
    def test_clear(self):
        queue = self.QueueClass(1, 2, 3, 4, 5)
        queue.clear()
        self.assertTrue(queue.is_empty())
        
    def test_copy(self):
        queue = self.QueueClass(1, 2, 3)
        copy_queue = queue.copy()
        self.assertEqual(len(copy_queue), len(queue))
        self.assertEqual(list(copy_queue), list(queue))
        queue.dequeue()
        self.assertNotEqual(len(copy_queue), len(queue))
        
    def test_iter_and_contains(self):
        queue = self.QueueClass(40, 50, 60, 70, 80)
        self.assertEqual(list(queue), [40, 50, 60, 70, 80])
        self.assertIn(70, queue)
        self.assertNotIn(999, queue)

class TestCircularQueueWrap(unittest.TestCase):
    def test_wraparound(self):
        queue = CircularQueue(1, 2, 3, capacity=4)
        queue.dequeue()
        queue.enqueue(5)
        queue.enqueue(99)
        self.assertEqual(queue.front, 2)
        self.assertEqual(queue.rear, 99)
        self.assertEqual(list(queue), [2, 3, 5, 99])
        self.assertEqual(queue.front_idx, 1)
        queue.dequeue()
        self.assertEqual(queue.front_idx, 2)
        self.assertEqual(queue.rear_idx, 0)

class TestQueueArray(QueueTestMixin, unittest.TestCase):
    QueueClass = QueueArray
    
class TestLinkedQueue(QueueTestMixin, unittest.TestCase):
    QueueClass = LinkedQueue
    
class TestCircularQueue(QueueTestMixin, unittest.TestCase):
    QueueClass = CircularQueue
    
class TestPriorityQueue(unittest.TestCase):
    def test_initialization_empty(self):
        queue = PriorityQueue()
        self.assertTrue(queue.is_empty())
        self.assertEqual(queue.size, 0)
        self.assertIsNone(queue.front)
        self.assertIsNone(queue.rear)
    
    def test_enqueue(self):
        queue = PriorityQueue()
        queue.enqueue(1, 5)
        queue.enqueue(2, 7)
        queue.enqueue(3, 5)
        queue.enqueue(4, 0)
        queue.enqueue(5, 19)
        self.assertEqual(queue.front, 5)
        self.assertEqual(queue.rear, 4)
        self.assertEqual(list(queue), [5, 2, 1, 3, 4])
    
    def test_dequeue_empty(self):
        queue = PriorityQueue()
        with self.assertRaises(Exception):
            queue.dequeue()
        