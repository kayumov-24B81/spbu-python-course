from functools import *


def curry_explicit(function, arity):
    if arity < 0:
        raise ValueError("Arity should not be negative")

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


def uncurry_explicit(function, arity):
    if arity < 0:
        raise ValueError("Arity should be positive")

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
