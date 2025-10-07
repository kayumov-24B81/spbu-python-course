from functools import reduce
from typing import (
    Union,
    Iterable,
    TypeVar,
    Generator,
    Iterator,
    Any,
    overload,
    Callable,
    Type,
)

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


def generator(data: Union[Iterable[T], T]) -> Generator[T, None, None]:
    """Universal data generator.

    Args:
        data: Iterable object or single value

    Yields:
        Data elements or singule value
    """
    if hasattr(data, "__iter__") and not (isinstance(data, (str, bytes))):
        yield from data
    else:
        yield data


@overload
def pipeline(generator: Iterator[T], *operations: tuple[Any, ...]) -> Iterator[Any]:
    ...


@overload
def pipeline(
    generator: Iterator[T],
    *operations: Union[tuple[Any, ...], Callable[[Iterator[Any]], Iterator[Any]]],
) -> Any:
    ...


def pipeline(
    generator: Iterator[T],
    *operations: Union[tuple[Any, ...], Callable[[Iterator[Any]], Any]],
) -> Union[Iterator[Any], Any]:
    """Data processing pipeline

    Args:
        generator: Source data generator
        *operations: Operations to apply

    Returns:
        Generator for streaming operations or result for terminal operations

    Raises:
        ValueError: For invalid operations
    """
    current: Union[Iterator[Any], Any] = generator

    for operation in operations:
        if isinstance(operation, tuple):
            operator, *args = operation

            if operator == reduce:
                if not args:
                    raise ValueError("Reduce requires function")

                elements = list(current)
                red_func: Callable[[Any, Any], Any] = args[0]

                if len(args) > 1:
                    initial = args[1]
                    return reduce(red_func, elements, initial)
                else:
                    return reduce(red_func, elements)

            elif operator in [filter, map]:
                if not args:
                    raise ValueError(f"{operator.__name__} requires function")
                func: Callable[[T], Any] = args[0]
                current = operator(func, current)
            else:
                current = operator(current, *args)
        else:
            cust_func: Callable[[Iterator[Any]], Iterator[Any]] = operation
            current = cust_func(current)
    return current


@overload
def collect(stream: Iterator[T], collection_type: Type[list] = list) -> list[T]:
    ...


@overload
def collect(stream: Iterator[T], collection_type: Type[set]) -> set[T]:
    ...


@overload
def collect(stream: Iterator[T], collection_type: Type[tuple]) -> tuple[T, ...]:
    ...


@overload
def collect(stream: Iterator[tuple[K, V]], collection_type: Type[dict]) -> dict[K, V]:
    ...


def collect(stream: Iterator[Any], collection_type: Type[Any] = list) -> Any:
    """Collects stream results into a collection

    Args:
        stream: Data stream to collect
        collection_type: Collection type (list, set, dict, tuple)

    Returns:
        Collection with stream elements

    Raises:
        ValueError: If stream is already terminal
    """
    if not hasattr(stream, "__iter__") and not callable(stream):
        raise ValueError("Cannot collect from terminal operation result")

    return collection_type(stream)
