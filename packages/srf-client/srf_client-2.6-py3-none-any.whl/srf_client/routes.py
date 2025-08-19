from .model import Location, Route, VehicleClass
from .paging import Page, PagingClient
from .util import parse_datetime, parse_distance


class RoutesClient(PagingClient[Route]):
    """
    Access to Routes API.

    Acquire an instance via ``SRFData.routes``.
    """

    def __init__(self, client):  # noqa: D107
        super().__init__(client, 'routes')

    def _parse_obj(self, data, uri) -> Route:
        return Route(
            client=self._client,
            uri=uri,
            org_uri=data['organisation']['_location'],
            start_location_uri=data['startLocation']['_location'],
            end_location_uri=data['endLocation']['_location'],
            depot_uri=data['depot']['_location'],
            vehicle_class_uri=data['vehicleClass']['_location'],
            plan=data['plan'],
            start_time=parse_datetime(data['startTime']),
            end_time=parse_datetime(data['endTime']),
            orders=data['orders'],
            shift_start=parse_datetime(data.get('shiftStart')),
            shift_end=parse_datetime(data.get('shiftEnd')),
            distance=parse_distance(data.get('distance')),
            registration=data.get('registration'),
            total_units=data.get('totalUnits'),
            total_weight=data.get('totalWeight')
        )

    def find_all(self, lazy=False, **kwargs) -> Page[Route]:
        """
        Find all known routes.

        :param lazy: Defer fetching of the Route objects
        :param kwargs: Additional field filters
        """
        params = {'includeItems': not lazy, **self._filter_params(**kwargs)}
        return self.get_page('/routes', params)

    def find_by_location(self, location: Location, lazy=False, **kwargs) \
            -> Page[Route]:
        """
        Find all routes involving the given location.

        :param location: Parent location object
        :param lazy: Defer fetching of the Route objects
        :param kwargs: Additional field filters
        """
        return self.find_by(location, lazy, **kwargs)

    def find_by_vehicle_class(self, vehicle_class: VehicleClass, lazy=False,
                              **kwargs) -> Page[Route]:
        """
        Find all routes using the given vehicle class.

        :param vehicle_class: Parent vehicle class object
        :param lazy: Defer fetching of the Route objects
        :param kwargs: Additional field filters
        """
        return self.find_by(vehicle_class, lazy, **kwargs)
