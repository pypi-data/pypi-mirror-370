""" This a collection of tools for SentryReporter and SentryScrubber aimed to
simplify work with several data structures.
"""
import re
from typing import Any, Callable, Dict, List, Optional, TypeVar


def get_first_item(items, default=None):
    return items[0] if items else default


def get_last_item(items, default=None):
    return items[-1] if items else default


def delete_item(d, key):
    if not d:
        return d

    if key in d:
        del d[key]
    return d


def get_value(d, key, default=None):
    return d.get(key, default) if d else default


def extract_dict(d, regex_key_pattern):
    if not d or not regex_key_pattern:
        return dict()

    matched_keys = [key for key in d if re.match(regex_key_pattern, key)]
    return {key: d[key] for key in matched_keys}


def modify_value(d, key, function):
    if not d or not key or not function:
        return d

    if key in d:
        d[key] = function(d[key])

    return d


T = TypeVar('T')


def distinct_by(items: Optional[List[T]], getter: Callable[[T], Any]) -> Optional[List[T]]:
    """This function removes all duplicates from a list of dictionaries. A duplicate
    here is a dictionary that have the same value of the given key.

    If no key field is presented in the dictionary, then the exception will be raised.

    Args:
        items: list of dictionaries
        getter: function that returns a key for the comparison

    Returns:
        Array of distinct items
    """

    if not items:
        return items

    distinct = {}
    for item in items:
        key = getter(item)
        if key not in distinct:
            distinct[key] = item
    return list(distinct.values())


def order_by_utc_time(breadcrumbs: Optional[List[Dict]], key: str = 'timestamp'):
    """ Order breadcrumbs by timestamp in ascending order.

    Args:
        breadcrumbs: List of breadcrumbs
        key: Field name that will be used for sorting

    Returns:
        Ordered list of breadcrumbs
    """
    if not breadcrumbs:
        return breadcrumbs

    return list(sorted(breadcrumbs, key=lambda breadcrumb: breadcrumb[key]))
