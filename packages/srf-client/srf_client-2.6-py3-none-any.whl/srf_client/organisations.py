from .model import Organisation
from .paging import Page, PagingClient


class OrganisationsClient(PagingClient[Organisation]):
    """
    Access to Organisations API.

    Acquire an instance via ``SRFData.organisations``.
    """

    def __init__(self, client):  # noqa: D107
        super().__init__(client, 'organisations')

    def _parse_obj(self, data, uri) -> Organisation:
        return Organisation(
            client=self._client,
            uri=uri,
            name=data['name']
        )

    def find_all(self, lazy=False, **kwargs) -> Page[Organisation]:
        """
        Find all known organisations.

        :param lazy: Defer fetching of the Organisation objects
        :param kwargs: Additional field filters
        """
        params = {'includeItems': not lazy, **self._filter_params(**kwargs)}
        return self.get_page('/organisations', params)
