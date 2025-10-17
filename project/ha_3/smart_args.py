import functools
import inspect
import copy


class Evaluated:
    def __init__(self, function):
        self.function = function

    def __call__(self):
        return self.function()


class Isolated:
    pass


def smart_args(function):
    sign = inspect.signature(function)

    has_evaluated = False
    has_isolated = False

    for param_name, param in sign.parameters.items():
        if param.kind != param.KEYWORD_ONLY:
            raise AssertionError(f"Argument '{param_name}' must be keyword-only")

        if isinstance(param.default, Evaluated):
            has_evaluated = True
        if param.default is Isolated:
            has_isolated = True

    if has_evaluated and has_isolated:
        raise AssertionError("Cannot mix Evaluated and Isolated in the same function")

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        new_kwargs = {}

        for param_name, param in sign.parameters.items():
            if param_name in kwargs:
                value = kwargs[param_name]
                if param.default is Isolated:
                    new_kwargs[param_name] = copy.deepcopy(value)

                else:
                    new_kwargs[param_name] = value

            else:
                if isinstance(param.default, Evaluated):
                    new_kwargs[param_name] = param.default.function()
                else:
                    new_kwargs[param_name] = param.default

        return function(**new_kwargs)

    return wrapper
