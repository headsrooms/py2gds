from typing import Dict, Any, Callable


def to_json_without_quotes(dictionary: Dict[Any, Any]):
    strings = [
        f'{key}: "{value}"' if isinstance(value, str) else f"{key}: {value}"
        for key, value in dictionary.items()
    ]
    return f"{{{', '.join(strings)}}}"


def match_clause(reference: str, label: str, filters: Dict[str, Any]):
    filter_string = to_json_without_quotes(filters)
    return f"MATCH ({reference}: {label} {filter_string})\n"


def builder(func: Callable) -> Callable:
    """
    Decorator for wrapper "builder" functions.  These are functions on the Query class or other classes used for
    building queries which mutate the query and return self.  To make the build functions immutable, this decorator is
    used which will deepcopy the current instance.  This decorator will return the return value of the inner function
    or the new copy of the instance.  The inner function does not need to return self.
    Copied from pypika.
    """
    import copy

    def _copy(self, *args, **kwargs):
        self_copy = copy.copy(self) if getattr(self, "immutable", True) else self
        result = func(self_copy, *args, **kwargs)

        # Return self if the inner function returns None.  This way the inner function can return something
        # different (for example when creating joins, a different builder is returned).
        if result is None:
            return self_copy

        return result

    return _copy
