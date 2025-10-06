from functools import reduce


def generator(data):
    if hasattr(data, "__iter__") and not (isinstance(data, (str, bytes))):
        yield from data
    else:
        yield data


def conveyor(generator, *operations):
    current = generator
    for operation in operations:
        if isinstance(operation, tuple):
            operator, *args = operation
            if operator == reduce:
                if not args:
                    raise ValueError("Reduce requires function")
                elements = list(current)
                if args:
                    func = args[0]
                    if len(args) > 1:
                        initial = args[1]
                        return reduce(func, elements, initial)
                    else:
                        return reduce(func, elements)
            elif operator in [filter, map]:
                if not args:
                    raise ValueError(f"{operator.__name__} requires function")
                current = operator(args[0], current)
            else:
                current = operator(current, *args)
        else:
            current = operation(current)
    return current


def collect(stream, collection_type=list):
    if not hasattr(stream, "__iter__") and not callable(stream):
        raise ValueError("Cannot collect from terminal operation result")
    return collection_type(stream)
