from gql import gql
from typing import Sequence

class listMethods:

    _ListProxyProviderVersionsQuery = """
    query ListProxyProviderVersions {
    ProviderVersions {
        id
        provider_id
        version_name
        hash
        url
        created
        Provider {
            name
        }
    }
}
    """

    def ListProxyProviderVersions(self):
        query = gql(self._ListProxyProviderVersionsQuery)
        variables = {
        }
        operation_name = "ListProxyProviderVersions"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
