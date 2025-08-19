from .model import Charger, Location, ChargerStatus
from .paging import Page, PagingClient
from .util import parse_datetime


class ChargersClient(PagingClient[Charger]):
    """
    Access to chargers API.

    Acquire an instance via ``SRFData.chargers``.
    """

    def __init__(self, client):  # noqa: D107
        super().__init__(client, 'chargers')
        self._status_client = _ChargerStatusClient(client)

    def _parse_obj(self, data, uri) -> Charger:
        return Charger(
            client=self._client,
            uri=uri,
            org_uri=data['organisation']['_location'],
            location_uri=data['location']['_location'],
            label=data['label']
        )

    def find_all(self, lazy=False, **kwargs) -> Page[Charger]:
        """
        Find all known chargers.

        :param lazy: Defer fetching of the Charger objects
        :param kwargs: Additional field filters
        """
        params = {'includeItems': not lazy, **self._filter_params(**kwargs)}
        return self.get_page('/chargers', params)

    def find_by_location(self, location: Location, lazy=False, **kwargs) \
            -> Page[Charger]:
        """
        Find all chargers at the given location.

        :param location: Parent location object
        :param lazy: Defer fetching of the Trip objects
        :param kwargs: Additional field filters
        """
        return self.find_by(location, lazy, **kwargs)

    def find_status(self, charger: Charger, **kwargs) -> Page[ChargerStatus]:
        """
        Get charger status.

        :param charger: Charger to query
        :param kwargs: Additional field filters
        """
        params = self._filter_params(**kwargs)
        return self._status_client.get_page(charger.uri + '/status', params)


class _ChargerStatusClient(PagingClient[ChargerStatus]):
    def __init__(self, client):
        super().__init__(client, None)

    def _parse_item(self, data) -> ChargerStatus:
        return self._parse_obj(data, NotImplemented)

    def _parse_obj(self, data, uri) -> ChargerStatus:
        return ChargerStatus(
            connector=data['connector'],
            timestamp=parse_datetime(data['timestamp']),
            status=data['status'],
            error=data['error'],
            message=data.get('message')
        )
