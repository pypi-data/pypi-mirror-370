from typing import Optional

from immutabledict import immutabledict

from .model import ExternalVehicleClass, VehicleClass
from .paging import Page, PagingClient


class VehicleClassesClient(PagingClient[VehicleClass]):
    """
    Access to VehicleClass API.

    Acquire an instance via ``SRFData.vehicle_classes``.
    """

    def __init__(self, client):  # noqa: D107
        super().__init__(client, 'vehicle_classes')

    def _parse_obj(self, data, uri) -> VehicleClass:
        return VehicleClass(
            client=self._client,
            uri=uri,
            org_uri=data['organisation']['_location'],
            description=data.get('description'),
            make=data.get('make'),
            model=data.get('model'),
            type=data.get('type'),
            fuel=data.get('fuel'),
            fuel_capacity=data.get('fuelCapacity'),
            fuel_efficiency=data.get('fuelEfficiency'),
            weight_class=data.get('weightClass'),
            euro_standard=data.get('euroStandard'),
            drive_power=data.get('drivePower'),
            fridge_power=data.get('fridgePower'),
            limits=immutabledict(data.get('limits', {}))
        )

    def find_all(self, lazy=False, **kwargs) -> Page[VehicleClass]:
        """
        Find all known vehicle_classes.

        :param lazy: Defer fetching of the VehicleClass objects
        :param kwargs: Additional field filters
        """
        params = {'includeItems': not lazy, **self._filter_params(**kwargs)}
        return self.get_page('/vehicle_classes', params)

    def lookup(self, registration: str) -> Optional[ExternalVehicleClass]:
        """
        Lookup vehicle details from an external system, e.g. the DVLA.

        :param registration: Vehicle registration to find
        """
        response = self._client.get(f'/{self._fragment}/lookup',
                                    params={'registration': registration})
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        return ExternalVehicleClass(
            description=data.get('description'),
            make=data.get('make'),
            model=data.get('model'),
            type=data.get('type'),
            fuel=data.get('fuel'),
            fuel_capacity=data.get('fuelCapacity'),
            fuel_efficiency=data.get('fuelEfficiency'),
            weight_class=data.get('weightClass'),
            euro_standard=data.get('euroStandard'),
            drive_power=data.get('drivePower'),
            fridge_power=data.get('fridgePower')
        )
