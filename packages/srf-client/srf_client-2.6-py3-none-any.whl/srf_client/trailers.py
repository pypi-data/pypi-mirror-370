from .model import Trailer
from .paging import Page, PagingClient


class TrailersClient(PagingClient[Trailer]):
    """
    Access to trailers API.

    Acquire an instance via ``SRFData.trailers``.
    """

    def __init__(self, client):  # noqa: D107
        super().__init__(client, 'trailers')

    def _parse_obj(self, data, uri) -> Trailer:
        return Trailer(
            client=self._client,
            uri=uri,
            serial=data['serial'],
            length=data.get('length'),
            make=data.get('make'),
            model=data.get('model'),
            type=data.get('type'),
            axles=data.get('axles'),
            tires_per_axle=data.get('tiresPerAxle'),
            description=data.get('description'),
            org_uri=data['organisation']['_location']
        )

    def find_all(self, lazy=False, **kwargs) -> Page[Trailer]:
        """
        Find all known trailers.

        :param lazy: Defer fetching of the Vehicle objects
        :param kwargs: Additional field filters
        """
        params = {'includeItems': not lazy, **self._filter_params(**kwargs)}
        return self.get_page('/trailers', params)
