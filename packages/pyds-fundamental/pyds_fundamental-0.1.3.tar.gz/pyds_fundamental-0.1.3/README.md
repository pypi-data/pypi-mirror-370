# `pyds-fundamental`: An Implementation of Data Structures

`pyds-fundamental` / `data_structures` contains implementations of various data structures. 

Currently trying to make this a fully functioning library where you can basically use implemented data structures as-intended.

To see all the functionalities, check out the [document here.](https://999-juicewrld.github.io/data_structures/data_structures.html)

Current data structures are:
- Linked Lists
    - Singly Linked List
    - Doubly Linked List
- Stacks
    - Array Stack
    - Linked Stack (Using Linked List)
- Queues
    - Array Queue
    - Linked Queue (Using Linked List)
    - Circular Queue
    - Priority Qeueue (Using Linked List)
- Binary Search Tree

**Currently Working On:** *AVL-Trees.*

To download this package, go to terminal:
```sh
pip install pyds-fundamental
```

Example usage:
```py
from data_structures import BinarySearchTree, AVLTree

bst = BinarySearchTree()
bst.insert(12)
bst.insert(8)
bst.insert(16)

for node in bst.inorder_traversal():
    print(node)

# 8
# 12
# 16

import random

avl = AVLTree()
for _ in range(20):
    avl.insert(random.randint(0, 100))
avl.pretty_print()

# Output:

           ________59___________     
          /                     \    
   ______15___           ______88_   
  /           \         /         \  
 _9___       20_       66___     95_ 
/     \     /   \     /     \       \
3    13_   19  41_   64    70_     98
 \  /   \         \       /   \      
 8 11  13        46      68  75 
```
