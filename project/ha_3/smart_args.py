import functools
import inspect
import copy


class Evaluated:
    def __init__(self, function):
        if not callable(function):
            raise ValueError("Evaluated wraps a callable function")
        self.function = function

    def __call__(self):
        return self.function()


class Isolated:
    pass


def smart_args(check_positional=False):
    def decorator(function):
        sign = inspect.signature(function)

        has_evaluated = False
        has_isolated = False
        positional_special = []

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
        def wrapper(*args, **kwargs):
            bound_args = sign.bind(*args, **kwargs)
            bound_args.apply_defaults()

            arguments = bound_args.arguments

            for param_name, param in sign.parameters.items():
                if param_name in arguments:

                    if param.default is Isolated:
                        arguments[param_name] = copy.deepcopy(arguments[param_name])

                    elif isinstance(param.default, Evaluated):
                        passed_explicitly = False

                        param_names = list(sign.parameters.keys())
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
