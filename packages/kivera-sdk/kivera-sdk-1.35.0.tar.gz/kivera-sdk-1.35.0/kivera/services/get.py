from gql import gql
from typing import Sequence

class getMethods:

    _GetServiceQuery = """
    query GetService($service_name: String!) {
  Services(where: {GlobalService: {name: {_eq: $service_name}}}) {
    id
    inspection
    GlobalService {
      id
      name
      title
      description
      Provider {
        id
        name
      }
    }
    organization_id
  }
}
    """

    def GetService(self, service_name: str):
        query = gql(self._GetServiceQuery)
        variables = {
            "service_name": service_name,
        }
        operation_name = "GetService"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetServiceV2Query = """
    query GetServiceV2($id: Int!) {
  Services_by_pk(id: $id) {
    id
    organization_id
    inspection
    GlobalService {
      id
      name
      title
      description
      Provider {
        id
        name
      }
    }
  }
}
    """

    def GetServiceV2(self, id: int):
        query = gql(self._GetServiceV2Query)
        variables = {
            "id": id,
        }
        operation_name = "GetServiceV2"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
