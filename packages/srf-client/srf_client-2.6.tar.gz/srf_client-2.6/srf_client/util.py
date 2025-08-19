import abc
import attrs
import sys
from datetime import datetime
from typing import Optional, TYPE_CHECKING

import lazy_object_proxy
from geopy import Point
from geopy.distance import Distance, geodesic

if sys.version_info < (3, 11):
    # noinspection PyUnresolvedReferences
    from iso8601 import parse_date as _fromisoformat
else:
    _fromisoformat = datetime.fromisoformat

if TYPE_CHECKING:
    from .paging import PagingClient


def parse_point(data) -> Optional[Point]:
    """Parse returned data into a ``Point`` object."""
    if data is None:
        return None
    else:
        return Point(data.get("lat"), data.get("lon"), data.get("alt"))


def parse_distance(value, unit='kilometers') -> Optional[Distance]:
    """Parse returned data into a ``Distance`` object."""
    if value is None:
        return None
    else:
        return geodesic(**{unit: value})


def parse_datetime(value) -> Optional[datetime]:
    """Parse returned data into a ``datetime`` object."""
    if value is None:
        return None
    else:
        return _fromisoformat(value)


@attrs.frozen(kw_only=True, eq=False)
class UriObject(abc.ABC):
    """Shared base for objects with a URI."""

    uri: str

    def __eq__(self, other) -> bool:
        return self.uri == other.uri

    def __hash__(self) -> int:
        return hash(self.uri)


class UriProxy(lazy_object_proxy.Proxy):
    """Transparent proxy for objects with a URI."""

    uri: str = None

    def __init__(self, uri: str, client: 'PagingClient'):
        """Initialize proxy with URI and typed client."""
        super().__init__(lambda: client.get(uri=uri))
        self.uri = uri

    def __eq__(self, other) -> bool:
        return self.uri == other.uri

    def __ne__(self, other) -> bool:
        return self.uri != other.uri

    def __hash__(self) -> int:
        return hash(self.uri)
