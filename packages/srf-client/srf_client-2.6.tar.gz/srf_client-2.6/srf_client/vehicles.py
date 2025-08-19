from typing import Optional

from .model import Vehicle
from .paging import Page, PagingClient


class VehiclesClient(PagingClient[Vehicle]):
    """
    Access to vehicles API.

    Acquire an instance via ``SRFData.vehicles``.
    """

    def __init__(self, client):  # noqa: D107
        super().__init__(client, 'vehicles')

    def _parse_obj(self, data, uri) -> Vehicle:
        return Vehicle(
            client=self._client,
            uri=uri,
            registration=data.get('registration'),
            vin=data.get('vin'),
            calibrated=data.get('calibrated', False),
            make=data.get('make'),
            model=data.get('model'),
            type=data.get('type'),
            fuel=data.get('fuel'),
            weight_class=data.get('weightClass'),
            euro_standard=data.get('euroStandard'),
            description=data.get('description'),
            outfit_weight=data.get('outfitWeight'),
            country=data.get('country'),
            org_uri=data['organisation']['_location']
        )

    def get(self, *, uri=None, obj_id=None) -> Optional[Vehicle]:
        """
        Get a single vehicle by its URI or unique identifier.

        :param uri: Uniform resource locator
        :param obj_id: Vehicle registration, VIN, or internal ID.
        """
        return super().get(uri=uri, obj_id=obj_id)

    def find_all(self, lazy=False, **kwargs) -> Page[Vehicle]:
        """
        Find all known vehicles.

        :param lazy: Defer fetching of the Vehicle objects
        :param kwargs: Additional field filters
        """
        params = {'includeItems': not lazy, **self._filter_params(**kwargs)}
        return self.get_page('/vehicles', params)
