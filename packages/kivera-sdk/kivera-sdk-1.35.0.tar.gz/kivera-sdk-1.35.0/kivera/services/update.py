from gql import gql
from typing import Sequence

class updateMethods:

    _UpdateServiceQuery = """
    mutation UpdateService($id: Int!, $inspection: services_inspection_modes!) {
  update_Services_by_pk(pk_columns: {id: $id}, _set: {inspection: $inspection}) {
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

    def UpdateService(self, id: int, inspection: dict):
        query = gql(self._UpdateServiceQuery)
        variables = {
            "id": id,
            "inspection": inspection,
        }
        operation_name = "UpdateService"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
