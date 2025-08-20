"""
Convenience functions and descriptors for HEA object attributes.
"""
from collections.abc import Iterable, MutableSequence
from yarl import URL
from typing import Any, cast, Generic, TypeVar, overload, Union, Callable
from abc import ABC, abstractmethod
from .util import raise_if_empty_string
from .decorators import AttributeMetadata, set_attribute_metadata


def sequence_of_non_empty_str_setter(self, attr_name: str, strings: str | Iterable[str] | None):
    """
    Sets a sequence of non-empty strings to an attribute. If the strings argument is None, the attribute is set to an
    empty list. If the strings argument is not an iterable, a TypeError is raised. If the strings argument contains
    empty strings, a ValueError is raised.

    :param attr_name: the name of the sequence-of-string attribute.
    :param strings: the iterable of non-empty strings to set.
    :raises TypeError: if the strings argument is not an iterable nor a string.
    :raises ValueError: if the strings argument contains empty strings.
    :raises AttributeError: if the attribute is not a mutable sequence.
    """
    sequence_of_str_setter(self, attr_name, strings, disallow_empty_strings=True)


def sequence_of_non_empty_str_adder(self, attr_name: str, string: str):
    """
    Adds a string to a sequence, disallowing the empty string. If the string argument is not a string, it is converted
    to a string.

    :param attr_name: the name of the sequence-of-string attribute.
    :param string: the non-empty string to add.
    """
    string_ = str(string)
    raise_if_empty_string(string_)
    if not hasattr(self, attr_name):
        setattr(self, attr_name, [string_])
    else:
        cast(MutableSequence[str], getattr(self, attr_name)).append(string_)


def sequence_of_non_empty_str_remover(self, attr_name: str, string: str):
    """
    Removes a string from a sequence. If it is not present, this operation does nothing.

    :param attr_name: the name of the sequence-of-string attribute.
    :param string: the string to remove.
    """
    try:
        attr = cast(MutableSequence[str], getattr(self, attr_name))
        if attr:
            attr.remove(string)
    except (AttributeError, ValueError) as e:
        pass


def set_of_non_empty_str_adder(self, attr_name: str, string: str):
    """
    Adds a non-empty string to a set, disallowing the empty string. If the string argument is not a string, it is
    converted to a string.

    :param attr_name: the name of the set-of-string attribute.
    :param string: the non-empty string to add.
    """
    string_ = str(string)
    raise_if_empty_string(string_)
    if not hasattr(self, attr_name):
        setattr(self, attr_name, {string_})
    else:
        cast(set, getattr(self, attr_name)).add(string_)


def set_of_non_empty_str_remover(self, attr_name: str, string: str):
    """
    Removes a string from a set. If it is not present, this operation does nothing.

    :param attr_name: the name of the set-of-string attribute.
    :param string: the string to remove.
    """
    try:
        attr = cast(set, getattr(self, attr_name))
        if attr:
            attr.remove(string)
    except (AttributeError, KeyError) as e:
        pass


def sequence_of_str_setter(self, attr_name: str, strings: str | Iterable[str] | None, disallow_empty_strings: bool = False):
    """
    Sets a sequence of non-empty strings to an attribute. If the strings argument is None, the attribute is set to an
    empty list. If the strings argument is not an iterable, a TypeError is raised. If the strings argument contains
    empty strings, a ValueError is raised.

    :param attr_name: the name of the sequence-of-string attribute.
    :param strings: the iterable of non-empty strings to set.
    :raises TypeError: if the strings argument is not an iterable nor a string.
    :raises ValueError: if the strings argument contains empty strings and disallow_empty_strings is True.
    :raises AttributeError: if the attribute is not a mutable sequence.
    """
    if isinstance(strings, str):
        strings = [strings]
    elif not isinstance(strings, Iterable):
        raise TypeError('Expected an iterable or a str')

    if (attr := cast(MutableSequence[str] | None, getattr(self, attr_name, None))) is None:
        setattr(self, attr_name, [])
        attr = getattr(self, attr_name)
    else:
        attr.clear()
    for s in strings:
        string_ = str(s)
        if disallow_empty_strings:
            raise_if_empty_string(string_)
        attr.append(string_)


def sequence_of_id_adder(self, attr_name: str, id_: str):
    """
    Adds a desktop object id string to a sequence. If the id_ argument is not a string, it is converted to a string.

    :param attr_name: the name of the sequence-of-string attribute.
    :param id_: the id to add.
    """
    sequence_of_non_empty_str_adder(self, attr_name, id_)


def sequence_of_id_remover(self, attr_name: str, id_: str):
    """
    Removes a desktop object id from a sequence. If it is not present, this operation does nothing.

    :param attr_name: the name of the sequence-of-string attribute.
    :param id_: the id to remove.
    """
    sequence_of_non_empty_str_remover(self, attr_name, id_)


def set_of_str_adder(self, attr_name: str, string: str):
    """
    Adds a string to a set. If the string argument is not a string, it is converted to a string.

    :param attr_name: the name of the set-of-string attribute.
    :param id_: the id to add.
    """
    string_ = str(string)
    if not hasattr(self, attr_name):
        setattr(self, attr_name, {string_})
    else:
        cast(set, getattr(self, attr_name)).add(string_)


def set_adder(self, attr_name: str, value: Any, type_: type | None = None):
    """
    Adds an object to a set. If the value argument is not of the expected type, a TypeError is raised.

    :param attr_name: the name of the set attribute.
    :param value: the object to add.
    :param type_: the type of the value argument. If not None, type checking is performed.
    :raises TypeError: if the value argument is not of the expected type.
    """
    if type_ is not None and not isinstance(value, type_):
        raise TypeError(f'Expected {type_}, got {type(value)}')
    if not hasattr(self, attr_name):
        setattr(self, attr_name, {value})
    else:
        cast(set, getattr(self, attr_name)).add(value)

def set_of_str_remover(self: Any, attr_name: str, string: str):
    """
    Removes a string from a set. If it is not present, this operation does nothing.

    :param attr_name: the name of the set-of-string attribute.
    :param string: the string to remove.
    """
    set_remover(self, attr_name, str(string))


def set_remover(self: Any, attr_name: str, value: Any):
    """
    Removes an object from a set. If it is not present, this operation does nothing.

    :param attr_name: the name of the set attribute.
    :param value: the object to remove.
    """
    try:
        attr = cast(set, getattr(self, attr_name))
        if attr:
            attr.remove(value)
    except AttributeError as e:
        pass


def sequence_of_str_adder(self: Any, attr_name: str, string: str):
    """
    Adds a string to a sequence. If the string argument is not a string, it is converted to a string.

    :param attr_name: the name of the sequence attribute.
    :param string: the string to add.
    """
    sequence_adder(self, attr_name, str(string))


def sequence_adder(self: Any, attr_name: str, value: Any, type_: type | None = None):
    """
    Adds an object to a sequence. If the value argument is not of the expected type, a TypeError is raised.

    :param attr_name: the name of the sequence attribute.
    :param value: the value to add.
    :param type_: the type of the value to be added. If not None, type checking is performed.
    :raises TypeError: if the value argument is not of the expected type.
    """
    if type_ is not None and not isinstance(value, type_):
        raise TypeError(f'Expected {type_}, got {type(value)}')
    if not hasattr(self, attr_name):
        setattr(self, attr_name, [value])
    else:
        cast(MutableSequence[Any], getattr(self, attr_name)).append(value)


def sequence_of_str_remover(self: Any, attr_name: str, string: str):
    """
    Removes a string from a sequence. If it is not present, this operation does nothing.

    :param attr_name: the name of the sequence attribute.
    :param string: the string to remove.
    """
    sequence_remover(self, attr_name, str(string))


def sequence_remover(self: Any, attr_name: str, value: Any):
    """
    Removes an object from a sequence. If it is not present, this operation does nothing.

    :param attr_name: the name of the sequence attribute.
    :param value: the object to remove.
    """
    try:
        attr = cast(MutableSequence[Any], getattr(self, attr_name))
        if attr:
            attr.remove(value)
    except (AttributeError, ValueError) as e:
        pass


T = TypeVar('T')


class HEAAttribute(Generic[T], ABC):
    """
    Base class for descriptors for HEA object attributes. It provides a way to define custom behavior for getting and
    setting attribute values, as well as a defining default values and type conversion between the attribute's type and
    an internal representation. It takes a type parameter T, which represents the type of the attribute value. To use
    this class, subclass it and implement the __get__ and __set__ methods to define the custom behavior for getting and
    setting the attribute value.
    """

    def __init__(self, doc: str | None = None, copier: Callable[[T], T] | None = None,
                 attribute_metadata: AttributeMetadata | None = None):
        """
        Constructor for HEAAttribute.

        :param doc: the attribute's docstring.
        """
        self.__doc__ = doc
        self.__attribute_metadata = attribute_metadata
        self._copier = copier

    def __set_name__(self, owner: type, name: str):
        """
        Called automatically when the descriptor is assigned to a class.

        :param owner: the class that owns the descriptor.
        :param name: the name of the descriptor.
        """
        self._private_name = f'_{owner.__name__}__{name}'
        self._public_name = name
        self._owner = owner
        if self.__attribute_metadata is not None:
            set_attribute_metadata(self, self.__attribute_metadata)

    @overload
    def _default_getter(self, obj: None, default_value: T, type_: Callable[[Any], T] | None = None) -> 'HEAAttribute': ...

    @overload
    def _default_getter(self, obj: object, default_value: T, type_: Callable[[Any], T] | None = None) -> T: ...

    def _default_getter(self, obj: object | None, default_value: T, type_: Callable[[Any], T] | None = None) -> 'HEAAttribute' | T:
        """
        A default implementation for returning the value of the attribute. If you wwant to use this method, implement
        __get__ to call this method.

        :param obj: the object to get the attribute from.
        :param default_value: the value to return if the attribute is not set.
        :param type_: the type to covert the result to. The type must be a callable that accepts the descriptor's
        internal representation of the attribute value. If None, no conversion is performed.
        :return: the value to return, or the default value if the attribute is not set.
        """
        if obj is None:
            return self
        try:
            result = getattr(obj, self._private_name)
            if self._copier:
                result = self._copier(result)
            return type_(result) if type_ else result
        except AttributeError:
            return default_value

    @abstractmethod
    def __get__(self, obj: object | None, objtype: type | None = None) -> T | 'HEAAttribute':
        """
        Gets the value of the attribute.

        :param obj: the object to get the attribute from.
        :param objtype: the type of the object.
        :return: the value of the attribute.
        """
        pass

    @abstractmethod
    def __set__(self, obj: object, value: T):
        """
        Sets the value of the attribute.

        :param obj: the object to set the attribute on.
        :param value: the value to set.
        """
        pass


class SimpleAttribute(Generic[T], HEAAttribute[T]):
    """
    A simple descriptor for attributes that can be set and get directly. Attempting to set this attribute to None will
    set it to the default value. The default value is also used when the attribute is not set.
    """

    def __init__(self, type_: type[T], default_value: T, doc: str | None = None,
                 attribute_metadata: AttributeMetadata | None = None):
        """
        Constructor for SimpleAttribute.

        :param type_: the type of the attribute.
        :param default_value: a default value for the attribute.
        :param doc: the attribute's docstring.
        :param attribute_metadata: metadata for the attribute.
        """
        super().__init__(doc=doc, attribute_metadata=attribute_metadata)
        self.__type = type_
        self.__default_value = default_value

    @overload
    def __get__(self, obj: None, objtype: type | None = None) -> 'SimpleAttribute': ...

    @overload
    def __get__(self, obj: object, objtype: type | None = None) -> T: ...

    def __get__(self, obj: object | None, objtype: type | None = None) -> Union[T, 'SimpleAttribute']:
        return self._default_getter(obj, default_value=self.__default_value)

    def __set__(self, obj: object, value: T):
        if value is None:
            value = self.__default_value
        if not isinstance(value, self.__type):
            raise TypeError(f'Expected {self.__type}, got {type(value)}')
        setattr(obj, self._private_name, value)



class URLAttribute(HEAAttribute[str | None]):
    """
    A URL descriptor.
    """

    def __init__(self, absolute = False, doc: str | None = None, attribute_metadata: AttributeMetadata | None = None):
        """
        Constructor for URLAttribute.

        :param absolute: if True, only absolute URLs are allowed.
        :param doc: the attribute's docstring.
        :param attribute_metadata: metadata for the attribute.
        """
        super().__init__(doc=doc, attribute_metadata=attribute_metadata)
        self.__absolute = absolute

    @overload
    def __get__(self, obj: None, objtype: type | None = None) -> 'URLAttribute': ...

    @overload
    def __get__(self, obj: object, objtype: type | None = None) -> str | None: ...

    def __get__(self, obj: object | None, objtype: type | None = None) -> Union[str, None, 'URLAttribute']:
        return self._default_getter(obj, default_value=None)

    def __set__(self, obj, value: str | None):
        if value is not None:
            u = URL(value)
            if self.__absolute and not u.is_absolute():
                raise ValueError(f'relative url {value} not allowed')
            setattr(obj, self._private_name, str(value))
        else:
            setattr(obj, self._private_name, None)


class StrOrNoneAttribute(HEAAttribute[str | None]):
    """
    A descriptor for attributes that can be either a str or None
    """

    @overload
    def __get__(self, obj: None, objtype: type | None = None) -> 'StrOrNoneAttribute': ...

    @overload
    def __get__(self, obj: object, objtype: type | None = None) -> str | None: ...

    def __get__(self, obj: object | None, objtype: type | None = None) -> Union[str, None, 'StrOrNoneAttribute']:
        return self._default_getter(obj, default_value=None)

    def __set__(self, obj, value: str | None):
        setattr(obj, self._private_name, str(value) if value is not None else None)


class NonEmptyStrOrNoneAttribute(HEAAttribute[str | None]):
    """
    A descriptor for attributes that can be either a non-empty str or None. The empty string is converted to None prior
    to assignment.
    """

    @overload
    def __get__(self, obj: None, objtype: type | None = None) -> 'NonEmptyStrOrNoneAttribute': ...

    @overload
    def __get__(self, obj: object, objtype: type | None = None) -> str | None: ...

    def __get__(self, obj: object | None, objtype: type | None = None) -> Union[str, None, 'NonEmptyStrOrNoneAttribute']:
        return self._default_getter(obj, default_value=None)

    def __set__(self, obj, value: str | None):
        raise_if_empty_string(value)
        setattr(obj, self._private_name, str(value) if value else None)


class IdAttribute(HEAAttribute[str | None]):
    """
    A descriptor for desktop object id attributes, which can be either a non-empty str or None.
    """

    @overload
    def __get__(self, obj: None, objtype: type | None = None) -> 'IdAttribute': ...

    @overload
    def __get__(self, obj: object, objtype: type | None = None) -> str | None: ...

    def __get__(self, obj: object | None, objtype: type | None = None) -> Union[str, None, 'IdAttribute']:
        return self._default_getter(obj, default_value=None)

    def __set__(self, obj, value: str | None):
        value_ = str(value)
        raise_if_empty_string(value_)
        setattr(obj, self._private_name, value_ if value_ else None)


class NameAttribute(HEAAttribute[str | None]):
    """
    A descriptor for desktop object name attributes, which can be either a non-empty str or None.
    """

    @overload
    def __get__(self, obj: None, objtype: type | None = None) -> 'NameAttribute': ...

    @overload
    def __get__(self, obj: object, objtype: type | None = None) -> str | None: ...

    def __get__(self, obj: object | None, objtype: type | None = None) -> Union[str, None, 'NameAttribute']:
        return self._default_getter(obj, default_value=None)

    def __set__(self, obj, value: str | None):
        value_ = str(value)
        raise_if_empty_string(value_)
        setattr(obj, self._private_name, value_ if value_ else None)


class StrListWithBackingSetAttribute(HEAAttribute[list[str]]):
    """
    A descriptor for lists of strings with a backing set. Passing a str into this attribute will set the attribute to a
    singleton set with that string. For other iterables, contained objects that are not strings are converted to
    strings prior to being added.
    """

    def __init__(self, disallow_empty_strings=False, doc: str | None = None,
                 attribute_metadata: AttributeMetadata | None = None):
        """
        Constructor for StrListWithBackingSetAttribute.

        :param disallow_empty_strings: if True, empty strings are not allowed in the list.
        :param doc: the attribute's docstring.
        :param attribute_metadata: metadata for the attribute.
        """
        super().__init__(doc=doc, attribute_metadata=attribute_metadata)
        self.__disallow_empty_strings = bool(disallow_empty_strings)

    @overload
    def __get__(self, obj: None, objtype: type | None = None) -> 'StrListWithBackingSetAttribute': ...

    @overload
    def __get__(self, obj: object, objtype: type | None = None) -> list[str]: ...

    def __get__(self, obj: object | None, objtype: type | None = None) -> Union[list[str], 'StrListWithBackingSetAttribute']:
        return self._default_getter(obj, default_value=[], type_=list)

    def __set__(self, obj, value: str | Iterable[str] | None):
        if isinstance(value, str):
            setattr(obj, self._private_name, {value})
        elif value is not None:
            if not isinstance(value, Iterable):
                raise TypeError('Expected an iterable or a str')
            set_ = set()
            for val in value:
                val_ = str(val)
                if self.__disallow_empty_strings:
                    raise_if_empty_string(val_)
                set_.add(val_)
            setattr(obj, self._private_name, set_)
        else:
            setattr(obj, self._private_name, set())

    def add(self, obj, value: str):
        """
        Adds an object to the list. If the value argument is not of the expected type, a TypeError is raised.

        :param obj: the object to add the value to.
        :param value: the value to add.
        """
        set_of_str_adder(obj, self._private_name, value)

    def remove(self, obj, value: str):
        """
        Removes an object from the list. If it is not present, this operation does nothing.

        :param obj: the object to remove the value from.
        :param value: the value to remove.
        """
        set_of_str_remover(obj, self._private_name, value)

U = TypeVar('U')


class ListAttribute(Generic[U], HEAAttribute[list[U]]):
    """
    A descriptor for lists. Passing a str into this attribute will set the attribute to a singleton list with that
    string. For other iterables, contained objects that are not strings are converted to strings prior to being added.
    """

    @overload
    def __get__(self, obj: None, objtype: type | None = None) -> 'ListAttribute': ...

    @overload
    def __get__(self, obj: object, objtype: type | None = None) -> list[U]: ...

    def __get__(self, obj: object | None, objtype: type | None = None) -> Union[list[U], 'ListAttribute']:
        return self._default_getter(obj, default_value=[])

    def __set__(self, obj, value: str | Iterable[U] | None):
        if isinstance(value, str):
            setattr(obj, self._private_name, [value])
        elif value is not None:
            if not isinstance(value, Iterable):
                raise TypeError('Expected an iterable')
            setattr(obj, self._private_name, list(value))
        else:
            setattr(obj, self._private_name, [])

    def add(self, obj, value: U, type_: type[U] | None = None):
        """
        Adds an object to the list. If the value argument is not of the expected type, a TypeError is raised.

        :param obj: the object to add the value to.
        :param value: the value to add.
        :param type_: the type of the value to be added. If not None, type checking is performed.
        """
        sequence_adder(obj, self._private_name, value, type_=type_)

    def remove(self, obj, value: U):
        """
        Removes an object from the list. If it is not present, this operation does nothing.

        :param obj: the object to remove the value from.
        :param value: the value to remove.
        """
        sequence_remover(obj, self._private_name, value)


class StrListAttribute(HEAAttribute[list[str]]):
    """
    A descriptor for lists of str. Passing a str into this attribute will set the attribute to a singleton list with that
    string. For other iterables, contained objects that are not strings are converted to strings prior to being added.
    """

    def __init__(self, disallow_empty_strings=False, doc: str | None = None,
                 attribute_metadata: AttributeMetadata | None = None):
        """
        Constructor for StrListAttribute.

        :param disallow_empty_strings: if True, empty strings are not allowed in the list.
        :param doc: the attribute's docstring.
        :param attribute_metadata: metadata for the attribute.
        """
        super().__init__(doc=doc, attribute_metadata=attribute_metadata)
        self.__disallow_empty_strings = bool(disallow_empty_strings)

    @overload
    def __get__(self, obj: None, objtype: type | None = None) -> 'StrListAttribute': ...

    @overload
    def __get__(self, obj: object, objtype: type | None = None) -> list[str]: ...

    def __get__(self, obj: object | None, objtype: type | None = None) -> Union[list[str], 'StrListAttribute']:
        return self._default_getter(obj, default_value=[])

    def __set__(self, obj, value: str | Iterable[str] | None):
        sequence_of_non_empty_str_setter(obj, self._private_name, value)

    def add(self, obj, value: str):
        """
        Adds a string to the list. If the value is not a string, it is converted to one.

        :param obj: the object to add the value to.
        :param value: the string to add.
        :param type_: the type of the value to be added. If not None, type checking is performed.
        """
        if self.__disallow_empty_strings:
            raise_if_empty_string(value)
        sequence_of_str_adder(obj, self._private_name, value)

    def remove(self, obj, value: str):
        """
        Removes a string from the list. If the value is not a string, it is converted to one prior to the lookup. If it
        is not present, this operation does nothing.

        :param obj: the object to remove the value from.
        :param value: the string to remove.
        """
        sequence_of_str_remover(obj, self._private_name, value)


class IdListWithBackingSetAttribute(HEAAttribute[list[str]]):
    """
    A descriptor for lists of desktop object ids with a backing set. Passing an id into this attribute will set the
    attribute to a singleton set with that id. For other iterables, contained objects that are not strings are
    converted to strings prior to being added.
    """

    @overload
    def __get__(self, obj: None, objtype: type | None = None) -> 'IdListWithBackingSetAttribute': ...

    @overload
    def __get__(self, obj: object, objtype: type | None = None) -> list[str]: ...

    def __get__(self, obj: object | None, objtype: type | None = None) -> Union[list[str], 'IdListWithBackingSetAttribute']:
        return self._default_getter(obj, default_value=[], type_=list)

    def __set__(self, obj, value: str | Iterable[str] | None):
        if isinstance(value, str):
            setattr(obj, self._private_name, {value})
        elif value is not None:
            if not isinstance(value, Iterable):
                raise TypeError('Expected an iterable')
            set_ = set()
            for val in value:
                val_ = str(val)
                raise_if_empty_string(val_)
                set_.add(val_)
            setattr(obj, self._private_name, set_)
        else:
            setattr(obj, self._private_name, set())

    def add(self, obj, id_: str):
        """
        Adds an id to the list.

        :param obj: the object to add the value to.
        :param id_: the id to add. If it is not a string, it is converted to one.
        """
        raise_if_empty_string(id_)
        set_of_str_adder(obj, self._private_name, id_)

    def remove(self, obj, id_: str):
        """
        Removes an id from the list. If it is not present, this operation does nothing. If the value is not a string,
        it is converted to one prior to the lookup.

        :param obj: the object to remove the value from.
        :param id_: the id to remove.
        """
        set_of_str_remover(obj, self._private_name, id_)
