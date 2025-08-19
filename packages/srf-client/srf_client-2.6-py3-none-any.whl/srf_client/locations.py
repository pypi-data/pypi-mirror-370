from .model import Location
from .paging import Page, PagingClient
from .util import parse_point


class LocationsClient(PagingClient[Location]):
    """
    Access to Locations API.

    Acquire an instance via ``SRFData.locations``.
    """

    def __init__(self, client):  # noqa: D107
        super().__init__(client, 'locations')

    def _parse_obj(self, data, uri) -> Location:
        return Location(
            client=self._client,
            uri=uri,
            org_uri=data['organisation']['_location'],
            name=data.get('name'),
            post_code=data.get('postCode'),
            point=parse_point(data.get('point'))
        )

    def find_all(self, lazy=False, **kwargs) -> Page[Location]:
        """
        Find all known locations.

        :param lazy: Defer fetching of the Location objects
        :param kwargs: Additional field filters
        """
        params = {'includeItems': not lazy, **self._filter_params(**kwargs)}
        return self.get_page('/locations', params)
