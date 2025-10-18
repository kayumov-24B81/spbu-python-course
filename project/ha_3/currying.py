import functools
from collections import OrderedDict
from typing import Any, Callable, Dict, Union
import inspect


def _make_hashable(obj: Any) -> Union[tuple, str, int, float, bool, None]:
    """
    Convert an object to a hashable form for caching keys.

    Handles basic types, collections, and custom objects.
    """
    if isinstance(obj, (int, float, str, bool, type(None))):
        return obj

    elif isinstance(obj, (tuple, list)):
        return tuple(_make_hashable(item) for item in obj)

    elif isinstance(obj, dict):
        sorted_items = sorted((k, _make_hashable(v)) for k, v in obj.items())
        return tuple(sorted_items)

    elif isinstance(obj, set):
        sorted_items = sorted(_make_hashable(item) for item in obj)
        return tuple(sorted_items)

    else:
        return f"{type(obj).__name__} object"


def curry_explicit(function: Callable, arity: int) -> Callable:
    """
    Explicitly curry a function with given arity.

    Args:
        function: Function to curry
        arity: Number of arguments the function expects

    Returns:
        Curried version of the function
    """
    if arity < 0:
        raise ValueError("Arity should not be negative")

    @functools.wraps(function)
    def curried(*args):
        if len(args) > arity:
            raise ValueError("Too many arguments for curried function")
        elif len(args) == arity:
            return function(*args)
        else:

            def next_func(*arguments):
                if len(arguments) != 1:
                    raise ValueError("Must provide exactly one argument")
                return curried(*(args + arguments))

            return next_func

    return curried


def uncurry_explicit(function: Callable, arity: int) -> Callable:
    """
    Uncurry a curried function back to its original form.

    Args:
        function: Curried function to uncurry
        arity: Original number of arguments

    Returns:
        Uncurried version of the function
    """
    if arity < 0:
        raise ValueError("Arity should not be negative")

    def uncurried(*args):
        if len(args) != arity:
            raise TypeError(f"Expected {arity} arguments, got {len(args)}.")

        if arity == 0:
            return function()

        result = function(args[0])
        for i in range(1, arity):
            result = result(args[i])
        return result

    return uncurried


def cache(limit: int = None) -> Callable:
    """
    Cache decorator with LRU eviction policy.

    Args:
        limit: Maximum number of results to cache. None means no caching.

    Returns:
        Decorated function with caching
    """

    def decorator(function):
        cache_dict = OrderedDict()

        if limit is None:
            return function

        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(function)

            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            hashable_args = _make_hashable(bound_args.args)
            hashable_kwargs = _make_hashable(bound_args.kwargs)

            key = (hashable_args, hashable_kwargs)

            if key in cache_dict:
                cache_dict.move_to_end(key)
                return cache_dict[key]

            result = function(*args, **kwargs)
            cache_dict[key] = result

            if len(cache_dict) > limit:
                cache_dict.popitem(last=False)

            return result

        wrapper.cache_dict = cache_dict

        return wrapper

    return decorator
