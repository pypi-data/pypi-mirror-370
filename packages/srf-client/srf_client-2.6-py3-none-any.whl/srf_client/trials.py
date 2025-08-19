from .model import Trial
from .paging import Page, PagingClient


class TrialsClient(PagingClient[Trial]):
    """
    Access to Trials API.

    Acquire an instance via ``SRFData.trials``.
    """

    def __init__(self, client):  # noqa: D107
        super().__init__(client, 'trials')

    def _parse_obj(self, data, uri) -> Trial:
        return Trial(
            client=self._client,
            uri=uri,
            description=data['description'],
            org_uri=data['organisation']['_location'],
            active=data.get('active')
        )

    def find_all(self, lazy=False, **kwargs) -> Page[Trial]:
        """
        Find all known trials.

        :param lazy: Defer fetching of the Trial objects
        :param kwargs: Additional field filters
        """
        params = {'includeItems': not lazy, **self._filter_params(**kwargs)}
        return self.get_page('/trials', params)
