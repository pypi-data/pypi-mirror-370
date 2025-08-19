from .model import Order, Route
from .paging import Page, PagingClient
from .util import parse_datetime, parse_distance


class OrdersClient(PagingClient[Order]):
    """
    Access to Orders API.

    Acquire an instance via ``SRFData.orders``.
    """

    def __init__(self, client):  # noqa: D107
        super().__init__(client, 'orders')

    def _parse_obj(self, data, uri) -> Order:
        return Order(
            client=self._client,
            uri=uri,
            route_uri=data['route']['_location'],
            time_window_start=parse_datetime(data.get('timeWindowStart')),
            time_window_end=parse_datetime(data.get('timeWindowEnd')),
            pickup=data.get('pickup'),
            pickup_arrive=parse_datetime(data.get('pickupArrive')),
            pickup_depart=parse_datetime(data.get('pickupDepart')),
            destination=data.get('destination'),
            destination_arrive=parse_datetime(data.get('destinationArrive')),
            destination_depart=parse_datetime(data.get('destinationDepart')),
            ambient=data.get('ambient'),
            chilled=data.get('chilled'),
            frozen=data.get('frozen'),
            weight=data.get('weight'),
            distance=parse_distance(data.get('distance'))
        )

    def find_all(self, lazy=False, **kwargs) -> Page[Order]:
        """
        Find all known orders.

        :param lazy: Defer fetching of the Order objects
        :param kwargs: Additional field filters
        """
        params = {'includeItems': not lazy, **self._filter_params(**kwargs)}
        return self.get_page('/orders', params)

    def find_by_route(self, route: Route, lazy=False, **kwargs) -> Page[Order]:
        """
        Find all orders for the given route.

        :param route: Parent route object
        :param lazy: Defer fetching of the Leg objects
        :param kwargs: Additional field filters
        """
        return self.find_by(route, lazy, **kwargs)
