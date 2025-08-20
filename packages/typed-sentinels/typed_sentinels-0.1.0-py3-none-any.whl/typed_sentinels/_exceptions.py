from typing import Any


class SentinelError(TypeError):
    """Base class from which all `typed-sentinels` `Exception` class objects inherit."""


class InvalidHintError(SentinelError):
    """Argument for `hint` cannot be a `Sentinel` instance, the `Sentinel` class itself, or `None`."""

    def __init__(self, hint: Any, /) -> None:
        """Initialize `InvalidHintError`.

        Parameters
        ----------
        hint : Any
            The invalid argument for `hint` as provided to the `Sentinel` class constructor.
        """
        msg = 'Argument for `hint` cannot be `None`\n'
        if hint is not None:
            msg = 'Argument for `hint` cannot be a `Sentinel` instance or `Sentinel` itself\n'
        msg += f"Received argument for hint: '{hint!r}'"
        super().__init__(msg)


class SubscriptedTypeError(SentinelError):
    """Subscripted type and explicit argument for `hint` must match."""

    def __init__(self, hint: Any, subscripted: Any) -> None:
        """Initialize with the mismatched types.

        Parameters
        ----------
        hint : Any
            Provided argument for `hint`.
        subscripted : Any
            Type provided via subscription notation to the `Sentinel` class object.
        """
        msg = "Subscripted type and explicit argument for 'hint' must match\n"
        msg += f'   Subscripted type: {subscripted!r}\n'
        msg += f'               Hint: {hint!r}'
        super().__init__(msg)
