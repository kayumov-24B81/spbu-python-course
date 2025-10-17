import functools
import inspect
import copy
from typing import Any, Callable, Dict, List, Set, TypeVar, Union

F = TypeVar("F", bound=Callable[..., Any])


class Evaluated:
    """Marker for dynamically computed default values."""

    def __init__(self, function: Callable[[], Any]) -> None:
        if not callable(function):
            raise ValueError("Evaluated wraps a callable function")
        self.function = function

    def __call__(self) -> Any:
        return self.function()


class Isolated:
    """Marker for arguments that should be deep-copied."""

    pass


def smart_args(check_positional: bool = False) -> Callable[[F], F]:
    """
    Decorator for smart argument processing with Evaluated and Isolated.

    Args:
        allow_positional: If True, allows Evaluated/Isolated in positional arguments

    Returns:
        Decorated function with smart argument processing
    """

    def decorator(function: F) -> F:
        sign: inspect.Signature = inspect.signature(function)

        has_evaluated: bool = False
        has_isolated: bool = False
        positional_special: List[str] = []

        for param_name, param in sign.parameters.items():
            if not check_positional:
                if (
                    isinstance(param.default, (Evaluated, Isolated))
                    and param.kind != param.KEYWORD_ONLY
                ):
                    positional_special.append(param_name)

            if isinstance(param.default, Evaluated):
                has_evaluated = True
            if param.default is Isolated:
                has_isolated = True

        if not check_positional and positional_special:
            raise AssertionError(
                f"Positional arguments with Evaluated/Isolated are not allowed."
                f"Conflicting arguments: {positional_special}."
                f"Use keyword-only arguments or check_positional = True"
            )

        if has_evaluated and has_isolated:
            raise AssertionError(
                "Cannot mix Evaluated and Isolated parameters in the same function"
            )

        @functools.wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            bound_args: inspect.BoundArguments = sign.bind(*args, **kwargs)
            bound_args.apply_defaults()

            arguments: Dict[str, Any] = bound_args.arguments

            for param_name, param in sign.parameters.items():
                if param_name in arguments:

                    if param.default is Isolated:
                        arguments[param_name] = copy.deepcopy(arguments[param_name])

                    elif isinstance(param.default, Evaluated):
                        passed_explicitly: bool = False

                        param_names: List[str] = list(sign.parameters.keys())
                        if param_name in param_names:
                            param_index = param_names.index(param_name)
                            if param_index < len(args):
                                passed_explicitly = True

                        if param_name in kwargs:
                            passed_explicitly = True

                        if not passed_explicitly:
                            arguments[param_name] = param.default.function()

            return function(**arguments)

        return wrapper

    return decorator
