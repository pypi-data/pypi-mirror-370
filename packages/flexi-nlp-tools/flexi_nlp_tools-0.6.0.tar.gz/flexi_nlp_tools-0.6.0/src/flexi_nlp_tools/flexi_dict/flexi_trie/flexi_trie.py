from collections import OrderedDict
from typing import Optional, Set, Dict, Union

from ..exceptions import KeyNotFoundError


class FlexiTrie:
    """
    A prefix tree (trie) implementation that stores integer values and maintains ordering of children keys.

    Attributes:
        _node_count (int): The total number of nodes in the trie.
        _root (FlexiTrieNode): The root node of the trie.

    Methods:
        add(keys, value, symbol_weights): Adds a value to the trie along the path specified by `keys`.
        find(keys): Retrieves the set of values stored at the node specified by `keys`.
        __len__(): Returns the total number of nodes in the trie.
        __str__(): Returns a string representation of the trie structure.
    """

    def __init__(self):
        """Initializes the FlexiTrie with an empty root node and sets the node counter to 0."""
        self._node_count = 0
        self._root = FlexiTrieNode(self)

    def __len__(self) -> int:
        """Returns the total number of nodes in the trie."""
        return self._node_count

    def __str__(self) -> str:
        """Returns a string representation of the trie structure."""
        def dfs(node: 'FlexiTrieNode') -> str:
            children_s = ', '.join(
                [f'{k}⟶{list(child.values) or ""}{dfs(child)}' for k, child in node.children.items()]
            )
            return f'{{{children_s}}}' if children_s else ""

        return f'FlexiTrie(node_count={self._node_count}, trie={dfs(self._root)})'

    @property
    def node_count(self) -> int:
        """Returns the current number of nodes in the trie."""
        return self._node_count

    def inc_node_count(self):
        """Increments the node count by one."""
        self._node_count += 1

    def add(self, keys: str, value: int, symbol_weights: Optional[Dict[str, float]] = None):
        """
        Adds a value to the trie along the path specified by the sequence of keys.

        Args:
            keys (str): A string representing the path to the node where the value will be stored.
            value (int): The value to be stored at the final node.
            symbol_weights (Optional[Dict[str, float]]): Optional weights for ordering children keys.
        """
        node = self._root
        for key in keys:
            node = node.add_child(key, symbol_weights)
        node.add_value(value)

    def find(self, keys: str) -> Optional[Set[int]]:
        """
        Retrieves the set of values stored at the node specified by the path of keys.

        Args:
            keys (str): A string representing the path to the node.

        Returns:
            Optional[Set[int]]: The set of values stored at the final node, or None if the path does not exist.
        """
        node = self._root
        for key in keys:
            node = node.get(key)
            if node is None:
                return None
        return node.values

    @property
    def root(self):
        """Returns the root node of the trie."""
        return self._root


class FlexiTrieNode:
    """
    A node in the FlexiTrie structure.

    Attributes:
        _trie (FlexiTrie): Reference to the parent trie.
        _idx (int): A unique index identifying this node.
        children (OrderedDict[str, FlexiTrieNode]): Ordered dictionary of child nodes.
        values (Set[int]): Set of integer values stored at this node.

    Methods:
        add_child(key, symbol_weights): Adds a child node for the given key if it does not exist.
        get(key): Retrieves the child node corresponding to the given key.
        add_value(value): Adds a single integer value to the node.
        add_values(values): Adds multiple integer values to the node.
    """

    def __init__(self, trie: FlexiTrie):
        """Initializes a node with a reference to its parent trie."""
        self._trie = trie
        self._idx = self._trie.node_count
        self._trie.inc_node_count()
        self.children: OrderedDict[str, 'FlexiTrieNode'] = OrderedDict()
        self.values: Set[Union[int, str]] = set()

    def add_child(self, key: str, symbol_weights: Optional[Dict[str, float]] = None) -> 'FlexiTrieNode':
        """
        Adds a child node for the given key if it does not already exist.

        Args:
            key (str): The key for the child node.
            symbol_weights (Optional[Dict[str, float]]): Optional weights for ordering children keys.

        Returns:
            FlexiTrieNode: The child node corresponding to the given key.
        """
        if key not in self.children:
            self.children[key] = FlexiTrieNode(self._trie)
            if symbol_weights:
                self.children = OrderedDict(
                    sorted(self.children.items(), key=lambda x: -symbol_weights.get(x[0], 0))
                )
        return self.children[key]

    def get(self, key: str) -> Optional['FlexiTrieNode']:
        """
        Retrieves the child node for the given key.

        Args:
            key (str): The key of the child node.

        Returns:
            Optional[FlexiTrieNode]: The child node if it exists, or None if it does not exist.
        """
        return self.children.get(key)

    def __getitem__(self, key: str) -> 'FlexiTrieNode':
        """
        Allows indexing to retrieve child nodes.

        Args:
            key (str): The key of the child node.

        Returns:
            FlexiTrieNode: The child node corresponding to the key.

        Raises:
            KeyError: If the key does not exist.
        """
        node = self.get(key)
        if node is None:
            raise KeyNotFoundError(key)
        return node

    def add_value(self, value: int):
        """
        Adds a single integer value to this node.

        Args:
            value (int): The value to add.
        """
        if value not in self.values:
            self.values.add(value)

    def add_values(self, values: Set[int]):
        """
        Adds multiple integer values to this node.

        Args:
            values (Set[int]): A set of values to add.
        """
        self.values.update(values)

    def __str__(self) -> str:
        """Returns a string representation of the node."""
        return f'FlexiTrieNode(idx={self._idx}, values={self.values}, children={list(self.children.keys())})'

    @property
    def idx(self):
        """Returns the unique index of this node."""
        return self._idx

    @property
    def tree(self):
        """Returns the parent trie of this node."""
        return self._trie
