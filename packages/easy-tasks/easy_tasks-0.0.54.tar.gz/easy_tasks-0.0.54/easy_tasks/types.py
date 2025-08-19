
def canfloat(num):
    """Check whether `num` can be a float or not.

    Args:
        num (Any): Instance of any type.

    Returns:
        bool: True if num can be a float, False otherwise.
    """
    try:
        float(num)
        return True
    except ValueError:
        return False


def canint(num):
    """Check whether `num` can be an integer or not.

    Args:
        num (Any): Instance of any type.

    Returns:
        bool: True if num can be an integer, False otherwise.
    """
    try:
        int(num)
        return True
    except ValueError:
        return False


def isstring(s):
    """Check whether `s` is a string or not.

    Args:
        s (Any): Instance of any type.

    Returns:
        bool: True if s is a string, False otherwise.
    """
    if isinstance(s, str):
        return True
    else:
        return False

