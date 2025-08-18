def print_widget_tree(widget, indent = "", last = True):
    """
        Recursively prints the widget hierarchy in a tree-like format.

        Parameters
        ----------
        widget : tkinter.Widget
            The root widget to start from.
        indent : str
            Current indentation (used internally for recursion).
        last : bool
            Whether this widget is the last child of its parent (for visual formatting).
    """

    if str(widget) == '.':
        print(str(widget))
    else:
        # Format for tree drawing
        branch = "└── " if last else "├── "
        print(indent + branch + str(widget))

        # Prepare indentation for children
        indent += "    " if last else "│   "

    # Convert children dict to list for ordering
    children = list(widget.children.values())
    for i, child in enumerate(children):
        print_widget_tree(child, indent, last=(i == len(children) - 1))
