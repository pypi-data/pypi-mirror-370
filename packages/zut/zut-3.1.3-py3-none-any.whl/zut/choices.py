"""
Allow usage of entity classes defined in libraries that may or may not have Django as a dependency depending on the library usage.
"""
from __future__ import annotations

try:
    from django.db.models import Choices, TextChoices, IntegerChoices # type: ignore

except ModuleNotFoundError:
    import enum
    from enum import EnumType
    from types import DynamicClassAttribute as enum_property

    class ChoicesType(EnumType):
        """A metaclass for creating a enum choices."""
        def __new__(metacls, classname, bases, classdict, **kwds):
            labels = []
            for key in classdict._member_names:
                value = classdict[key]
                if isinstance(value, (list, tuple)) and len(value) > 1 and isinstance(value[-1], str):
                    *value, label = value
                    value = tuple(value)
                else:
                    label = key.replace("_", " ").title()
                labels.append(label)
                dict.__setitem__(classdict, key, value) # Use dict.__setitem__() to suppress defenses against double assignment in enum's classdict.
            cls = super().__new__(metacls, classname, bases, classdict, **kwds)
            for member, label in zip(cls.__members__.values(), labels):
                member._label_ = label # type: ignore
            return enum.unique(cls) # type: ignore

    class Choices(enum.Enum, metaclass=ChoicesType):
        """Class for creating enumerated choices."""
        @enum_property
        def label(self):
            return self._label_ # type: ignore

        def __str__(self):
            return str(self.value)
        
        def __repr__(self):
            return f"{self.__class__.__qualname__}.{self._name_}"

    class IntegerChoices(int, Choices):
        """Class for creating enumerated integer choices."""
        pass


    class TextChoices(str, Choices):
        """Class for creating enumerated string choices."""
        @staticmethod
        def _generate_next_value_(name, start, count, last_values):
            return name

__all__ = ("Choices", "IntegerChoices", "TextChoices",)
