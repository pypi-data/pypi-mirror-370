from collections.abc import Callable
from threading import Lock
from typing import Any, ClassVar, NoReturn, SupportsIndex, TypeGuard, TypeVar, cast, final
from weakref import WeakValueDictionary

from ._exceptions import InvalidHintError, SubscriptedTypeError

type _InstanceCache = WeakValueDictionary[tuple[str, Any], 'Sentinel[Any]']

_OBJECT = object()


@final
class Sentinel[T: Any]:
    """Statically-typed sentinel objects with singleton qualities.

    `Sentinel` instances provide unique placeholder objects that maintain singleton behavior for a given type hint. They
    are particularly useful as default parameter values when `None` is not appropriate or when type safety is desired.

    The `Sentinel` class is particularly well-suited for use with types requiring parameters which are only available at
    runtime, where creating a default instance of the type may not be possible in advance, but the structural contract
    of the type is otherwise guaranteed to be fulfilled once present.

    **Key features:**

    - **Versatile:** Emulate any type, including user-defined types and types requiring parameters.
    - **Type-safe:** Appears to the type-checker as an *instance* of the target type.
    - **Thread-safe:** Safe for concurrent access across multiple threads.
    - **Singleton behavior:** Only one instance exists per type hint.
    - **Serializable:** Maintains singleton property across pickle operations.
    - **Lightweight:** Sentinels are incredibly lightweight objects.
    - **Immutable:** Cannot be modified after creation.
    - **Falsy:** Always evaluates to `False` in boolean contexts.
    - **Callable:** Calling a `Sentinel` instance always returns the instance.

    Examples
    --------
    **Basic usage:**

    >>> UNSET: str = Sentinel(str)
    >>> def process(value: str = UNSET) -> str:
    ...     if not value:  # Sentinels are always falsy
    ...         return 'No value'
    ...     return f'Got: {value}'

    **Type subscription syntax:**

    >>> UNSET = Sentinel[str]()
    >>> OTHER = Sentinel[str]()
    >>> UNSET is OTHER  # True - Singleton behavior
    True

    **With complex types:**

    >>> CONFIG: dict[str, Any] = Sentinel(dict[str, Any])
    >>> def setup(config: dict[str, Any] = CONFIG) -> None:
    ...     if not config:
    ...         config = {'default': True}
    """

    __slots__ = ('__weakref__', '_hint')

    _cls_cache: ClassVar[_InstanceCache] = WeakValueDictionary()
    _cls_hint: ClassVar[Any] = _OBJECT
    _cls_lock: ClassVar[Lock] = Lock()

    _hint: T

    @property
    def hint(self) -> T:
        """Return the type hint associated with this `Sentinel` instance.

        Returns
        -------
        T
            Type represented by the `Sentinel` instance.
        """
        return self._hint

    def __class_getitem__(cls, key: Any) -> T:
        """Support type subscription syntax like (e.g., `Sentinel[str]()`).

        Parameters
        ----------
        key : Any
            Type to be used as the hint for the sentinel.

        Returns
        -------
        T
            Class object with the type hint stored for later instantiation, cast to the specified type.
        """
        cls._cls_hint = key
        if type(key) is TypeVar:
            cls._cls_hint = Any
        return cast('T', cls)

    def __new__(cls, hint: Any = _OBJECT, /) -> Any:
        """Create or retrieve a `Sentinel` instance for the given `hint` type.

        Implements the singleton pattern, ensuring that only one `Sentinel` instance exists for each unique
        `(cls.__name__, hint)` combination. The method is thread-safe and lightweight; it attempts to return early with
        any cached instance that might exist, doing so before acquiring the class-level lock.

        Parameters
        ----------
        hint : Any, optional
            Type that this `Sentinel` should represent. If not provided, and if the class has not been otherwise
            parameterized via subscription notation, defaults to `Any`.

        Returns
        -------
        Sentinel[T]
            `Sentinel` object instance for the given `hint` type, either created anew or retrievd from the class-level
            `WeakValueDictionary` cache.

        Raises
        ------
        InvalidHintError
            If `hint` is `None`, a `Sentinel` instance, or the `Sentinel` class object itself.
        SubscriptedTypeError
            If provided both a subscripted type parameter and a direct type argument and the types should differ (e.g.,
            `Sentinel[A](B)` will raise a `SubscriptedTypeErorr`).
        """
        if (_cls_hint := cls._cls_hint) is not _OBJECT:
            cls._cls_hint = _OBJECT
        if (hint is _OBJECT) and (_cls_hint is not _OBJECT):
            hint = _cls_hint
        if hint is _OBJECT:
            hint = Any

        key = (cls.__name__, hint)
        if (inst := cls._cls_cache.get(key)) is not None:
            return cast('T', inst)

        if (hint is not _OBJECT) and (_cls_hint is not _OBJECT):
            if (hint is not Any) and (_cls_hint is not Any):
                if (hint != _cls_hint) and (hint is not _cls_hint):
                    raise SubscriptedTypeError(hint=hint, subscripted=_cls_hint)

        if isinstance(hint, Sentinel) or (hint is Sentinel) or (hint is None):
            raise InvalidHintError(hint)

        with cls._cls_lock:
            if (inst := cls._cls_cache.get(key)) is None:
                inst = super().__new__(cls)
                super().__setattr__(inst, '_hint', hint)
                cls._cls_cache[key] = inst

        return cast('T', inst)

    def __getitem__(self, key: Any) -> T:
        return cast('T', self)

    def __call__(self, *args: Any, **kwds: Any) -> T:
        return cast('T', self)

    def __str__(self) -> str:
        hint_name = str(self._hint)
        if hint_name.startswith("<class '") and hint_name.endswith("'>"):
            hint_name = hint_name[8:-2]
        return f'<Sentinel: {hint_name}>'

    def __repr__(self) -> str:
        return f'<Sentinel: {self._hint!r}>'

    def __hash__(self) -> int:
        return hash((self.__class__, self._hint))

    def __bool__(self) -> bool:
        """Return `False` - Sentinels are always "falsy".

        This allows for natural usage patterns like:

        ```pycon
        >>> if not value:  # Where `value` might be a `Sentinel` instance
        ```

        Returns
        -------
        bool
            Always `False`.
        """
        return False

    def __eq__(self, other: object) -> bool:
        """Check equality with another object.

        Two `Sentinels` are equal if they have the same `__class__` and `hint` type.

        Parameters
        ----------
        other : object
            Object with which to compare.

        Returns
        -------
        bool
            - `True` if `other` is an object of the same `__class__` and `hint`.
            - `False` otherwise.
        """
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__ == other.__class__ and self._hint == other._hint

    def __copy__(self) -> 'Sentinel[T]':
        return self

    def __deepcopy__(self, _: Any) -> 'Sentinel[T]':
        return self

    def __reduce__(self) -> tuple[Callable[..., 'Sentinel[T]'], tuple[T]]:
        return (self.__class__, (self._hint,))

    def __reduce_ex__(self, protocol: SupportsIndex) -> tuple[Callable[..., 'Sentinel[T]'], tuple[T]]:
        return self.__reduce__()

    def __setattr__(self, name: str, value: Any) -> NoReturn:
        msg = f'Cannot modify attributes of {self!r}'
        raise AttributeError(msg)

    def __delattr__(self, name: str) -> NoReturn:
        msg = f'Cannot delete attributes of {self!r}'
        raise AttributeError(msg)


def is_sentinel[T](obj: Any, typ: T | None = None) -> TypeGuard[Sentinel[T]]:
    """Return `True` if `obj` is a `Sentinel` instance, optionally further narrowed to be of type `typ`.

    Parameters
    ----------
    obj : Any
        Possible `Sentinel` object instance.
    typ : T | None, optional
        Optional type to be used to further narrow the type of the `Sentinel` object instance.
        If provided, and if `obj` is a `Sentinel` object instance, this must match `obj.hint`.

    Returns
    -------
    TypeGuard[Sentinel[T]]
        - `True` if `obj` is a `Sentinel` instance.
        - `False` otherwise.
    """
    if typ is not None:
        return isinstance(obj, Sentinel) and obj.hint == typ
    return isinstance(obj, Sentinel)
