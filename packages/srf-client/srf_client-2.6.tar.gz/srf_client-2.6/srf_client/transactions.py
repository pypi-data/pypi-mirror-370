from typing import Iterable

from .model import Charger, ChargerTransaction, ChargerMeter, Vehicle
from .paging import Page, PagingClient
from .util import parse_datetime


class TransactionsClient(PagingClient[ChargerTransaction]):
    """
    Access to transactions API.

    Acquire an instance via ``SRFData.transactions``.
    """

    def __init__(self, client):  # noqa: D107
        super().__init__(client, 'transactions')

    def _parse_obj(self, data, uri) -> ChargerTransaction:
        return ChargerTransaction(
            client=self._client,
            uri=uri,
            charger_uri=data['charger']['_location'],
            vehicle_uri=data['vehicle']['_location'],
            connector=data['connector'],
            start_time=parse_datetime(data['startTime']),
            end_time=parse_datetime(data.get('endTime')),
            start_meter=data['startMeter'],
            end_meter=data.get('endMeter')
        )

    def find_all(self, lazy=False, **kwargs) -> Page[ChargerTransaction]:
        """
        Find all recorded charging transactions.

        :param lazy: Defer fetching of the ChargerTransaction objects
        :param kwargs: Additional field filters
        """
        params = {'includeItems': not lazy, **self._filter_params(**kwargs)}
        return self.get_page('/transactions', params)

    def find_by_charger(self, charger: Charger, lazy=False, **kwargs) \
            -> Page[ChargerTransaction]:
        """
        Find all transactions for the given charger.

        :param charger: Parent charger object
        :param lazy: Defer fetching of the ChargerTransaction objects
        :param kwargs: Additional field filters
        """
        return self.find_by(charger, lazy, **kwargs)

    def find_by_vehicle(self, vehicle: Vehicle, lazy=False, **kwargs) \
            -> Page[ChargerTransaction]:
        """
        Find all transactions for the given vehicle.

        :param vehicle: Parent vehicle object
        :param lazy: Defer fetching of the ChargerTransaction objects
        :param kwargs: Additional field filters
        """
        return self.find_by(vehicle, lazy, **kwargs)

    def get_data(self, transaction: ChargerTransaction) \
            -> Iterable[ChargerMeter]:
        """
        Fetch meter readings for transaction.

        :param transaction: Parent transaction object
        """
        response = self._client.get(transaction.uri + '/data')
        response.raise_for_status()
        return (ChargerMeter(
            timestamp=parse_datetime(item['timestamp']),
            value=item['value']
        ) for item in response.json())
