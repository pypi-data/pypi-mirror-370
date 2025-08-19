# -*- coding: utf-8 -*-
"""List ustils"""

def last(lst: list, default=None):
    """Return the last item in a list or a default value if the list is empty."""
    try:
        return lst[-1]
    except IndexError:
        return default
