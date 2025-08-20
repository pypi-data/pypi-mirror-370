# `pyds-fundamental`: An Implementation of Data Structures

`pyds-fundamental` / `data_structures` contains implementations of various data structures. 

Currently trying to make this a fully functioning library where you can basically use implemented data structures as-intended. I will implement AVL & red-black trees, and hopefully graphs.

To see all the functionalities, check out the [document here.](https://999-juicewrld.github.io/data_structures/data_structures.html)

To download this package, go to terminal:
```sh
pip install pyds-fundamental
```

Example usage:
```py
from data_structures import BinarySearchTree

bst = BinarySearchTree()
bst.insert(12)
bst.insert(8)
bst.insert(16)

for node in bst.inorder_traversal():
    print(node)

# 8
# 12
# 16
```

Current data structures are:
- Linked Lists
- Stacks
- Queues
- Binary Search Tree
