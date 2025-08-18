from enum import Enum
from types import DynamicClassAttribute

from enums.framework.item import StandardEnumItem
from enums.utils.general import (
    convert_enum_to_choices,
    convert_enum_to_values_array,
    convert_enum_to_dict,
)


class StandardEnum(Enum):
    """
    Represents a standard enumeration with additional functionalities for accessing
    values, choices, dictionaries, and resolving enum names.

    This class extends `Enum` to provide utility methods for working with enumerations
    in a standard format. It allows the retrieval of detailed custom values for
    enumeration items, returns choices for use in selection fields, constructs
    dictionaries representing the enumeration, and provides methods for resolving
    values to their respective names.

    """

    @DynamicClassAttribute
    def raw_value(self):
        """
        An overridden property for accessing the raw value of the object through the
        base class mechanism. The property dynamically retrieves and returns the value
        from the superclass's `value` property.

        This class attribute provides a mechanism for accessing the raw data without
        any modifications applied at the subclass level.

        :return: The raw value from the superclass implementation of the `value`
                 property.
        :rtype: Any
        """
        return super().value

    @DynamicClassAttribute
    def value(self):
        """
        Gets the transformed value based on the raw value stored in the instance.

        If the raw value is of type `StandardEnumItem`, its `code` attribute is
        returned. Otherwise, the raw value itself is returned.

        :return: The extracted or original value of the attribute.
        :rtype: Any
        """
        raw_value = self.raw_value
        if isinstance(raw_value, StandardEnumItem):
            return raw_value.code
        return raw_value

    @DynamicClassAttribute
    def code(self):
        """
        Dynamically retrieves the code attribute from the raw_value. If the raw_value
        is an instance of StandardEnumItem, it fetches and returns the code property
        of that instance. Otherwise, it directly returns the raw_value. This method
        ensures the proper retrieval of the value in cases where the raw_value may
        be an enumeration item with additional properties.

        :return: The `code` property of the raw_value if it's an instance of
            StandardEnumItem; otherwise, the raw_value itself.
        :rtype: Any
        """
        raw_value = self.raw_value
        if isinstance(raw_value, StandardEnumItem):
            return raw_value.code
        return raw_value

    @DynamicClassAttribute
    def visible_name(self):
        """
        Returns a user-friendly name for the `raw_value`, either directly or through
        a `StandardEnumItem` instance.

        This property provides a readable representation of the attribute value that
        is intended to be displayed to end-users or in user interfaces. If the
        `raw_value` is an instance of `StandardEnumItem`, its `visible_name` is
        used. Otherwise, the `raw_value` itself is returned directly.

        :raises AttributeError: If accessing `raw_value` or its `visible_name` fails.

        :return: Friendly name representation of the `raw_value`, or the value itself
            if it is not an instance of `StandardEnumItem`.
        :rtype: Any
        """
        raw_value = self.raw_value
        if isinstance(raw_value, StandardEnumItem):
            return raw_value.visible_name
        return raw_value

    @DynamicClassAttribute
    def extra_data(self):
        """
        Provides access to additional data stored in the `raw_value` attribute.

        This property dynamically evaluates the `raw_value` attribute. If the `raw_value`
        is an instance of `StandardEnumItem`, it retrieves and returns its `extra_data`
        attribute. Otherwise, it returns an empty dictionary.

        :return: Returns the `extra_data` if `raw_value` is a `StandardEnumItem`.
                 Otherwise, an empty dictionary.
        :rtype: dict
        """
        raw_value = self.raw_value
        if isinstance(raw_value, StandardEnumItem):
            return raw_value.extra_data
        return {}

    @classmethod
    def choices(cls):
        return convert_enum_to_choices(cls)

    @classmethod
    def values(cls):
        return convert_enum_to_values_array(cls)

    @classmethod
    def values_tuple(cls):
        return tuple(cls.values())

    @classmethod
    def dict(cls):
        return convert_enum_to_dict(cls)

    @classmethod
    def resolve(cls, val):
        for i in cls:
            if i.value == val:
                return i.name
        return val

    @classmethod
    def get_visible_name(cls, code):
        """
        Retrieves the visible name associated with the provided code. This method searches
        through the class attributes and matches the provided code against the attribute's
        code value. If a match is found, the corresponding visible name is returned; otherwise,
        it returns None.

        :param code: The code to be matched against the class attributes.
        :type code: Any
        :return: The visible name corresponding to the provided code, or None if no match
                 is found.
        :rtype: Optional[str]
        """
        for i in cls:
            if i.code == code:
                return i.visible_name
        return None

    @classmethod
    def get_full_representation(cls):
        """
        Constructs and returns a complete representation of the class by iterating over
        the class itself, extracting raw values, and appending all elements of the
        `StandardEnumItem` to the resulting list if a raw value is of that type.

        :rtype: list
        :return: A list representing the full collection of `all` attributes from
            `StandardEnumItem` instances within the class' iterable construct.
        """
        representation = []
        for i in cls:
            raw_value = i.raw_value
            if isinstance(raw_value, StandardEnumItem):
                representation.append(raw_value.all)
        return representation
