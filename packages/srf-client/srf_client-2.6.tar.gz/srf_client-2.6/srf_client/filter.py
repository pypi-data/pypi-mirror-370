"""
Use with listing methods to filter the results.

    .. code:: python

        srf.trips.find_all(distance=between(0, 50))

Related entities can be traversed, which requires using dict syntax:

    .. code:: python

        srf.trips.find_all(**{'vehicle.make': eq('Scania')})

.. warning::
    Using unsupported operators for a field type will give unexpected
    results.
"""

from abc import ABC
from datetime import date, datetime, timedelta
from math import isinf
from numbers import Real
from typing import Any, Union

from geopy import Point
from geopy.distance import Distance

__all__ = [
    'Equals', 'Prefix', 'Between', 'Contains', 'AnyOf', 'Near',
    'eq', 'prefix', 'between', 'contains', 'any_of', 'near'
]


class Operator(ABC):
    def __init__(self, *values: str):
        self.values = values

    def __iter__(self):
        return iter(self.values)

    @staticmethod
    def _convert(value: Any) -> str:
        if isinstance(value, (date, datetime)):
            return value.isoformat(timespec='milliseconds')
        elif isinstance(value, timedelta):
            return f'P{value.days}DT{value.seconds}.{value.microseconds:06}S'
        elif isinstance(value, Real) and isinf(value):
            return 'Infinity' if value > 0 else '-Infinity'
        else:
            return str(value)


class Equals(Operator):
    """Field equals value."""

    def __init__(self, value: Any):
        super().__init__(self._convert(value))


class Prefix(Operator):
    """String field starts with value."""

    def __init__(self, value: Union[str, bytes]):
        super().__init__(str(value) + '*')


class Between(Operator):
    """Field is between two values (inclusive)."""

    def __init__(self, v1: Any, v2: Any):
        super().__init__(self._convert(v1), self._convert(v2))


class Contains(Operator):
    """Array field contains value(s)."""

    def __init__(self, *values: Any):
        super().__init__(*(self._convert(v) for v in values))


class AnyOf(Operator):
    """String field matches any of these operators."""

    def __init__(self, *args: Operator):
        super().__init__(*(v for op in args for v in op.values))


class Near(Operator):
    """Point is within region centred on point."""

    def __init__(self, point: Point, distance: Distance):
        super().__init__(f'({point.latitude},{point.longitude}),{distance.km}')


eq = Equals
prefix = Prefix
between = Between
contains = Contains
any_of = AnyOf
near = Near
