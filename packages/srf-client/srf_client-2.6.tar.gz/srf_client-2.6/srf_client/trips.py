from .model import Trailer, Trial, Trip, Vehicle
from .paging import Page, PagingClient
from .util import parse_datetime, parse_distance


class TripsClient(PagingClient[Trip]):
    """
    Access to trips API.

    Acquire an instance via ``SRFData.trips``.
    """

    def __init__(self, client):  # noqa: D107
        super().__init__(client, 'trips')

    def _parse_obj(self, data, uri) -> Trip:
        return Trip(
            client=self._client,
            uri=uri,
            source=data['source'],
            types=frozenset(data['types']),
            start_time=parse_datetime(data.get('startTime')),
            end_time=parse_datetime(data.get('endTime')),
            consumption=data.get('consumption'),
            distance=parse_distance(data.get('distance')),
            trailer_uri=data['trailer']['_location'],
            trial_uri=data['trial']['_location'],
            vehicle_uri=data['vehicle']['_location']
        )

    def find_all(self, lazy=False, **kwargs) -> Page[Trip]:
        """
        Find all recorded trips.

        :param lazy: Defer fetching of the Trip objects
        :param kwargs: Additional field filters
        """
        params = {'includeItems': not lazy, **self._filter_params(**kwargs)}
        return self.get_page('/trips', params)

    def find_by_vehicle(self, vehicle: Vehicle, lazy=False, **kwargs) \
            -> Page[Trip]:
        """
        Find all trips for the given vehicle.

        :param vehicle: Parent vehicle object
        :param lazy: Defer fetching of the Trip objects
        :param kwargs: Additional field filters
        """
        return self.find_by(vehicle, lazy, **kwargs)

    def find_by_trial(self, trial: Trial, lazy=False, **kwargs) -> Page[Trip]:
        """
        Find all trips for the given trial.

        :param trial: Parent trial object
        :param lazy: Defer fetching of the Trip objects
        :param kwargs: Additional field filters
        """
        return self.find_by(trial, lazy, **kwargs)

    def find_by_trailer(self, trailer: Trailer, lazy=False, **kwargs) \
            -> Page[Trip]:
        """
        Find all trips for the given trailer.

        :param trailer: Parent trailer object
        :param lazy: Defer fetching of the Trip objects
        :param kwargs: Additional field filters
        """
        return self.find_by(trailer, lazy, **kwargs)
