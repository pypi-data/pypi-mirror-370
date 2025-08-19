from .model import Fleet, FleetEntry
from .paging import Page, PagingClient


class FleetsClient(PagingClient[Fleet]):
    """
    Access to Fleets API.

    Acquire an instance via ``SRFData.fleets``.
    """

    def __init__(self, client):  # noqa: D107
        super().__init__(client, 'fleets')
        self._entries = FleetEntriesClient(client)

    def _parse_obj(self, data, uri) -> Fleet:
        return Fleet(
            client=self._client,
            uri=uri,
            org_uri=data['organisation']['_location'],
            name=data['name'],
            entries=tuple(e for e in self._entries.find_by_fleet(uri))
        )

    def find_all(self, lazy=False, **kwargs) -> Page[Fleet]:
        """
        Find all known fleets.

        :param lazy: Defer fetching of the Fleet objects
        :param kwargs: Additional field filters
        """
        params = {'includeItems': not lazy, **self._filter_params(**kwargs)}
        return self.get_page('/fleets', params)


class FleetEntriesClient(PagingClient[FleetEntry]):
    """Internal access to Fleet Entries API."""

    def __init__(self, client):  # noqa: D107
        super().__init__(client, None)

    def _parse_obj(self, data, uri) -> FleetEntry:
        return FleetEntry(
            client=self._client,
            location_uri=data['location']['_location'],
            vehicle_class_uri=data['vehicleClass']['_location'],
            count=data['count']
        )

    def _parse_item(self, data) -> FleetEntry:
        return self._parse_obj(data, NotImplemented)

    def find_by_fleet(self, fleet_uri: str) -> Page[FleetEntry]:
        """
        Get fleet composition entries.

        :param fleet_uri: Fleet to enumerate
        """
        return self.get_page(fleet_uri + '/entries')
