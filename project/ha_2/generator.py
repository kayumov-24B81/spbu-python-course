from functools import reduce


def range_gen(begin: int = 0, end: int = 10, step: int = 1):
    num = begin
    while num < end:
        yield num
        num += step


def custom_map(function):
    def mapper(stream):
        return map(function, stream)

    return mapper


def custom_filter(function):
    def filtrator(stream):
        return filter(function, stream)

    return filtrator


def custom_zip(generator):
    def zipper(stream):
        return zip(stream, generator)

    return zipper


def custom_reduce(function, initial=None):
    def reducer(stream):
        elements = list(stream)
        if initial is not None:
            return reduce(function, elements, initial)
        else:
            return reduce(function, elements)

    return reducer


def custom_enumerate(start=0):
    def enumerator(stream):
        return enumerate(stream, start)

    return enumerator


def pipeline(generator, *operations):
    current = generator
    for operation in operations:
        if callable(operation):
            current = operation(current)
    return current


# TODO: implement reduce collection
def collect(stream, type=list):
    if type == list:
        return list(stream)
    elif type == set:
        return set(stream)
    elif type == dict:
        return dict(stream)
    else:
        return type(stream)
