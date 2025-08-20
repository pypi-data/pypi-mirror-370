from gql import gql
from typing import Sequence

class getMethods:

    _GetProviderQuery = """
    query GetProvider($provider: String!) {
  Providers(where: {name: {_eq: $provider}}) {
    name
    id
  }
}
    """

    def GetProvider(self, provider: str):
        query = gql(self._GetProviderQuery)
        variables = {
            "provider": provider,
        }
        operation_name = "GetProvider"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetProvidersQuery = """
    query GetProviders {
  Providers {
    name
    id
    ProviderDomains {
      domain_regex
    }
  }
}
    """

    def GetProviders(self):
        query = gql(self._GetProvidersQuery)
        variables = {
        }
        operation_name = "GetProviders"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
