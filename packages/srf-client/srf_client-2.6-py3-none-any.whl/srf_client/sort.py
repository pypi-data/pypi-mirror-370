"""
Can be passed with field filters to control the sort order.

    .. code:: python

        srf.organisations.find_all(sort=asc('name'))

"""

from abc import ABC

__all__ = [
    'Ascending', 'Descending',
    'asc', 'desc'
]


class Sort(ABC):
    def __init__(self, field: str, direction: str):
        self.field = field
        self.direction = direction

    def __str__(self):
        return f'{self.field},{self.direction}'


class Ascending(Sort):
    """
    Ascending sort order.

    :param field: Field to sort by
    """

    def __init__(self, field: str):
        super().__init__(field, 'asc')


class Descending(Sort):
    """
    Descending sort order.

    :param field: Field to sort by
    """

    def __init__(self, field: str):
        super().__init__(field, 'desc')


asc = Ascending
desc = Descending
