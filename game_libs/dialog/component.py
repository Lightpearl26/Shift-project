#-*- coding: utf-8 -*-

"""dialog.component
___________________________________________________________________________________________________
This module defines the DialogComponent class, which is responsible for displaying dialog boxes
in the game.
___________________________________________________________________________________________________
(c) Lafiteau Franck 2026
"""

# import built-in modules
from __future__ import annotations
from typing import Optional


# ----- Node -----
class Node:
    """
    Data structure of a node
    """


# ----- Tree -----
class Tree:
    """
    Data structure of a tree
    
    Operators for building dialog trees:
    - `node | tree` : Attach a node to a tree (creates new tree with node as root)
    - `tree1 + tree2` : Combine two trees as siblings (for branching options)
    - `tree1 >> tree2` : Chain trees sequentially (tree2 follows tree1)
    """
    def __init__(self, node: Node, children: list[Tree]):
        self.node = node
        self.children = children
        
    def __repr__(self):
        return f"Tree(node={self.node}, children={self.children})"
    
    def __add__(self, other: Tree) -> Tree:
        """
        Combine two trees as siblings (useful for creating multiple choice branches).
        Returns a new tree with no node and both trees as children.
        """
        return Tree(None, [self, other])
    
    def __or__(self, other: Node) -> Tree:
        """
        Attach a node to this tree (node becomes the root, preserving children).
        Usage: node | tree
        """
        if isinstance(other, Tree):
            raise TypeError("Cannot use '|' operator between two Tree instances. Its intended to attach a node to a tree.")
        return Tree(other, self.children)
    
    def __ror__(self, other: Node) -> Tree:
        """
        Attach a node to this tree (reversed operator).
        Usage: node | tree
        """
        if isinstance(other, Tree):
            raise TypeError("Cannot use '|' operator between two Tree instances. Its intended to attach a node to a tree.")
        return Tree(other, self.children)
    
    def __rshift__(self, other: Tree) -> Tree:
        """
        Chain this tree to another tree sequentially.
        Returns this tree with the other tree appended as a child.
        Usage: tree1 >> tree2 (tree2 follows tree1)
        """
        if isinstance(other, Node):
            # If other is just a node, wrap it in a tree
            other = Tree(other, [])
        # Add other as a child to self
        new_children = self.children + [other]
        return Tree(self.node, new_children)


# ----- DialogParagraph -----
class DialogParagraph(Node):
    """
    A dialog paragraph is a node of the dialog tree. It contains the text to display.
    """
    def __init__(self, lines: list[str]):
        self.lines = lines
    
    def __repr__(self):
        return f"DialogParagraph(lines={self.lines})"

    def __matmul__(self, options_names: list[str]) -> DialogOption:
        """
        Create a DialogOption from this paragraph and the given option names.
        Usage: paragraph @ ["Yes", "No"]
        """
        return DialogOption(self, options_names)


# ----- DialogGoto -----
class DialogGoto(Node):
    """
    A dialog goto is a reference to another dialog by name.
    It must be resolved by the dialog runtime or manager.
    """
    def __init__(self, target_name: str):
        self.target_name = target_name
    
    def __repr__(self):
        return f"DialogGoto(target_name={self.target_name})"


# ----- DialogOption -----
class DialogOption(Node):
    """
    A dialog option is a tree that contains a dialog paragraph and its children are the options that the player can choose.
    """
    def __init__(self, paragraph: DialogParagraph, options_names: list[str]):
        self.paragraph = paragraph
        self.options_names = options_names
        
    def __repr__(self):
        return f"DialogOption(paragraph={self.paragraph}, options_names={self.options_names})"

    def __floordiv__(self, branches: list[Dialog]) -> Dialog:
        """
        Attach branches to this option node and return a Dialog tree.
        Usage: (paragraph @ ["Yes", "No"]) // [branch_yes, branch_no]
        """
        if len(branches) != len(self.options_names):
            raise ValueError(
                "Branches count must match options count. "
                f"Options: {self.options_names}, branches: {len(branches)}."
            )
        return Dialog(self, branches)


# ----- Dialog -----
class Dialog(Tree):
    """
    A dialog is a tree that contains dialog paragraphs and options.
    If the node is a DialogParagraph, it has no options and there is max one child, which is the next dialog paragraph.
    If the node is a DialogOption, it has options and its children are the options that the player can choose.
    If the node is None, then it means the Dialog ended and there is no more dialog to display.
    """
    def __init__(self, node: Node, children: list[Dialog]):
        super().__init__(node, children)

    @property
    def paragraph(self) -> Optional[DialogParagraph]:
        """
        Get the dialog paragraph of the current node.
        If the current node is None, it returns None, which means the dialog ended
        and there is no more dialog to display.
        DialogGoto nodes return None as they don't have text to display, only navigate.
        """
        if isinstance(self.node, DialogParagraph):
            return self.node
        elif isinstance(self.node, DialogOption):
            return self.node.paragraph
        elif isinstance(self.node, DialogGoto):
            # DialogGoto doesn't display anything, it just navigates
            return None
        else:
            return None

    @property
    def options_names(self) -> Optional[list[str]]:
        """
        Get the options names of the current node.
        If it returns None, it means there is no options to choose, which means the current node
        is a DialogParagraph or the dialog ended.
        """
        if isinstance(self.node, DialogOption):
            return self.node.options_names
        else:
            return None

    @property
    def end(self) -> bool:
        """
        Check if the dialog ended, which means there is no more dialog to display.
        It returns True if the current node is None, which means the dialog ended.
        """
        return self.node is None

    def __rshift__(self, other: Dialog) -> Dialog:
        """
        Chain dialogs sequentially.
        Usage: dialog1 >> dialog2
        """
        if isinstance(other, Node):
            other = Dialog(other, [])
        return _append_to_leaves(self, other)


def _append_to_leaves(dialog: Dialog, next_dialog: Dialog) -> Dialog:
    """
    Append the next dialog to all leaf nodes of the current dialog.
    This allows chaining after choices while preserving branches.
    DialogGoto nodes are not modified.
    """
    if dialog is None or dialog.node is None:
        return next_dialog
    
    # Don't append to DialogGoto nodes
    if isinstance(dialog.node, DialogGoto):
        return dialog
    
    if dialog.options_names:
        new_children = [_append_to_leaves(child, next_dialog) for child in dialog.children]
        return Dialog(dialog.node, new_children)
    if len(dialog.children) > 1:
        raise ValueError(
            f"DialogParagraph node cannot have more than one child. Current children: {dialog.children}."
        )
    if dialog.children:
        new_child = _append_to_leaves(dialog.children[0], next_dialog)
        return Dialog(dialog.node, [new_child])
    return Dialog(dialog.node, [next_dialog])
