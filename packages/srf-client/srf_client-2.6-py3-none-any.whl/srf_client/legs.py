import time
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from typing import Collection, Iterable, Union

from .model import Calibration, Leg, Measurement, Trip
from .paging import Page, PagingClient
from .util import parse_datetime, parse_distance, parse_point


class LegsClient(PagingClient[Leg]):
    """
    Access to legs API.

    Acquire an instance via ``SRFData.trips``.
    """

    def __init__(self, client):  # noqa: D107
        super().__init__(client, 'legs')

    def _parse_obj(self, data, uri) -> Leg:
        return Leg(
            client=self._client,
            uri=uri,
            trip_uri=data['trip']['_location'],
            start_time=parse_datetime(data['startTime']),
            end_time=parse_datetime(data['endTime']),
            types=frozenset(data['types']),
            start_location=parse_point(data.get('startLocation')),
            end_location=parse_point(data.get('endLocation')),
            start_distance=parse_distance(data.get('startDistance')),
            end_distance=parse_distance(data.get('endDistance')),
            consumption=data.get('consumption'),
            fuel_level=data.get('fuelLevel'),
            weight=data.get('weight'),
            weight_source=data.get('weightSource'),
            destination=data.get('destination')
        )

    def find_all(self, lazy=False, **kwargs) -> Page[Leg]:
        """
        Find all recorded legs.

        :param lazy: Defer fetching of the Leg objects
        :param kwargs: Additional field filters
        """
        params = {'includeItems': not lazy, **self._filter_params(**kwargs)}
        return self.get_page('/legs', params)

    def find_by_trip(self, trip: Trip, lazy=False, **kwargs) -> Page[Leg]:
        """
        Find all legs for the given trip.

        :param trip: Parent trip object
        :param lazy: Defer fetching of the Leg objects
        :param kwargs: Additional field filters
        """
        return self.find_by(trip, lazy, **kwargs)

    def get_calibration(self, leg: Leg) -> Calibration:
        """Return the raw calibration data for a given leg."""
        response = self._client.get(leg.uri + '/data', stream=True)
        response.raise_for_status()
        header = next(response.iter_lines(decode_unicode=True))
        parts = header.split(',')
        return Calibration(
            forward=tuple(float(n) for n in parts[5].split(':')),
            left=tuple(float(n) for n in parts[6].split(':')),
            up=tuple(float(n) for n in parts[7].split(':')),
            inv_gravity=tuple(float(n) for n in parts[8].split(':'))
        )

    def get_data(
        self,
        leg: Leg,
        include: Union[str, Collection, None] = None,
        include_can_source: bool = None
    ) -> Iterable[Measurement]:
        """
        Return available measurements.

        :param leg: Parent leg object
        :param include: Data types to include. By default, all are included.
        :param include_can_source: Include additional field with CAN data.

        .. versionchanged:: 2.3
           Added ``include_can_source`` parameter.
        """
        params = {}
        if isinstance(include, str):
            params['include'] = [include]
        elif include is not None:
            params['include'] = list(include)
        if include_can_source is not None:
            params['include_can_source'] = include_can_source

        response = self._client.get(leg.uri + '/data',
                                    params=params,
                                    stream=True)
        response.raise_for_status()
        it = response.iter_lines(decode_unicode=True)
        return (m for m in (Measurement(*line.split(',', maxsplit=2))
                            for line in it if line)
                if m.data)

    def get_raw_data(
        self,
        leg: Leg,
        include: Union[str, Collection, None] = None
    ) -> Iterable[str]:
        """
        Return the raw data. Format depends on source.

        :param leg: Parent leg object
        :param include: Data types to include. By default, all are included.
        """
        if isinstance(include, str):
            include = [include]
        elif include is not None:
            include = list(include)

        response = self._client.get(leg.uri + '/raw',
                                    params={'include': include},
                                    stream=True)
        response.raise_for_status()
        return response.iter_lines(decode_unicode=True)

    def get_gradient(
        self,
        leg: Leg,
        generate: bool = False,
        timeout: timedelta = timedelta(minutes=5)
    ) -> Iterable[Measurement]:
        """
        Return computed gradient data for the leg.

        :param leg: Parent leg object
        :param generate: Request and wait for generation if not available
        :param timeout: How long to wait if requesting generation
        """
        start_time = datetime.now(tz=timezone.utc)

        response = self._client.get(leg.uri + '/gradient', stream=True)
        if response.status_code == 404:
            if not generate:
                return []

            headers = {'If-Unmodified-Since': format_datetime(start_time,
                                                              usegmt=True)}
            response = self._client.post(leg.uri + '/gradient',
                                         headers=headers)
            if response.status_code not in (202, 409, 412):
                response.raise_for_status()

            while start_time + timeout > datetime.now(tz=timezone.utc):
                time.sleep(1)
                response = self._client.get(leg.uri + '/gradient', stream=True)
                if response.status_code == 200:
                    break
                elif response.status_code == 404:
                    continue
                else:
                    response.raise_for_status()
            else:
                raise TimeoutError

        response.raise_for_status()
        it = response.iter_lines(decode_unicode=True)
        return (m for m in (Measurement(*line.split(',', maxsplit=2))
                            for line in it if line)
                if m.data)
