# -*- coding: utf-8 -*-
"""Internal node implementation for the gentrie package."""

from copy import deepcopy
from textwrap import indent
from typing import Any, Optional, TYPE_CHECKING

from .protocols import TrieKeyToken
from .types import TrieId

if TYPE_CHECKING:
    from .trie import GeneralizedTrie


class Node:  # pylint: disable=too-few-public-methods
    """A node in the trie.

    A node is a container for a key in the trie. It has a unique identifier
    and a reference to the key.

    Attributes:
        ident (TrieId): Unique identifier for the key.
        token (TrieKeyToken): Token for the key.
        parent (Optional[GeneralizedTrie | Node): Reference to the parent node.
        children (dict[TrieKeyToken, Node]): Dictionary of child nodes.
    """

    def __init__(self, token: TrieKeyToken, parent: "GeneralizedTrie | Node", value: Optional[Any] = None) -> None:
        self.ident: Optional[TrieId] = None
        self.token: TrieKeyToken = token
        self.value: Optional[Any] = value
        self.parent: Optional["GeneralizedTrie | Node"] = parent
        self.children: dict[TrieKeyToken, "Node"] = {}

    def __str__(self) -> str:
        """Generates a stringified version of the trie for visual examination.

        The output IS NOT executable code but more in the nature of debug and testing support."""
        output: list[str] = ["{"]
        if self.parent is None:
            output.append("  parent = None")
        else:
            from .trie import GeneralizedTrie  # pylint: disable=import-outside-toplevel
            if isinstance(self.parent, GeneralizedTrie):
                output.append("  parent = root node")
            else:
                output.append(f"  parent = {repr(self.parent.token)}")
        output.append(f"  node token = {repr(self.token)}")
        if self.ident:
            output.append(f"  trie id = {self.ident}")
        if self.children:
            output.append("  children = {")
            for child_key, child_value in self.children.items():
                output.append(f"    {repr(child_key)} = " + indent(str(child_value), "    ").lstrip())
            output.append("  }")
        output.append("}")
        return "\n".join(output)

    def _as_dict(self) -> dict[str, Any]:
        """Converts the node to a dictionary representation.

        This is useful for tests and debugging purposes and is not intended
        for general purpose serialization of the trie. It's output is not
        suitable for use with :func:`json.dumps()` or similar functions and
        is subject to change without notice. This is NOT a public API - it is
        intended for internal use by tests only.

        Returns:
            :class:`dict[str, Any]`: Dictionary representation of the node.
            The dictionary contains the following keys:
                - "ident": The unique identifier of the node.
                - "token": The token of the node.
                - "value": The value associated with the node.
                - "parent": The token of the parent node, or None if there is no parent.
                - "children": A dictionary of child nodes, where the keys are the tokens
                  of the child nodes and the values are dictionaries representing the child nodes.
        """
        # pylint: disable=protected-access
        # Using deepcopy to ensure that the dictionary is a copy of the data in the trie,
        # not a dictionary of live references to it
        return deepcopy(
            {
                "ident": self.ident,
                "token": self.token,
                "value": self.value,
                "parent": self.parent.token if self.parent else None,
                "children": {str(k): v._as_dict() for k, v in self.children.items()},
            }
        )
