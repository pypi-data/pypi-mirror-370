from gql import gql
from typing import Sequence

class deleteMethods:

    _DeleteServiceQuery = """
    mutation DeleteService($id: Int!) {
  delete_Services_by_pk(id:$id) {
    id
    organization_id
    inspection
    GlobalService {
      id
      provider_id
      Provider {
        name
      }
    }
  }
}
    """

    def DeleteService(self, id: int):
        query = gql(self._DeleteServiceQuery)
        variables = {
            "id": id,
        }
        operation_name = "DeleteService"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
