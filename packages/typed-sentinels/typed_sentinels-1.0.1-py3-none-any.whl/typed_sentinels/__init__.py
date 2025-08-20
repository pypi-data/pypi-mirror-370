"""Statically-typed sentinel objects with singleton qualities.

`Sentinel` instances provide unique placeholder objects that maintain singleton behavior for a given type hint. They
are particularly useful as default parameter values when `None` is not appropriate or when type safety is desired.

The `Sentinel` class is particularly well-suited for use with types requiring parameters which are only available at
runtime, where creating a default instance of the type may not be possible in advance, but the structural contract
of the type is otherwise guaranteed to be fulfilled once present.

Key Features
-------------
- **Versatile:** Emulate any type, including user-defined types and types requiring parameters.
- **Type-safe:** Appears to the type-checker as an *instance* of the target type.
- **Thread-safe:** Safe for concurrent access across multiple threads.
- **Singleton behavior:** Only one instance exists per type hint.
- **Serializable:** Maintains singleton property across pickle operations.
- **Lightweight:** Sentinels are incredibly lightweight objects.
- **Immutable:** Cannot be modified after creation.
- **Falsy:** Always evaluates to `False` in boolean contexts.
- **Callable:** Calling a `Sentinel` instance always returns the instance.
"""

# Core
from ._core import Sentinel as Sentinel
from ._core import is_sentinel as is_sentinel

# Exceptions
from ._exceptions import InvalidHintError as InvalidHintError
from ._exceptions import SentinelError as SentinelError
from ._exceptions import SubscriptedTypeError as SubscriptedTypeError

__all__ = (
    'InvalidHintError',
    'Sentinel',
    'SentinelError',
    'SubscriptedTypeError',
    'is_sentinel',
)
