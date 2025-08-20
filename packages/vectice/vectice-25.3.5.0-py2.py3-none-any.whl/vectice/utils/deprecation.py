from __future__ import annotations

import inspect
import os
import warnings
from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from typing import Any, Callable

from packaging.version import Version

from vectice.__version__ import __version__

CURRENT_VERSION = Version(Version(__version__).base_version)
_WARN_DEPR_REMOVAL = os.getenv("VECTICE_WARN_DEPR_REMOVAL", "0") == "1"


class DeprecationError(BaseException):
    """An exception raised when a deprecated object is used."""


def _exceeds(at: str | datetime | None) -> bool:
    if isinstance(at, str) and Version(at) <= CURRENT_VERSION:
        return True
    if isinstance(at, datetime) and at <= datetime.now():
        return True
    return False


def _deprecated_use(
    *,
    parameter: str | None,
    default: bool,
    args: tuple,
    kwargs: dict[str, Any],
    param_names: list[str],
) -> bool:
    # no parameter was specified for deprecation
    if parameter is None:
        return True
    # checking presence/absence of parameter in given arguments
    if default:
        # parameter must be present
        if parameter not in kwargs and len(args) <= param_names.index(parameter):
            return True
    else:
        # parameter must be absent
        if parameter in kwargs or len(args) > param_names.index(parameter):
            return True
    # no deprecated use detected
    return False


def deprecate(
    reason: str,
    *,
    parameter: str | None = None,
    default: bool = False,
    warn_at: str | datetime | None = None,
    fail_at: str | datetime | None = None,
    remove_at: str | datetime | None = None,
) -> Callable[[Callable], Callable]:
    """Deprecate a function. Internal-use only.

    This decorator can be used to deprecate a function or class method, or a parameter of this function/method.

    Parameters:
        reason: The reason why the function/method is deprecated. Useful information
            can be provided to the users, such as what to use instead of the deprecated function.
            Placeholders can be used in the reason string: `{name}`, `{parameter}`, `{warn_at}`, `{fail_at}` and `{remove_at}`:
            they will be replaced by their actual values, `name` being the name of the function.
        parameter: The name of the parameter to deprecate. If none,
            the whole function is deprecated.
        default: Whether to deprecate the default value of the given parameter (`True`),
            or the use of the parameter itself (`False`, default).
        warn_at: Version or date at which to start emitting a deprecation warning to the user.
            The user will see a deprecation warning when executing the function.
        fail_at: Version or date at which to start raising a deprecation error.
        remove_at: Internal-use only. Version or date at which to remove the deprecated code
            from the code base. It will start emitting a deprecation warning to the developers.
            The test suite will fail as long as the deprecated code is not removed.

    The `warn_at`, `fail_at` and `remove_at` values can be strings or instances of `datetime.datetime`.
    Strings are parsed as PEP 440 versions, see https://peps.python.org/pep-0440/.

    Although you don't have to always provide the three `warn_at`, `fail_at` and `remove_at` parameters,
    it is recommended to provide all three, to ensure the full life-cycle management of the deprecated function.

    IMPORTANT: Deprecation warnings are not enabled by default in Python,
    so users might need to enable them with `python -Walways`.
    More information on warnings control: https://docs.python.org/3/library/warnings.html.

    Examples:
        ```python
        # deprecating a function

        # --------------------------------------
        # vectice code in vectice/module.py
        from vectice.utils.deprecation import deprecate

        @deprecate(
            warn_at="2.1",
            fail_at="3.0",
            remove_at="4.0",
            reason="Function {name} is deprecated since version {warn_at}. "
            "Starting at version {fail_at}, it raises / will raise an exception. "
            "It will be removed at version {remove_at}. "
            "Please use 'other_function' instead.",
        )
        def my_deprecated_function(): ...
        # tests suite fails if version is >= 4.0


        # --------------------------------------
        # user code
        from vectice.module import my_deprecated_function

        my_deprecated_function()
        # exception raised if version is >= 3.0
        # warning emitted if version is >= 2.1
        # nothing happens if version is < 2.1
        ```

        ```python
        # deprecating a class method
        from vectice.utils.deprecation import deprecate


        class MyClass:
            @deprecate(warn_at="1", fail_at="2", remove_at="3", reason="This method is deprecated.")
            def my_deprecated_method(self): ...
        ```

        ```python
        # deprecating a module attribute
        from vectice.utils.deprecation import deprecate

        @deprecate(warn_at="1", fail_at="2", remove_at="3", reason="This attribute is deprecated.")
        def _get_my_deprecated_attribute():
            return "value'

        def __getattr__(name):
            if name == "my_deprecated_attribute":
                return _get_my_deprecated_attribute()
            raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
        ```

        ```python
        # deprecating a class attribute
        from vectice.utils.deprecation import deprecate


        class MyClass:
            _my_deprecated_attribute = "..."

            @deprecate(warn_at="1", fail_at="2", remove_at="3", reason="This attribute is deprecated.")
            def my_deprecated_attribute(self):
                return self._my_deprecated_attribute
        ```

        ```python
        # deprecating a function parameter
        from vectice.utils.deprecation import deprecate


        @deprecate(
            parameter="my_deprecated_parameter",
            warn_at="1",
            fail_at="2",
            remove_at="3",
            reason="This parameter is deprecated.",
        )
        def my_function(my_deprecated_parameter=None): ...
        ```

        ```python
        # deprecating a parameter default value
        from vectice.utils.deprecation import deprecate


        @deprecate(
            parameter="my_parameter",
            default=True,
            warn_at="1",
            fail_at="2",
            remove_at="3",
            reason="This default value is deprecated.",
        )
        def my_function(my_parameter="my_deprecated_default_value"): ...
        ```

    Returns:
        This function returns the actual decorator that must be called again
            with the function to decorate as argument.
    """

    def decorator(func: Callable) -> Callable:
        formatted_reason = reason.format(
            name=func.__name__,
            warn_at=warn_at,
            fail_at=fail_at,
            remove_at=remove_at,
            parameter=parameter,
        )
        if _WARN_DEPR_REMOVAL and _exceeds(remove_at):
            at = f"v{remove_at}" if isinstance(remove_at, str) else remove_at
            param = (f"({parameter})" + (" (default value)" if default else "")) if parameter else ""
            warnings.warn(
                f"Reminder: {func.__module__}.{func.__qualname__}{param} has reached its End-Of-Life, "
                f"planned at {at} - you should remove it from the code base. "
                f"Deprecation reason: {formatted_reason}",
                DeprecationWarning,
                stacklevel=2,
            )

        # we make sure the parameter exists and is not required,
        # and we don't guard behind _WARN_DEPR_REMOVAL
        # so that we never fail to detect such an error,
        # to protect users from getting an exception themselves
        params = inspect.signature(func).parameters
        if parameter:
            if parameter not in params:
                raise DeprecationError(
                    f"Cannot deprecate parameter '{parameter}' in callable {func}: no such parameter"
                )
            if params[parameter].default is inspect._empty:  # pyright: ignore[reportPrivateUsage]
                default_value = "default value " if default else ""
                raise DeprecationError(
                    f"Cannot deprecate parameter '{parameter}' {default_value}in callable {func}: parameter is required"
                )

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            if _deprecated_use(
                parameter=parameter,
                default=default,
                args=args,
                kwargs=kwargs,
                param_names=list(params),
            ):
                if _exceeds(fail_at):
                    raise DeprecationError(formatted_reason)
                if _exceeds(warn_at):
                    warnings.warn(formatted_reason, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator


@contextmanager
def ignore_deprecation_warnings():
    """Temporarily ignore deprecation warnings. Internal-use only.

    Yields:
        Nothing: this function is a context manager.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        yield
