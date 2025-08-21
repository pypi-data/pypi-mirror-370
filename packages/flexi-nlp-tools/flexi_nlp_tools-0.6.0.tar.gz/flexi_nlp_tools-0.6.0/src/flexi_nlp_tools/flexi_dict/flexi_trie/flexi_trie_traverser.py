from typing import List, Tuple
from collections import deque

from .flexi_trie import FlexiTrieNode
from ..config import DEFAULT_TOPN_LEAVES


class FlexiTrieTraverser:
    """
    A utility class for traversing and interacting with a prefix tree (trie).

    This class provides methods to:
    - Apply a string to the tree and collect the nodes along the path.
    - Retrieve leaf nodes and their associated paths starting from a given node.

    Methods:
        apply_string(node, s): Applies a string to the prefix tree and returns the path of nodes traversed.
        get_node_leaves(node, topn): Collects up to `topn` leaf nodes and their paths from a given starting node.
    """

    @staticmethod
    def apply_string(node: FlexiTrieNode, s: str) -> List[FlexiTrieNode]:
        """
        Traverses the prefix tree using the given string, starting from the specified node.

        Args:
            node (FlexiTrieNode): The starting node of the traversal.
            s (str): The string to apply to the prefix tree.

        Returns:
            List[FlexiTrieNode]: A list of nodes traversed along the path determined by the string.
                                 If a character in the string does not exist in the tree, traversal stops, and the path is returned up to that point.

        Example:
            >>> root = FlexiTrieNode()
            >>> traverser = FlexiTrieTraverser()
            >>> nodes = traverser.apply_string(root, "test")
            >>> print(nodes)  # List of nodes representing the path for "test".
        """
        path_nodes: List[FlexiTrieNode] = []

        for char in s:
            node = node.get(char)
            if not node:
                return path_nodes

            path_nodes.append(node)

        return path_nodes

    @staticmethod
    def get_node_leaves(node: FlexiTrieNode, topn: int = DEFAULT_TOPN_LEAVES) -> List[Tuple[int, List[str]]]:
        """
        Collects leaf node values and their paths from the given starting node.

        Args:
            node (FlexiTrieNode): The starting node of the tree or subtree to begin the search.
            topn (int, optional): The maximum number of leaf nodes to retrieve. Defaults to `DEFAULT_TOPN_LEAVES`.

        Returns:
            List[Tuple[int, List[str]]]: A list of tuples where each tuple contains:
                                          - `int`: The value stored at the leaf node.
                                          - `List[str]`: The sequence of symbols (path) leading to the leaf node.

        Example:
            >>> root = FlexiTrieNode()
            >>> traverser = FlexiTrieTraverser()
            >>> leaves = traverser.get_node_leaves(root, topn=5)
            >>> print(leaves)  # [(value1, ['a', 'b']), (value2, ['c', 'd']), ...]

        Notes:
            - If the number of available leaves is less than `topn`, all leaves will be returned.
            - If the starting node has no leaves, the result will be an empty list.
        """
        queue = deque([(child, [key]) for key, child in node.children.items()])  # Queue holds pairs of (current_node, current_path)
        leaves = []

        while queue:
            current_node, current_path = queue.popleft()

            # If the current node is a leaf (it has values), add its values and paths
            if current_node.values:
                for value in current_node.values:
                    leaves.append((value, current_path))
                    if len(leaves) >= topn:
                        return leaves[:topn]

                if len(leaves) >= topn:
                    return leaves[:topn]

            # Add the children to the queue with the updated path
            queue.extend((child, current_path + [symbol]) for symbol, child in current_node.children.items())

        return leaves[:topn]
