from gql import gql
from typing import Sequence

class getMethods:

    _GetProxyApiKeyQuery = """
    query GetProxyApiKey($proxy_id: Int!) {
  ProxyApiKeys(where: {proxy_id: {_eq: $proxy_id}}) {
    proxy_id
    id
    api_key
    Proxy {
      id
      organization_id
      status
    }
  }
}
    """

    def GetProxyApiKey(self, proxy_id: int):
        query = gql(self._GetProxyApiKeyQuery)
        variables = {
            "proxy_id": proxy_id,
        }
        operation_name = "GetProxyApiKey"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
