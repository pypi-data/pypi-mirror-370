from dlubal.api.common.packing import get_internal_value, set_internal_value


def _get_subtree_item(subtree, path: list[str]):
    """
    Recursively retrieve an item from a subtree based on the specified path.

    Args:
        subtree: The starting subtree object which may have children.
        path (list[str]): A list of keys representing the path to the desired item.

    Returns:
        The subtree item at the specified path if found, otherwise None.
    """
    if not path:
        return subtree

    if not hasattr(subtree, 'children'):
        return None
    for child in subtree.children:
        if hasattr(child, 'key') and child.key == path[0]:
            return _get_subtree_item(child, path[1:])
    return None


def get_tree_item(tree, path: list[str]):
    """
    Retrieve an item from a tree table protobuf message based on the specified path.

    Args:
        tree: The root tree object which contains rows.
        path (list[str]): A list of keys representing the path to the desired item.

    Returns:
        The tree item at the specified path if found, otherwise None.
    """
    if not path:
        return tree

    if not hasattr(tree, 'rows'):
        return None
    for row in tree.rows:
        if hasattr(row, 'key') and row.key == path[0]:
            return _get_subtree_item(row, path[1:])
    return None


def get_tree_value(tree, path: list[str]) -> int | float | str | bool | None:
    """
    Retrieve the value from a tree table protobuf message at the specified path.

    Args:
        tree: The root tree object which contains rows.
        path (list[str]): A list of keys representing the path to the desired value.

    Returns:
        The value at the specified path if found, otherwise None.
    """
    row = get_tree_item(tree, path)
    if not row:
        return None
    return get_internal_value(row.value)


def set_tree_value(tree, path: list[str], value: int | float | str | bool | None):
    """
    Set a value in a tree table protobuf message at the specified path.
    Creates intermediate rows if they do not exist.

    Args:
        tree: The root tree object which contains rows or children.
        path (list[str]): A list of keys representing the path to the desired item.
        value (int | float | str | bool | None): The value to set at the specified path.

    Returns:
        None
    """
    if not path:
        return

    current = tree
    for key in path[:-1]:
        # Determine container: rows or children
        if hasattr(current, 'rows'):
            container = current.rows
        elif hasattr(current, 'children'):
            container = current.children
        else:
            # Cannot proceed if no container
            return

        # Find child with key
        child = None
        for row in container:
            if row.key == key:
                child = row
                break

        # If not found, create new row
        if child is None:
            child = container.add()
            child.key = key

        current = child

    # Handle last key
    last_key = path[-1]
    if hasattr(current, 'rows'):
        container = current.rows
    elif hasattr(current, 'children'):
        container = current.children
    else:
        return

    # Find or create last row
    last_row = None
    for row in container:
        if row.key == last_key:
            last_row = row
            break

    if last_row is None:
        last_row = container.add()
        last_row.key = last_key

    # Set the value
    set_internal_value(last_row.value, value)
