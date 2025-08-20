"""Generic purpose classes and methods such as metadata models.

Metadata includes the kinds, labels, weights and annotations that we assign to our data
objects. Standardizing this enables a more predictable experience.
"""

import enum
import uuid as _uuid
from collections import defaultdict
from copy import deepcopy
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Set,
    Union,
)
from warnings import warn


try:
    StrEnum = enum.StrEnum
except Exception:
    from strenum import StrEnum  # type: ignore
finally:
    if TYPE_CHECKING:
        StrEnum = enum.StrEnum


class Convention(StrEnum):
    """Convention for matrix conversion to follow. Either:

    - Inputs in rows, feedback above diagonal (IR_FAD)
    - Inputs in columns, feedback below diagonal (IC_FBD)
    """

    IR_FAD = enum.auto()
    """Inputs in rows, feedback above diagonal."""

    IC_FBD = enum.auto()
    """Inputs in columns, feedback below diagonal."""


class MappingValidationError(Exception):
    pass


def field(fget: Callable):
    """A [`Mapping`][ragraph.generic.Mapping] `field` is a property that utilizes the
    [`Mapping`][ragraph.generic.Mapping]'s data.

    Use it like the ``@property`` decorator and leave the function body blank (or pass):

    By inspecting the wrapped method's name we derive the property's key.

    Getting data from the mapping is done by retrieving the key from the set values. If that key is
    not found, an attempt is made on the defaults. An error is thrown when the key is neither to be
    found in the data or defaults.

    Setting data checks for nested [`Mapping`][ragraph.generic.Mapping] keys to update those and
    otherwise defaults to simply storing the value. Updating a nested
    [`Mapping`][ragraph.generic.Mapping] field only updates the keys that are provided.

    Deleting data pops the key from the set values, but does not remove any defaults.

    Note:
        The method contents of a [`Mapping`][ragraph.generic.Mapping] `field` are ignored.
    """
    key = fget.__name__

    def getter(self):
        """Get a mapping value."""
        if key in self._data:
            return self._data[key]

        if key in self._defaults:
            return self._defaults[key]

        raise AttributeError(f"Mapping does not contain a (default) value for key '{key}'.")

    def setter(self, value: Any):
        """Set a mapping value."""
        # Setting the mapping to None means resetting it to default.
        if value is None:
            self._data.pop(key, None)
            return

        # Handle nested mapping keys.
        if self._is_mapping(key):
            if key in self._data:
                # Mapping already set, update it.
                self._data[key].update(value)
            else:
                # Create a copy of the default and update that.
                self._data[key] = deepcopy(self._defaults.get(key))
                self._data[key].update(value)
            return

        # Otherwise just store the value.
        else:
            self._data[key] = value

    def deleter(self):
        """Delete a mapping value (e.g. unset it)."""
        self._data.pop(key, None)

    return property(fget=getter, fset=setter, fdel=deleter, doc=fget.__doc__)


class Mapping:
    """A dictionary like object that with property-based access fields.

    It's possible to include allowed keys, default values, and optional validators for
    certain keys/properties of a derived class.

    ```py
    from ragraph.generic import Mapping, field
    def check_int(value):
        assert value == 1

    class MyMap(Mapping):
        _protected = True
        _defaults = dict(myfield=1)
        _validators = dict(myfield=check_int)
        @field
        def myfield(self) -> int:
            '''My field's docstring'''

    m = MyMap(myfield=3)
    assert m.myfield == 3,            "This should return our set value."
    assert m.myfield == m['myfield'], "A mapping works like a dictionary."
    del(m.myfield)                    # This deletes our override.
    m.validate()                      # Checks whether myfield == 1.
    ```
    """

    _protected = False
    """Setting public properties is restricted to those in
    [`self.keys`][ragraph.generic.Mapping.keys].
    """

    _defaults: Dict[str, Any] = dict()
    """Default values for included keys."""

    _keys: Optional[Set[str]] = None
    """Set of always allowed keys to set."""

    _validators: Dict[str, Callable] = dict()
    """Validators for included keys. Used when calling
    [`self.validate`][ragraph.generic.Mapping.validate].
    Also see [`self._post_validation`][ragraph.generic.Mapping._post_validation]."""

    def __init__(self, *args, **kwargs):
        # The internal storage dictionary.
        self._data: Dict[str, Any] = dict()

        # Update the mapping with args and kwargs.
        self.update(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({str(self.as_dict())})"

    def __repr__(self) -> str:
        values = ", ".join([str(k) + "=" + str(v) for k, v in self.as_dict().items()])
        return "<{}.{}({}) at {}>".format(
            self.__class__.__module__, self.__class__.__name__, values, hex(id(self))
        )

    def __eq__(self, other: Any) -> bool:
        try:
            return self.as_dict() == other.as_dict()
        except Exception:
            return False

    def __getitem__(self, key: str) -> Any:
        """Get an attribute via a dictionary accessor: `self['key']`."""
        return getattr(self, key)

    def get(self, key: str, fallback: Any = None) -> Any:
        """Get an attribute with a fallback value if it isn't found."""
        return getattr(self, key, fallback)

    def __setattr__(self, key: str, value: Any) -> None:
        """Set an attribute : `self.key = value`.

        Private properties are left untouched, public properties need permission.
        """
        if not key.startswith("_"):
            keys = set() if self._keys is None else self._keys
            keys = keys.union(self.keys())
            if key not in keys:
                if self._protected:
                    raise KeyError(f"Key or property '{key}' is not allowed. Only '{keys}'.")
                else:
                    # Dynamically create a new field.
                    def stub(self):
                        f"""{key} mapping field."""
                        pass

                    stub.__name__ = key
                    setattr(self.__class__, key, field(stub))

        super().__setattr__(key, value)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set an attribute via a dictionary accessor: `self['key'] = value`.

        Private properties are left untouched, public properties need permission.
        """
        setattr(self, key, value)

    def update(self, *args: Dict[str, Any], **kwargs: Any) -> None:
        """Update multiple keys at once.

        Arguments:
            args: Dictionaries of key value pairs to update the set data with.
            kwargs: Keyword arguments to update the set data with.
        """
        for arg in args:
            try:
                for key, value in arg.items():
                    setattr(self, key, value)
            except AttributeError:
                raise TypeError(f"Expected a dictionary or a Mapping. Found a {type(arg)}.")
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __iter__(self):
        """Provide an iterator."""
        yield from self.items()

    def _is_mapping(self, key) -> bool:
        """Check whether this key is a mapping."""
        return isinstance(getattr(self, key, None), Mapping)

    def items(self):
        """Get defaults and overrides as a (key, value) dict_items iterator."""
        m = deepcopy(self._defaults)
        m.update(self._data)
        return m.items()

    def keys(self) -> Set[str]:
        """The keys in this mapping. (defaults and overrides)."""
        return set(self._defaults.keys()).union(set(self._data.keys()))

    def validate(self) -> None:
        """Check whether the current data passes validation."""
        # Get the complete mapping (default overridden with set values).
        m = deepcopy(self._defaults)
        m.update(self._data)

        # Per key validation.
        for key, value in m.items():
            try:
                # Validate submappings.
                if isinstance(value, Mapping):
                    value.validate()

                # Validate using validator if available.
                validator = self._validators.get(key)
                if validator is not None:
                    validator(value)
            except Exception:
                raise MappingValidationError(
                    f"Validation of '{key}' failed: '{value}' did not pass validation."
                )

        # Post-validation.
        try:
            self._post_validation()
        except Exception:
            raise MappingValidationError("Post-validation did not succeed.")

    def _post_validation(self) -> None:
        """Validation to run at the end of regular validation. Does nothing by default.

        Useful when a derived class needs to cross-validate certain keys instead of just
        a dedicated method per key.
        """
        pass

    def as_dict(self) -> Dict[str, Any]:
        """Return a copy as a dictionary with all sub-mappings as dictionaries, too."""
        m = self._defaults.copy()
        m.update(self._data)
        for key, value in m.items():
            if isinstance(value, Mapping):
                m[key] = value.as_dict()
        return deepcopy(m)


class Annotations(Mapping):
    """Miscellaneous properties mapping such as tool-specific metadata."""

    _protected = False


class Bound:
    """Numerical lower or upper bound for a value. Use with comparison operators.

    Arguments:
        value: Numerical bound value.
        inclusive: Whether the bound is inclusive.
        report: Whether to report an "error", "warn" or nothing (`None`) on
            bound violations.
    """

    def __init__(
        self,
        value: Union[int, float],
        inclusive: bool = True,
        report: Optional["str"] = None,
    ):
        self.value = value
        self.inclusive = inclusive
        self.report = report

    def __str__(self) -> str:
        return "Bound(value={}, inclusive={}, report={})".format(
            self.value, self.inclusive, self.report
        )

    def __lt__(self, other: Union[int, float]) -> bool:
        """Used as a lower bound."""
        if other < self.value:
            if self.report is not None:
                self._report(f"Value '{other}' below bound '{self.value}'.")
            return False
        elif not self.inclusive and other == self.value:
            if self.report is not None:
                self._report(f"Value '{other}' is at the exclusive lower bound value.")
            return False
        return True

    def __gt__(self, other: Union[int, float]) -> bool:
        """Used as an upper bound."""
        if other > self.value:
            if self.report is not None:
                self._report(f"Value '{other}' above bound '{self.value}'.")
            return False
        elif not self.inclusive and other == self.value:
            if self.report is not None:
                self._report(f"Value '{other}' is at the exclusive upper bound value.")
            return False
        return True

    def _report(self, msg: str) -> None:
        """Report an error or warning depending on if the bound is set to 'hard'."""
        if self.report == "warn":
            warn(msg)
        else:
            raise ValueError(msg)

    def as_dict(self) -> Dict[str, Any]:
        """Serializable dictionary representation."""
        return dict(value=self.value, inclusive=self.inclusive, report=self.report)


class ContinuousDomain:
    """Numerical domain for a value. Use with "in" operator."""

    def __init__(
        self,
        lower: Optional[Bound] = None,
        upper: Optional[Bound] = None,
    ):
        self.lower = lower
        self.upper = upper

    def __str__(self) -> str:
        if self.lower is None:
            lb = "(-inf"
        else:
            lb = "{}{}".format("[" if self.lower.inclusive else "(", self.lower.value)

        if self.upper is None:
            ub = "inf)"
        else:
            ub = "{}{}".format(self.upper.value, "]" if self.upper.inclusive else "]")
        return f"{lb}, {ub}"

    def __repr__(self) -> str:
        return "<{}.{}({}) at {}>".format(
            self.__class__.__module__, self.__class__.__name__, str(self), hex(id(self))
        )

    def __contains__(self, value: Union[int, float]) -> bool:
        """Whether this continuous domain contains a value."""
        return (value > self.lower if self.lower is not None else True) and (
            value < self.upper if self.upper is not None else True
        )

    def as_dict(self) -> Dict[str, Any]:
        """Serializable dictionary representation."""
        return dict(
            lower=None if self.lower is None else self.lower.as_dict(),
            upper=None if self.upper is None else self.upper.as_dict(),
        )


class Metadata:
    """Metadata for graph elements.

    Arguments:
        name: Instance name. Set to a copy of the UUID if `None` provided.
        kind: Kind or main category of this instance.
        labels: Labels categorizing this instance.
        weights: Dictionary of weights attached to this instance.
        annotations: Miscellaneous properties of this instance.
        uuid: UUID of this instance, generated when `None` provided.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        kind: Optional[str] = None,
        labels: Optional[List[str]] = None,
        weights: Optional[Dict[str, Union[int, float]]] = None,
        annotations: Optional[Union[Annotations, Dict[str, Any]]] = None,
        uuid: Optional[Union[str, _uuid.UUID]] = None,
    ):
        self._uuid: _uuid.UUID
        self._name: str
        self._kind: str
        self._labels: List[str]
        self._weights: Dict[str, Union[int, float]]
        self._annotations: Annotations

        setattr(self, "uuid", uuid)
        setattr(self, "name", name)
        setattr(self, "kind", kind)
        setattr(self, "labels", labels)
        setattr(self, "weights", weights)
        setattr(self, "annotations", annotations)

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        result.uuid = None
        return result

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        result.uuid = None
        return result

    @property
    def uuid(self) -> _uuid.UUID:
        """Instance UUID."""
        return self._uuid

    @uuid.setter
    def uuid(self, value: Optional[Union[str, _uuid.UUID]]):
        if value is None:
            uuid = _uuid.uuid4()
        elif isinstance(value, _uuid.UUID):
            uuid = value
        else:
            uuid = _uuid.UUID(value)
        self._uuid = uuid

    @property
    def name(self) -> str:
        """Instance name. Given a UUID if None was provided."""
        return self._name

    @name.setter
    def name(self, value: Optional[str]):
        if value is None:
            value = str(self.uuid)
        self._name = str(value)

    @property
    def kind(self) -> str:
        """Kind or main category of this instance."""
        return self._kind

    @kind.setter
    def kind(self, value: str):
        if not value:
            self._kind = "default"
        else:
            self._kind = str(value)

    @property
    def labels(self) -> List[str]:
        """Labels categorizing this instance."""
        return self._labels

    @labels.setter
    def labels(self, value: List[str]):
        if not value:
            self._labels = ["default"]
        else:
            self._labels = list(value)

    @property
    def weights(self) -> Dict[str, Union[int, float]]:
        """Dictionary of weights attached to this instance."""
        return self._weights

    @weights.setter
    def weights(self, value: Optional[Dict[str, Union[int, float]]]):
        if not value:
            self._weights = dict(default=1)
        else:
            self._weights = dict(value)

    @property
    def weight(self) -> Union[int, float]:
        """Cumulative weight of this instance (read-only).

        Returns the sum of [`self.weights`][ragraph.generic.Metadata.weights].
        """
        return sum(self._weights.values())

    @property
    def annotations(self) -> Annotations:
        """Annotations of this instance.

        Defaults to an empty [`Annotations`][ragraph.generic.Annotations] instance.
        """
        return self._annotations

    @annotations.setter
    def annotations(self, value: Optional[Union[Annotations, Dict[str, Any]]]):
        if value is None:
            self._annotations = Annotations()
        elif isinstance(value, Annotations):
            self._annotations = value
        else:
            self._annotations = Annotations(**value)


class MetadataFilter:
    """Metadata filtering options.

    Arguments:
        uuids: Filter by UUIDs.
        names: Filter by names.
        kinds: Filter by kinds.
        labels: Filter by labels. Items should match at least one.
        weights: Filter by weight labels. Items should match at least one.
        weight_domains: Filter items by weight domains. (upper/lower bound)
        annotations: Filter by annotation keys. Items should match at least one.
    """

    _filters = [
        "uuids",
        "names",
        "kinds",
        "labels",
        "weights",
        "weight_domains",
        "annotations",
    ]

    def __init__(
        self,
        uuids: Optional[Union[Iterable[str], Iterable[_uuid.UUID]]] = None,
        names: Optional[Iterable[str]] = None,
        kinds: Optional[Iterable[str]] = None,
        labels: Optional[Iterable[str]] = None,
        weights: Optional[Iterable[str]] = None,
        weight_domains: Optional[Dict[str, ContinuousDomain]] = None,
        annotations: Optional[Iterable[str]] = None,
    ):
        if uuids:
            self.uuids: Set[_uuid.UUID] = {
                i if isinstance(i, _uuid.UUID) else _uuid.UUID(i) for i in uuids
            }
        if names:
            self.names: Set[str] = set(names)
        if kinds:
            self.kinds: Set[str] = set(kinds)
        if labels:
            self.labels: Set[str] = set(labels)
        if weights:
            self.weights: Set[str] = set(weights)
        if weight_domains:
            self.weight_domains: Dict[str, ContinuousDomain] = weight_domains
        if annotations:
            self.annotations: Set[str] = set(annotations)

    def __call__(self, item: Metadata) -> bool:
        """Apply this metadata filter to an item."""
        return all(check(item) for check in self.get_checks())

    def get_checks(self) -> List[Callable[[Metadata], bool]]:
        """Active filter methods."""
        return [
            getattr(self, f"check_{filter}")
            for filter in self._filters
            if getattr(self, filter, False)
        ]

    def filter(
        self, data: Iterable[Metadata], as_list: bool = True
    ) -> Union[List[Metadata], Generator[Metadata, None, None]]:
        """Filter data using the set metadata filters."""

        def _generator():
            checks = self.get_checks()
            if checks:
                for item in data:
                    if all(check(item) for check in checks):
                        yield item
            else:
                yield from data

        generator = _generator()
        return list(generator) if as_list else generator

    def check_uuids(self, item: Metadata) -> bool:
        """Check if item satisfies UUID filter."""
        return item.uuid in self.uuids

    def check_names(self, item: Metadata) -> bool:
        """Check if item satisfies names filter."""
        return item.name in self.names

    def check_kinds(self, item: Metadata) -> bool:
        """Check if item satisfies kinds filter."""
        return item.kind in self.kinds

    def check_labels(self, item: Metadata) -> bool:
        """Check if item satisfies labels filter."""
        return any(self.labels.intersection(item.labels))

    def check_weights(self, item: Metadata) -> bool:
        """Check if item satisfies weight keys filter."""
        return any(self.weights.intersection(item.weights.keys()))

    def check_weight_domains(self, item: Metadata) -> bool:
        """Check if item satisfies weight domains filter."""
        return all(
            (key in item.weights and item.weights[key] in domain)
            for key, domain in self.weight_domains.items()
        )

    def check_annotations(self, item: Metadata) -> bool:
        """Check if item satisfies annotation keys filter."""
        return any(self.annotations.intersection(item.annotations.keys()))


class MetadataOptions:
    """Seen values in an iterable of Metadata instances.

    Arguments:
        objects: Objects derivated of the Metadata class.
        skip_names: Whether to skip the names field.
    """

    def __init__(
        self,
        objects: Iterable[Metadata],
        skip_uuids: bool = False,
        skip_names: bool = False,
    ):
        uuids: Optional[Set[_uuid.UUID]] = None if skip_uuids else set()
        names: Optional[Set[str]] = None if skip_names else set()

        kinds: Set[str] = set()
        labels: Set[str] = set()
        weights: Set[str] = set()
        weight_domains: Dict[str, ContinuousDomain] = defaultdict(ContinuousDomain)
        annotations: Set[str] = set()

        for obj in objects:
            if uuids is not None:
                uuids.add(obj.uuid)
            if names is not None:
                names.add(obj.name)
            kinds.add(obj.kind)
            labels.update(obj.labels)
            weights.update(obj.weights.keys())
            annotations.update(obj.annotations.keys())

            for k, v in obj.weights.items():
                domain = weight_domains[k]
                if domain.lower is None or v < domain.lower:
                    domain.lower = Bound(value=v, inclusive=True, report=None)
                if domain.upper is None or v > domain.upper:
                    domain.upper = Bound(value=v, inclusive=True, report=None)

        self.uuids = uuids
        self.names = names
        self.kinds = kinds
        self.labels = labels
        self.weights = weights
        self.weight_domains = weight_domains
        self.annotations = annotations

    def as_dict(self) -> Dict[str, Any]:
        """Serializable dictionary representation."""
        result: Dict[str, Any] = dict(
            kinds=sorted(self.kinds),
            labels=sorted(self.labels),
            weights=sorted(self.weights),
            weight_domains={k: v.as_dict() for k, v in self.weight_domains.items()},
            annotations=sorted(self.annotations),
        )
        if self.uuids is not None:
            result["uuids"] = sorted(self.uuids, key=lambda x: str(x))
        if self.names is not None:
            result["names"] = sorted(self.names)

        return result
