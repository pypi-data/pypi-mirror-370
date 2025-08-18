import abc
from typing import Any, Optional

import bitstruct


class Nested:
    """Nested pack metadata, used to annotate nested structured fields."""


class PackMetadata(abc.ABC):
    """Base class for all pack metadata classes."""

    _format_type: str
    """The format type of the field, e.g. 'u' for unsigned integer."""

    def __init__(
        self,
        size: int,
        *,
        default: Optional[Any] = None,
        order: Optional[str] = None,
        msb_first: bool = True,
    ):
        """Initialize the pack metadata class.

        :param size: The size of the field in bits.
        :param default: The default value of the field if its value is None.
            If no default value is provided and the fields value is None, a
            ValueError will be raised when attempting to pack the object.
        :param order: The ordering constraint of the field.
            The ordering constraint can be one of the following:
            - 'first': This field will be at first position in the objects un/pack format.
              There can only be one field with a 'first' constraint per object.
            - 'last': This field will be at last position in the objects un/pack format.
              There can only be one field with a 'last' constraint per object.
            - 'before:<other_field_name>': This field will be placed before the other field in
               the objects un/pack format. There can be multiple fields with a 'before'
               constraint, however no circular references are allowed.
            - 'after:<other_field_name>': This field will be placed after the other field in
              the objects un/pack format. There can be multiple fields with an 'after'
              constraint, however no circular references are allowed.
            Note that an exception will be when resolving the un/pack format if any of the
            ordering constraints are not satisfiable, for example if a field demands to be
            placed before a field that demands to be placed first.
        :param msb_first: Pack the field with the MSB first (True) or the LSB first (False).
        """

        self.size = size
        self.default = default
        self.msb_first = msb_first

        # Refers back to the type/object & field that this annotation is attached to
        self._type: Optional[type] = None
        self._object: Optional[object] = None
        self._field: Optional[str] = None

        # Ordering constraint
        self.order = order
        self.order_type: Optional[str] = None
        self.order_ref: Optional[str] = None

        if order is not None:
            parts = order.split(":")
            if len(parts) == 1:
                if parts[0] not in ("first", "last"):
                    raise ValueError(f"Invalid ordering constraint: '{order}'")
                self.order_type = parts[0]
            elif len(parts) == 2:
                if parts[0] not in ("before", "after"):
                    raise ValueError(f"Invalid ordering constraint: '{order}'")
                self.order_type = parts[0]
                self.order_ref = parts[1]
            else:
                raise ValueError(f"Invalid ordering constraint: '{order}'")

    def format_string(self, msb_first: Optional[bool] = None) -> str:
        """Returns the format string of the field.

        :param msb_first: Indicates the MSB first setting of the context.
            Will cause the bit order marker to be suppressed if the field's
            MSB first setting is the same as the context.
            Otherwise, the bit order marker will be set to '>' or '<'.
            If None, the bit order marker will always be set.
        :return: The format string of the field.
        """

        assert self._format_type in ("u", "s", "f", "b", "t", "r", "p", "P")
        if msb_first is not None and msb_first == self.msb_first:
            m = ""
        else:
            m = ">" if self.msb_first else "<"
        s = self.size
        return f"{m}{self._format_type}{s}"

    def value(self) -> Any:
        """Returns the value of the field. If the field value is None, the default value is returned.

        Only callable if this metadata is attached to an object, not to a type.

        :return: The value of the field, or the default value if the field value is None.
        """

        assert self._object is not None and self._field is not None, "Cannot get value of field from type"

        v = getattr(self._object, self._field)

        if v is None:
            if self.default is None:
                raise ValueError(f"Field '{self._field}' has no value and no default")
            else:
                return self.default
        else:
            return v

    def write_value(self, value: Any):
        """Writes the field value to the object.

        Only callable if this metadata is attached to an object, not to a type.

        :param value: The value to write to the field.
        """

        assert (
            self._object is not None and self._field is not None
        ), "Metadata must be attached to an object to write field value"

        setattr(self._object, self._field, value)


class Bool(PackMetadata):
    """Boolean pack metadata class, bitstruct format 'b<size>'."""

    _format_type = "b"


class Float(PackMetadata):
    """Float pack metadata class, bitstruct format 'f<size>'."""

    _format_type = "f"


class PaddingOnes(PackMetadata):
    """Padding with ones pack metadata class, bitstruct format 'P<size>'."""

    _format_type = "P"


class PaddingZeros(PackMetadata):
    """Padding with zeros pack metadata class, bitstruct format 'p<size>'."""

    _format_type = "p"


class Raw(PackMetadata):
    """Raw (bytes) pack metadata class, bitstruct format 'r<size>'."""

    _format_type = "r"


class Signed(PackMetadata):
    """Signed integer pack metadata class, bitstruct format 's<size>'."""

    _format_type = "s"


class Text(PackMetadata):
    """Text pack metadata class, bitstruct format 't<size>'."""

    _format_type = "t"


class Unsigned(PackMetadata):
    """Unsigned integer pack metadata class, bitstruct format 'u<size>'."""

    _format_type = "u"


def _collect_metadata(obj_or_cls: object | type) -> list[PackMetadata]:
    """Collects all PackMetadata annotations from the given object or class.

    This function will traverse the object's/class's annotations recursively
    to collect pack metadata for annotated fields. Recursion is necessary
    to collect metadata from nested structured fields.

    The returned list is in the order of the fields as they are encountered
    in the object/class hierarchy. Ordering constraints are not considered
    by this function.

    :param obj_or_cls: The object or class to collect pack metadata from.
    :return: A list of PackMetadata annotations.
    """

    cls = obj_or_cls if isinstance(obj_or_cls, type) else obj_or_cls.__class__
    obj = obj_or_cls if not isinstance(obj_or_cls, type) else None

    annotations = []
    mro_with_annotations = list(c for c in cls.__mro__ if "__annotations__" in c.__dict__)
    for mro_cls in reversed(mro_with_annotations):
        for field, annotation in mro_cls.__annotations__.items():
            if hasattr(annotation, "__metadata__"):
                for md in annotation.__metadata__:
                    if isinstance(md, PackMetadata):
                        md._type = mro_cls
                        md._object = obj
                        md._field = field
                        annotations.append(md)
                    elif isinstance(md, Nested):
                        # If obj is None, we are dealing with a class, so recurse into the origin
                        # annotation of the field. Otherwise, resolve the fields value and recurse
                        # into the value.
                        if obj is None:
                            origin = getattr(annotation, "__origin__")
                            recurse = _collect_metadata(origin)
                            annotations.extend(recurse)
                        else:
                            recurse = _collect_metadata(getattr(obj, field))
                            annotations.extend(recurse)

    return annotations


def _reorder_metadata(metadata: list[PackMetadata]) -> list[PackMetadata]:
    """Reorders the given metadata list according to the ordering constraints.

    Ordering is performed using an iterative approach on an output list in two steps:
    1. Insert metadata with 'first'/'last' constraints or no constraints into the output list.
    2. Iteratively, insert any metadata with 'before'/'after' constraints into the output list
       before/after the referenced field until all metadata has been inserted.

    In case any constraints are not satisfiable, a ValueError is raised. Particularly,
    the following cases result in an exception:
    - Multiple fields with 'first'/'last' constraints.
    - Circular references in 'before'/'after' constraints.
    - A field with 'before'/'after' constraint that references a field with 'first'/'last' constraint.
    - A reference to a field that does not exist in the metadata list.

    :param metadata: The list of metadata to reorder.
    :return: The reordered list of metadata.
    """

    # 1.Insert metadata with 'first'/'last' and no constraints
    reordered = (
        [m for m in metadata if m.order_type == "first"]
        + [m for m in metadata if m.order_type is None]
        + [m for m in metadata if m.order_type == "last"]
    )

    # 2. Iteratively insert metadata with 'before'/'after' constraints
    count_remaining = len(metadata) - len(reordered)
    while remaining := [m for m in metadata if m not in reordered]:
        for md in remaining:
            for m in reordered:
                if m._field is not None and m._field == md.order_ref:
                    if md.order_type == "before":
                        reordered.insert(reordered.index(m), md)
                    elif md.order_type == "after":
                        reordered.insert(reordered.index(m) + 1, md)
                    else:
                        # Already reordered fields can't have unknown ordering types
                        raise ValueError(f"Unknown ordering type: '{md.order_type}'")  # pragma: no cover
                    break

        # Ensure that progress has been made, else raise an exception
        new_count_remaining = len(metadata) - len(reordered)
        if new_count_remaining == count_remaining:
            raise ValueError(f"Could not satisfy constraints of fields: {','.join(str(md._field) for md in remaining)}")
        count_remaining = new_count_remaining

    # At this point, count_remaining should be 0
    assert count_remaining == 0

    _check_ordering(reordered)
    return reordered


def _check_ordering(metadata: list[PackMetadata]):
    """Checks if the ordering constraints are satisfied.

    Raises a ValueError if any of the constraints are not satisfied.

    :param metadata: The list of metadata to check constraints for.
    """

    for i, md in enumerate(metadata):
        if md.order_type == "before":
            if i < len(metadata) - 1 and metadata[i + 1]._field != md.order_ref:
                raise ValueError(
                    f"Field '{md._field}' has 'before' constraint but the next field is not '{md.order_ref}'"
                )
        elif md.order_type == "after":
            if i > 0 and metadata[i - 1]._field != md.order_ref:
                raise ValueError(
                    f"Field '{md._field}' has 'after' constraint but the previous field is not '{md.order_ref}'"
                )
        elif md.order_type == "first":
            if i != 0:
                raise ValueError(f"Field '{md._field}' has 'first' constraint but is not the first field")
        elif md.order_type == "last":
            if i != len(metadata) - 1:
                raise ValueError(f"Field '{md._field}' has 'last' constraint but is not the last field")
        else:
            assert md.order_type is None, f"Unknown ordering type: '{md.order_type}'"


def _collect_reorder_metadata(obj: object | type) -> list[PackMetadata]:
    """Returns the PackMetadata annotation for the given object or class.

    List of PackMetadata for the given object/type is retrieved from the cache
    (attr '__pack_metadata') if it exists, otherwise the PackMetadata is collected
    and stored in the cache.

    :param obj: The object or class to get the metadata from.

    :return: The PackMetadata annotation for the given field.
    """

    return _reorder_metadata(_collect_metadata(obj))


def _format_string_by_metadata(metadata: list[PackMetadata]) -> str:
    """Generates a format string from a list of PackMetadata annotations.

    :param metadata: The list of metadata annotations to generate the format string from.
    :return: The format string for the metadata annotations.
    """

    # Generate a format string, keeping track of the current MSB/LSB first setting
    # to avoid redundant bit order markers.
    previous_msb_first = None
    fmt = []
    for md in metadata:
        fmt.append(md.format_string(previous_msb_first))
        previous_msb_first = md.msb_first
    return "".join(fmt)


def format_string(obj_or_cls: object | type) -> str:
    """Generates a format string for the given object or class.

    This function will traverse the object's/class's annotations recursively
    to collect pack metadata for annotated fields. Recursion is necessary
    to collect metadata from nested structured fields.

    Ordering constraints are taken into account when generating the format string.

    :param obj_or_cls: The object or class to generate the format string for.
    :return: The format string for the object or class.
    """

    # Generate the format string
    return _format_string_by_metadata(metadata=_collect_reorder_metadata(obj_or_cls))


def _field_values_by_metadata(metadata: list[PackMetadata]) -> tuple:
    """Collects all field values from the given metadata list.

    Skips padding fields when collecting field values.

    :param metadata: The list of metadata to collect field values from.
    :return: A tuple of field values.
    """

    return tuple(md.value() for md in metadata if not isinstance(md, (PaddingZeros, PaddingOnes)))


def field_values(obj: object) -> tuple:
    """Collects all field values from the given object that are packable.

    This function can only be used on objects, not on classes.

    :param obj: The object to collect field values from.
    :return: A tuple of field values.
    """

    assert isinstance(obj, object), f"Expected object, got: {type(obj)}"
    return _field_values_by_metadata(metadata=_collect_reorder_metadata(obj))


def pack(obj: object) -> bytes:
    """Packs the given object according to its field's PackMetadata annotations.

    This function will obtain the format string and field values from the object,
    then use the bitstruct library to pack field values as bytes.

    :param obj: The object to pack.
    :return: The packed object as bytes
    """

    metadata = _collect_reorder_metadata(obj)
    return bitstruct.pack(_format_string_by_metadata(metadata), *_field_values_by_metadata(metadata))


def unpack(obj: object, data: bytes) -> object:
    """Unpacks the given data into the object according to its field's PackMetadata annotations.

    This function will unpack the data into the object's fields according to the
    PackMetadata annotations. The object will be modified in-place.

    A pre-initialized object is required to unpack into because this function
    makes no assumption about the object's classes constructor.

    :param obj: The object to unpack into.
    :param data: The data to unpack.
    :return: The object that the data was unpacked into.
    """

    fmt = format_string(obj)
    values = bitstruct.unpack(fmt, data)

    metadata = _collect_reorder_metadata(obj)

    for md, value in zip(metadata, values):
        md.write_value(value)

    return obj


__all__ = [
    "Bool",
    "Float",
    "PaddingOnes",
    "PaddingZeros",
    "Raw",
    "Signed",
    "Text",
    "Unsigned",
    "Nested",
    "format_string",
    "field_values",
    "pack",
    "unpack",
]
