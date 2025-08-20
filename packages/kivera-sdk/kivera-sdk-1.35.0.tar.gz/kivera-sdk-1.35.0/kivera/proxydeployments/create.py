from gql import gql
from typing import Sequence

class createMethods:

    _CreateProxyDeploymentQuery = """
    mutation CreateProxyDeployment($proxy_id: Int!, $status: String!, $config_version: String!, $config: jsonb) {
  insert_ProxyDeployments(objects: {config: $config, config_version: $config_version, proxy_id: $proxy_id, status: $status}) {
    affected_rows
  }
}
    """

    def CreateProxyDeployment(self, proxy_id: int, status: str, config_version: str, config: dict = None):
        query = gql(self._CreateProxyDeploymentQuery)
        variables = {
            "proxy_id": proxy_id,
            "status": status,
            "config_version": config_version,
            "config": config,
        }
        operation_name = "CreateProxyDeployment"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
