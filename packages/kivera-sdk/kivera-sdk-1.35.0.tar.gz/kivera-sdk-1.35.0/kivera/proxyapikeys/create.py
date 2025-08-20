from gql import gql
from typing import Sequence

class createMethods:

    _CreateProxyApiKeyQuery = """
    mutation CreateProxyApiKey($object: ProxyApiKeys_insert_input!) {
  insert_ProxyApiKeys_one(object: $object) {
    api_key
    id
    proxy_id
  }
}
    """

    def CreateProxyApiKey(self, object: dict):
        query = gql(self._CreateProxyApiKeyQuery)
        variables = {
            "object": object,
        }
        operation_name = "CreateProxyApiKey"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
